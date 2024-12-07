import React from 'react';
import {
  Grid,
  Paper,
  Typography,
  Box,
  Card,
  CardContent,
  CardHeader,
  List,
  ListItem,
  ListItemText,
  Divider,
} from '@mui/material';
import {
  Timeline,
  Assignment,
  Notifications,
  Schedule,
} from '@mui/icons-material';
import { useSelector } from 'react-redux';

const Dashboard: React.FC = () => {
  const user = useSelector((state: any) => state.auth.user);

  const upcomingEvents = [
    { title: 'Examen de Mathématiques', date: '2024-12-15', time: '09:00' },
    { title: 'Remise du projet Java', date: '2024-12-18', time: '23:59' },
    { title: 'Séminaire IA', date: '2024-12-20', time: '14:00' },
  ];

  const recentAnnouncements = [
    {
      title: 'Fermeture pour maintenance',
      content: 'La bibliothèque sera fermée ce weekend pour maintenance.',
      date: '2024-12-05',
    },
    {
      title: 'Nouveaux cours disponibles',
      content: 'Les inscriptions pour les cours du prochain semestre sont ouvertes.',
      date: '2024-12-04',
    },
  ];

  return (
    <Box sx={{ flexGrow: 1 }}>
      <Grid container spacing={3}>
        {/* En-tête de bienvenue */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3, mb: 3 }}>
            <Typography variant="h4" gutterBottom>
              Bienvenue, {user?.firstName} !
            </Typography>
            <Typography variant="subtitle1" color="textSecondary">
              {new Date().toLocaleDateString('fr-FR', {
                weekday: 'long',
                year: 'numeric',
                month: 'long',
                day: 'numeric',
              })}
            </Typography>
          </Paper>
        </Grid>

        {/* Statistiques rapides */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardHeader
              avatar={<Timeline color="primary" />}
              title="Progression"
              subheader="Ce semestre"
            />
            <CardContent>
              <Typography variant="h3" align="center" color="primary">
                75%
              </Typography>
              <Typography variant="body2" color="textSecondary" align="center">
                Moyenne générale
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardHeader
              avatar={<Assignment color="secondary" />}
              title="Devoirs"
              subheader="Cette semaine"
            />
            <CardContent>
              <Typography variant="h3" align="center" color="secondary">
                5
              </Typography>
              <Typography variant="body2" color="textSecondary" align="center">
                Devoirs à rendre
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardHeader
              avatar={<Notifications color="error" />}
              title="Notifications"
              subheader="Non lues"
            />
            <CardContent>
              <Typography variant="h3" align="center" color="error">
                3
              </Typography>
              <Typography variant="body2" color="textSecondary" align="center">
                Messages importants
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Événements à venir */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader
              avatar={<Schedule color="primary" />}
              title="Événements à venir"
            />
            <CardContent>
              <List>
                {upcomingEvents.map((event, index) => (
                  <React.Fragment key={index}>
                    <ListItem>
                      <ListItemText
                        primary={event.title}
                        secondary={`${event.date} à ${event.time}`}
                      />
                    </ListItem>
                    {index < upcomingEvents.length - 1 && <Divider />}
                  </React.Fragment>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>

        {/* Annonces récentes */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader
              avatar={<Notifications color="primary" />}
              title="Annonces récentes"
            />
            <CardContent>
              <List>
                {recentAnnouncements.map((announcement, index) => (
                  <React.Fragment key={index}>
                    <ListItem>
                      <ListItemText
                        primary={announcement.title}
                        secondary={
                          <>
                            <Typography component="span" variant="body2" color="textSecondary">
                              {announcement.date} -
                            </Typography>
                            {" " + announcement.content}
                          </>
                        }
                      />
                    </ListItem>
                    {index < recentAnnouncements.length - 1 && <Divider />}
                  </React.Fragment>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;
