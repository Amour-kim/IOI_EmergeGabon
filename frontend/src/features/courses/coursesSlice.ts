import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { Course, CourseEnrollment, CourseProgress, CoursesState } from './types';
import axios from 'axios';

const initialState: CoursesState = {
  courses: [],
  currentCourse: null,
  enrollments: [],
  progress: [],
  loading: false,
  error: null,
};

export const fetchCourses = createAsyncThunk(
  'courses/fetchCourses',
  async () => {
    const response = await axios.get('/api/courses');
    return response.data;
  }
);

export const fetchCourseById = createAsyncThunk(
  'courses/fetchCourseById',
  async (courseId: string) => {
    const response = await axios.get(`/api/courses/${courseId}`);
    return response.data;
  }
);

export const enrollInCourse = createAsyncThunk(
  'courses/enrollInCourse',
  async (courseId: string) => {
    const response = await axios.post(`/api/courses/${courseId}/enroll`);
    return response.data;
  }
);

export const updateCourseProgress = createAsyncThunk(
  'courses/updateProgress',
  async (progress: Partial<CourseProgress>) => {
    const response = await axios.post('/api/courses/progress', progress);
    return response.data;
  }
);

const coursesSlice = createSlice({
  name: 'courses',
  initialState,
  reducers: {
    setCurrentCourse: (state, action: PayloadAction<Course | null>) => {
      state.currentCourse = action.payload;
    },
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch Courses
      .addCase(fetchCourses.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchCourses.fulfilled, (state, action: PayloadAction<Course[]>) => {
        state.loading = false;
        state.courses = action.payload;
      })
      .addCase(fetchCourses.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Une erreur est survenue lors du chargement des cours.';
      })

      // Fetch Course by ID
      .addCase(fetchCourseById.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchCourseById.fulfilled, (state, action: PayloadAction<Course>) => {
        state.loading = false;
        state.currentCourse = action.payload;
      })
      .addCase(fetchCourseById.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Une erreur est survenue lors du chargement du cours.';
      })

      // Enroll in Course
      .addCase(enrollInCourse.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(enrollInCourse.fulfilled, (state, action: PayloadAction<CourseEnrollment>) => {
        state.loading = false;
        state.enrollments.push(action.payload);
      })
      .addCase(enrollInCourse.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Une erreur est survenue lors de l\'inscription au cours.';
      })

      // Update Course Progress
      .addCase(updateCourseProgress.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(updateCourseProgress.fulfilled, (state, action: PayloadAction<CourseProgress>) => {
        state.loading = false;
        const index = state.progress.findIndex(
          (p) => p.courseId === action.payload.courseId && p.userId === action.payload.userId
        );
        if (index !== -1) {
          state.progress[index] = action.payload;
        } else {
          state.progress.push(action.payload);
        }
      })
      .addCase(updateCourseProgress.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Une erreur est survenue lors de la mise à jour de la progression.';
      });
  },
});

export const { setCurrentCourse, clearError } = coursesSlice.actions;

export default coursesSlice.reducer;
