import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { ScrollArea } from '@/components/ui/scroll-area';
import { getCourseInfo, resetCourse } from '@/lib/api';
import type { Course, CourseStats, DirectoryNode, LessonItem } from '@/types/api';
import { ArrowLeft, CheckCircle2, Circle, Play, ChevronDown, ChevronRight, Video, Music, FileText } from 'lucide-react';

interface LearningPathDashboardProps {
    onReset: () => void;
}

export function LearningPathDashboard({ onReset }: LearningPathDashboardProps) {
    const navigate = useNavigate();
    const [course, setCourse] = useState<Course | null>(null);
    const [stats, setStats] = useState<CourseStats | null>(null);
    const [subCourses, setSubCourses] = useState<SubCourseInfo[]>([]);
    const [expandedCourse, setExpandedCourse] = useState<string | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        getCourseInfo().then((data) => {
            if (data) {
                setCourse(data.course);
                setStats(data.stats);
                const subs = extractSubCourses(data.course.root_node, data.course.path);
                setSubCourses(subs);
            }
            setLoading(false);
        });
    }, []);

    const handleReset = async () => {
        await resetCourse();
        onReset();
    };

    const navigateToLesson = (subCoursePath: string, lessonTitle: string) => {
        const relativePath = subCoursePath.replace(course?.path || '', '').replace(/\\/g, '/').replace(/^[\\/]/, '');
        const fullPath = `${relativePath}/${lessonTitle.replace(/ /g, '_')}`;
        navigate(`/lesson/${encodeURIComponent(fullPath)}`);
    };

    const toggleExpand = (path: string) => {
        setExpandedCourse(expandedCourse === path ? null : path);
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-background flex items-center justify-center">
                <div className="text-muted-foreground">Loading learning path...</div>
            </div>
        );
    }

    if (!course) {
        return null;
    }

    return (
        <div className="min-h-screen bg-background">
            {/* Header */}
            <header className="border-b bg-card sticky top-0 z-10">
                <div className="container py-4 flex items-center justify-between">
                    <div className="flex items-center gap-4">
                        <Button variant="ghost" onClick={handleReset} className="gap-2">
                            <ArrowLeft className="h-4 w-4" />
                            Back to Library
                        </Button>
                    </div>
                    <div className="text-sm text-muted-foreground">
                        {subCourses.length} courses
                    </div>
                </div>
            </header>

            {/* Main Content */}
            <main className="container py-8 max-w-4xl mx-auto space-y-6">
                {/* Learning Path Header */}
                <div className="text-center space-y-4">
                    <h1 className="text-3xl font-bold">{course.name}</h1>
                    <p className="text-muted-foreground">Learning Path</p>

                    {stats && (
                        <div className="max-w-md mx-auto space-y-2">
                            <div className="flex justify-between text-sm">
                                <span>{stats.completed_lessons} of {stats.total_lessons} lessons</span>
                                <span className="font-bold">{stats.completion_percentage.toFixed(0)}%</span>
                            </div>
                            <Progress value={stats.completion_percentage} className="h-3" />
                        </div>
                    )}
                </div>

                {/* Sub-Courses List */}
                <div className="space-y-3">
                    {subCourses.map((sub, index) => {
                        const isExpanded = expandedCourse === sub.path;

                        return (
                            <Card key={sub.path} className={sub.progress === 100 ? 'border-green-500/50' : ''}>
                                {/* Course Header - Clickable */}
                                <CardHeader
                                    className="cursor-pointer hover:bg-muted/30 transition-colors"
                                    onClick={() => toggleExpand(sub.path)}
                                >
                                    <CardTitle className="flex items-center gap-3">
                                        <span className="flex items-center justify-center w-8 h-8 rounded-full bg-primary text-primary-foreground text-sm font-bold shrink-0">
                                            {index + 1}
                                        </span>

                                        <div className="flex-1 min-w-0">
                                            <div className="flex items-center gap-2">
                                                <span className="truncate">{sub.name}</span>
                                                {sub.progress === 100 && (
                                                    <CheckCircle2 className="h-4 w-4 text-green-500 shrink-0" />
                                                )}
                                            </div>
                                            <div className="text-sm text-muted-foreground font-normal mt-1">
                                                {sub.completedLessons}/{sub.totalLessons} lessons • {sub.progress.toFixed(0)}%
                                            </div>
                                        </div>

                                        {isExpanded ? (
                                            <ChevronDown className="h-5 w-5 text-muted-foreground shrink-0" />
                                        ) : (
                                            <ChevronRight className="h-5 w-5 text-muted-foreground shrink-0" />
                                        )}
                                    </CardTitle>

                                    <Progress value={sub.progress} className="h-1.5 mt-2" />
                                </CardHeader>

                                {/* Expanded Lessons */}
                                {isExpanded && (
                                    <CardContent className="pt-0 pb-4">
                                        <div className="max-h-[300px] overflow-y-auto">
                                            <div className="space-y-1">
                                                {sub.lessons.map((lesson) => {
                                                    const TypeIcon = lesson.lesson_type === 'video' ? Video
                                                        : lesson.lesson_type === 'audio' ? Music
                                                            : FileText;

                                                    return (
                                                        <button
                                                            key={lesson.path}
                                                            onClick={() => navigateToLesson(lesson.path, lesson.title)}
                                                            className="w-full flex items-center gap-3 p-3 rounded-lg text-left hover:bg-muted/50 transition-colors"
                                                        >
                                                            {lesson.completed ? (
                                                                <CheckCircle2 className="h-4 w-4 text-green-500 shrink-0" />
                                                            ) : (
                                                                <Circle className="h-4 w-4 text-muted-foreground shrink-0" />
                                                            )}
                                                            <span className="flex-1">{(lesson as FolderLessonItem).displayName || lesson.title}</span>
                                                            <TypeIcon className="h-4 w-4 text-muted-foreground shrink-0" />
                                                        </button>
                                                    );
                                                })}
                                            </div>
                                        </div>

                                        {/* Start/Continue Button */}
                                        <div className="mt-4">
                                            <Button
                                                className="w-full gap-2"
                                                onClick={() => {
                                                    const nextLesson = sub.lessons.find(l => !l.completed) || sub.lessons[0];
                                                    if (nextLesson) {
                                                        navigateToLesson(nextLesson.path, nextLesson.title);
                                                    }
                                                }}
                                            >
                                                <Play className="h-4 w-4" />
                                                {sub.progress === 0 ? 'Start Course'
                                                    : sub.progress === 100 ? 'Review Course'
                                                        : 'Continue Course'}
                                            </Button>
                                        </div>
                                    </CardContent>
                                )}
                            </Card>
                        );
                    })}
                </div>
            </main>
        </div>
    );
}

