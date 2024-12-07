from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.utils import timezone
from .models import (
    ConfigurationEmail, CompteEmail, Alias, ListeDiffusion
)
from .serializers import (
    ConfigurationEmailSerializer, CompteEmailSerializer,
    AliasSerializer, ListeDiffusionSerializer
)
from .services import ServiceEmail

class ConfigurationEmailViewSet(viewsets.ModelViewSet):
    """ViewSet pour la configuration email"""
    queryset = ConfigurationEmail.objects.all()
    serializer_class = ConfigurationEmailSerializer
    permission_classes = [permissions.IsAdminUser]
    
    @action(detail=True, methods=['post'])
    def tester_connexion(self, request, pk=None):
        """Teste la connexion aux serveurs email"""
        configuration = self.get_object()
        service = ServiceEmail(configuration)
        
        try:
            # Test SMTP
            smtp = service.get_smtp_connection()
            smtp_ok = True
        except Exception as e:
            smtp_ok = False
            smtp_error = str(e)
        
        try:
            # Test IMAP
            imap = service.get_imap_connection()
            imap_ok = True
        except Exception as e:
            imap_ok = False
            imap_error = str(e)
        
        service.close_connections()
        
        return Response({
            'smtp_ok': smtp_ok,
            'smtp_error': smtp_error if not smtp_ok else None,
            'imap_ok': imap_ok,
            'imap_error': imap_error if not imap_ok else None
        })
    
    @action(detail=True, methods=['post'])
    def verifier_dns(self, request, pk=None):
        """Vérifie les enregistrements DNS"""
        configuration = self.get_object()
        import dns.resolver
        
        resultats = {
            'mx': [],
            'spf': [],
            'dkim': [],
            'dmarc': []
        }
        
        try:
            # Vérification MX
            mx = dns.resolver.resolve(configuration.nom_domaine, 'MX')
            for record in mx:
                resultats['mx'].append(str(record.exchange))
        except Exception as e:
            resultats['mx'] = [f'Erreur: {str(e)}']
        
        try:
            # Vérification SPF
            spf = dns.resolver.resolve(configuration.nom_domaine, 'TXT')
            for record in spf:
                if 'v=spf1' in str(record):
                    resultats['spf'].append(str(record))
        except Exception as e:
            resultats['spf'] = [f'Erreur: {str(e)}']
        
        if configuration.dkim_active:
            try:
                # Vérification DKIM
                selector = configuration.dkim_selector
                dkim = dns.resolver.resolve(
                    f'{selector}._domainkey.{configuration.nom_domaine}',
                    'TXT'
                )
                for record in dkim:
                    resultats['dkim'].append(str(record))
            except Exception as e:
                resultats['dkim'] = [f'Erreur: {str(e)}']
        
        if configuration.dmarc_active:
            try:
                # Vérification DMARC
                dmarc = dns.resolver.resolve(
                    f'_dmarc.{configuration.nom_domaine}',
                    'TXT'
                )
                for record in dmarc:
                    if 'v=DMARC1' in str(record):
                        resultats['dmarc'].append(str(record))
            except Exception as e:
                resultats['dmarc'] = [f'Erreur: {str(e)}']
        
        return Response(resultats)

