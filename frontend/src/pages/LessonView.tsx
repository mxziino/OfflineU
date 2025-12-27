import { useState, useEffect, useRef, useMemo } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Progress } from '@/components/ui/progress';
import {
    ContextMenu,
    ContextMenuContent,
    ContextMenuItem,
    ContextMenuTrigger,
} from '@/components/ui/context-menu';
import { getCourseInfo, getLessonDetails, updateProgress, getFileUrl } from '@/lib/api';
import type { Lesson, DirectoryNode, Course, CourseStats, LessonItem } from '@/types/api';
import {
    ArrowLeft, ChevronLeft, ChevronRight, CheckCircle2, Circle,
    PanelRightClose, PanelRightOpen, Video, Music, FileText,
    ChevronDown, ChevronRight as ChevronRightIcon, FolderOpen, Copy
} from 'lucide-react';

export function LessonView() {
    const { '*': lessonPath } = useParams();
    const navigate = useNavigate();

    // Lesson state
    const [lesson, setLesson] = useState<Lesson | null>(null);
    const [prevLesson, setPrevLesson] = useState<string | null>(null);
    const [nextLesson, setNextLesson] = useState<string | null>(null);
    const [isCompleted, setIsCompleted] = useState(false);
    const [loading, setLoading] = useState(true);

    // Sidebar state
    const [course, setCourse] = useState<Course | null>(null);
    const [stats, setStats] = useState<CourseStats | null>(null);
    const [sidebarOpen, setSidebarOpen] = useState(true);

    const mediaRef = useRef<HTMLVideoElement | HTMLAudioElement | null>(null);
    const lastSaveTime = useRef(0);

    // Load lesson details
    useEffect(() => {
        if (!lessonPath) return;

        getLessonDetails(lessonPath).then((data) => {
            if (data) {
                setLesson(data.lesson);
                setPrevLesson(data.prev_lesson);
                setNextLesson(data.next_lesson);
                setIsCompleted(data.lesson.completed);
            }
            setLoading(false);
        });
    }, [lessonPath]);

    // Load course info for sidebar
    useEffect(() => {
        getCourseInfo().then((data) => {
            if (data) {
                setCourse(data.course);
                setStats(data.stats);
            }
        });
    }, []);

    // Find the sub-course that contains the current lesson
    // This is used when viewing a lesson within a learning path
    const { activeSubCourse, activeSubCoursePath, sidebarStats } = useMemo(() => {
        if (!course || !lessonPath) {
            return { activeSubCourse: course?.root_node, activeSubCoursePath: course?.path, sidebarStats: stats };
        }

        // In a learning path, the root_node.children are the sub-courses
        // Check if the lessonPath starts with any of the sub-course names
        const children = Object.values(course.root_node.children);

        for (const child of children) {
            // Get the relative path of this child from the course root
            const childRelPath = child.path.replace(course.path, '').replace(/\\/g, '/').replace(/^[\\/]/, '');

            // Check if the lesson path starts with this child's relative path
            if (lessonPath.startsWith(childRelPath + '/') || lessonPath.startsWith(childRelPath.replace(/ /g, '_') + '/')) {
                // Calculate stats for just this sub-course
                const subLessons = getAllLessonsFromNode(child);
                const completedCount = subLessons.filter(l => l.completed).length;
                const subStats: CourseStats = {
                    total_lessons: subLessons.length,
                    completed_lessons: completedCount,
                    completion_percentage: subLessons.length > 0 ? (completedCount / subLessons.length) * 100 : 0
                };
                return {
                    activeSubCourse: child,
                    activeSubCoursePath: child.path,
                    sidebarStats: subStats
                };
            }
        }

        // No sub-course match, show the full course (this is a regular course, not a learning path)
        return { activeSubCourse: course.root_node, activeSubCoursePath: course.path, sidebarStats: stats };
    }, [course, lessonPath, stats]);

    const saveProgress = async (progressSeconds: number, completed: boolean = false) => {
        if (!lessonPath) return;
        await updateProgress({
            lesson_path: lessonPath,
            completed,
            progress_seconds: Math.floor(progressSeconds),
        });
        // Refresh course info to update sidebar
        if (completed) {
            const data = await getCourseInfo();
            if (data) {
                setCourse(data.course);
                setStats(data.stats);
            }
        }
    };

    const toggleCompletion = async () => {
        const newState = !isCompleted;
        setIsCompleted(newState);
        const currentTime = mediaRef.current?.currentTime || 0;
        await saveProgress(currentTime, newState);
    };

    const handleTimeUpdate = () => {
        if (!mediaRef.current) return;
        const currentTime = mediaRef.current.currentTime;
        if (currentTime - lastSaveTime.current > 15) {
            saveProgress(currentTime);
            lastSaveTime.current = currentTime;
        }
    };

    const handleEnded = () => {
        if (!mediaRef.current) return;
        saveProgress(mediaRef.current.currentTime, true);
        setIsCompleted(true);
    };

    const navigateToLesson = (path: string) => {
        navigate(`/lesson/${encodeURIComponent(path)}`);
    };

    const markLessonComplete = async (lessonPath: string, completed: boolean) => {
        await updateProgress({
            lesson_path: lessonPath,
            completed,
            progress_seconds: 0,
        });
        // Refresh course info to update sidebar
        const data = await getCourseInfo();
        if (data) {
            setCourse(data.course);
            setStats(data.stats);
        }
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-background flex items-center justify-center">
                <div className="text-muted-foreground">Loading lesson...</div>
            </div>
        );
    }

    if (!lesson) {
        return (
            <div className="min-h-screen bg-background flex items-center justify-center flex-col gap-4">
                <div className="text-muted-foreground">Lesson not found</div>
                <Button onClick={() => navigate('/')}>Back to Course</Button>
            </div>
        );
    }

    const sidebarWidth = 420;

    return (
        <div className="min-h-screen bg-background">
            {/* Header - Full Width */}
            <header className="border-b bg-card sticky top-0 z-20">
                <div className="flex items-center justify-between gap-4 px-4 py-3">
                    <div className="flex items-center gap-4 min-w-0">
                        <Button variant="ghost" size="sm" onClick={() => navigate('/')} className="gap-2 shrink-0">
                            <ArrowLeft className="h-4 w-4" />
                            <span className="hidden sm:inline">Back</span>
                        </Button>
                        <div className="min-w-0 hidden sm:block">
                            <h1 className="text-sm font-medium truncate">{lesson.title}</h1>
                            {stats && (
                                <p className="text-xs text-muted-foreground">
                                    {stats.completed_lessons}/{stats.total_lessons} lessons completed
                                </p>
                            )}
                        </div>
                    </div>

                    <div className="flex items-center gap-2 shrink-0">
                        <Button
                            onClick={toggleCompletion}
                            size="sm"
                            variant={isCompleted ? 'default' : 'outline'}
                            className={isCompleted ? 'bg-green-600 hover:bg-green-700 gap-2' : 'gap-2'}
                        >
                            {isCompleted ? <CheckCircle2 className="h-4 w-4" /> : <Circle className="h-4 w-4" />}
                            <span className="hidden sm:inline">{isCompleted ? 'Completed' : 'Mark Complete'}</span>
                        </Button>

                        <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => setSidebarOpen(!sidebarOpen)}
                            title={sidebarOpen ? 'Hide sidebar' : 'Show sidebar'}
                        >
                            {sidebarOpen ? <PanelRightClose className="h-4 w-4" /> : <PanelRightOpen className="h-4 w-4" />}
                        </Button>
                    </div>
                </div>
            </header>

            {/* Main Layout */}
            <div className="flex">
                {/* Main Content Area - always centered */}
                <main className="flex-1 min-w-0">
                    <div className="max-w-4xl mx-auto p-6 space-y-6">
                        {/* Mobile title */}
                        <div className="sm:hidden">
                            <h1 className="text-xl font-bold">{lesson.title}</h1>
                        </div>

                        {/* Video Player */}
                        {lesson.video_file && (
                            <div className="space-y-2">
                                <video
                                    ref={mediaRef as React.RefObject<HTMLVideoElement>}
                                    controls
                                    preload="metadata"
                                    className="w-full rounded-lg bg-black aspect-video"
                                    onTimeUpdate={handleTimeUpdate}
                                    onEnded={handleEnded}
                                >
                                    <source src={getFileUrl(lesson.video_file)} type="video/mp4" />
                                    {lesson.subtitle_file && (
                                        <track kind="subtitles" src={getFileUrl(lesson.subtitle_file)} srcLang="en" label="English" />
                                    )}
                                </video>
                                {lesson.progress_seconds > 0 && (
                                    <p className="text-sm text-muted-foreground">
                                        Resume from {Math.floor(lesson.progress_seconds / 60)}:{String(lesson.progress_seconds % 60).padStart(2, '0')}
                                    </p>
                                )}
                            </div>
                        )}

                        {/* Audio Player */}
                        {lesson.audio_file && (
                            <div className="space-y-2">
                                <h3 className="font-medium">Audio</h3>
                                <audio
                                    ref={mediaRef as React.RefObject<HTMLAudioElement>}
                                    controls
                                    preload="metadata"
                                    className="w-full"
                                    onTimeUpdate={handleTimeUpdate}
                                    onEnded={handleEnded}
                                >
                                    <source src={getFileUrl(lesson.audio_file)} type="audio/mp3" />
                                </audio>
                            </div>
                        )}

                        {/* Text Content */}
                        {lesson.text_files.length > 0 && (
                            <div className="space-y-4">
                                <h3 className="font-medium">Resources</h3>
                                {lesson.text_files.map((file, i) => (
                                    <div key={i} className="rounded-lg border bg-card p-4">
                                        <a href={getFileUrl(file)} target="_blank" rel="noopener noreferrer"
                                            className="text-primary hover:underline">
                                            📄 {file.split('/').pop()} →
                                        </a>
                                    </div>
                                ))}
                            </div>
                        )}

                        {/* Navigation */}
                        <div className="flex justify-between items-center pt-6 border-t gap-4">
                            <Button
                                variant="outline"
                                onClick={() => prevLesson && navigateToLesson(prevLesson)}
                                disabled={!prevLesson}
                                className="gap-2"
                            >
                                <ChevronLeft className="h-4 w-4" />
                                Previous
                            </Button>

                            <Button
                                onClick={toggleCompletion}
                                variant={isCompleted ? 'default' : 'secondary'}
                                className={isCompleted ? 'bg-green-600 hover:bg-green-700 gap-2' : 'gap-2'}
                            >
                                {isCompleted ? <CheckCircle2 className="h-4 w-4" /> : <Circle className="h-4 w-4" />}
                                {isCompleted ? 'Completed ✓' : 'Mark as Complete'}
                            </Button>

                            <Button
                                variant="outline"
                                onClick={() => nextLesson && navigateToLesson(nextLesson)}
                                disabled={!nextLesson}
                                className="gap-2"
                            >
                                Next
                                <ChevronRight className="h-4 w-4" />
                            </Button>
                        </div>
                    </div>
                </main>

                {/* Sidebar - Course Content */}
                {sidebarOpen && course && activeSubCourse && (
                    <aside
                        className="fixed right-0 top-[53px] bottom-0 border-l bg-card overflow-hidden flex flex-col"
                        style={{ width: sidebarWidth }}
                    >
                        {/* Sidebar Header */}
                        <div className="p-4 border-b shrink-0">
                            <h2 className="font-semibold text-sm mb-2">{activeSubCourse.name}</h2>
                            {sidebarStats && (
                                <div className="space-y-2">
                                    <div className="flex justify-between text-xs text-muted-foreground">
                                        <span>{sidebarStats.completed_lessons} of {sidebarStats.total_lessons} lessons</span>
                                        <span>{sidebarStats.completion_percentage.toFixed(0)}%</span>
                                    </div>
                                    <Progress value={sidebarStats.completion_percentage} className="h-2" />
                                </div>
                            )}
                        </div>

                        {/* Sidebar Content - scrollable */}
                        <ScrollArea className="flex-1 min-h-0">
                            <div className="p-3">
                                <SidebarNode
                                    node={activeSubCourse}
                                    coursePath={course.path}
                                    currentLessonPath={lessonPath || ''}
                                    onLessonClick={navigateToLesson}
                                    onMarkComplete={markLessonComplete}
                                />
                            </div>
                        </ScrollArea>
                    </aside>
                )}
            </div>
        </div>
    );
}

