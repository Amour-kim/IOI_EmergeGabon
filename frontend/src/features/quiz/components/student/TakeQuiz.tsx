import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  FormControl,
  FormControlLabel,
  Radio,
  RadioGroup,
  Checkbox,
  TextField,
  LinearProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  Card,
  CardContent,
  Chip,
  Grid,
} from '@mui/material';
import {
  Timer,
  NavigateNext,
  NavigateBefore,
  Flag,
  Check,
  Warning,
} from '@mui/icons-material';
import { Quiz, QuizQuestion, QuestionType, QuizAnswer } from '../../types';

const mockQuiz: Quiz = {
  id: '1',
  courseId: 'CS101',
  title: 'Quiz sur les Algorithmes de Tri',
  description: 'Évaluez vos connaissances sur les différents algorithmes de tri.',
  timeLimit: 30,
  startDate: '2024-01-20T10:00:00',
  endDate: '2024-01-20T11:00:00',
  totalPoints: 20,
  passingScore: 60,
  shuffleQuestions: true,
  showResults: true,
  allowReview: true,
  maxAttempts: 1,
  questions: [
    {
      id: '1',
      quizId: '1',
      type: QuestionType.SINGLE_CHOICE,
      question: 'Quelle est la complexité temporelle moyenne du tri rapide (Quicksort) ?',
      points: 2,
      options: [
        { id: '1', text: 'O(n)' },
        { id: '2', text: 'O(n log n)' },
        { id: '3', text: 'O(n²)' },
        { id: '4', text: 'O(log n)' },
      ],
      correctAnswers: ['2'],
      order: 1,
    },
    // Ajoutez d'autres questions ici
  ],
  status: 'ACTIVE',
  createdAt: '2024-01-15T00:00:00',
  updatedAt: '2024-01-15T00:00:00',
  createdBy: 'prof.dupont',
};

