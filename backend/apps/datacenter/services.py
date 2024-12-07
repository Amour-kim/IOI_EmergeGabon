from typing import Optional, Dict, Any
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from .models import (
    Datacenter, Bibliotheque, Documentation,
    Mediatheque, Livre, Document, Media
)

class DatacenterService:
    """Service de gestion du datacenter"""
    
    LIMITES_ABONNEMENT = {
        'BASIC': {
            'stockage_total': 100,  # Go
            'stockage_bibliotheque': 40,
            'stockage_documentation': 30,
            'stockage_mediatheque': 30,
            'backup_inclus': False
        },
        'STANDARD': {
            'stockage_total': 500,
            'stockage_bibliotheque': 200,
            'stockage_documentation': 150,
            'stockage_mediatheque': 150,
            'backup_inclus': True,
            'frequence_backup': 'HEBDOMADAIRE'
        },
        'PREMIUM': {
            'stockage_total': 2000,
            'stockage_bibliotheque': 800,
            'stockage_documentation': 600,
            'stockage_mediatheque': 600,
            'backup_inclus': True,
            'frequence_backup': 'QUOTIDIEN'
        },
        'ENTERPRISE': {
            'stockage_total': 5000,
            'stockage_bibliotheque': 2000,
            'stockage_documentation': 1500,
            'stockage_mediatheque': 1500,
            'backup_inclus': True,
            'frequence_backup': 'TEMPS_REEL'
        }
    }
    
    @classmethod
    def creer_datacenter(
        cls,
        universite,
        type_abonnement: str,
        nom: str,
        description: str = ''
    ) -> Datacenter:
        """Crée un nouveau datacenter"""
        if type_abonnement not in cls.LIMITES_ABONNEMENT:
            raise ValidationError('Type d\'abonnement invalide')
        
        limites = cls.LIMITES_ABONNEMENT[type_abonnement]
        
        # Création du datacenter
        datacenter = Datacenter.objects.create(
            universite=universite,
            nom=nom,
            description=description,
            capacite_totale=limites['stockage_total'],
            backup_actif=limites.get('backup_inclus', False),
            frequence_backup=limites.get('frequence_backup', '')
        )
        
        # Création des espaces de stockage
        Bibliotheque.objects.create(
            datacenter=datacenter,
            nom=f'Bibliothèque de {universite.nom}',
            description='Bibliothèque numérique principale',
            capacite_stockage=limites['stockage_bibliotheque']
        )
        
        Documentation.objects.create(
            datacenter=datacenter,
            nom=f'Documentation de {universite.nom}',
            description='Centre de documentation principal',
            capacite_stockage=limites['stockage_documentation']
        )
        
        Mediatheque.objects.create(
            datacenter=datacenter,
            nom=f'Médiathèque de {universite.nom}',
            description='Médiathèque multimédia principale',
            capacite_stockage=limites['stockage_mediatheque']
        )
        
        return datacenter
    
    @classmethod
    def verifier_stockage(
        cls,
        datacenter: Datacenter
    ) -> Dict[str, Any]:
        """Vérifie l'état du stockage"""
        bibliotheque = datacenter.bibliotheques.first()
        documentation = datacenter.documentations.first()
        mediatheque = datacenter.mediatheques.first()
        
        return {
            'total': {
                'alloue': datacenter.capacite_totale,
                'utilise': datacenter.stockage_utilise,
                'disponible': datacenter.capacite_totale - datacenter.stockage_utilise,
                'pourcentage': (
                    datacenter.stockage_utilise / datacenter.capacite_totale
                ) * 100 if datacenter.capacite_totale > 0 else 0
            },
            'bibliotheque': {
                'alloue': bibliotheque.capacite_stockage,
                'utilise': bibliotheque.stockage_utilise,
                'disponible': (
                    bibliotheque.capacite_stockage - bibliotheque.stockage_utilise
                ),
                'pourcentage': (
                    bibliotheque.stockage_utilise / bibliotheque.capacite_stockage
                ) * 100 if bibliotheque.capacite_stockage > 0 else 0
            },
            'documentation': {
                'alloue': documentation.capacite_stockage,
                'utilise': documentation.stockage_utilise,
                'disponible': (
                    documentation.capacite_stockage - documentation.stockage_utilise
                ),
                'pourcentage': (
                    documentation.stockage_utilise / documentation.capacite_stockage
                ) * 100 if documentation.capacite_stockage > 0 else 0
            },
            'mediatheque': {
                'alloue': mediatheque.capacite_stockage,
                'utilise': mediatheque.stockage_utilise,
                'disponible': (
                    mediatheque.capacite_stockage - mediatheque.stockage_utilise
                ),
                'pourcentage': (
                    mediatheque.stockage_utilise / mediatheque.capacite_stockage
                ) * 100 if mediatheque.capacite_stockage > 0 else 0
            }
        }
    
    @classmethod
    def verifier_espace_disponible(
        cls,
        stockage,
        taille_fichier: int
    ) -> bool:
        """Vérifie si l'espace est disponible"""
        return (
            stockage.capacite_stockage - stockage.stockage_utilise
        ) >= taille_fichier
    
    @classmethod
    def ajouter_livre(
        cls,
        bibliotheque: Bibliotheque,
        section,
        donnees: Dict[str, Any]
    ) -> Optional[Livre]:
        """Ajoute un livre à la bibliothèque"""
        taille = donnees['taille']
        
        # Vérification de l'espace
        if not cls.verifier_espace_disponible(bibliotheque, taille):
            raise ValidationError('Espace de stockage insuffisant')
        
        # Vérification de la capacité de la section
        if section.livres.count() >= section.capacite:
            raise ValidationError('Section pleine')
        
        try:
            livre = Livre.objects.create(
                section=section,
                titre=donnees['titre'],
                auteurs=donnees['auteurs'],
                isbn=donnees['isbn'],
                edition=donnees['edition'],
                annee_publication=donnees['annee_publication'],
                langue=donnees['langue'],
                format=donnees['format'],
                taille=taille,
                fichier=donnees['fichier'],
                mots_cles=donnees.get('mots_cles', ''),
                description=donnees.get('description', '')
            )
            
            # Mise à jour du stockage
            bibliotheque.stockage_utilise += taille
            bibliotheque.save()
            
            # Mise à jour du datacenter
            datacenter = bibliotheque.datacenter
            datacenter.stockage_utilise += taille
            datacenter.save()
            
            return livre
            
        except Exception as e:
            raise ValidationError(f'Erreur lors de l\'ajout du livre: {str(e)}')
    
    @classmethod
    def ajouter_document(
        cls,
        documentation: Documentation,
        donnees: Dict[str, Any]
    ) -> Optional[Document]:
        """Ajoute un document à la documentation"""
        taille = donnees['taille']
        
        # Vérification de l'espace
        if not cls.verifier_espace_disponible(documentation, taille):
            raise ValidationError('Espace de stockage insuffisant')
        
        try:
            document = Document.objects.create(
                documentation=documentation,
                titre=donnees['titre'],
                type_document=donnees['type_document'],
                auteur=donnees['auteur'],
                version=donnees['version'],
                format=donnees['format'],
                taille=taille,
                fichier=donnees['fichier'],
                mots_cles=donnees.get('mots_cles', ''),
                description=donnees.get('description', '')
            )
            
            # Mise à jour du stockage
            documentation.stockage_utilise += taille
            documentation.save()
            
            # Mise à jour du datacenter
            datacenter = documentation.datacenter
            datacenter.stockage_utilise += taille
            datacenter.save()
            
            return document
            
        except Exception as e:
            raise ValidationError(f'Erreur lors de l\'ajout du document: {str(e)}')
    
    @classmethod
    def ajouter_media(
        cls,
        mediatheque: Mediatheque,
        donnees: Dict[str, Any]
    ) -> Optional[Media]:
        """Ajoute un média à la médiathèque"""
        taille = donnees['taille']
        
        # Vérification de l'espace
        if not cls.verifier_espace_disponible(mediatheque, taille):
            raise ValidationError('Espace de stockage insuffisant')
        
        try:
            media = Media.objects.create(
                mediatheque=mediatheque,
                titre=donnees['titre'],
                type_media=donnees['type_media'],
                auteur=donnees['auteur'],
                duree=donnees.get('duree'),
                format=donnees['format'],
                resolution=donnees.get('resolution', ''),
                taille=taille,
                fichier=donnees['fichier'],
                vignette=donnees.get('vignette'),
                mots_cles=donnees.get('mots_cles', ''),
                description=donnees.get('description', '')
            )
            
            # Mise à jour du stockage
            mediatheque.stockage_utilise += taille
            mediatheque.save()
            
            # Mise à jour du datacenter
            datacenter = mediatheque.datacenter
            datacenter.stockage_utilise += taille
            datacenter.save()
            
            return media
            
        except Exception as e:
            raise ValidationError(f'Erreur lors de l\'ajout du média: {str(e)}')
