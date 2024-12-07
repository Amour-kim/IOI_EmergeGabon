from django.contrib import admin
from django.utils.html import format_html
from .models import Quiz, Question, Reponse, Tentative, ReponseEtudiant

class ReponseInline(admin.TabularInline):
    """Inline admin pour les réponses"""
    model = Reponse
    extra = 0
    fields = ('texte', 'correcte', 'explication', 'ordre')

class QuestionInline(admin.TabularInline):
    """Inline admin pour les questions"""
    model = Question
    extra = 0
    fields = (
        'texte', 'type_question', 'points',
        'explication', 'ordre'
    )
    show_change_link = True

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    """Admin pour le modèle Quiz"""
    list_display = (
        'titre', 'cours', 'type_quiz', 'duree',
        'note_passage', 'actif', 'date_debut',
        'date_fin', 'createur'
    )
    list_filter = (
        'type_quiz', 'actif', 'cours',
        'date_debut', 'date_fin'
    )
    search_fields = ('titre', 'description')
    inlines = [QuestionInline]
    date_hierarchy = 'created_at'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'cours', 'createur'
        )

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    """Admin pour le modèle Question"""
    list_display = (
        'texte_court', 'quiz', 'type_question',
        'points', 'ordre'
    )
    list_filter = ('type_question', 'quiz')
    search_fields = ('texte', 'explication')
    inlines = [ReponseInline]
    
    def texte_court(self, obj):
        return obj.texte[:100] + '...' if len(obj.texte) > 100 else obj.texte
    texte_court.short_description = 'Texte'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('quiz')

class ReponseEtudiantInline(admin.TabularInline):
    """Inline admin pour les réponses des étudiants"""
    model = ReponseEtudiant
    extra = 0
    fields = (
        'question', 'reponses', 'texte_reponse',
        'correcte', 'points_obtenus', 'commentaire'
    )
    readonly_fields = ('correcte', 'points_obtenus')

@admin.register(Tentative)
class TentativeAdmin(admin.ModelAdmin):
    """Admin pour le modèle Tentative"""
    list_display = (
        'etudiant', 'quiz', 'date_debut',
        'date_fin', 'statut', 'note',
        'temps_passe', 'numero_tentative'
    )
    list_filter = (
        'statut', 'quiz', 'date_debut',
        'date_fin'
    )
    search_fields = (
        'etudiant__username',
        'etudiant__first_name',
        'etudiant__last_name',
        'quiz__titre'
    )
    inlines = [ReponseEtudiantInline]
    readonly_fields = (
        'date_debut', 'date_fin', 'temps_passe',
        'numero_tentative'
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'quiz', 'etudiant'
        )

@admin.register(ReponseEtudiant)
class ReponseEtudiantAdmin(admin.ModelAdmin):
    """Admin pour le modèle ReponseEtudiant"""
    list_display = (
        'tentative_etudiant', 'question',
        'correcte', 'points_obtenus'
    )
    list_filter = (
        'correcte', 'tentative__quiz',
        'question__type_question'
    )
    search_fields = (
        'tentative__etudiant__username',
        'tentative__etudiant__first_name',
        'tentative__etudiant__last_name',
        'question__texte'
    )
    readonly_fields = ('correcte', 'points_obtenus')
    
    def tentative_etudiant(self, obj):
        return f"{obj.tentative.etudiant.get_full_name()} - {obj.tentative.quiz.titre}"
    tentative_etudiant.short_description = "Tentative"
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'tentative__etudiant',
            'tentative__quiz',
            'question'
        )
