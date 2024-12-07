from typing import Dict, Any, Optional
from datetime import timedelta
from django.utils import timezone
from django.core.exceptions import ValidationError
from .models import PlanAbonnement, Abonnement, HistoriquePaiement

class AbonnementService:
    """Service de gestion des abonnements"""
    
    @classmethod
    def creer_abonnement(
        cls,
        universite,
        plan_id: int,
        periodicite: str = 'ANNUEL'
    ) -> Abonnement:
        """Crée un nouvel abonnement"""
        try:
            plan = PlanAbonnement.objects.get(id=plan_id, actif=True)
        except PlanAbonnement.DoesNotExist:
            raise ValidationError('Plan d\'abonnement invalide')
        
        # Vérification d'un abonnement existant
        if Abonnement.objects.filter(universite=universite, etat='ACTIF').exists():
            raise ValidationError('Un abonnement actif existe déjà')
        
        # Calcul des dates
        date_debut = timezone.now()
        if periodicite == 'MENSUEL':
            date_fin = date_debut + timedelta(days=30)
            montant = plan.prix_mensuel
        else:
            date_fin = date_debut + timedelta(days=365)
            montant = plan.prix_annuel
        
        # Création de l'abonnement
        abonnement = Abonnement.objects.create(
            universite=universite,
            plan=plan,
            periodicite=periodicite,
            date_debut=date_debut,
            date_fin=date_fin,
            date_prochain_paiement=date_fin
        )
        
        # Création du premier paiement
        HistoriquePaiement.objects.create(
            abonnement=abonnement,
            montant=montant,
            date_paiement=timezone.now(),
            methode_paiement='CREATION',
            reference_transaction='INITIAL',
            statut='VALIDE',
            details='Paiement initial de l\'abonnement'
        )
        
        return abonnement
    
    @classmethod
    def renouveler_abonnement(
        cls,
        abonnement: Abonnement,
        methode_paiement: str,
        reference_transaction: str
    ) -> bool:
        """Renouvelle un abonnement"""
        if not abonnement.renouvellement_auto:
            raise ValidationError('Renouvellement automatique désactivé')
        
        # Calcul des nouvelles dates
        date_debut = abonnement.date_fin
        if abonnement.periodicite == 'MENSUEL':
            date_fin = date_debut + timedelta(days=30)
            montant = abonnement.plan.prix_mensuel
        else:
            date_fin = date_debut + timedelta(days=365)
            montant = abonnement.plan.prix_annuel
        
        # Création du paiement
        paiement = HistoriquePaiement.objects.create(
            abonnement=abonnement,
            montant=montant,
            date_paiement=timezone.now(),
            methode_paiement=methode_paiement,
            reference_transaction=reference_transaction,
            statut='VALIDE',
            details='Renouvellement automatique'
        )
        
        # Mise à jour de l'abonnement
        abonnement.date_fin = date_fin
        abonnement.date_dernier_paiement = paiement.date_paiement
        abonnement.date_prochain_paiement = date_fin
        abonnement.save()
        
        return True
    
    @classmethod
    def suspendre_abonnement(cls, abonnement: Abonnement, raison: str):
        """Suspend un abonnement"""
        if abonnement.etat != 'ACTIF':
            raise ValidationError('L\'abonnement n\'est pas actif')
        
        abonnement.etat = 'SUSPENDU'
        abonnement.notes += f'\nSuspendu le {timezone.now()}: {raison}'
        abonnement.save()
    
    @classmethod
    def reactiver_abonnement(cls, abonnement: Abonnement, raison: str):
        """Réactive un abonnement suspendu"""
        if abonnement.etat != 'SUSPENDU':
            raise ValidationError('L\'abonnement n\'est pas suspendu')
        
        abonnement.etat = 'ACTIF'
        abonnement.notes += f'\nRéactivé le {timezone.now()}: {raison}'
        abonnement.save()
    
    @classmethod
    def resilier_abonnement(cls, abonnement: Abonnement, raison: str):
        """Résilie un abonnement"""
        if abonnement.etat not in ['ACTIF', 'SUSPENDU']:
            raise ValidationError('État de l\'abonnement invalide')
        
        abonnement.etat = 'RESILIE'
        abonnement.renouvellement_auto = False
        abonnement.notes += f'\nRésilié le {timezone.now()}: {raison}'
        abonnement.save()
    
    @classmethod
    def verifier_limites(
        cls,
        abonnement: Abonnement,
        service: str
    ) -> Dict[str, Any]:
        """Vérifie les limites d'un service"""
        if not abonnement.est_actif():
            raise ValidationError('Abonnement inactif')
        
        plan = abonnement.plan
        limites = {
            'datacenter': {
                'utilise': abonnement.nb_datacenters_utilises,
                'maximum': plan.nb_max_datacenters,
                'disponible': (
                    plan.nb_max_datacenters - abonnement.nb_datacenters_utilises
                ),
                'capacite': plan.capacite_datacenter
            },
            'bibliotheque': {
                'utilise': abonnement.nb_bibliotheques_utilisees,
                'maximum': plan.nb_max_bibliotheques,
                'disponible': (
                    plan.nb_max_bibliotheques - abonnement.nb_bibliotheques_utilisees
                ),
                'capacite': plan.capacite_bibliotheque
            },
            'documentation': {
                'utilise': abonnement.nb_documentations_utilisees,
                'maximum': plan.nb_max_documentations,
                'disponible': (
                    plan.nb_max_documentations - abonnement.nb_documentations_utilisees
                ),
                'capacite': plan.capacite_documentation
            },
            'serveur_mail': {
                'utilise': abonnement.nb_serveurs_mail_utilises,
                'maximum': plan.nb_max_serveurs_mail,
                'disponible': (
                    plan.nb_max_serveurs_mail - abonnement.nb_serveurs_mail_utilises
                ),
                'capacite': plan.capacite_mail,
                'nb_max_utilisateurs': plan.nb_max_utilisateurs_mail
            },
            'mediatheque': {
                'utilise': abonnement.nb_mediatheques_utilisees,
                'maximum': plan.nb_max_mediatheques,
                'disponible': (
                    plan.nb_max_mediatheques - abonnement.nb_mediatheques_utilisees
                ),
                'capacite': plan.capacite_mediatheque
            }
        }
        
        if service not in limites:
            raise ValidationError('Service invalide')
        
        return limites[service]
    
    @classmethod
    def incrementer_utilisation(
        cls,
        abonnement: Abonnement,
        service: str
    ) -> bool:
        """Incrémente l'utilisation d'un service"""
        if not abonnement.est_actif():
            raise ValidationError('Abonnement inactif')
        
        limites = cls.verifier_limites(abonnement, service)
        if limites['utilise'] >= limites['maximum']:
            raise ValidationError(f'Limite de {service}s atteinte')
        
        # Mise à jour du compteur
        if service == 'datacenter':
            abonnement.nb_datacenters_utilises += 1
        elif service == 'bibliotheque':
            abonnement.nb_bibliotheques_utilisees += 1
        elif service == 'documentation':
            abonnement.nb_documentations_utilisees += 1
        elif service == 'serveur_mail':
            abonnement.nb_serveurs_mail_utilises += 1
        elif service == 'mediatheque':
            abonnement.nb_mediatheques_utilisees += 1
        
        abonnement.save()
        return True
    
    @classmethod
    def decrementer_utilisation(
        cls,
        abonnement: Abonnement,
        service: str
    ) -> bool:
        """Décrémente l'utilisation d'un service"""
        if not abonnement.est_actif():
            raise ValidationError('Abonnement inactif')
        
        # Mise à jour du compteur
        if service == 'datacenter':
            if abonnement.nb_datacenters_utilises > 0:
                abonnement.nb_datacenters_utilises -= 1
        elif service == 'bibliotheque':
            if abonnement.nb_bibliotheques_utilisees > 0:
                abonnement.nb_bibliotheques_utilisees -= 1
        elif service == 'documentation':
            if abonnement.nb_documentations_utilisees > 0:
                abonnement.nb_documentations_utilisees -= 1
        elif service == 'serveur_mail':
            if abonnement.nb_serveurs_mail_utilises > 0:
                abonnement.nb_serveurs_mail_utilises -= 1
        elif service == 'mediatheque':
            if abonnement.nb_mediatheques_utilisees > 0:
                abonnement.nb_mediatheques_utilisees -= 1
        else:
            raise ValidationError('Service invalide')
        
        abonnement.save()
        return True
