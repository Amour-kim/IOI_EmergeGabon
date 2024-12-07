from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.utils import timezone
from django.conf import settings
import weasyprint
import os

from ..models import DossierInscription, Certificat
from ..serializers import CertificatSerializer
from ..permissions import IsAdminOrScolarite, IsOwnerOrAdmin
from ..utils import generer_qr_code

class DocumentViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    
    def get_dossier(self, pk):
        """Récupère un dossier et vérifie les permissions"""
        dossier = get_object_or_404(DossierInscription, pk=pk)
        if not (
            self.request.user.is_staff or
            self.request.user == dossier.etudiant
        ):
            raise PermissionDenied()
        return dossier
    
    def generer_document(self, dossier, type_certificat, template_name):
        """Génère un document PDF à partir d'un template"""
        # Vérification du statut du dossier
        if dossier.statut != 'VALIDE':
            return Response(
                {'statut': 'Le dossier doit être validé'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Génération du numéro unique
        prefix = {
            'SCOLARITE': 'CS',
            'INSCRIPTION': 'AI',
            'CARTE': 'CE'
        }[type_certificat]
        numero = f"{prefix}-{dossier.etudiant.matricule}"
        
        # Génération du QR code pour la vérification
        qr_code = generer_qr_code(
            f"{settings.SITE_URL}/verifier/{numero}"
        )
        
        # Contexte pour le template
        context = {
            'etudiant': dossier.etudiant,
            'dossier': dossier,
            'universite': {
                'nom': settings.NOM_UNIVERSITE,
                'nom_court': settings.NOM_COURT_UNIVERSITE,
                'adresse': settings.ADRESSE_UNIVERSITE,
                'ville': settings.VILLE_UNIVERSITE,
                'site_web': settings.SITE_URL,
                'recteur': settings.RECTEUR,
            },
            'qr_code_url': qr_code,
            'logo_url': settings.LOGO_URL,
        }
        
        # Génération du HTML
        html = render_to_string(template_name, context)
        
        # Génération du PDF
        pdf = weasyprint.HTML(string=html).write_pdf()
        
        # Sauvegarde du fichier
        filename = f'{type_certificat.lower()}_{numero}.pdf'
        filepath = os.path.join('certificats', filename)
        
        # Création ou mise à jour du certificat
        certificat = Certificat.objects.filter(
            dossier=dossier,
            type_certificat=type_certificat
        ).first()
        
        if not certificat:
            certificat = Certificat(
                dossier=dossier,
                type_certificat=type_certificat
            )
        
        certificat.numero = numero
        certificat.valide_jusqu_au = timezone.now().date().replace(
            month=9, day=30
        )
        if timezone.now().month >= 9:
            certificat.valide_jusqu_au = certificat.valide_jusqu_au.replace(
                year=certificat.valide_jusqu_au.year + 1
            )
        
        # Sauvegarde du fichier dans le storage
        with open(filepath, 'wb') as f:
            f.write(pdf)
        certificat.fichier.name = filepath
        certificat.save()
        
        return Response(
            CertificatSerializer(certificat).data,
            status=status.HTTP_201_CREATED
        )
    
    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAdminOrScolarite]
    )
    def certificat_scolarite(self, request, pk=None):
        """Génère un certificat de scolarité"""
        dossier = self.get_dossier(pk)
        return self.generer_document(
            dossier,
            'SCOLARITE',
            'inscriptions/certificat_scolarite.html'
        )
    
    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAdminOrScolarite]
    )
    def attestation_inscription(self, request, pk=None):
        """Génère une attestation d'inscription"""
        dossier = self.get_dossier(pk)
        return self.generer_document(
            dossier,
            'INSCRIPTION',
            'inscriptions/attestation_inscription.html'
        )
    
    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAdminOrScolarite]
    )
    def carte_etudiant(self, request, pk=None):
        """Génère une carte d'étudiant"""
        dossier = self.get_dossier(pk)
        return self.generer_document(
            dossier,
            'CARTE',
            'inscriptions/carte_etudiant.html'
        )
    
    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated]
    )
    def mes_certificats(self, request):
        """Liste les certificats de l'étudiant connecté"""
        certificats = Certificat.objects.filter(
            dossier__etudiant=request.user
        ).order_by('-date_generation')
        return Response(
            CertificatSerializer(
                certificats,
                many=True,
                context={'request': request}
            ).data
        )
    
    @action(detail=False, methods=['get'])
    def verifier(self, request, numero):
        """Vérifie l'authenticité d'un certificat"""
        certificat = get_object_or_404(Certificat, numero=numero)
        return Response({
            'statut': 'VALIDE' if certificat.est_valide else 'EXPIRE',
            'type': certificat.type_certificat,
            'date_generation': certificat.date_generation,
            'valide_jusqu_au': certificat.valide_jusqu_au,
            'etudiant': {
                'matricule': certificat.dossier.etudiant.matricule,
                'nom_complet': certificat.dossier.etudiant.get_full_name(),
                'niveau_etude': certificat.dossier.niveau_etude,
            }
        })
