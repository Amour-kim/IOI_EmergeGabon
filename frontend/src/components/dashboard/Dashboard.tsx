import React from 'react';
import {
  Box,
  Container,
  Grid,
  Paper,
  Typography,
  Card,
  CardContent,
  CardHeader,
} from '@mui/material';
import {
  School as SchoolIcon,
  Book as BookIcon,
  Assignment as AssignmentIcon,
  Notifications as NotificationsIcon,
} from '@mui/icons-material';

const Dashboard: React.FC = () => {
  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Grid container spacing={3}>
        {/* Statistiques */}
        <Grid item xs={12} md={3}>
          <Paper
            sx={{
              p: 2,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              bgcolor: 'primary.light',
              color: 'white',
            }}
          >
            <SchoolIcon sx={{ fontSize: 40 }} />
            <Typography component="p" variant="h6">
              12 Cours
            </Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} md={3}>
          <Paper
            sx={{
              p: 2,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              bgcolor: 'secondary.light',
              color: 'white',
            }}
          >
            <BookIcon sx={{ fontSize: 40 }} />
            <Typography component="p" variant="h6">
              45 Étudiants
            </Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} md={3}>
          <Paper
            sx={{
              p: 2,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              bgcolor: 'success.light',
              color: 'white',
            }}
          >
            <AssignmentIcon sx={{ fontSize: 40 }} />
            <Typography component="p" variant="h6">
              8 Devoirs
            </Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} md={3}>
          <Paper
            sx={{
              p: 2,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              bgcolor: 'warning.light',
              color: 'white',
            }}
          >
            <NotificationsIcon sx={{ fontSize: 40 }} />
            <Typography component="p" variant="h6">
              5 Notifications
            </Typography>
          </Paper>
        </Grid>

        {/* Cours récents */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader title="Cours Récents" />
            <CardContent>
              <Typography variant="body2" color="text.secondary">
                • Introduction à l'informatique
              </Typography>
              <Typography variant="body2" color="text.secondary">
                • Mathématiques avancées
              </Typography>
              <Typography variant="body2" color="text.secondary">
                • Sciences économiques
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Annonces */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader title="Annonces Récentes" />
            <CardContent>
              <Typography variant="body2" color="text.secondary">
                • Réunion des enseignants - 15/02/2024
              </Typography>
              <Typography variant="body2" color="text.secondary">
                • Examens de mi-semestre - 20/02/2024
              </Typography>
              <Typography variant="body2" color="text.secondary">
                • Conférence académique - 25/02/2024
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Container>
  );
};

export default Dashboard;
