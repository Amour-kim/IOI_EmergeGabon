import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Button,
  TextField,
  Slider,
  Chip,
  Divider,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Card,
  CardContent,
} from '@mui/material';
import {
  Assignment,
  Person,
  AttachFile,
  Grade as GradeIcon,
  Comment,
  Download,
  Preview,
  Send,
} from '@mui/icons-material';
import { Assignment as AssignmentType, AssignmentSubmission } from '../../types';

const mockSubmission: AssignmentSubmission = {
  id: '1',
  assignmentId: '1',
  studentId: 'student123',
  submittedAt: '2024-01-15T14:30:00',
  status: 'SUBMITTED',
  attachments: [
    {
      id: '1',
      submissionId: '1',
      fileName: 'devoir_algo_tri.py',
      fileUrl: '/files/devoir_algo_tri.py',
      fileType: 'text/x-python',
      fileSize: 4096,
      uploadedAt: '2024-01-15T14:30:00',
    },
    {
      id: '2',
      submissionId: '1',
      fileName: 'rapport.pdf',
      fileUrl: '/files/rapport.pdf',
      fileType: 'application/pdf',
      fileSize: 2097152,
      uploadedAt: '2024-01-15T14:30:00',
    },
  ],
  attempts: 1,
  lastModified: '2024-01-15T14:30:00',
};

interface RubricCriteria {
  id: string;
  title: string;
  description: string;
  maxPoints: number;
  weight: number;
}

const mockRubric: RubricCriteria[] = [
  {
    id: '1',
    title: 'Implémentation des algorithmes',
    description: 'Qualité et exactitude de l\'implémentation des trois algorithmes de tri',
    maxPoints: 10,
    weight: 0.4,
  },
  {
    id: '2',
    title: 'Analyse de complexité',
    description: 'Précision de l\'analyse de la complexité temporelle et spatiale',
    maxPoints: 5,
    weight: 0.3,
  },
  {
    id: '3',
    title: 'Tests et comparaison',
    description: 'Qualité des tests et pertinence de la comparaison des performances',
    maxPoints: 5,
    weight: 0.3,
  },
];

const GradeAssignment: React.FC = () => {
  const [grades, setGrades] = useState<{ [key: string]: number }>({});
  const [feedback, setFeedback] = useState('');
  const [previewDialogOpen, setPreviewDialogOpen] = useState(false);
  const [selectedFile, setSelectedFile] = useState<string | null>(null);

  const handleGradeChange = (criteriaId: string, value: number) => {
    setGrades({ ...grades, [criteriaId]: value });
  };

  const calculateTotalGrade = () => {
    return mockRubric.reduce((total, criteria) => {
      const grade = grades[criteria.id] || 0;
      return total + (grade * criteria.weight);
    }, 0);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('fr-FR', {
      day: '2-digit',
      month: 'long',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <Box sx={{ p: 3 }}>
      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3, mb: 3 }}>
            <Typography variant="h5" gutterBottom>
              Notation du devoir
            </Typography>
            <Box sx={{ mb: 3 }}>
              <Typography variant="subtitle1" color="textSecondary" gutterBottom>
                Soumis le {formatDate(mockSubmission.submittedAt)}
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Person sx={{ mr: 1 }} />
                <Typography>
                  Jean Dupont (ID: {mockSubmission.studentId})
                </Typography>
              </Box>
              <Chip
                label={`Tentative ${mockSubmission.attempts}`}
                color="primary"
                size="small"
              />
            </Box>

            <Typography variant="h6" gutterBottom>
              Fichiers soumis
            </Typography>
            <List>
              {mockSubmission.attachments.map((attachment) => (
                <ListItem key={attachment.id}>
                  <ListItemIcon>
                    <AttachFile />
                  </ListItemIcon>
                  <ListItemText
                    primary={attachment.fileName}
                    secondary={formatFileSize(attachment.fileSize)}
                  />
                  <Box sx={{ display: 'flex', gap: 1 }}>
                    <IconButton
                      onClick={() => {
                        setSelectedFile(attachment.fileUrl);
                        setPreviewDialogOpen(true);
                      }}
                    >
                      <Preview />
                    </IconButton>
                    <IconButton href={attachment.fileUrl} download>
                      <Download />
                    </IconButton>
                  </Box>
                </ListItem>
              ))}
            </List>
          </Paper>

          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Grille de notation
            </Typography>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Critère</TableCell>
                    <TableCell align="center">Points</TableCell>
                    <TableCell align="right">Note</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {mockRubric.map((criteria) => (
                    <TableRow key={criteria.id}>
                      <TableCell>
                        <Typography variant="subtitle1">{criteria.title}</Typography>
                        <Typography variant="body2" color="textSecondary">
                          {criteria.description}
                        </Typography>
                      </TableCell>
                      <TableCell align="center">
                        <Typography color="textSecondary">
                          /{criteria.maxPoints}
                        </Typography>
                      </TableCell>
                      <TableCell align="right" sx={{ width: '200px' }}>
                        <Slider
                          value={grades[criteria.id] || 0}
                          onChange={(_, value) =>
                            handleGradeChange(criteria.id, value as number)
                          }
                          min={0}
                          max={criteria.maxPoints}
                          step={0.5}
                          marks
                          valueLabelDisplay="auto"
                        />
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Paper>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Note finale
              </Typography>
              <Typography variant="h3" color="primary" align="center">
                {calculateTotalGrade().toFixed(1)} / 20
              </Typography>
            </CardContent>
          </Card>

          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Commentaires
            </Typography>
            <TextField
              fullWidth
              multiline
              rows={6}
              value={feedback}
              onChange={(e) => setFeedback(e.target.value)}
              placeholder="Ajoutez vos commentaires ici..."
              sx={{ mb: 2 }}
            />
            <Button
              fullWidth
              variant="contained"
              color="primary"
              startIcon={<Send />}
              onClick={() => {
                // Implémenter la soumission de la note
                console.log('Grade:', calculateTotalGrade());
                console.log('Feedback:', feedback);
              }}
            >
              Soumettre la note
            </Button>
          </Paper>
        </Grid>
      </Grid>

      <Dialog
        open={previewDialogOpen}
        onClose={() => setPreviewDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Aperçu du fichier</DialogTitle>
        <DialogContent>
          {/* Implémenter l'aperçu du fichier ici */}
          <Typography>
            Aperçu non disponible pour {selectedFile}
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setPreviewDialogOpen(false)}>
            Fermer
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default GradeAssignment;