// ============================================
// Helper Types and Functions
// ============================================

interface SubCourseInfo {
    name: string;
    path: string;
    totalLessons: number;
    completedLessons: number;
    progress: number;
    lessons: FolderLessonItem[];
}

// Extended lesson item with display name for folder navigation
interface FolderLessonItem extends LessonItem {
    displayName?: string; // Folder name to show in UI, title is for navigation
}

function extractSubCourses(rootNode: DirectoryNode, coursePath: string): SubCourseInfo[] {
    const subs: SubCourseInfo[] = [];

    for (const child of Object.values(rootNode.children)) {
        // Get all lessons (files) for counting
        const allLessons = getAllLessons(child);
        const completed = allLessons.filter(l => l.completed).length;

        // Get child folders as the "lesson" entries to display
        // These are the actual lesson folders like "01 Setting Up Python (Overview)"
        const childFolders = getChildFoldersAsLessons(child);

        subs.push({
            name: child.name,
            path: child.path,
            totalLessons: allLessons.length,
            completedLessons: completed,
            progress: allLessons.length > 0 ? (completed / allLessons.length) * 100 : 0,
            lessons: childFolders,
        });
    }

    // Natural sort: extract leading numbers and sort numerically
    return subs.sort((a, b) => {
        const numA = parseInt(a.name.match(/^(\d+)/)?.[1] || '999999');
        const numB = parseInt(b.name.match(/^(\d+)/)?.[1] || '999999');
        if (numA !== numB) return numA - numB;
        return a.name.localeCompare(b.name);
    });
}

// Get child folders as LessonItem-like entries for display
function getChildFoldersAsLessons(node: DirectoryNode): FolderLessonItem[] {
    const folderLessons: FolderLessonItem[] = [];

    // Get child folders sorted naturally
    const sortedChildren = Object.values(node.children).sort((a, b) => {
        const numA = parseInt(a.name.match(/^(\d+)/)?.[1] || '999999');
        const numB = parseInt(b.name.match(/^(\d+)/)?.[1] || '999999');
        if (numA !== numB) return numA - numB;
        return a.name.localeCompare(b.name);
    });

    for (const child of sortedChildren) {
        // Get all lessons in this folder to determine completion
        const lessonsInFolder = getAllLessons(child);
        const allCompleted = lessonsInFolder.length > 0 && lessonsInFolder.every(l => l.completed);

        // Determine the primary lesson type based on what's inside
        let lessonType: 'video' | 'audio' | 'text' | 'quiz' | 'mixed' = 'text';
        if (lessonsInFolder.some(l => l.lesson_type === 'video')) lessonType = 'video';
        else if (lessonsInFolder.some(l => l.lesson_type === 'audio')) lessonType = 'audio';
        else if (lessonsInFolder.some(l => l.lesson_type === 'quiz')) lessonType = 'quiz';

        // Get the first lesson inside for navigation (typically video or main content)
        const firstLesson = lessonsInFolder.find(l => l.lesson_type === 'video') || lessonsInFolder[0];

        if (firstLesson) {
            folderLessons.push({
                title: firstLesson.title, // Use file's title for navigation
                displayName: child.name,  // Use folder name for display
                path: firstLesson.path,
                lesson_type: lessonType,
                completed: allCompleted,
            });
        }
    }

    // If no child folders, fall back to showing direct lessons
    if (folderLessons.length === 0) {
        return [...node.lessons];
    }

    return folderLessons;
}

function getAllLessons(node: DirectoryNode): LessonItem[] {
    let lessons: LessonItem[] = [...node.lessons];

    for (const child of Object.values(node.children)) {
        lessons = lessons.concat(getAllLessons(child));
    }

    return lessons;
}
