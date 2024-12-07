export interface Assignment {
  id: string;
  courseId: string;
  title: string;
  description: string;
  type: AssignmentType;
  dueDate: string;
  totalPoints: number;
  weight: number;
  status: AssignmentStatus;
  attachments: AssignmentAttachment[];
  submissionType: SubmissionType[];
  createdAt: string;
  updatedAt: string;
  createdBy: string;
}

export interface AssignmentAttachment {
  id: string;
  fileName: string;
  fileUrl: string;
  fileType: string;
  fileSize: number;
  uploadedAt: string;
}

export interface AssignmentSubmission {
  id: string;
  assignmentId: string;
  studentId: string;
  submittedAt: string;
  status: SubmissionStatus;
  grade?: number;
  feedback?: string;
  attachments: SubmissionAttachment[];
  attempts: number;
  lastModified: string;
}

export interface SubmissionAttachment {
  id: string;
  submissionId: string;
  fileName: string;
  fileUrl: string;
  fileType: string;
  fileSize: number;
  uploadedAt: string;
}

export interface AssignmentGrade {
  id: string;
  assignmentId: string;
  studentId: string;
  grade: number;
  feedback: string;
  gradedBy: string;
  gradedAt: string;
  status: GradeStatus;
}

export enum AssignmentType {
  HOMEWORK = 'HOMEWORK',
  QUIZ = 'QUIZ',
  EXAM = 'EXAM',
  PROJECT = 'PROJECT',
  PRESENTATION = 'PRESENTATION'
}

export enum AssignmentStatus {
  DRAFT = 'DRAFT',
  PUBLISHED = 'PUBLISHED',
  CLOSED = 'CLOSED',
  GRADING = 'GRADING',
  GRADED = 'GRADED'
}

export enum SubmissionType {
  FILE = 'FILE',
  TEXT = 'TEXT',
  LINK = 'LINK',
  CODE = 'CODE'
}

export enum SubmissionStatus {
  DRAFT = 'DRAFT',
  SUBMITTED = 'SUBMITTED',
  LATE = 'LATE',
  RESUBMITTED = 'RESUBMITTED',
  GRADED = 'GRADED'
}

export enum GradeStatus {
  PENDING = 'PENDING',
  GRADED = 'GRADED',
  DISPUTED = 'DISPUTED',
  REVISED = 'REVISED'
}

export interface AssignmentsState {
  assignments: Assignment[];
  currentAssignment: Assignment | null;
  submissions: AssignmentSubmission[];
  grades: AssignmentGrade[];
  loading: boolean;
  error: string | null;
}
