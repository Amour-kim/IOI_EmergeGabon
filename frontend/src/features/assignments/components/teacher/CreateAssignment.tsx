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
  Chip,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  FormHelperText,
  Switch,
  FormControlLabel,
} from '@mui/material';
import {
  Save,
  CloudUpload,
  Delete,
  Description,
  Preview,
  Publish,
} from '@mui/icons-material';
import { useFormik } from 'formik';
import * as Yup from 'yup';
import { AssignmentType, SubmissionType } from '../../types';
import { DateTimePicker } from '@mui/x-date-pickers/DateTimePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { fr } from 'date-fns/locale';

const validationSchema = Yup.object({
  title: Yup.string()
    .required('Le titre est requis')
    .min(5, 'Le titre doit contenir au moins 5 caractères'),
  description: Yup.string()
    .required('La description est requise')
    .min(20, 'La description doit contenir au moins 20 caractères'),
  type: Yup.string().required('Le type est requis'),
  dueDate: Yup.date()
    .required('La date limite est requise')
    .min(new Date(), 'La date limite doit être dans le futur'),
  totalPoints: Yup.number()
    .required('Le nombre de points est requis')
    .min(1, 'Le minimum est 1 point')
    .max(100, 'Le maximum est 100 points'),
  weight: Yup.number()
    .required('La pondération est requise')
    .min(0, 'La pondération minimum est 0')
    .max(1, 'La pondération maximum est 1'),
  submissionTypes: Yup.array()
    .of(Yup.string())
    .min(1, 'Au moins un type de soumission est requis'),
});

