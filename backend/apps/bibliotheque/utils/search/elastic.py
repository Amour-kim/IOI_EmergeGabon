from elasticsearch_dsl import (
    Document, Text, Keyword, Integer,
    Float, Date, Boolean, Index
)
from elasticsearch_dsl.connections import connections
from django.conf import settings
from ...models import Ressource

# Connexion à Elasticsearch
connections.create_connection(
    hosts=[settings.ELASTICSEARCH_HOST],
    timeout=20
)

class RessourceDocument(Document):
    """Document Elasticsearch pour les ressources"""
    titre = Text(analyzer='french')
    description = Text(analyzer='french')
    auteur = Text(analyzer='french')
    type_ressource = Keyword()
    langue = Keyword()
    annee_publication = Integer()
    mots_cles = Text(analyzer='french')
    categorie = Text(analyzer='french')
    cours = Text(analyzer='french')
    departement = Text(analyzer='french')
    note_moyenne = Float()
    nombre_telechargements = Integer()
    nombre_evaluations = Integer()
    est_public = Boolean()
    date_creation = Date()
    date_modification = Date()

    class Index:
        name = 'ressources'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0
        }

    class Meta:
        model = Ressource

    def prepare_categorie(self, instance):
        """Prépare le champ catégorie"""
        return instance.categorie.chemin_complet

    def prepare_cours(self, instance):
        """Prépare le champ cours"""
        if instance.cours:
            return f"{instance.cours.code} - {instance.cours.intitule}"
        return None

    def prepare_departement(self, instance):
        """Prépare le champ département"""
        if instance.cours and instance.cours.departement:
            return instance.cours.departement.nom
        return None

def bulk_index_ressources():
    """Indexe toutes les ressources"""
    RessourceDocument.init()
    bulk_data = []
    for ressource in Ressource.objects.select_related(
        'categorie',
        'cours__departement'
    ).iterator():
        doc = RessourceDocument(meta={'id': ressource.id})
        doc.titre = ressource.titre
        doc.description = ressource.description
        doc.auteur = ressource.auteur
        doc.type_ressource = ressource.type_ressource
        doc.langue = ressource.langue
        doc.annee_publication = ressource.annee_publication
        doc.mots_cles = ressource.mots_cles
        doc.categorie = doc.prepare_categorie(ressource)
        doc.cours = doc.prepare_cours(ressource)
        doc.departement = doc.prepare_departement(ressource)
        doc.note_moyenne = ressource.note_moyenne
        doc.nombre_telechargements = ressource.nombre_telechargements
        doc.nombre_evaluations = ressource.nombre_evaluations
        doc.est_public = ressource.est_public
        doc.date_creation = ressource.created_at
        doc.date_modification = ressource.updated_at
        bulk_data.append(doc)

        if len(bulk_data) >= 1000:
            doc.bulk_create(bulk_data)
            bulk_data = []

    if bulk_data:
        doc.bulk_create(bulk_data)

def search_ressources(query, filters=None, sort=None, page=1, size=10):
    """
    Recherche des ressources
    
    Args:
        query: Requête de recherche
        filters: Filtres (type, langue, année, etc.)
        sort: Tri (pertinence, date, popularité)
        page: Numéro de page
        size: Nombre de résultats par page
    """
    s = RessourceDocument.search()
    
    # Requête principale
    if query:
        s = s.query('multi_match', query=query, fields=[
            'titre^3',
            'description^2',
            'auteur^2',
            'mots_cles^2',
            'categorie',
            'cours',
            'departement'
        ])
    
    # Filtres
    if filters:
        if 'type_ressource' in filters:
            s = s.filter('terms', type_ressource=filters['type_ressource'])
        if 'langue' in filters:
            s = s.filter('terms', langue=filters['langue'])
        if 'annee_min' in filters:
            s = s.filter(
                'range',
                annee_publication={'gte': filters['annee_min']}
            )
        if 'annee_max' in filters:
            s = s.filter(
                'range',
                annee_publication={'lte': filters['annee_max']}
            )
        if 'categorie' in filters:
            s = s.filter('match', categorie=filters['categorie'])
        if 'departement' in filters:
            s = s.filter('match', departement=filters['departement'])
    
    # Tri
    if sort:
        if sort == 'date':
            s = s.sort('-date_creation')
        elif sort == 'popularite':
            s = s.sort('-nombre_telechargements')
        elif sort == 'note':
            s = s.sort('-note_moyenne')
    
    # Pagination
    s = s[(page - 1) * size:page * size]
    
    # Exécution de la requête
    response = s.execute()
    
    return {
        'total': response.hits.total.value,
        'results': [hit.to_dict() for hit in response],
        'page': page,
        'size': size,
        'pages': (response.hits.total.value + size - 1) // size
    }
