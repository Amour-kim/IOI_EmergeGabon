import React, { useState } from 'react';
import {
  Box,
  Grid,
  Paper,
  Typography,
  Tabs,
  Tab,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Button,
  Divider,
  Chip,
  Card,
  CardContent,
  LinearProgress,
} from '@mui/material';
import {
  Description,
  Schedule,
  Person,
  School,
  Assignment,
  PlayCircleOutline,
  Article,
  QuestionAnswer,
} from '@mui/icons-material';
import { useParams } from 'react-router-dom';
import { Course, CourseModule, CourseContent } from '../types';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

const TabPanel: React.FC<TabPanelProps> = ({ children, value, index }) => (
  <div role="tabpanel" hidden={value !== index}>
    {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
  </div>
);

const mockCourse: Course = {
  id: '1',
  title: 'Introduction à la Programmation',
  code: 'CS101',
  description: 'Un cours complet d\'introduction aux concepts fondamentaux de la programmation. Les étudiants apprendront les bases de la logique de programmation, les structures de données et les algorithmes de base.',
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
    {
      id: '2',
      dayOfWeek: 3,
      startTime: '14:00',
      endTime: '16:00',
      room: 'A101',
    },
  ],
  prerequisites: [],
  status: 'ACTIVE',
};

const mockModules: CourseModule[] = [
  {
    id: '1',
    courseId: '1',
    title: 'Introduction aux concepts de base',
    description: 'Comprendre les fondamentaux de la programmation',
    order: 1,
    content: [
      {
        id: '1',
        moduleId: '1',
        title: 'Qu\'est-ce que la programmation ?',
        type: 'VIDEO',
        content: 'url-to-video',
        duration: 15,
        order: 1,
        isRequired: true,
        completionStatus: 'COMPLETED',
      },
      {
        id: '2',
        moduleId: '1',
        title: 'Variables et types de données',
        type: 'DOCUMENT',
        content: 'url-to-document',
        order: 2,
        isRequired: true,
        completionStatus: 'IN_PROGRESS',
      },
    ],
  },
  // Ajoutez d'autres modules ici
];

const CourseDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [tabValue, setTabValue] = useState(0);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const getContentIcon = (type: CourseContent['type']) => {
    switch (type) {
      case 'VIDEO':
        return <PlayCircleOutline />;
      case 'DOCUMENT':
        return <Article />;
      case 'QUIZ':
        return <QuestionAnswer />;
      default:
        return <Assignment />;
    }
  };

  const getCompletionColor = (status?: string) => {
    switch (status) {
      case 'COMPLETED':
        return 'success';
      case 'IN_PROGRESS':
        return 'warning';
      default:
        return 'default';
    }
  };

  const getDayOfWeek = (day: number) => {
    const days = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche'];
    return days[day - 1];
  };

  return (
    <Box sx={{ p: 3 }}>
      <Paper sx={{ p: 3, mb: 3 }}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={8}>
            <Typography variant="h4" gutterBottom>
              {mockCourse.title}
            </Typography>
            <Typography variant="subtitle1" color="textSecondary" gutterBottom>
              {mockCourse.code}
            </Typography>
            <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
              <Chip label={`${mockCourse.credits} crédits`} />
              <Chip label={mockCourse.level} />
              <Chip label={mockCourse.language} />
            </Box>
            <Typography variant="body1" paragraph>
              {mockCourse.description}
            </Typography>
          </Grid>
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Progression du cours
                </Typography>
                <LinearProgress
                  variant="determinate"
                  value={60}
                  sx={{ mb: 2 }}
                />
                <Typography variant="body2" color="textSecondary" align="center">
                  60% complété
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Paper>

      <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Tabs value={tabValue} onChange={handleTabChange}>
          <Tab label="Contenu" />
          <Tab label="Informations" />
          <Tab label="Planning" />
        </Tabs>
      </Box>

      <TabPanel value={tabValue} index={0}>
        <List>
          {mockModules.map((module) => (
            <React.Fragment key={module.id}>
              <ListItem>
                <ListItemText
                  primary={
                    <Typography variant="h6">
                      {module.title}
                    </Typography>
                  }
                  secondary={module.description}
                />
              </ListItem>
              <List component="div" disablePadding>
                {module.content.map((content) => (
                  <ListItem
                    key={content.id}
                    button
                    sx={{ pl: 4 }}
                  >
                    <ListItemIcon>
                      {getContentIcon(content.type)}
                    </ListItemIcon>
                    <ListItemText
                      primary={content.title}
                      secondary={`${content.duration || ''} ${content.duration ? 'minutes' : ''}`}
                    />
                    <Chip
                      size="small"
                      label={content.completionStatus || 'NON COMMENCÉ'}
                      color={getCompletionColor(content.completionStatus)}
                    />
                  </ListItem>
                ))}
              </List>
              <Divider />
            </React.Fragment>
          ))}
        </List>
      </TabPanel>

      <TabPanel value={tabValue} index={1}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Typography variant="h6" gutterBottom>
              Enseignant
            </Typography>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
              <Person sx={{ mr: 1 }} />
              <Typography>
                {`${mockCourse.teacher.firstName} ${mockCourse.teacher.lastName}`}
              </Typography>
            </Box>

            <Typography variant="h6" gutterBottom>
              Prérequis
            </Typography>
            {mockCourse.prerequisites.length > 0 ? (
              <List>
                {mockCourse.prerequisites.map((prereq, index) => (
                  <ListItem key={index}>
                    <ListItemText primary={prereq} />
                  </ListItem>
                ))}
              </List>
            ) : (
              <Typography color="textSecondary">
                Aucun prérequis
              </Typography>
            )}
          </Grid>

          <Grid item xs={12} md={6}>
            <Typography variant="h6" gutterBottom>
              Informations générales
            </Typography>
            <List>
              <ListItem>
                <ListItemIcon>
                  <School />
                </ListItemIcon>
                <ListItemText
                  primary="Nombre d'étudiants"
                  secondary={`${mockCourse.enrolledStudents}/${mockCourse.maxStudents}`}
                />
              </ListItem>
              <ListItem>
                <ListItemIcon>
                  <Schedule />
                </ListItemIcon>
                <ListItemText
                  primary="Période"
                  secondary={`${new Date(mockCourse.startDate).toLocaleDateString()} - ${new Date(mockCourse.endDate).toLocaleDateString()}`}
                />
              </ListItem>
            </List>
          </Grid>
        </Grid>
      </TabPanel>

      <TabPanel value={tabValue} index={2}>
        <List>
          {mockCourse.schedule.map((schedule) => (
            <ListItem key={schedule.id}>
              <ListItemIcon>
                <Schedule />
              </ListItemIcon>
              <ListItemText
                primary={getDayOfWeek(schedule.dayOfWeek)}
                secondary={`${schedule.startTime} - ${schedule.endTime} | Salle ${schedule.room}`}
              />
            </ListItem>
          ))}
        </List>
      </TabPanel>

      <Box sx={{ mt: 3, display: 'flex', justifyContent: 'flex-end' }}>
        <Button
          variant="contained"
          color="primary"
          startIcon={<Assignment />}
        >
          S'inscrire au cours
        </Button>
      </Box>
    </Box>
  );
};

export default CourseDetail;
