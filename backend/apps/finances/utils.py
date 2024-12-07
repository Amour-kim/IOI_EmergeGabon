import uuid
from decimal import Decimal
from django.utils import timezone
from django.template.loader import render_to_string
from django.conf import settings
import weasyprint
from io import BytesIO

def generer_reference_paiement():
    """Génère une référence unique pour un paiement"""
    return f"PAY{uuid.uuid4().hex[:8].upper()}"

def generer_numero_facture():
    """Génère un numéro unique pour une facture"""
    return f"FACT{uuid.uuid4().hex[:8].upper()}"

def calculer_montant_ht(montant_ttc, tva=Decimal('18.00')):
    """Calcule le montant HT à partir du montant TTC"""
    tva_decimal = tva / Decimal('100.00')
    return round(montant_ttc / (1 + tva_decimal), 2)

def generer_pdf_facture(facture):
    """Génère le PDF d'une facture"""
    # Contexte pour le template
    context = {
        'facture': facture,
        'paiement': facture.paiement,
        'etudiant': facture.paiement.etudiant,
        'date_generation': timezone.now(),
        'logo_url': settings.STATIC_URL + 'images/logo.png',
        'coordonnees_universite': {
            'nom': settings.NOM_UNIVERSITE,
            'adresse': settings.ADRESSE_UNIVERSITE,
            'telephone': settings.TELEPHONE_UNIVERSITE,
            'email': settings.EMAIL_UNIVERSITE,
        }
    }
    
    # Génération du HTML
    html_string = render_to_string('finances/facture_pdf.html', context)
    
    # Conversion en PDF
    pdf_file = BytesIO()
    weasyprint.HTML(string=html_string).write_pdf(pdf_file)
    
    return pdf_file.getvalue()

def calculer_statistiques_paiements(queryset):
    """Calcule les statistiques des paiements"""
    total_paiements = queryset.count()
    montant_total = queryset.filter(statut='VALIDE').aggregate(
        total=models.Sum('montant')
    )['total'] or Decimal('0')
    
    # Statistiques par type de paiement
    stats_par_type = {}
    for type_choice in Paiement.TYPE_CHOICES:
        type_code = type_choice[0]
        montant = queryset.filter(
            type_paiement=type_code,
            statut='VALIDE'
        ).aggregate(total=models.Sum('montant'))['total'] or Decimal('0')
        stats_par_type[type_code] = {
            'nombre': queryset.filter(type_paiement=type_code).count(),
            'montant_total': montant
        }
    
    # Statistiques par mode de paiement
    stats_par_mode = {}
    for mode_choice in Paiement.MODE_PAIEMENT_CHOICES:
        mode_code = mode_choice[0]
        montant = queryset.filter(
            mode_paiement=mode_code,
            statut='VALIDE'
        ).aggregate(total=models.Sum('montant'))['total'] or Decimal('0')
        stats_par_mode[mode_code] = {
            'nombre': queryset.filter(mode_paiement=mode_code).count(),
            'montant_total': montant
        }
    
    return {
        'total_paiements': total_paiements,
        'montant_total': montant_total,
        'stats_par_type': stats_par_type,
        'stats_par_mode': stats_par_mode
    }

def verifier_paiement_complet(dossier_inscription, type_paiement):
    """Vérifie si un type de paiement a été entièrement payé pour un dossier"""
    if type_paiement == 'SCOLARITE':
        frais = FraisScolarite.objects.get(
            departement=dossier_inscription.departement,
            cycle=dossier_inscription.niveau[:7],  # LICENCE, MASTER, etc.
            annee_academique=dossier_inscription.annee_academique
        )
        montant_requis = frais.montant
    else:
        # Autres types de frais (à implémenter selon les besoins)
        return True
    
    montant_paye = Paiement.objects.filter(
        dossier_inscription=dossier_inscription,
        type_paiement=type_paiement,
        statut='VALIDE'
    ).aggregate(total=models.Sum('montant'))['total'] or Decimal('0')
    
    return montant_paye >= montant_requis

def envoyer_notification_paiement(paiement):
    """Envoie une notification concernant un paiement"""
    from apps.messaging.utils import envoyer_email, envoyer_sms
    
    # Notification par email
    context = {
        'paiement': paiement,
        'etudiant': paiement.etudiant
    }
    
    if paiement.statut == 'VALIDE':
        template_email = 'finances/emails/paiement_valide.html'
        sujet = 'Confirmation de votre paiement'
    elif paiement.statut == 'REJETE':
        template_email = 'finances/emails/paiement_rejete.html'
        sujet = 'Rejet de votre paiement'
    else:
        return
    
    envoyer_email(
        destinataire=paiement.etudiant.email,
        sujet=sujet,
        template=template_email,
        context=context
    )
    
    # Notification par SMS si un numéro est disponible
    if paiement.etudiant.telephone:
        if paiement.statut == 'VALIDE':
            message = f"Votre paiement de {paiement.montant} FCFA a été validé. Réf: {paiement.reference}"
        else:
            message = f"Votre paiement de {paiement.montant} FCFA a été rejeté. Réf: {paiement.reference}"
        
        envoyer_sms(
            numero=paiement.etudiant.telephone,
            message=message
        )
