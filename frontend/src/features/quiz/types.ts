export interface Quiz {
  id: string;
  courseId: string;
  title: string;
  description: string;
  timeLimit: number; // en minutes
  startDate: string;
  endDate: string;
  totalPoints: number;
  passingScore: number;
  shuffleQuestions: boolean;
  showResults: boolean;
  allowReview: boolean;
  maxAttempts: number;
  questions: QuizQuestion[];
  status: QuizStatus;
  createdAt: string;
  updatedAt: string;
  createdBy: string;
}

export interface QuizQuestion {
  id: string;
  quizId: string;
  type: QuestionType;
  question: string;
  points: number;
  options: QuestionOption[];
  correctAnswers: string[];
  explanation?: string;
  order: number;
}

export interface QuestionOption {
  id: string;
  text: string;
  isCorrect?: boolean;
}

export interface QuizAttempt {
  id: string;
  quizId: string;
  studentId: string;
  startTime: string;
  endTime?: string;
  score?: number;
  status: AttemptStatus;
  answers: QuizAnswer[];
  timeSpent: number; // en secondes
  isCompleted: boolean;
}

export interface QuizAnswer {
  questionId: string;
  selectedOptions: string[];
  isCorrect?: boolean;
  points?: number;
}

export interface QuizStatistics {
  quizId: string;
  totalAttempts: number;
  averageScore: number;
  highestScore: number;
  lowestScore: number;
  medianScore: number;
  passingRate: number;
  averageTimeSpent: number;
  questionStats: QuestionStatistics[];
}

export interface QuestionStatistics {
  questionId: string;
  correctAnswerRate: number;
  averagePoints: number;
  mostChosenOptions: string[];
}

export enum QuestionType {
  MULTIPLE_CHOICE = 'MULTIPLE_CHOICE',
  SINGLE_CHOICE = 'SINGLE_CHOICE',
  TRUE_FALSE = 'TRUE_FALSE',
  SHORT_ANSWER = 'SHORT_ANSWER',
  MATCHING = 'MATCHING'
}

export enum QuizStatus {
  DRAFT = 'DRAFT',
  SCHEDULED = 'SCHEDULED',
  ACTIVE = 'ACTIVE',
  CLOSED = 'CLOSED',
  ARCHIVED = 'ARCHIVED'
}

export enum AttemptStatus {
  IN_PROGRESS = 'IN_PROGRESS',
  SUBMITTED = 'SUBMITTED',
  TIMED_OUT = 'TIMED_OUT',
  GRADED = 'GRADED'
}

export interface QuizState {
  quizzes: Quiz[];
  currentQuiz: Quiz | null;
  attempts: QuizAttempt[];
  currentAttempt: QuizAttempt | null;
  statistics: QuizStatistics | null;
  loading: boolean;
  error: string | null;
}
