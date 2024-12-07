from rest_framework import serializers
from django.utils import timezone
from .models import Quiz, Question, Reponse, Tentative, ReponseEtudiant

class ReponseSerializer(serializers.ModelSerializer):
    """Serializer pour le modèle Reponse"""
    class Meta:
        model = Reponse
        fields = [
            'id', 'texte', 'correcte', 'explication',
            'ordre', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

class QuestionSerializer(serializers.ModelSerializer):
    """Serializer pour le modèle Question"""
    reponses = ReponseSerializer(many=True, required=False)

    class Meta:
        model = Question
        fields = [
            'id', 'quiz', 'texte', 'type_question',
            'points', 'explication', 'ordre', 'reponses',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def create(self, validated_data):
        reponses_data = validated_data.pop('reponses', [])
        question = Question.objects.create(**validated_data)
        
        for reponse_data in reponses_data:
            Reponse.objects.create(question=question, **reponse_data)
        
        return question

class QuizListSerializer(serializers.ModelSerializer):
    """Serializer pour la liste des quiz"""
    nombre_questions = serializers.IntegerField(
        source='questions.count',
        read_only=True
    )
    nombre_tentatives_total = serializers.IntegerField(
        source='tentatives.count',
        read_only=True
    )
    createur_nom = serializers.CharField(
        source='createur.get_full_name',
        read_only=True
    )

    class Meta:
        model = Quiz
        fields = [
            'id', 'titre', 'description', 'cours',
            'type_quiz', 'duree', 'nombre_tentatives',
            'note_passage', 'actif', 'date_debut',
            'date_fin', 'aleatoire', 'createur',
            'createur_nom', 'nombre_questions',
            'nombre_tentatives_total', 'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

class QuizDetailSerializer(QuizListSerializer):
    """Serializer pour le détail d'un quiz"""
    questions = QuestionSerializer(many=True, required=False)

    class Meta(QuizListSerializer.Meta):
        fields = QuizListSerializer.Meta.fields + ['questions']

    def create(self, validated_data):
        questions_data = validated_data.pop('questions', [])
        quiz = Quiz.objects.create(**validated_data)
        
        for question_data in questions_data:
            reponses_data = question_data.pop('reponses', [])
            question = Question.objects.create(quiz=quiz, **question_data)
            
            for reponse_data in reponses_data:
                Reponse.objects.create(question=question, **reponse_data)
        
        return quiz

class ReponseEtudiantSerializer(serializers.ModelSerializer):
    """Serializer pour le modèle ReponseEtudiant"""
    class Meta:
        model = ReponseEtudiant
        fields = [
            'id', 'tentative', 'question', 'reponses',
            'texte_reponse', 'correcte', 'points_obtenus',
            'commentaire', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'correcte', 'points_obtenus', 'created_at',
            'updated_at'
        ]

class TentativeListSerializer(serializers.ModelSerializer):
    """Serializer pour la liste des tentatives"""
    etudiant_nom = serializers.CharField(
        source='etudiant.get_full_name',
        read_only=True
    )
    quiz_titre = serializers.CharField(
        source='quiz.titre',
        read_only=True
    )

    class Meta:
        model = Tentative
        fields = [
            'id', 'quiz', 'quiz_titre', 'etudiant',
            'etudiant_nom', 'date_debut', 'date_fin',
            'statut', 'note', 'temps_passe',
            'numero_tentative', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'date_fin', 'statut', 'note', 'temps_passe',
            'numero_tentative', 'created_at', 'updated_at'
        ]

    def validate(self, data):
        quiz = data['quiz']
        etudiant = data['etudiant']
        
        # Vérifie si le quiz est actif
        if not quiz.actif:
            raise serializers.ValidationError(
                "Ce quiz n'est pas disponible actuellement."
            )
        
        # Vérifie les dates de début et de fin
        now = timezone.now()
        if quiz.date_debut and quiz.date_debut > now:
            raise serializers.ValidationError(
                "Ce quiz n'est pas encore disponible."
            )
        if quiz.date_fin and quiz.date_fin < now:
            raise serializers.ValidationError(
                "Ce quiz n'est plus disponible."
            )
        
        # Vérifie le nombre de tentatives
        tentatives_count = Tentative.objects.filter(
            quiz=quiz,
            etudiant=etudiant
        ).count()
        
        if tentatives_count >= quiz.nombre_tentatives:
            raise serializers.ValidationError(
                "Vous avez atteint le nombre maximum de tentatives pour ce quiz."
            )
        
        return data

class TentativeDetailSerializer(TentativeListSerializer):
    """Serializer pour le détail d'une tentative"""
    reponses_etudiant = ReponseEtudiantSerializer(
        many=True,
        required=False
    )

    class Meta(TentativeListSerializer.Meta):
        fields = TentativeListSerializer.Meta.fields + ['reponses_etudiant']
