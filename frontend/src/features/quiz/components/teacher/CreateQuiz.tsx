import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Grid,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  FormControlLabel,
  Switch,
  IconButton,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Card,
  CardContent,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Tooltip,
} from '@mui/material';
import {
  Add as AddIcon,
  Delete as DeleteIcon,
  DragIndicator,
  Save,
  Preview,
  Publish,
} from '@mui/icons-material';
import { useFormik } from 'formik';
import * as Yup from 'yup';
import { QuestionType, QuizStatus } from '../../types';
import { DateTimePicker } from '@mui/x-date-pickers/DateTimePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { fr } from 'date-fns/locale';
import { DragDropContext, Droppable, Draggable } from 'react-beautiful-dnd';

const validationSchema = Yup.object({
  title: Yup.string()
    .required('Le titre est requis')
    .min(5, 'Le titre doit contenir au moins 5 caractères'),
  description: Yup.string()
    .required('La description est requise')
    .min(20, 'La description doit contenir au moins 20 caractères'),
  timeLimit: Yup.number()
    .required('La durée est requise')
    .min(1, 'La durée minimum est de 1 minute')
    .max(180, 'La durée maximum est de 180 minutes'),
  startDate: Yup.date()
    .required('La date de début est requise')
    .min(new Date(), 'La date de début doit être dans le futur'),
  endDate: Yup.date()
    .required('La date de fin est requise')
    .min(Yup.ref('startDate'), 'La date de fin doit être après la date de début'),
  passingScore: Yup.number()
    .required('Le score minimum est requis')
    .min(0, 'Le score minimum est 0')
    .max(100, 'Le score maximum est 100'),
  maxAttempts: Yup.number()
    .required('Le nombre de tentatives est requis')
    .min(1, 'Le minimum est 1 tentative'),
});

interface QuestionFormData {
  type: QuestionType;
  question: string;
  points: number;
  options: { text: string; isCorrect: boolean }[];
  explanation?: string;
}

const initialQuestionForm: QuestionFormData = {
  type: QuestionType.SINGLE_CHOICE,
  question: '',
  points: 1,
  options: [
    { text: '', isCorrect: false },
    { text: '', isCorrect: false },
  ],
};

