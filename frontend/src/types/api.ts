// API Types for OfflineU

export interface DirectoryInfo {
    name: string;
    path: string;
    media_files: number;
    is_course_candidate: boolean;
}

export interface BrowseResponse {
    current_path: string;
    parent_path: string | null;
    directories: DirectoryInfo[];
    error?: string;
}

export interface Lesson {
    title: string;
    path: string;
    lesson_type: 'video' | 'audio' | 'text' | 'quiz' | 'mixed';
    video_file: string | null;
    audio_file: string | null;
    subtitle_file: string | null;
    text_files: string[];
    completed: boolean;
    progress_seconds: number;
}

export interface DirectoryNode {
    name: string;
    path: string;
    type: string;
    has_content: boolean;
    children: Record<string, DirectoryNode>;
    lessons: LessonItem[];
}

export interface LessonItem {
    title: string;
    path: string;
    lesson_type: 'video' | 'audio' | 'text' | 'quiz' | 'mixed';
    completed: boolean;
}

export interface Course {
    name: string;
    path: string;
    root_node: DirectoryNode;
    progress_file: string;
    last_accessed_path: string | null;
}

export interface CourseStats {
    total_lessons: number;
    completed_lessons: number;
    completion_percentage: number;
    last_accessed_path?: string;
}

export interface CourseInfoResponse {
    course: Course;
    stats: CourseStats;
}

export interface LoadCourseResponse {
    success: boolean;
    course_name?: string;
    error?: string;
}

export interface ProgressUpdateRequest {
    lesson_path: string;
    completed: boolean;
    progress_seconds: number;
}