class CompteEmailViewSet(viewsets.ModelViewSet):
    """ViewSet pour les comptes email"""
    queryset = CompteEmail.objects.all()
    serializer_class = CompteEmailSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filtre les comptes selon l'utilisateur"""
        if self.request.user.is_staff:
            return CompteEmail.objects.all()
        return CompteEmail.objects.filter(utilisateur=self.request.user)
    
    @action(detail=True, methods=['post'])
    def envoyer_email(self, request, pk=None):
        """Envoie un email"""
        compte = self.get_object()
        service = ServiceEmail(compte.configuration)
        
        # Validation des données
        destinataires = request.data.get('destinataires', [])
        sujet = request.data.get('sujet')
        contenu = request.data.get('contenu')
        
        if not destinataires or not sujet or not contenu:
            return Response(
                {'error': 'Données manquantes'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Envoi de l'email
        succes = service.envoyer_email(
            expediteur=compte,
            destinataires=destinataires,
            sujet=sujet,
            contenu_texte=contenu,
            contenu_html=request.data.get('contenu_html'),
            pieces_jointes=request.data.get('pieces_jointes'),
            cc=request.data.get('cc'),
            bcc=request.data.get('bcc')
        )
        
        if succes:
            return Response({'status': 'Email envoyé'})
        return Response(
            {'error': 'Erreur lors de l\'envoi'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    @action(detail=True, methods=['get'])
    def lire_emails(self, request, pk=None):
        """Lit les emails d'un compte"""
        compte = self.get_object()
        service = ServiceEmail(compte.configuration)
        
        dossier = request.query_params.get('dossier', 'INBOX')
        non_lus = request.query_params.get('non_lus', 'false') == 'true'
        limite = int(request.query_params.get('limite', 50))
        
        emails = service.lire_emails(
            compte=compte,
            dossier=dossier,
            non_lus=non_lus,
            limite=limite
        )
        
        return Response(emails)
    
    @action(detail=True, methods=['post'])
    def marquer_comme_lu(self, request, pk=None):
        """Marque des emails comme lus"""
        compte = self.get_object()
        service = ServiceEmail(compte.configuration)
        
        message_ids = request.data.get('message_ids', [])
        dossier = request.data.get('dossier', 'INBOX')
        
        if not message_ids:
            return Response(
                {'error': 'IDs de messages manquants'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        succes = service.marquer_comme_lu(compte, message_ids, dossier)
        
        if succes:
            return Response({'status': 'Emails marqués comme lus'})
        return Response(
            {'error': 'Erreur lors du marquage'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    @action(detail=True, methods=['post'])
    def supprimer_emails(self, request, pk=None):
        """Supprime des emails"""
        compte = self.get_object()
        service = ServiceEmail(compte.configuration)
        
        message_ids = request.data.get('message_ids', [])
        dossier = request.data.get('dossier', 'INBOX')
        
        if not message_ids:
            return Response(
                {'error': 'IDs de messages manquants'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        succes = service.supprimer_emails(compte, message_ids, dossier)
        
        if succes:
            return Response({'status': 'Emails supprimés'})
        return Response(
            {'error': 'Erreur lors de la suppression'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    @action(detail=True, methods=['post'])
    def deplacer_emails(self, request, pk=None):
        """Déplace des emails"""
        compte = self.get_object()
        service = ServiceEmail(compte.configuration)
        
        message_ids = request.data.get('message_ids', [])
        dossier_source = request.data.get('dossier_source', 'INBOX')
        dossier_destination = request.data.get('dossier_destination')
        
        if not message_ids or not dossier_destination:
            return Response(
                {'error': 'Données manquantes'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        succes = service.deplacer_emails(
            compte,
            message_ids,
            dossier_source,
            dossier_destination
        )
        
        if succes:
            return Response({'status': 'Emails déplacés'})
        return Response(
            {'error': 'Erreur lors du déplacement'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    @action(detail=True, methods=['post'])
    def creer_dossier(self, request, pk=None):
        """Crée un nouveau dossier"""
        compte = self.get_object()
        service = ServiceEmail(compte.configuration)
        
        nom_dossier = request.data.get('nom_dossier')
        
        if not nom_dossier:
            return Response(
                {'error': 'Nom du dossier manquant'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        succes = service.creer_dossier(compte, nom_dossier)
        
        if succes:
            return Response({'status': 'Dossier créé'})
        return Response(
            {'error': 'Erreur lors de la création'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    @action(detail=True, methods=['delete'])
    def supprimer_dossier(self, request, pk=None):
        """Supprime un dossier"""
        compte = self.get_object()
        service = ServiceEmail(compte.configuration)
        
        nom_dossier = request.data.get('nom_dossier')
        
        if not nom_dossier:
            return Response(
                {'error': 'Nom du dossier manquant'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        succes = service.supprimer_dossier(compte, nom_dossier)
        
        if succes:
            return Response({'status': 'Dossier supprimé'})
        return Response(
            {'error': 'Erreur lors de la suppression'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    @action(detail=True, methods=['get'])
    def lister_dossiers(self, request, pk=None):
        """Liste tous les dossiers"""
        compte = self.get_object()
        service = ServiceEmail(compte.configuration)
        
        dossiers = service.lister_dossiers(compte)
        return Response(dossiers)
    
    @action(detail=True, methods=['get'])
    def verifier_quota(self, request, pk=None):
        """Vérifie le quota utilisé"""
        compte = self.get_object()
        service = ServiceEmail(compte.configuration)
        
        quota = service.verifier_quota(compte)
        return Response(quota)

class AliasViewSet(viewsets.ModelViewSet):
    """ViewSet pour les alias email"""
    queryset = Alias.objects.all()
    serializer_class = AliasSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filtre les alias selon l'utilisateur"""
        if self.request.user.is_staff:
            return Alias.objects.all()
        return Alias.objects.filter(compte__utilisateur=self.request.user)

class ListeDiffusionViewSet(viewsets.ModelViewSet):
    """ViewSet pour les listes de diffusion"""
    queryset = ListeDiffusion.objects.all()
    serializer_class = ListeDiffusionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filtre les listes selon l'utilisateur"""
        user = self.request.user
        if user.is_staff:
            return ListeDiffusion.objects.all()
        return ListeDiffusion.objects.filter(
            Q(moderateurs__utilisateur=user) |
            Q(membres__utilisateur=user)
        ).distinct()
    
    @action(detail=True, methods=['post'])
    def ajouter_membre(self, request, pk=None):
        """Ajoute un membre à la liste"""
        liste = self.get_object()
        email = request.data.get('email')
        
        if not email:
            return Response(
                {'error': 'Email manquant'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            compte = CompteEmail.objects.get(adresse_email=email)
            liste.membres.add(compte)
            return Response({'status': 'Membre ajouté'})
        except CompteEmail.DoesNotExist:
            return Response(
                {'error': 'Compte email non trouvé'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'])
    def retirer_membre(self, request, pk=None):
        """Retire un membre de la liste"""
        liste = self.get_object()
        email = request.data.get('email')
        
        if not email:
            return Response(
                {'error': 'Email manquant'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            compte = CompteEmail.objects.get(adresse_email=email)
            liste.membres.remove(compte)
            return Response({'status': 'Membre retiré'})
        except CompteEmail.DoesNotExist:
            return Response(
                {'error': 'Compte email non trouvé'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'])
    def envoyer_message(self, request, pk=None):
        """Envoie un message à la liste"""
        liste = self.get_object()
        expediteur = request.user.compte_email
        
        # Vérification des droits
        if not liste.membres.filter(id=expediteur.id).exists():
            return Response(
                {'error': 'Non autorisé à envoyer des messages'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        sujet = request.data.get('sujet')
        contenu = request.data.get('contenu')
        
        if not sujet or not contenu:
            return Response(
                {'error': 'Données manquantes'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        service = ServiceEmail(liste.configuration)
        
        # Envoi à tous les membres
        destinataires = [
            membre.adresse_email
            for membre in liste.membres.all()
            if membre.id != expediteur.id
        ]
        
        succes = service.envoyer_email(
            expediteur=expediteur,
            destinataires=destinataires,
            sujet=f'[{liste.nom}] {sujet}',
            contenu_texte=contenu,
            contenu_html=request.data.get('contenu_html'),
            pieces_jointes=request.data.get('pieces_jointes')
        )
        
        if succes:
            return Response({'status': 'Message envoyé'})
        return Response(
            {'error': 'Erreur lors de l\'envoi'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
