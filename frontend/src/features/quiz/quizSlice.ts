import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import {
  Quiz,
  QuizAttempt,
  QuizStatistics,
  QuizState,
  QuizAnswer,
} from './types';
import axios from 'axios';

const initialState: QuizState = {
  quizzes: [],
  currentQuiz: null,
  attempts: [],
  currentAttempt: null,
  statistics: null,
  loading: false,
  error: null,
};

export const fetchQuizzes = createAsyncThunk(
  'quiz/fetchQuizzes',
  async (courseId?: string) => {
    const response = await axios.get(
      courseId ? `/api/quizzes?courseId=${courseId}` : '/api/quizzes'
    );
    return response.data;
  }
);

export const fetchQuizById = createAsyncThunk(
  'quiz/fetchQuizById',
  async (quizId: string) => {
    const response = await axios.get(`/api/quizzes/${quizId}`);
    return response.data;
  }
);

export const createQuiz = createAsyncThunk(
  'quiz/createQuiz',
  async (quizData: Partial<Quiz>) => {
    const response = await axios.post('/api/quizzes', quizData);
    return response.data;
  }
);

export const startQuizAttempt = createAsyncThunk(
  'quiz/startAttempt',
  async (quizId: string) => {
    const response = await axios.post(`/api/quizzes/${quizId}/attempts`);
    return response.data;
  }
);

export const submitQuizAttempt = createAsyncThunk(
  'quiz/submitAttempt',
  async ({
    quizId,
    attemptId,
    answers,
  }: {
    quizId: string;
    attemptId: string;
    answers: QuizAnswer[];
  }) => {
    const response = await axios.post(
      `/api/quizzes/${quizId}/attempts/${attemptId}/submit`,
      { answers }
    );
    return response.data;
  }
);

export const fetchQuizStatistics = createAsyncThunk(
  'quiz/fetchStatistics',
  async (quizId: string) => {
    const response = await axios.get(`/api/quizzes/${quizId}/statistics`);
    return response.data;
  }
);

const quizSlice = createSlice({
  name: 'quiz',
  initialState,
  reducers: {
    setCurrentQuiz: (state, action: PayloadAction<Quiz | null>) => {
      state.currentQuiz = action.payload;
    },
    updateCurrentAttempt: (state, action: PayloadAction<Partial<QuizAttempt>>) => {
      if (state.currentAttempt) {
        state.currentAttempt = {
          ...state.currentAttempt,
          ...action.payload,
        };
      }
    },
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch Quizzes
      .addCase(fetchQuizzes.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchQuizzes.fulfilled, (state, action: PayloadAction<Quiz[]>) => {
        state.loading = false;
        state.quizzes = action.payload;
      })
      .addCase(fetchQuizzes.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Une erreur est survenue lors du chargement des quiz.';
      })

      // Fetch Quiz by ID
      .addCase(fetchQuizById.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchQuizById.fulfilled, (state, action: PayloadAction<Quiz>) => {
        state.loading = false;
        state.currentQuiz = action.payload;
      })
      .addCase(fetchQuizById.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Une erreur est survenue lors du chargement du quiz.';
      })

      // Create Quiz
      .addCase(createQuiz.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(createQuiz.fulfilled, (state, action: PayloadAction<Quiz>) => {
        state.loading = false;
        state.quizzes.push(action.payload);
      })
      .addCase(createQuiz.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Une erreur est survenue lors de la création du quiz.';
      })

      // Start Quiz Attempt
      .addCase(startQuizAttempt.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(startQuizAttempt.fulfilled, (state, action: PayloadAction<QuizAttempt>) => {
        state.loading = false;
        state.currentAttempt = action.payload;
        state.attempts.push(action.payload);
      })
      .addCase(startQuizAttempt.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Une erreur est survenue lors du démarrage du quiz.';
      })

      // Submit Quiz Attempt
      .addCase(submitQuizAttempt.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(submitQuizAttempt.fulfilled, (state, action: PayloadAction<QuizAttempt>) => {
        state.loading = false;
        state.currentAttempt = action.payload;
        const index = state.attempts.findIndex((a) => a.id === action.payload.id);
        if (index !== -1) {
          state.attempts[index] = action.payload;
        }
      })
      .addCase(submitQuizAttempt.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Une erreur est survenue lors de la soumission du quiz.';
      })

      // Fetch Quiz Statistics
      .addCase(fetchQuizStatistics.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchQuizStatistics.fulfilled, (state, action: PayloadAction<QuizStatistics>) => {
        state.loading = false;
        state.statistics = action.payload;
      })
      .addCase(fetchQuizStatistics.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Une erreur est survenue lors du chargement des statistiques.';
      });
  },
});

export const { setCurrentQuiz, updateCurrentAttempt, clearError } = quizSlice.actions;

export default quizSlice.reducer;