const CreateQuiz: React.FC = () => {
  const [questions, setQuestions] = useState<QuestionFormData[]>([]);
  const [questionDialogOpen, setQuestionDialogOpen] = useState(false);
  const [currentQuestion, setCurrentQuestion] = useState<QuestionFormData>(initialQuestionForm);
  const [editingIndex, setEditingIndex] = useState<number | null>(null);

  const formik = useFormik({
    initialValues: {
      title: '',
      description: '',
      timeLimit: 30,
      startDate: new Date(),
      endDate: new Date(),
      totalPoints: 0,
      passingScore: 60,
      shuffleQuestions: true,
      showResults: true,
      allowReview: true,
      maxAttempts: 1,
    },
    validationSchema,
    onSubmit: (values) => {
      const quizData = {
        ...values,
        questions,
        status: QuizStatus.DRAFT,
      };
      console.log('Quiz Data:', quizData);
      // Implémenter la soumission du quiz
    },
  });

  const handleQuestionSubmit = () => {
    if (editingIndex !== null) {
      const updatedQuestions = [...questions];
      updatedQuestions[editingIndex] = currentQuestion;
      setQuestions(updatedQuestions);
    } else {
      setQuestions([...questions, currentQuestion]);
    }
    setQuestionDialogOpen(false);
    setCurrentQuestion(initialQuestionForm);
    setEditingIndex(null);
  };

  const handleQuestionEdit = (index: number) => {
    setCurrentQuestion(questions[index]);
    setEditingIndex(index);
    setQuestionDialogOpen(true);
  };

  const handleQuestionDelete = (index: number) => {
    setQuestions(questions.filter((_, i) => i !== index));
  };

  const handleOptionChange = (index: number, value: string) => {
    const updatedOptions = [...currentQuestion.options];
    updatedOptions[index] = { ...updatedOptions[index], text: value };
    setCurrentQuestion({ ...currentQuestion, options: updatedOptions });
  };

  const handleCorrectAnswerChange = (index: number) => {
    const updatedOptions = currentQuestion.options.map((option, i) => ({
      ...option,
      isCorrect: currentQuestion.type === QuestionType.SINGLE_CHOICE
        ? i === index
        : i === index ? !option.isCorrect : option.isCorrect,
    }));
    setCurrentQuestion({ ...currentQuestion, options: updatedOptions });
  };

  const handleDragEnd = (result: any) => {
    if (!result.destination) return;

    const items = Array.from(questions);
    const [reorderedItem] = items.splice(result.source.index, 1);
    items.splice(result.destination.index, 0, reorderedItem);

    setQuestions(items);
  };

  return (
    <LocalizationProvider dateAdapter={AdapterDateFns} adapterLocale={fr}>
      <Box sx={{ p: 3 }}>
        <Paper sx={{ p: 3 }}>
          <Typography variant="h4" gutterBottom>
            Créer un nouveau quiz
          </Typography>

          <form onSubmit={formik.handleSubmit}>
            <Grid container spacing={3}>
              <Grid item xs={12} md={8}>
                <TextField
                  fullWidth
                  label="Titre"
                  name="title"
                  value={formik.values.title}
                  onChange={formik.handleChange}
                  error={formik.touched.title && Boolean(formik.errors.title)}
                  helperText={formik.touched.title && formik.errors.title}
                  sx={{ mb: 3 }}
                />

                <TextField
                  fullWidth
                  label="Description"
                  name="description"
                  multiline
                  rows={4}
                  value={formik.values.description}
                  onChange={formik.handleChange}
                  error={formik.touched.description && Boolean(formik.errors.description)}
                  helperText={formik.touched.description && formik.errors.description}
                  sx={{ mb: 3 }}
                />

                <Grid container spacing={3}>
                  <Grid item xs={12} md={6}>
                    <DateTimePicker
                      label="Date de début"
                      value={formik.values.startDate}
                      onChange={(value) => formik.setFieldValue('startDate', value)}
                      slotProps={{
                        textField: {
                          fullWidth: true,
                          error: formik.touched.startDate && Boolean(formik.errors.startDate),
                          helperText: formik.touched.startDate && formik.errors.startDate,
                        },
                      }}
                    />
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <DateTimePicker
                      label="Date de fin"
                      value={formik.values.endDate}
                      onChange={(value) => formik.setFieldValue('endDate', value)}
                      slotProps={{
                        textField: {
                          fullWidth: true,
                          error: formik.touched.endDate && Boolean(formik.errors.endDate),
                          helperText: formik.touched.endDate && formik.errors.endDate,
                        },
                      }}
                    />
                  </Grid>
                </Grid>
              </Grid>

              <Grid item xs={12} md={4}>
                <Card sx={{ mb: 3 }}>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Paramètres
                    </Typography>
                    <TextField
                      fullWidth
                      label="Durée (minutes)"
                      name="timeLimit"
                      type="number"
                      value={formik.values.timeLimit}
                      onChange={formik.handleChange}
                      error={formik.touched.timeLimit && Boolean(formik.errors.timeLimit)}
                      helperText={formik.touched.timeLimit && formik.errors.timeLimit}
                      sx={{ mb: 2 }}
                    />
                    <TextField
                      fullWidth
                      label="Score minimum (%)"
                      name="passingScore"
                      type="number"
                      value={formik.values.passingScore}
                      onChange={formik.handleChange}
                      error={formik.touched.passingScore && Boolean(formik.errors.passingScore)}
                      helperText={formik.touched.passingScore && formik.errors.passingScore}
                      sx={{ mb: 2 }}
                    />
                    <TextField
                      fullWidth
                      label="Nombre de tentatives"
                      name="maxAttempts"
                      type="number"
                      value={formik.values.maxAttempts}
                      onChange={formik.handleChange}
                      error={formik.touched.maxAttempts && Boolean(formik.errors.maxAttempts)}
                      helperText={formik.touched.maxAttempts && formik.errors.maxAttempts}
                      sx={{ mb: 2 }}
                    />
                    <FormControlLabel
                      control={
                        <Switch
                          name="shuffleQuestions"
                          checked={formik.values.shuffleQuestions}
                          onChange={formik.handleChange}
                        />
                      }
                      label="Mélanger les questions"
                    />
                    <FormControlLabel
                      control={
                        <Switch
                          name="showResults"
                          checked={formik.values.showResults}
                          onChange={formik.handleChange}
                        />
                      }
                      label="Montrer les résultats"
                    />
                    <FormControlLabel
                      control={
                        <Switch
                          name="allowReview"
                          checked={formik.values.allowReview}
                          onChange={formik.handleChange}
                        />
                      }
                      label="Permettre la révision"
                    />
                  </CardContent>
                </Card>
              </Grid>

              <Grid item xs={12}>
                <Paper sx={{ p: 2 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                    <Typography variant="h6">
                      Questions ({questions.length})
                    </Typography>
                    <Button
                      variant="contained"
                      startIcon={<AddIcon />}
                      onClick={() => {
                        setCurrentQuestion(initialQuestionForm);
                        setEditingIndex(null);
                        setQuestionDialogOpen(true);
                      }}
                    >
                      Ajouter une question
                    </Button>
                  </Box>

                  <DragDropContext onDragEnd={handleDragEnd}>
                    <Droppable droppableId="questions">
                      {(provided) => (
                        <List {...provided.droppableProps} ref={provided.innerRef}>
                          {questions.map((question, index) => (
                            <Draggable
                              key={index}
                              draggableId={`question-${index}`}
                              index={index}
                            >
                              {(provided) => (
                                <ListItem
                                  ref={provided.innerRef}
                                  {...provided.draggableProps}
                                  sx={{ border: 1, borderColor: 'divider', mb: 1 }}
                                >
                                  <Box {...provided.dragHandleProps} sx={{ mr: 2 }}>
                                    <DragIndicator />
                                  </Box>
                                  <ListItemText
                                    primary={question.question}
                                    secondary={`${question.type} - ${question.points} points`}
                                  />
                                  <ListItemSecondaryAction>
                                    <IconButton
                                      edge="end"
                                      onClick={() => handleQuestionEdit(index)}
                                      sx={{ mr: 1 }}
                                    >
                                      <Preview />
                                    </IconButton>
                                    <IconButton
                                      edge="end"
                                      onClick={() => handleQuestionDelete(index)}
                                    >
                                      <DeleteIcon />
                                    </IconButton>
                                  </ListItemSecondaryAction>
                                </ListItem>
                              )}
                            </Draggable>
                          ))}
                          {provided.placeholder}
                        </List>
                      )}
                    </Droppable>
                  </DragDropContext>
                </Paper>
              </Grid>

              <Grid item xs={12}>
                <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
                  <Button
                    variant="outlined"
                    startIcon={<Save />}
                    onClick={() => formik.submitForm()}
                  >
                    Enregistrer comme brouillon
                  </Button>
                  <Button
                    variant="contained"
                    color="primary"
                    startIcon={<Publish />}
                    onClick={() => formik.submitForm()}
                    disabled={questions.length === 0}
                  >
                    Publier
                  </Button>
                </Box>
              </Grid>
            </Grid>
          </form>
        </Paper>

        <Dialog
          open={questionDialogOpen}
          onClose={() => setQuestionDialogOpen(false)}
          maxWidth="md"
          fullWidth
        >
          <DialogTitle>
            {editingIndex !== null ? 'Modifier la question' : 'Nouvelle question'}
          </DialogTitle>
          <DialogContent>
            <Box sx={{ pt: 2 }}>
              <FormControl fullWidth sx={{ mb: 3 }}>
                <InputLabel>Type de question</InputLabel>
                <Select
                  value={currentQuestion.type}
                  onChange={(e) => setCurrentQuestion({
                    ...currentQuestion,
                    type: e.target.value as QuestionType,
                  })}
                >
                  <MenuItem value={QuestionType.SINGLE_CHOICE}>Choix unique</MenuItem>
                  <MenuItem value={QuestionType.MULTIPLE_CHOICE}>Choix multiple</MenuItem>
                  <MenuItem value={QuestionType.TRUE_FALSE}>Vrai/Faux</MenuItem>
                  <MenuItem value={QuestionType.SHORT_ANSWER}>Réponse courte</MenuItem>
                </Select>
              </FormControl>

              <TextField
                fullWidth
                label="Question"
                value={currentQuestion.question}
                onChange={(e) => setCurrentQuestion({
                  ...currentQuestion,
                  question: e.target.value,
                })}
                multiline
                rows={3}
                sx={{ mb: 3 }}
              />

              <TextField
                fullWidth
                label="Points"
                type="number"
                value={currentQuestion.points}
                onChange={(e) => setCurrentQuestion({
                  ...currentQuestion,
                  points: Number(e.target.value),
                })}
                sx={{ mb: 3 }}
              />

              {currentQuestion.type !== QuestionType.SHORT_ANSWER && (
                <Box sx={{ mb: 3 }}>
                  <Typography variant="subtitle1" gutterBottom>
                    Options
                  </Typography>
                  {currentQuestion.options.map((option, index) => (
                    <Box key={index} sx={{ display: 'flex', gap: 2, mb: 2 }}>
                      <TextField
                        fullWidth
                        label={`Option ${index + 1}`}
                        value={option.text}
                        onChange={(e) => handleOptionChange(index, e.target.value)}
                      />
                      <FormControlLabel
                        control={
                          <Switch
                            checked={option.isCorrect}
                            onChange={() => handleCorrectAnswerChange(index)}
                          />
                        }
                        label="Correcte"
                      />
                      {index > 1 && (
                        <IconButton onClick={() => {
                          const updatedOptions = [...currentQuestion.options];
                          updatedOptions.splice(index, 1);
                          setCurrentQuestion({
                            ...currentQuestion,
                            options: updatedOptions,
                          });
                        }}>
                          <DeleteIcon />
                        </IconButton>
                      )}
                    </Box>
                  ))}
                  <Button
                    startIcon={<AddIcon />}
                    onClick={() => setCurrentQuestion({
                      ...currentQuestion,
                      options: [...currentQuestion.options, { text: '', isCorrect: false }],
                    })}
                  >
                    Ajouter une option
                  </Button>
                </Box>
              )}

              <TextField
                fullWidth
                label="Explication (optionnelle)"
                value={currentQuestion.explanation || ''}
                onChange={(e) => setCurrentQuestion({
                  ...currentQuestion,
                  explanation: e.target.value,
                })}
                multiline
                rows={2}
              />
            </Box>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setQuestionDialogOpen(false)}>
              Annuler
            </Button>
            <Button
              onClick={handleQuestionSubmit}
              variant="contained"
              color="primary"
              disabled={!currentQuestion.question || currentQuestion.points < 1}
            >
              {editingIndex !== null ? 'Modifier' : 'Ajouter'}
            </Button>
          </DialogActions>
        </Dialog>
      </Box>
    </LocalizationProvider>
  );
};

export default CreateQuiz;
