import React from 'react';
import {
  Box,
  Container,
  Typography,
  Button,
  Grid,
  Card,
  CardContent,
  CardMedia,
  useTheme,
  useMediaQuery,
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import {
  School,
  Computer,
  Group,
  Assignment,
} from '@mui/icons-material';

const Home: React.FC = () => {
  const theme = useTheme();
  const navigate = useNavigate();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  const features = [
    {
      icon: <School fontSize="large" color="primary" />,
      title: 'Apprentissage en Ligne',
      description: 'Accédez aux cours et ressources pédagogiques à tout moment',
    },
    {
      icon: <Computer fontSize="large" color="primary" />,
      title: 'Plateforme Interactive',
      description: 'Participez aux quiz, devoirs et discussions en ligne',
    },
    {
      icon: <Group fontSize="large" color="primary" />,
      title: 'Collaboration',
      description: 'Travaillez en groupe et échangez avec vos professeurs',
    },
    {
      icon: <Assignment fontSize="large" color="primary" />,
      title: 'Suivi Personnalisé',
      description: 'Suivez votre progression et vos résultats en temps réel',
    },
  ];

  return (
    <Box>
      {/* Hero Section */}
      <Box
        sx={{
          bgcolor: 'primary.main',
          color: 'white',
          py: 8,
          position: 'relative',
          overflow: 'hidden',
        }}
      >
        <Container maxWidth="lg">
          <Grid container spacing={4} alignItems="center">
            <Grid item xs={12} md={6}>
              <Typography
                variant="h2"
                component="h1"
                sx={{
                  fontWeight: 700,
                  mb: 2,
                  fontSize: isMobile ? '2.5rem' : '3.5rem',
                }}
              >
                Bienvenue sur la Plateforme Éducative du Gabon
              </Typography>
              <Typography variant="h5" sx={{ mb: 4, opacity: 0.9 }}>
                L'excellence académique à portée de clic
              </Typography>
              <Button
                variant="contained"
                color="secondary"
                size="large"
                onClick={() => navigate('/login')}
                sx={{ mr: 2 }}
              >
                Commencer
              </Button>
              <Button
                variant="outlined"
                color="inherit"
                size="large"
                onClick={() => navigate('/about')}
              >
                En savoir plus
              </Button>
            </Grid>
            <Grid item xs={12} md={6}>
              {/* Vous pouvez ajouter une image d'illustration ici */}
            </Grid>
          </Grid>
        </Container>
      </Box>

      {/* Features Section */}
      <Container maxWidth="lg" sx={{ py: 8 }}>
        <Typography
          variant="h3"
          component="h2"
          align="center"
          sx={{ mb: 6 }}
        >
          Nos Services
        </Typography>
        <Grid container spacing={4}>
          {features.map((feature, index) => (
            <Grid item xs={12} sm={6} md={3} key={index}>
              <Card
                sx={{
                  height: '100%',
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  textAlign: 'center',
                  p: 2,
                }}
                elevation={2}
              >
                <Box sx={{ p: 2 }}>{feature.icon}</Box>
                <CardContent>
                  <Typography
                    gutterBottom
                    variant="h5"
                    component="h3"
                    sx={{ mb: 2 }}
                  >
                    {feature.title}
                  </Typography>
                  <Typography variant="body1" color="text.secondary">
                    {feature.description}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Container>

      {/* Call to Action Section */}
      <Box sx={{ bgcolor: 'secondary.main', color: 'white', py: 8 }}>
        <Container maxWidth="md">
          <Typography
            variant="h4"
            align="center"
            sx={{ mb: 4 }}
          >
            Prêt à commencer votre parcours académique ?
          </Typography>
          <Box sx={{ textAlign: 'center' }}>
            <Button
              variant="contained"
              color="primary"
              size="large"
              onClick={() => navigate('/register')}
              sx={{
                bgcolor: 'white',
                color: 'secondary.main',
                '&:hover': {
                  bgcolor: 'grey.100',
                },
              }}
            >
              S'inscrire maintenant
            </Button>
          </Box>
        </Container>
      </Box>
    </Box>
  );
};

export default Home;