const CreateAssignment: React.FC = () => {
  const [attachments, setAttachments] = useState<File[]>([]);
  const [previewMode, setPreviewMode] = useState(false);

  const formik = useFormik({
    initialValues: {
      title: '',
      description: '',
      type: '',
      dueDate: new Date(),
      totalPoints: 20,
      weight: 0.1,
      submissionTypes: [] as string[],
      allowLateSubmissions: false,
      maxAttempts: 1,
      requiresRubric: false,
    },
    validationSchema,
    onSubmit: (values) => {
      console.log('Form Values:', values);
      console.log('Attachments:', attachments);
      // Implémenter la soumission du formulaire
    },
  });

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files) {
      setAttachments([...attachments, ...Array.from(event.target.files)]);
    }
  };

  const handleRemoveFile = (index: number) => {
    setAttachments(attachments.filter((_, i) => i !== index));
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <LocalizationProvider dateAdapter={AdapterDateFns} adapterLocale={fr}>
      <Box sx={{ p: 3 }}>
        <Paper sx={{ p: 3 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
            <Typography variant="h4">Créer un nouveau devoir</Typography>
            <FormControlLabel
              control={
                <Switch
                  checked={previewMode}
                  onChange={(e) => setPreviewMode(e.target.checked)}
                />
              }
              label="Mode aperçu"
            />
          </Box>

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
                  disabled={previewMode}
                  sx={{ mb: 3 }}
                />

                <TextField
                  fullWidth
                  label="Description"
                  name="description"
                  multiline
                  rows={6}
                  value={formik.values.description}
                  onChange={formik.handleChange}
                  error={formik.touched.description && Boolean(formik.errors.description)}
                  helperText={formik.touched.description && formik.errors.description}
                  disabled={previewMode}
                  sx={{ mb: 3 }}
                />

                <Grid container spacing={3}>
                  <Grid item xs={12} md={6}>
                    <FormControl fullWidth error={formik.touched.type && Boolean(formik.errors.type)}>
                      <InputLabel>Type</InputLabel>
                      <Select
                        name="type"
                        value={formik.values.type}
                        onChange={formik.handleChange}
                        disabled={previewMode}
                      >
                        {Object.values(AssignmentType).map((type) => (
                          <MenuItem key={type} value={type}>
                            {type}
                          </MenuItem>
                        ))}
                      </Select>
                      <FormHelperText>
                        {formik.touched.type && formik.errors.type}
                      </FormHelperText>
                    </FormControl>
                  </Grid>

                  <Grid item xs={12} md={6}>
                    <DateTimePicker
                      label="Date limite"
                      value={formik.values.dueDate}
                      onChange={(value) => formik.setFieldValue('dueDate', value)}
                      disabled={previewMode}
                      slotProps={{
                        textField: {
                          fullWidth: true,
                          error: formik.touched.dueDate && Boolean(formik.errors.dueDate),
                          helperText: formik.touched.dueDate && formik.errors.dueDate,
                        },
                      }}
                    />
                  </Grid>
                </Grid>
              </Grid>

              <Grid item xs={12} md={4}>
                <Paper sx={{ p: 2, mb: 3 }}>
                  <Typography variant="h6" gutterBottom>
                    Notation
                  </Typography>
                  <TextField
                    fullWidth
                    label="Points totaux"
                    name="totalPoints"
                    type="number"
                    value={formik.values.totalPoints}
                    onChange={formik.handleChange}
                    error={formik.touched.totalPoints && Boolean(formik.errors.totalPoints)}
                    helperText={formik.touched.totalPoints && formik.errors.totalPoints}
                    disabled={previewMode}
                    sx={{ mb: 2 }}
                  />
                  <TextField
                    fullWidth
                    label="Pondération"
                    name="weight"
                    type="number"
                    inputProps={{ step: 0.1, min: 0, max: 1 }}
                    value={formik.values.weight}
                    onChange={formik.handleChange}
                    error={formik.touched.weight && Boolean(formik.errors.weight)}
                    helperText={formik.touched.weight && formik.errors.weight}
                    disabled={previewMode}
                  />
                </Paper>

                <Paper sx={{ p: 2, mb: 3 }}>
                  <Typography variant="h6" gutterBottom>
                    Options de soumission
                  </Typography>
                  <FormControl
                    fullWidth
                    error={
                      formik.touched.submissionTypes && Boolean(formik.errors.submissionTypes)
                    }
                  >
                    <InputLabel>Types de soumission</InputLabel>
                    <Select
                      multiple
                      name="submissionTypes"
                      value={formik.values.submissionTypes}
                      onChange={formik.handleChange}
                      disabled={previewMode}
                      renderValue={(selected) => (
                        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                          {(selected as string[]).map((value) => (
                            <Chip key={value} label={value} />
                          ))}
                        </Box>
                      )}
                    >
                      {Object.values(SubmissionType).map((type) => (
                        <MenuItem key={type} value={type}>
                          {type}
                        </MenuItem>
                      ))}
                    </Select>
                    <FormHelperText>
                      {formik.touched.submissionTypes && formik.errors.submissionTypes}
                    </FormHelperText>
                  </FormControl>

                  <FormControlLabel
                    control={
                      <Switch
                        name="allowLateSubmissions"
                        checked={formik.values.allowLateSubmissions}
                        onChange={formik.handleChange}
                        disabled={previewMode}
                      />
                    }
                    label="Autoriser les soumissions en retard"
                    sx={{ mt: 2 }}
                  />

                  <TextField
                    fullWidth
                    label="Nombre maximum de tentatives"
                    name="maxAttempts"
                    type="number"
                    value={formik.values.maxAttempts}
                    onChange={formik.handleChange}
                    disabled={previewMode}
                    sx={{ mt: 2 }}
                  />
                </Paper>
              </Grid>

              <Grid item xs={12}>
                <Paper sx={{ p: 2 }}>
                  <Typography variant="h6" gutterBottom>
                    Pièces jointes
                  </Typography>
                  <input
                    type="file"
                    multiple
                    onChange={handleFileSelect}
                    style={{ display: 'none' }}
                    id="file-input"
                    disabled={previewMode}
                  />
                  <label htmlFor="file-input">
                    <Button
                      variant="outlined"
                      component="span"
                      startIcon={<CloudUpload />}
                      disabled={previewMode}
                    >
                      Ajouter des fichiers
                    </Button>
                  </label>

                  <List>
                    {attachments.map((file, index) => (
                      <ListItem key={index}>
                        <ListItemIcon>
                          <Description />
                        </ListItemIcon>
                        <ListItemText
                          primary={file.name}
                          secondary={formatFileSize(file.size)}
                        />
                        <ListItemSecondaryAction>
                          <IconButton
                            edge="end"
                            onClick={() => handleRemoveFile(index)}
                            disabled={previewMode}
                          >
                            <Delete />
                          </IconButton>
                        </ListItemSecondaryAction>
                      </ListItem>
                    ))}
                  </List>
                </Paper>
              </Grid>

              <Grid item xs={12}>
                <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
                  <Button
                    variant="outlined"
                    startIcon={<Save />}
                    onClick={() => formik.submitForm()}
                    disabled={previewMode}
                  >
                    Enregistrer comme brouillon
                  </Button>
                  <Button
                    variant="contained"
                    color="primary"
                    startIcon={<Publish />}
                    onClick={() => formik.submitForm()}
                    disabled={previewMode}
                  >
                    Publier
                  </Button>
                </Box>
              </Grid>
            </Grid>
          </form>
        </Paper>
      </Box>
    </LocalizationProvider>
  );
};

export default CreateAssignment;
