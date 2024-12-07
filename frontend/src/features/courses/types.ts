export interface Course {
  id: string;
  title: string;
  code: string;
  description: string;
  teacher: {
    id: string;
    firstName: string;
    lastName: string;
  };
  credits: number;
  level: string;
  language: string;
  maxStudents: number;
  enrolledStudents: number;
  startDate: string;
  endDate: string;
  schedule: CourseSchedule[];
  prerequisites: string[];
  status: 'ACTIVE' | 'INACTIVE' | 'ARCHIVED';
}

export interface CourseSchedule {
  id: string;
  dayOfWeek: number;
  startTime: string;
  endTime: string;
  room: string;
}

export interface CourseModule {
  id: string;
  courseId: string;
  title: string;
  description: string;
  order: number;
  content: CourseContent[];
}

export interface CourseContent {
  id: string;
  moduleId: string;
  title: string;
  type: 'VIDEO' | 'DOCUMENT' | 'QUIZ';
  content: string;
  duration?: number;
  order: number;
  isRequired: boolean;
  completionStatus?: 'NOT_STARTED' | 'IN_PROGRESS' | 'COMPLETED';
}

export interface CourseProgress {
  courseId: string;
  userId: string;
  progress: number;
  lastAccessed: string;
  completedModules: string[];
  completedContent: string[];
}

export interface CourseEnrollment {
  courseId: string;
  userId: string;
  enrollmentDate: string;
  status: 'ENROLLED' | 'COMPLETED' | 'DROPPED';
  grade?: number;
}

export interface CoursesState {
  courses: Course[];
  currentCourse: Course | null;
  enrollments: CourseEnrollment[];
  progress: CourseProgress[];
  loading: boolean;
  error: string | null;
}
