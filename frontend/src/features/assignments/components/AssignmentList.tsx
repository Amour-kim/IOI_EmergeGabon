import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  Card,
  CardContent,
  CardActions,
  Button,
  Chip,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  IconButton,
} from '@mui/material';
import {
  Assignment as AssignmentIcon,
  Search,
  FilterList,
  CalendarToday,
  Grade,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { Assignment, AssignmentType, AssignmentStatus } from '../types';

const mockAssignments: Assignment[] = [
  {
    id: '1',
    courseId: 'CS101',
    title: 'Devoir de Programmation #1',
    description: 'Implémenter un algorithme de tri en Python',
    type: AssignmentType.HOMEWORK,
    dueDate: '2024-01-20T23:59:59',
    totalPoints: 20,
    weight: 0.15,
    status: AssignmentStatus.PUBLISHED,
    attachments: [],
    submissionType: ['FILE', 'CODE'],
    createdAt: '2024-01-01T10:00:00',
    updatedAt: '2024-01-01T10:00:00',
    createdBy: 'prof.dupont',
  },
  // Ajoutez d'autres devoirs ici
];

const AssignmentList: React.FC = () => {
  const navigate = useNavigate();
  const [searchTerm, setSearchTerm] = useState('');
  const [typeFilter, setTypeFilter] = useState<string>('');
  const [statusFilter, setStatusFilter] = useState<string>('');

  const getStatusColor = (status: AssignmentStatus) => {
    switch (status) {
      case AssignmentStatus.PUBLISHED:
        return 'primary';
      case AssignmentStatus.CLOSED:
        return 'error';
      case AssignmentStatus.GRADING:
        return 'warning';
      case AssignmentStatus.GRADED:
        return 'success';
      default:
        return 'default';
    }
  };

  const getTypeLabel = (type: AssignmentType) => {
    const labels = {
      [AssignmentType.HOMEWORK]: 'Devoir',
      [AssignmentType.QUIZ]: 'Quiz',
      [AssignmentType.EXAM]: 'Examen',
      [AssignmentType.PROJECT]: 'Projet',
      [AssignmentType.PRESENTATION]: 'Présentation',
    };
    return labels[type];
  };

  const getStatusLabel = (status: AssignmentStatus) => {
    const labels = {
      [AssignmentStatus.DRAFT]: 'Brouillon',
      [AssignmentStatus.PUBLISHED]: 'Publié',
      [AssignmentStatus.CLOSED]: 'Fermé',
      [AssignmentStatus.GRADING]: 'En cours de notation',
      [AssignmentStatus.GRADED]: 'Noté',
    };
    return labels[status];
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

  const filteredAssignments = mockAssignments.filter((assignment) => {
    const matchesSearch = assignment.title.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesType = !typeFilter || assignment.type === typeFilter;
    const matchesStatus = !statusFilter || assignment.status === statusFilter;
    return matchesSearch && matchesType && matchesStatus;
  });

  return (
    <Box sx={{ p: 3 }}>
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h4" gutterBottom>
          Devoirs et Examens
        </Typography>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              variant="outlined"
              placeholder="Rechercher un devoir..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              InputProps={{
                startAdornment: <Search color="action" sx={{ mr: 1 }} />,
              }}
            />
          </Grid>
          <Grid item xs={12} md={3}>
            <FormControl fullWidth>
              <InputLabel>Type</InputLabel>
              <Select
                value={typeFilter}
                label="Type"
                onChange={(e) => setTypeFilter(e.target.value)}
              >
                <MenuItem value="">Tous</MenuItem>
                {Object.values(AssignmentType).map((type) => (
                  <MenuItem key={type} value={type}>
                    {getTypeLabel(type)}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={3}>
            <FormControl fullWidth>
              <InputLabel>Statut</InputLabel>
              <Select
                value={statusFilter}
                label="Statut"
                onChange={(e) => setStatusFilter(e.target.value)}
              >
                <MenuItem value="">Tous</MenuItem>
                {Object.values(AssignmentStatus).map((status) => (
                  <MenuItem key={status} value={status}>
                    {getStatusLabel(status)}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
        </Grid>
      </Paper>

      <Grid container spacing={3}>
        {filteredAssignments.map((assignment) => (
          <Grid item xs={12} md={6} lg={4} key={assignment.id}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <AssignmentIcon color="primary" sx={{ mr: 1 }} />
                  <Typography variant="h6" component="div">
                    {assignment.title}
                  </Typography>
                </Box>

                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  {assignment.description}
                </Typography>

                <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                  <Chip
                    label={getTypeLabel(assignment.type)}
                    size="small"
                    color="primary"
                  />
                  <Chip
                    label={getStatusLabel(assignment.status)}
                    size="small"
                    color={getStatusColor(assignment.status)}
                  />
                </Box>

                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <CalendarToday sx={{ mr: 1, fontSize: 'small' }} color="action" />
                  <Typography variant="body2" color="text.secondary">
                    À rendre le : {formatDate(assignment.dueDate)}
                  </Typography>
                </Box>

                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <Grade sx={{ mr: 1, fontSize: 'small' }} color="action" />
                  <Typography variant="body2" color="text.secondary">
                    {assignment.totalPoints} points ({Math.round(assignment.weight * 100)}% de la note finale)
                  </Typography>
                </Box>
              </CardContent>
              <CardActions>
                <Button
                  size="small"
                  color="primary"
                  onClick={() => navigate(`/assignments/${assignment.id}`)}
                >
                  Voir les détails
                </Button>
                <Button
                  size="small"
                  color="secondary"
                  onClick={() => navigate(`/assignments/${assignment.id}/submit`)}
                >
                  Soumettre
                </Button>
              </CardActions>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
};

export default AssignmentList;
