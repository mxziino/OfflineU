import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { getCourseInfo, resetCourse } from '@/lib/api';
import type { Course, CourseStats, DirectoryNode, LessonItem } from '@/types/api';
import { ChevronRight, ChevronDown, Folder, Video, Music, FileText, FileQuestion, Package, CheckCircle, Circle, ArrowLeft, Play } from 'lucide-react';

interface CourseDashboardProps {
    onReset: () => void;
}

export function CourseDashboard({ onReset }: CourseDashboardProps) {
    const navigate = useNavigate();
    const [course, setCourse] = useState<Course | null>(null);
    const [stats, setStats] = useState<CourseStats | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        getCourseInfo().then((data) => {
            if (data) {
                setCourse(data.course);
                setStats(data.stats);
            }
            setLoading(false);
        });
    }, []);

    const handleReset = async () => {
        await resetCourse();
        onReset();
    };

    const handleLessonClick = (lessonPath: string) => {
        navigate(`/lesson/${encodeURIComponent(lessonPath)}`);
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-background flex items-center justify-center">
                <div className="text-muted-foreground">Loading course...</div>
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
                            Select Different Course
                        </Button>
                    </div>
                    <div className="text-sm text-muted-foreground">
                        {stats?.total_lessons} lessons
                    </div>
                </div>
            </header>

            {/* Main Content */}
            <main className="container py-6 space-y-6">
                {/* Course Info Card */}
                <Card>
                    <CardHeader>
                        <CardTitle className="text-2xl">{course.name}</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div className="flex items-center justify-between">
                            <span className="font-medium">
                                {stats?.completed_lessons}/{stats?.total_lessons} lessons completed
                            </span>
                            <span className="text-primary text-lg font-semibold">
                                {stats?.completion_percentage.toFixed(1)}%
                            </span>
                        </div>
                        <Progress value={stats?.completion_percentage || 0} className="h-3" />

                        {stats?.last_accessed_path && (
                            <div className="flex items-center justify-between bg-green-500/10 rounded-lg p-3 border border-green-500/20">
                                <span className="text-sm">
                                    <strong>Last Accessed:</strong> {stats.last_accessed_path}
                                </span>
                                <Button size="sm" onClick={() => handleLessonClick(stats.last_accessed_path!)} className="gap-2">
                                    <Play className="h-4 w-4" />
                                    Continue
                                </Button>
                            </div>
                        )}
                    </CardContent>
                </Card>

                {/* Course Tree */}
                <div className="space-y-2">
                    <TreeNode
                        node={course.root_node}
                        onLessonClick={handleLessonClick}
                        coursePath={course.path}
                    />
                </div>
            </main>
        </div>
    );
}

interface TreeNodeProps {
    node: DirectoryNode;
    onLessonClick: (path: string) => void;
    coursePath: string;
    depth?: number;
}

function TreeNode({ node, onLessonClick, coursePath, depth = 0 }: TreeNodeProps) {
    const [expanded, setExpanded] = useState(depth < 1);
    const hasChildren = Object.keys(node.children).length > 0 || node.lessons.length > 0;
    const itemCount = Object.keys(node.children).length + node.lessons.length;

    if (!hasChildren) return null;

    return (
        <div className="space-y-1">
            {/* Directory Header */}
            <button
                onClick={() => setExpanded(!expanded)}
                className="w-full flex items-center gap-2 p-3 rounded-lg bg-card hover:bg-muted/50 transition-colors border-l-2 border-primary"
                style={{ marginLeft: depth * 16 }}
            >
                {expanded ? (
                    <ChevronDown className="h-4 w-4 text-muted-foreground" />
                ) : (
                    <ChevronRight className="h-4 w-4 text-muted-foreground" />
                )}
                <Folder className="h-4 w-4 text-primary" />
                <span className="font-medium flex-1 text-left">{node.name}</span>
                <span className="text-sm text-muted-foreground">{itemCount} items</span>
            </button>

            {/* Children */}
            {expanded && (
                <div className="space-y-1">
                    {/* Child Directories - sorted numerically by leading number */}
                    {Object.values(node.children)
                        .sort((a, b) => {
                            const numA = parseInt(a.name.match(/^(\d+)/)?.[1] || '999999');
                            const numB = parseInt(b.name.match(/^(\d+)/)?.[1] || '999999');
                            if (numA !== numB) return numA - numB;
                            return a.name.localeCompare(b.name);
                        })
                        .map((child) => (
                            <TreeNode
                                key={child.path}
                                node={child}
                                onLessonClick={onLessonClick}
                                coursePath={coursePath}
                                depth={depth + 1}
                            />
                        ))}

                    {/* Lessons */}
                    {node.lessons.map((lesson) => (
                        <LessonItem
                            key={lesson.path}
                            lesson={lesson}
                            onClick={() => {
                                // Create relative path
                                const relativePath = lesson.path.replace(coursePath, '').replace(/^[\\\/]/, '').replace(/\\/g, '/');
                                onLessonClick(`${relativePath}/${lesson.title.replace(/ /g, '_')}`);
                            }}
                            depth={depth + 1}
                        />
                    ))}
                </div>
            )}
        </div>
    );
}

interface LessonItemProps {
    lesson: LessonItem;
    onClick: () => void;
    depth: number;
}

function LessonItem({ lesson, onClick, depth }: LessonItemProps) {
    const iconMap = {
        video: Video,
        audio: Music,
        text: FileText,
        quiz: FileQuestion,
        mixed: Package,
    };
    const TypeIcon = iconMap[lesson.lesson_type] || FileText;

    const typeColors = {
        video: 'bg-red-500',
        audio: 'bg-purple-500',
        text: 'bg-slate-500',
        quiz: 'bg-yellow-500',
        mixed: 'bg-teal-500',
    };

    return (
        <button
            onClick={onClick}
            className={`w-full flex items-center gap-3 p-3 rounded-lg transition-all hover:translate-x-1 ${lesson.completed
                ? 'bg-green-500/10 border-l-2 border-green-500'
                : 'bg-card hover:bg-muted/50 border-l-2 border-transparent'
                }`}
            style={{ marginLeft: depth * 16 }}
        >
            <TypeIcon className="h-4 w-4" />
            <span className="flex-1 text-left">{lesson.title}</span>
            <Badge className={`${typeColors[lesson.lesson_type]} text-white text-xs`}>
                {lesson.lesson_type}
            </Badge>
            {lesson.completed ? (
                <CheckCircle className="h-5 w-5 text-green-500" />
            ) : (
                <Circle className="h-5 w-5 text-muted-foreground" />
            )}
        </button>
    );
}
