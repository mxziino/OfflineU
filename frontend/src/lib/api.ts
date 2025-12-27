// API functions for OfflineU

import type {
    BrowseResponse,
    LoadCourseResponse,
    CourseInfoResponse,
    ProgressUpdateRequest,
    Lesson
} from '@/types/api';

const API_BASE = '';

export async function browseFolders(path: string = ''): Promise<BrowseResponse> {
    const response = await fetch(`${API_BASE}/api/browse?path=${encodeURIComponent(path)}`);
    return response.json();
}

export async function loadCourse(coursePath: string, mode: 'course' | 'learning_path' = 'course'): Promise<LoadCourseResponse> {
    const response = await fetch(`${API_BASE}/api/course/load`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ course_path: coursePath, load_as: mode }),
    });
    return response.json();
}

export async function getCourseInfo(): Promise<CourseInfoResponse | null> {
    const response = await fetch(`${API_BASE}/api/course/info`);
    if (!response.ok) return null;
    return response.json();
}

export async function getLessonDetails(lessonPath: string): Promise<{ lesson: Lesson; course_name: string; prev_lesson: string | null; next_lesson: string | null } | null> {
    const response = await fetch(`${API_BASE}/api/lesson/${encodeURIComponent(lessonPath)}`);
    if (!response.ok) return null;
    return response.json();
}

export async function updateProgress(data: ProgressUpdateRequest): Promise<void> {
    await fetch(`${API_BASE}/api/progress`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
    });
}

export async function resetCourse(): Promise<void> {
    await fetch(`${API_BASE}/api/course/reset`, { method: 'POST' });
}

export function getFileUrl(filePath: string): string {
    return `${API_BASE}/files/${encodeURIComponent(filePath)}`;
}

// ============================================
// Library API (backend storage)
// ============================================

export interface LibraryCourse {
    name: string;
    path: string;
    last_accessed: string;
}

export async function getLibrary(): Promise<LibraryCourse[]> {
    const response = await fetch(`${API_BASE}/api/library`);
    if (!response.ok) return [];
    return response.json();
}

export async function addToLibrary(name: string, path: string, load_mode: 'course' | 'learning_path' = 'course'): Promise<void> {
    await fetch(`${API_BASE}/api/library`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, path, load_mode }),
    });
}

export async function removeFromLibrary(path: string): Promise<void> {
    await fetch(`${API_BASE}/api/library`, {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ path }),
    });
}

export async function updateLibraryTags(path: string, tags: string[]): Promise<void> {
    await fetch(`${API_BASE}/api/library/tags`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ path, tags }),
    });
}

export async function getAllTags(): Promise<string[]> {
    const response = await fetch(`${API_BASE}/api/library/tags`);
    if (!response.ok) return [];
    const data = await response.json();
    return data.tags || [];
}

// Statistics API
export interface DashboardStats {
    total_lessons_completed: number;
    total_time_spent_seconds: number;
    active_days: number;
    current_streak: number;
    today_lessons_completed: number;
    today_time_spent_seconds: number;
    total_courses: number;
}

export interface DailyStat {
    date: string;
    lessons_completed: number;
    time_spent_seconds: number;
    courses_accessed: number;
}

export async function getDashboardStats(): Promise<DashboardStats | null> {
    try {
        const res = await fetch(`${API_BASE}/api/stats/dashboard`);
        if (!res.ok) return null;
        return res.json();
    } catch {
        return null;
    }
}

export async function getWeeklyStats(): Promise<DailyStat[]> {
    try {
        const res = await fetch(`${API_BASE}/api/stats/weekly`);
        if (!res.ok) return [];
        return res.json();
    } catch {
        return [];
    }
}

export async function getMonthlyStats(): Promise<DailyStat[]> {
    try {
        const res = await fetch(`${API_BASE}/api/stats/monthly`);
        if (!res.ok) return [];
        return res.json();
    } catch {
        return [];
    }
}

export async function getStreak(): Promise<number> {
    try {
        const res = await fetch(`${API_BASE}/api/stats/streak`);
        if (!res.ok) return 0;
        const data = await res.json();
        return data.streak || 0;
    } catch {
        return 0;
    }
}