// ============================================
// Sidebar Components
// ============================================

interface SidebarNodeProps {
    node: DirectoryNode;
    coursePath: string;
    currentLessonPath: string;
    onLessonClick: (path: string) => void;
    onMarkComplete: (lessonPath: string, completed: boolean) => Promise<void>;
    depth?: number;
}

function SidebarNode({ node, coursePath, currentLessonPath, onLessonClick, onMarkComplete, depth = 0 }: SidebarNodeProps) {
    // Helper to build the full path for a lesson
    const buildLessonFullPath = (lessonItem: { path: string; title: string }) => {
        // Normalize both paths to use forward slashes before comparison
        const normalizedLessonPath = lessonItem.path.replace(/\\/g, '/');
        const normalizedCoursePath = coursePath.replace(/\\/g, '/');
        const relativePath = normalizedLessonPath.replace(normalizedCoursePath, '').replace(/^\//, '');
        return `${relativePath}/${lessonItem.title.replace(/ /g, '_')}`;
    };

    // Check if any lesson in this folder matches the current path
    const containsCurrentLesson = node.lessons.some(l => {
        const fullPath = buildLessonFullPath(l);
        return currentLessonPath === fullPath;
    }) || Object.values(node.children).some(child => {
        // Check if current path starts with this child's relative path
        const childRelPath = child.path.replace(coursePath, '').replace(/\\/g, '/').replace(/^[\\\/]/, '');
        return currentLessonPath.startsWith(childRelPath + '/');
    });

    // Root level or folder containing current lesson starts expanded
    const [expanded, setExpanded] = useState(depth === 0 || containsCurrentLesson);
    const hasChildren = Object.keys(node.children).length > 0 || node.lessons.length > 0;

    if (!hasChildren) return null;

    const TypeIcons: Record<string, typeof Video> = {
        video: Video,
        audio: Music,
        text: FileText,
        mixed: FileText,
        quiz: FileText
    };

    // Check if this folder directly contains the current lesson
    const isActiveFolder = node.lessons.some(l => {
        const fullPath = buildLessonFullPath(l);
        return currentLessonPath === fullPath;
    });

    // Helper to get all lesson full paths from a node recursively
    const getAllLessonPaths = (targetNode: DirectoryNode): string[] => {
        let paths: string[] = [];

        for (const lesson of targetNode.lessons) {
            paths.push(buildLessonFullPath(lesson));
        }

        for (const child of Object.values(targetNode.children)) {
            paths = paths.concat(getAllLessonPaths(child));
        }

        return paths;
    };

    // Check if all lessons in this folder are completed
    const allLessonsInNode = getAllLessonsFromNode(node);
    const allCompleted = allLessonsInNode.length > 0 && allLessonsInNode.every(l => l.completed);

    // Mark all lessons in folder as complete/incomplete
    const markFolderComplete = async (completed: boolean) => {
        const lessonPaths = getAllLessonPaths(node);
        // Run all updates in parallel for instant completion
        await Promise.all(lessonPaths.map(lessonPath => onMarkComplete(lessonPath, completed)));
    };

    return (
        <div>
            {/* Folder header - only show for nested folders */}
            {depth > 0 && (
                <ContextMenu>
                    <ContextMenuTrigger asChild>
                        <button
                            onClick={() => setExpanded(!expanded)}
                            className={`w-full flex items-center gap-2 p-2 rounded-md text-left text-sm mb-1 ${isActiveFolder
                                ? 'bg-muted border border-primary/30'
                                : 'hover:bg-muted/50'
                                }`}
                        >
                            {expanded ? (
                                <ChevronDown className="h-4 w-4 text-muted-foreground shrink-0" />
                            ) : (
                                <ChevronRightIcon className="h-4 w-4 text-muted-foreground shrink-0" />
                            )}
                            <FolderOpen className={`h-4 w-4 shrink-0 ${isActiveFolder ? 'text-primary' : 'text-primary'}`} />
                            <span className="truncate font-medium">{node.name}</span>
                            {allCompleted && (
                                <CheckCircle2 className="h-3 w-3 text-green-500 shrink-0 ml-auto" />
                            )}
                        </button>
                    </ContextMenuTrigger>
                    <ContextMenuContent>
                        <ContextMenuItem
                            onClick={() => markFolderComplete(!allCompleted)}
                        >
                            {allCompleted ? (
                                <>
                                    <Circle className="h-4 w-4 mr-2" />
                                    Mark All as Incomplete
                                </>
                            ) : (
                                <>
                                    <CheckCircle2 className="h-4 w-4 mr-2" />
                                    Mark All as Complete
                                </>
                            )}
                        </ContextMenuItem>
                        <ContextMenuItem
                            onClick={() => {
                                navigator.clipboard.writeText(node.path);
                            }}
                        >
                            <Copy className="h-4 w-4 mr-2" />
                            Copy Folder Path
                        </ContextMenuItem>
                    </ContextMenuContent>
                </ContextMenu>
            )}

            {expanded && (
                <div className={depth > 0 ? 'ml-3 pl-3 border-l border-border' : ''}>
                    {/* Child folders - sorted numerically */}
                    {Object.values(node.children)
                        .sort((a, b) => {
                            const numA = parseInt(a.name.match(/^(\d+)/)?.[1] || '999999');
                            const numB = parseInt(b.name.match(/^(\d+)/)?.[1] || '999999');
                            if (numA !== numB) return numA - numB;
                            return a.name.localeCompare(b.name);
                        })
                        .map((child) => (
                            <SidebarNode
                                key={child.path}
                                node={child}
                                coursePath={coursePath}
                                currentLessonPath={currentLessonPath}
                                onLessonClick={onLessonClick}
                                onMarkComplete={onMarkComplete}
                                depth={depth + 1}
                            />
                        ))}

                    {/* Lessons - sorted numerically */}
                    {[...node.lessons]
                        .sort((a, b) => {
                            const numA = parseInt(a.title.match(/^(\d+)/)?.[1] || '999999');
                            const numB = parseInt(b.title.match(/^(\d+)/)?.[1] || '999999');
                            if (numA !== numB) return numA - numB;
                            return a.title.localeCompare(b.title);
                        })
                        .map((lessonItem) => {
                            const relativePath = lessonItem.path.replace(coursePath, '').replace(/\\/g, '/').replace(/^[\\\/]/, '');
                            const fullPath = `${relativePath}/${lessonItem.title.replace(/ /g, '_')}`;
                            const isCurrent = currentLessonPath === fullPath;
                            const Icon = TypeIcons[lessonItem.lesson_type] || FileText;

                            // Extract file extension from path
                            const ext = lessonItem.path.match(/\.([^.]+)$/)?.[1]?.toLowerCase() || '';

                            return (
                                <ContextMenu key={lessonItem.path}>
                                    <ContextMenuTrigger asChild>
                                        <button
                                            onClick={() => {
                                                window.location.href = `/lesson/${encodeURIComponent(fullPath)}`;
                                            }}
                                            className={`w-full flex items-start gap-2 p-2 rounded-md text-left text-sm transition-colors mb-0.5 ${isCurrent
                                                ? 'bg-primary text-primary-foreground'
                                                : 'hover:bg-muted/50'
                                                }`}
                                        >
                                            {/* Completion Icon */}
                                            {lessonItem.completed ? (
                                                <CheckCircle2 className={`h-4 w-4 shrink-0 mt-0.5 ${isCurrent ? 'text-primary-foreground' : 'text-green-500'}`} />
                                            ) : (
                                                <Circle className={`h-4 w-4 shrink-0 mt-0.5 ${isCurrent ? 'text-primary-foreground' : 'text-muted-foreground'}`} />
                                            )}

                                            {/* Lesson Title with extension */}
                                            <span className="flex-1 leading-snug">
                                                {lessonItem.title}
                                                {ext && (
                                                    <span className={`ml-1 text-xs ${isCurrent ? 'text-primary-foreground/70' : 'text-muted-foreground'}`}>
                                                        .{ext}
                                                    </span>
                                                )}
                                            </span>
                                        </button>
                                    </ContextMenuTrigger>
                                    <ContextMenuContent>
                                        <ContextMenuItem
                                            onClick={async () => {
                                                await onMarkComplete(fullPath, !lessonItem.completed);
                                            }}
                                        >
                                            {lessonItem.completed ? (
                                                <>
                                                    <Circle className="h-4 w-4 mr-2" />
                                                    Mark as Incomplete
                                                </>
                                            ) : (
                                                <>
                                                    <CheckCircle2 className="h-4 w-4 mr-2" />
                                                    Mark as Complete
                                                </>
                                            )}
                                        </ContextMenuItem>
                                        <ContextMenuItem
                                            onClick={() => {
                                                navigator.clipboard.writeText(lessonItem.path);
                                            }}
                                        >
                                            <Copy className="h-4 w-4 mr-2" />
                                            Copy File Path
                                        </ContextMenuItem>
                                    </ContextMenuContent>
                                </ContextMenu>
                            );
                        })}
                </div>
            )}
        </div>
    );
}

// Helper function to get all lessons from a node recursively
function getAllLessonsFromNode(node: DirectoryNode): LessonItem[] {
    let lessons: LessonItem[] = [...node.lessons];

    for (const child of Object.values(node.children)) {
        lessons = lessons.concat(getAllLessonsFromNode(child));
    }

    return lessons;
}

