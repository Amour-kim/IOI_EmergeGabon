import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  Card,
  CardContent,
  Button,
  Chip,
  Divider,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
} from '@mui/material';
import {
  Assignment as AssignmentIcon,
  CalendarToday,
  AttachFile,
  CloudUpload,
  Grade,
  Description,
  Delete,
} from '@mui/icons-material';
import { useParams } from 'react-router-dom';
import { Assignment, AssignmentStatus, SubmissionStatus } from '../types';

const mockAssignment: Assignment = {
  id: '1',
  courseId: 'CS101',
  title: 'Devoir de Programmation #1',
  description: `Dans ce devoir, vous devrez implémenter trois algorithmes de tri différents en Python :
  1. Tri à bulles
  2. Tri par insertion
  3. Tri rapide (Quicksort)
  
  Pour chaque algorithme, vous devrez :
  - Écrire une implémentation propre et commentée
  - Analyser la complexité temporelle et spatiale
  - Comparer les performances sur différentes tailles de données`,
  type: 'HOMEWORK',
  dueDate: '2024-01-20T23:59:59',
  totalPoints: 20,
  weight: 0.15,
  status: AssignmentStatus.PUBLISHED,
  attachments: [
    {
      id: '1',
      fileName: 'consignes_devoir.pdf',
      fileUrl: '/files/consignes_devoir.pdf',
      fileType: 'application/pdf',
      fileSize: 245760,
      uploadedAt: '2024-01-01T10:00:00',
    },
    {
      id: '2',
      fileName: 'donnees_test.zip',
      fileUrl: '/files/donnees_test.zip',
      fileType: 'application/zip',
      fileSize: 1048576,
      uploadedAt: '2024-01-01T10:00:00',
    },
  ],
  submissionType: ['FILE', 'CODE'],
  createdAt: '2024-01-01T10:00:00',
  updatedAt: '2024-01-01T10:00:00',
  createdBy: 'prof.dupont',
};

const AssignmentDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [uploadDialogOpen, setUploadDialogOpen] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [comment, setComment] = useState('');

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

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files) {
      setSelectedFiles(Array.from(event.target.files));
    }
  };

  const handleSubmit = () => {
    // Implémenter la logique de soumission ici
    console.log('Files:', selectedFiles);
    console.log('Comment:', comment);
    setUploadDialogOpen(false);
  };

  return (
    <Box sx={{ p: 3 }}>
      <Paper sx={{ p: 3, mb: 3 }}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={8}>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              <AssignmentIcon color="primary" sx={{ mr: 2, fontSize: 40 }} />
              <Box>
                <Typography variant="h4" gutterBottom>
                  {mockAssignment.title}
                </Typography>
                <Typography variant="subtitle1" color="textSecondary">
                  Cours : Introduction à la Programmation (CS101)
                </Typography>
              </Box>
            </Box>

            <Box sx={{ display: 'flex', gap: 1, mb: 3 }}>
              <Chip label="Devoir" color="primary" />
              <Chip label="Publié" color="success" />
            </Box>

            <Typography variant="h6" gutterBottom>
              Description
            </Typography>
            <Typography variant="body1" paragraph sx={{ whiteSpace: 'pre-line' }}>
              {mockAssignment.description}
            </Typography>
          </Grid>

          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Informations
                </Typography>
                <List>
                  <ListItem>
                    <ListItemIcon>
                      <CalendarToday />
                    </ListItemIcon>
                    <ListItemText
                      primary="Date limite"
                      secondary={formatDate(mockAssignment.dueDate)}
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemIcon>
                      <Grade />
                    </ListItemIcon>
                    <ListItemText
                      primary="Points"
                      secondary={`${mockAssignment.totalPoints} points (${Math.round(mockAssignment.weight * 100)}% de la note finale)`}
                    />
                  </ListItem>
                </List>

                <Button
                  variant="contained"
                  color="primary"
                  fullWidth
                  startIcon={<CloudUpload />}
                  onClick={() => setUploadDialogOpen(true)}
                  sx={{ mt: 2 }}
                >
                  Soumettre le devoir
                </Button>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Paper>

      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>
          Fichiers joints
        </Typography>
        <List>
          {mockAssignment.attachments.map((attachment) => (
            <ListItem
              key={attachment.id}
              secondaryAction={
                <Button
                  startIcon={<AttachFile />}
                  href={attachment.fileUrl}
                  target="_blank"
                >
                  Télécharger
                </Button>
              }
            >
              <ListItemIcon>
                <Description />
              </ListItemIcon>
              <ListItemText
                primary={attachment.fileName}
                secondary={formatFileSize(attachment.fileSize)}
              />
            </ListItem>
          ))}
        </List>
      </Paper>

      <Dialog
        open={uploadDialogOpen}
        onClose={() => setUploadDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Soumettre le devoir</DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 2 }}>
            <Typography variant="subtitle1" gutterBottom>
              Fichiers sélectionnés
            </Typography>
            <input
              type="file"
              multiple
              onChange={handleFileSelect}
              style={{ display: 'none' }}
              id="file-input"
            />
            <label htmlFor="file-input">
              <Button
                variant="outlined"
                component="span"
                startIcon={<CloudUpload />}
                sx={{ mb: 2 }}
              >
                Sélectionner des fichiers
              </Button>
            </label>
            <List>
              {selectedFiles.map((file, index) => (
                <ListItem
                  key={index}
                  secondaryAction={
                    <IconButton
                      edge="end"
                      onClick={() => {
                        setSelectedFiles(selectedFiles.filter((_, i) => i !== index));
                      }}
                    >
                      <Delete />
                    </IconButton>
                  }
                >
                  <ListItemIcon>
                    <Description />
                  </ListItemIcon>
                  <ListItemText
                    primary={file.name}
                    secondary={formatFileSize(file.size)}
                  />
                </ListItem>
              ))}
            </List>

            <TextField
              fullWidth
              label="Commentaire (optionnel)"
              multiline
              rows={4}
              value={comment}
              onChange={(e) => setComment(e.target.value)}
              sx={{ mt: 2 }}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setUploadDialogOpen(false)}>Annuler</Button>
          <Button
            onClick={handleSubmit}
            variant="contained"
            color="primary"
            disabled={selectedFiles.length === 0}
          >
            Soumettre
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default AssignmentDetail;