const TakeQuiz: React.FC = () => {
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [answers, setAnswers] = useState<{ [key: string]: string[] }>({});
  const [flaggedQuestions, setFlaggedQuestions] = useState<Set<number>>(new Set());
  const [timeLeft, setTimeLeft] = useState(mockQuiz.timeLimit * 60);
  const [confirmSubmitOpen, setConfirmSubmitOpen] = useState(false);
  const [confirmLeaveOpen, setConfirmLeaveOpen] = useState(false);

  useEffect(() => {
    const timer = setInterval(() => {
      setTimeLeft((prev) => {
        if (prev <= 1) {
          clearInterval(timer);
          handleSubmit();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  const formatTime = (seconds: number) => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  const handleAnswerChange = (questionId: string, value: string[]) => {
    setAnswers({
      ...answers,
      [questionId]: value,
    });
  };

  const toggleFlaggedQuestion = (index: number) => {
    const newFlagged = new Set(flaggedQuestions);
    if (newFlagged.has(index)) {
      newFlagged.delete(index);
    } else {
      newFlagged.add(index);
    }
    setFlaggedQuestions(newFlagged);
  };

  const handleSubmit = () => {
    const quizAnswers: QuizAnswer[] = Object.entries(answers).map(([questionId, selectedOptions]) => ({
      questionId,
      selectedOptions,
    }));
    console.log('Quiz Answers:', quizAnswers);
    // Implémenter la soumission du quiz
  };

  const currentQuestion = mockQuiz.questions[currentQuestionIndex];
  const progress = (Object.keys(answers).length / mockQuiz.questions.length) * 100;

  const renderQuestion = (question: QuizQuestion) => {
    switch (question.type) {
      case QuestionType.SINGLE_CHOICE:
        return (
          <FormControl component="fieldset">
            <RadioGroup
              value={answers[question.id]?.[0] || ''}
              onChange={(e) => handleAnswerChange(question.id, [e.target.value])}
            >
              {question.options.map((option) => (
                <FormControlLabel
                  key={option.id}
                  value={option.id}
                  control={<Radio />}
                  label={option.text}
                />
              ))}
            </RadioGroup>
          </FormControl>
        );

      case QuestionType.MULTIPLE_CHOICE:
        return (
          <FormControl component="fieldset">
            {question.options.map((option) => (
              <FormControlLabel
                key={option.id}
                control={
                  <Checkbox
                    checked={answers[question.id]?.includes(option.id) || false}
                    onChange={(e) => {
                      const currentAnswers = answers[question.id] || [];
                      const newAnswers = e.target.checked
                        ? [...currentAnswers, option.id]
                        : currentAnswers.filter((id) => id !== option.id);
                      handleAnswerChange(question.id, newAnswers);
                    }}
                  />
                }
                label={option.text}
              />
            ))}
          </FormControl>
        );

      case QuestionType.SHORT_ANSWER:
        return (
          <TextField
            fullWidth
            multiline
            rows={4}
            value={answers[question.id]?.[0] || ''}
            onChange={(e) => handleAnswerChange(question.id, [e.target.value])}
            placeholder="Entrez votre réponse ici..."
          />
        );

      default:
        return null;
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Paper sx={{ p: 3, mb: 3 }}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={8}>
            <Typography variant="h4" gutterBottom>
              {mockQuiz.title}
            </Typography>
            <Typography variant="body1" color="textSecondary" paragraph>
              {mockQuiz.description}
            </Typography>
          </Grid>
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Timer sx={{ mr: 1 }} color="error" />
                  <Typography variant="h5" color="error">
                    {formatTime(timeLeft)}
                  </Typography>
                </Box>
                <Typography variant="body2" gutterBottom>
                  Questions répondues: {Object.keys(answers).length} / {mockQuiz.questions.length}
                </Typography>
                <LinearProgress
                  variant="determinate"
                  value={progress}
                  sx={{ mb: 1 }}
                />
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Paper>

      <Paper sx={{ p: 3, mb: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
          <Typography variant="h6">
            Question {currentQuestionIndex + 1} sur {mockQuiz.questions.length}
          </Typography>
          <Box>
            <Chip
              icon={<Flag />}
              label={flaggedQuestions.has(currentQuestionIndex) ? 'Marquée' : 'Marquer'}
              onClick={() => toggleFlaggedQuestion(currentQuestionIndex)}
              color={flaggedQuestions.has(currentQuestionIndex) ? 'warning' : 'default'}
              sx={{ mr: 1 }}
            />
            <Chip
              icon={answers[currentQuestion.id] ? <Check /> : <Warning />}
              label={answers[currentQuestion.id] ? 'Répondu' : 'Non répondu'}
              color={answers[currentQuestion.id] ? 'success' : 'error'}
            />
          </Box>
        </Box>

        <Typography variant="body1" paragraph>
          {currentQuestion.question}
        </Typography>

        <Box sx={{ my: 3 }}>
          {renderQuestion(currentQuestion)}
        </Box>

        <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 3 }}>
          <Button
            startIcon={<NavigateBefore />}
            onClick={() => setCurrentQuestionIndex(currentQuestionIndex - 1)}
            disabled={currentQuestionIndex === 0}
          >
            Question précédente
          </Button>
          {currentQuestionIndex === mockQuiz.questions.length - 1 ? (
            <Button
              variant="contained"
              color="primary"
              onClick={() => setConfirmSubmitOpen(true)}
            >
              Terminer le quiz
            </Button>
          ) : (
            <Button
              endIcon={<NavigateNext />}
              onClick={() => setCurrentQuestionIndex(currentQuestionIndex + 1)}
              variant="contained"
            >
              Question suivante
            </Button>
          )}
        </Box>
      </Paper>

      <Dialog
        open={confirmSubmitOpen}
        onClose={() => setConfirmSubmitOpen(false)}
      >
        <DialogTitle>Confirmer la soumission</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Êtes-vous sûr de vouloir soumettre le quiz ? Cette action ne peut pas être annulée.
            {Object.keys(answers).length < mockQuiz.questions.length && (
              <Typography color="error" sx={{ mt: 2 }}>
                Attention : vous n'avez pas répondu à toutes les questions.
              </Typography>
            )}
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setConfirmSubmitOpen(false)}>
            Continuer le quiz
          </Button>
          <Button
            onClick={handleSubmit}
            variant="contained"
            color="primary"
          >
            Soumettre
          </Button>
        </DialogActions>
      </Dialog>

      <Dialog
        open={confirmLeaveOpen}
        onClose={() => setConfirmLeaveOpen(false)}
      >
        <DialogTitle>Quitter le quiz ?</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Si vous quittez maintenant, votre progression ne sera pas sauvegardée.
            Êtes-vous sûr de vouloir quitter ?
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setConfirmLeaveOpen(false)}>
            Continuer le quiz
          </Button>
          <Button
            onClick={() => {/* Implémenter la navigation */}}
            color="error"
          >
            Quitter
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default TakeQuiz;
