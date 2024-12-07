import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import {
  Assignment,
  AssignmentSubmission,
  AssignmentGrade,
  AssignmentsState,
} from './types';
import axios from 'axios';

const initialState: AssignmentsState = {
  assignments: [],
  currentAssignment: null,
  submissions: [],
  grades: [],
  loading: false,
  error: null,
};

export const fetchAssignments = createAsyncThunk(
  'assignments/fetchAssignments',
  async (courseId?: string) => {
    const response = await axios.get(
      courseId ? `/api/assignments?courseId=${courseId}` : '/api/assignments'
    );
    return response.data;
  }
);

export const fetchAssignmentById = createAsyncThunk(
  'assignments/fetchAssignmentById',
  async (assignmentId: string) => {
    const response = await axios.get(`/api/assignments/${assignmentId}`);
    return response.data;
  }
);

export const submitAssignment = createAsyncThunk(
  'assignments/submitAssignment',
  async ({
    assignmentId,
    files,
    comment,
  }: {
    assignmentId: string;
    files: File[];
    comment?: string;
  }) => {
    const formData = new FormData();
    files.forEach((file) => {
      formData.append('files', file);
    });
    if (comment) {
      formData.append('comment', comment);
    }

    const response = await axios.post(
      `/api/assignments/${assignmentId}/submit`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return response.data;
  }
);

export const gradeAssignment = createAsyncThunk(
  'assignments/gradeAssignment',
  async ({
    submissionId,
    grade,
    feedback,
  }: {
    submissionId: string;
    grade: number;
    feedback: string;
  }) => {
    const response = await axios.post(`/api/submissions/${submissionId}/grade`, {
      grade,
      feedback,
    });
    return response.data;
  }
);

const assignmentsSlice = createSlice({
  name: 'assignments',
  initialState,
  reducers: {
    setCurrentAssignment: (state, action: PayloadAction<Assignment | null>) => {
      state.currentAssignment = action.payload;
    },
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch Assignments
      .addCase(fetchAssignments.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchAssignments.fulfilled, (state, action: PayloadAction<Assignment[]>) => {
        state.loading = false;
        state.assignments = action.payload;
      })
      .addCase(fetchAssignments.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Une erreur est survenue lors du chargement des devoirs.';
      })

      // Fetch Assignment by ID
      .addCase(fetchAssignmentById.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchAssignmentById.fulfilled, (state, action: PayloadAction<Assignment>) => {
        state.loading = false;
        state.currentAssignment = action.payload;
      })
      .addCase(fetchAssignmentById.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Une erreur est survenue lors du chargement du devoir.';
      })

      // Submit Assignment
      .addCase(submitAssignment.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(submitAssignment.fulfilled, (state, action: PayloadAction<AssignmentSubmission>) => {
        state.loading = false;
        state.submissions.push(action.payload);
      })
      .addCase(submitAssignment.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Une erreur est survenue lors de la soumission du devoir.';
      })

      // Grade Assignment
      .addCase(gradeAssignment.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(gradeAssignment.fulfilled, (state, action: PayloadAction<AssignmentGrade>) => {
        state.loading = false;
        state.grades.push(action.payload);
      })
      .addCase(gradeAssignment.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Une erreur est survenue lors de la notation du devoir.';
      });
  },
});

export const { setCurrentAssignment, clearError } = assignmentsSlice.actions;

export default assignmentsSlice.reducer;
