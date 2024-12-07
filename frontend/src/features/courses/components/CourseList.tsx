import React, { useState } from 'react';
import {
  Grid,
  Card,
  CardContent,
  CardHeader,
  CardActions,
  Typography,
  Button,
  Chip,
  TextField,
  Box,
  IconButton,
  Menu,
  MenuItem,
  FormControl,
  InputLabel,
  Select,
} from '@mui/material';
import {
  Search,
  FilterList,
  MoreVert,
  School,
  Schedule,
  Person,
} from '@mui/icons-material';
import { Course } from '../types';
import { useNavigate } from 'react-router-dom';

const mockCourses: Course[] = [
  {
    id: '1',
    title: 'Introduction à la Programmation',
    code: 'CS101',
    description: 'Cours d\'introduction aux concepts de base de la programmation',
    teacher: {
      id: '1',
      firstName: 'Jean',
      lastName: 'Dupont',
    },
    credits: 3,
    level: 'Débutant',
    language: 'Français',
    maxStudents: 50,
    enrolledStudents: 35,
    startDate: '2024-01-15',
    endDate: '2024-05-30',
    schedule: [
      {
        id: '1',
        dayOfWeek: 1,
        startTime: '09:00',
        endTime: '11:00',
        room: 'A101',
      },
    ],
    prerequisites: [],
    status: 'ACTIVE',
  },
  // Ajoutez d'autres cours ici
];

const CourseList: React.FC = () => {
  const navigate = useNavigate();
  const [searchTerm, setSearchTerm] = useState('');
  const [filterAnchorEl, setFilterAnchorEl] = useState<null | HTMLElement>(null);
  const [levelFilter, setLevelFilter] = useState<string>('');
  const [languageFilter, setLanguageFilter] = useState<string>('');

  const handleFilterClick = (event: React.MouseEvent<HTMLElement>) => {
    setFilterAnchorEl(event.currentTarget);
  };

  const handleFilterClose = () => {
    setFilterAnchorEl(null);
  };

  const filteredCourses = mockCourses.filter((course) => {
    const matchesSearch = course.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      course.code.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesLevel = !levelFilter || course.level === levelFilter;
    const matchesLanguage = !languageFilter || course.language === languageFilter;
    return matchesSearch && matchesLevel && matchesLanguage;
  });

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" gutterBottom>
          Cours disponibles
        </Typography>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              variant="outlined"
              placeholder="Rechercher un cours..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              InputProps={{
                startAdornment: <Search color="action" sx={{ mr: 1 }} />,
              }}
            />
          </Grid>
          <Grid item>
            <IconButton onClick={handleFilterClick}>
              <FilterList />
            </IconButton>
            <Menu
              anchorEl={filterAnchorEl}
              open={Boolean(filterAnchorEl)}
              onClose={handleFilterClose}
            >
              <Box sx={{ p: 2, minWidth: 200 }}>
                <FormControl fullWidth sx={{ mb: 2 }}>
                  <InputLabel>Niveau</InputLabel>
                  <Select
                    value={levelFilter}
                    label="Niveau"
                    onChange={(e) => setLevelFilter(e.target.value)}
                  >
                    <MenuItem value="">Tous</MenuItem>
                    <MenuItem value="Débutant">Débutant</MenuItem>
                    <MenuItem value="Intermédiaire">Intermédiaire</MenuItem>
                    <MenuItem value="Avancé">Avancé</MenuItem>
                  </Select>
                </FormControl>
                <FormControl fullWidth>
                  <InputLabel>Langue</InputLabel>
                  <Select
                    value={languageFilter}
                    label="Langue"
                    onChange={(e) => setLanguageFilter(e.target.value)}
                  >
                    <MenuItem value="">Toutes</MenuItem>
                    <MenuItem value="Français">Français</MenuItem>
                    <MenuItem value="Anglais">Anglais</MenuItem>
                  </Select>
                </FormControl>
              </Box>
            </Menu>
          </Grid>
        </Grid>
      </Box>

      <Grid container spacing={3}>
        {filteredCourses.map((course) => (
          <Grid item xs={12} md={6} lg={4} key={course.id}>
            <Card>
              <CardHeader
                action={
                  <IconButton>
                    <MoreVert />
                  </IconButton>
                }
                title={course.title}
                subheader={course.code}
              />
              <CardContent>
                <Typography variant="body2" color="text.secondary" noWrap sx={{ mb: 2 }}>
                  {course.description}
                </Typography>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <Person sx={{ mr: 1 }} />
                  <Typography variant="body2">
                    {`${course.teacher.firstName} ${course.teacher.lastName}`}
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <School sx={{ mr: 1 }} />
                  <Typography variant="body2">
                    {`${course.enrolledStudents}/${course.maxStudents} étudiants`}
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Schedule sx={{ mr: 1 }} />
                  <Typography variant="body2">
                    {`${new Date(course.startDate).toLocaleDateString()} - ${new Date(course.endDate).toLocaleDateString()}`}
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                  <Chip label={`${course.credits} crédits`} size="small" />
                  <Chip label={course.level} size="small" />
                  <Chip label={course.language} size="small" />
                </Box>
              </CardContent>
              <CardActions>
                <Button
                  size="small"
                  color="primary"
                  onClick={() => navigate(`/courses/${course.id}`)}
                >
                  Voir les détails
                </Button>
                <Button
                  size="small"
                  color="secondary"
                  onClick={() => navigate(`/courses/${course.id}/enroll`)}
                >
                  S'inscrire
                </Button>
              </CardActions>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
};

export default CourseList;
