import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { FolderBrowser, type LoadMode } from '@/components/FolderBrowser';
import { loadCourse, getLibrary, addToLibrary, removeFromLibrary, type LibraryCourse } from '@/lib/api';
import { Folder, BookOpen, Video, Music, FileText, Subtitles, Clock, Trash2, Library } from 'lucide-react';

interface CourseSelectorProps {
    onCourseLoaded: (mode: LoadMode) => void;
}

export function CourseSelector({ onCourseLoaded }: CourseSelectorProps) {
    const [coursePath, setCoursePath] = useState('');
    const [browserOpen, setBrowserOpen] = useState(false);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [library, setLibrary] = useState<LibraryCourse[]>([]);

    useEffect(() => {
        getLibrary().then(setLibrary);
    }, []);

    const handleLoadCourse = async (path?: string, mode: LoadMode = 'course') => {
        const targetPath = path || coursePath;
        if (!targetPath.trim()) {
            setError('Please enter or select a course path');
            return;
        }

        setLoading(true);
        setError(null);

        try {
            const result = await loadCourse(targetPath, mode);
            if (result.success && result.course_name) {
                await addToLibrary(result.course_name, targetPath);
                onCourseLoaded(mode);
            } else {
                setError(result.error || 'Failed to load course');
            }
        } catch {
            setError('Error loading course');
        } finally {
            setLoading(false);
        }
    };

    const handleFolderSelect = (path: string, mode: LoadMode) => {
        setCoursePath(path);
        handleLoadCourse(path, mode);
    };

    const handleRemoveFromLibrary = async (path: string, e: React.MouseEvent) => {
        e.stopPropagation();
        await removeFromLibrary(path);
        setLibrary(await getLibrary());
    };

    return (
        <div className="min-h-screen bg-background flex flex-col">
            {/* Header */}
            <header className="border-b bg-card">
                <div className="container py-6">
                    <h1 className="text-3xl font-bold text-primary">OfflineU</h1>
                    <p className="text-muted-foreground mt-1">Self-hosted course viewer & progress tracker</p>
                </div>
            </header>

            {/* Main Content */}
            <main className="flex-1 container py-8">
                <div className="max-w-2xl mx-auto space-y-6">
                    {/* Course Selection Card */}
                    <Card className="border-dashed border-2">
                        <CardHeader>
                            <CardTitle className="flex items-center gap-2">
                                <BookOpen className="h-5 w-5" />
                                Select a Course
                            </CardTitle>
                            <CardDescription>
                                Browse your folders or enter the path to your course directory
                            </CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <div className="flex gap-2">
                                <input
                                    type="text"
                                    value={coursePath}
                                    onChange={(e) => setCoursePath(e.target.value)}
                                    placeholder="e.g., C:\Users\YourName\Documents\MyCourse"
                                    className="flex-1 px-3 py-2 rounded-md border bg-background text-sm focus:outline-none focus:ring-2 focus:ring-primary"
                                    onKeyDown={(e) => e.key === 'Enter' && handleLoadCourse()}
                                />
                                <Button
                                    variant="secondary"
                                    onClick={() => setBrowserOpen(true)}
                                    className="flex items-center gap-2"
                                >
                                    <Folder className="h-4 w-4" />
                                    Browse
                                </Button>
                                <Button onClick={() => handleLoadCourse()} disabled={loading}>
                                    {loading ? 'Loading...' : 'Load Course'}
                                </Button>
                            </div>

                            {error && (
                                <p className="text-sm text-destructive">{error}</p>
                            )}

                            <p className="text-sm text-muted-foreground">
                                💡 <strong>Tip:</strong> Click "Browse" to visually navigate to your course directory.
                                Folders with media files are highlighted in green.
                            </p>
                        </CardContent>
                    </Card>

                    {/* Recent Courses Library */}
                    {library.length > 0 && (
                        <Card>
                            <CardHeader>
                                <CardTitle className="flex items-center gap-2 text-lg">
                                    <Clock className="h-5 w-5" />
                                    Recent Courses
                                </CardTitle>
                            </CardHeader>
                            <CardContent className="space-y-2">
                                {library.map((course) => (
                                    <button
                                        key={course.path}
                                        onClick={() => handleLoadCourse(course.path)}
                                        className="w-full flex items-center gap-3 p-3 rounded-lg bg-muted/30 hover:bg-muted/50 transition-colors text-left group"
                                    >
                                        <BookOpen className="h-5 w-5 text-primary" />
                                        <div className="flex-1 min-w-0">
                                            <div className="font-medium truncate">{course.name}</div>
                                            <div className="text-sm text-muted-foreground truncate">{course.path}</div>
                                        </div>
                                        <Button
                                            variant="ghost"
                                            size="sm"
                                            className="opacity-0 group-hover:opacity-100 transition-opacity"
                                            onClick={(e) => handleRemoveFromLibrary(course.path, e)}
                                        >
                                            <Trash2 className="h-4 w-4" />
                                        </Button>
                                    </button>
                                ))}
                            </CardContent>
                        </Card>
                    )}

                    {/* Info Cards */}
                    <div className="grid md:grid-cols-2 gap-4">
                        <Card>
                            <CardHeader>
                                <CardTitle className="text-lg">How to Use</CardTitle>
                            </CardHeader>
                            <CardContent className="space-y-2 text-sm text-muted-foreground">
                                <p>1. Prepare your course files in a directory</p>
                                <p>2. Click "Browse" to navigate to the folder</p>
                                <p>3. Select the course directory</p>
                                <p>4. Start learning! Progress saves automatically</p>
                            </CardContent>
                        </Card>

                        <Card>
                            <CardHeader>
                                <CardTitle className="text-lg">Supported Files</CardTitle>
                            </CardHeader>
                            <CardContent className="space-y-2 text-sm">
                                <div className="flex items-center gap-2">
                                    <Video className="h-4 w-4 text-red-400" />
                                    <span>.mp4, .mkv, .avi, .mov, .webm</span>
                                </div>
                                <div className="flex items-center gap-2">
                                    <Music className="h-4 w-4 text-purple-400" />
                                    <span>.mp3, .wav, .m4a, .aac</span>
                                </div>
                                <div className="flex items-center gap-2">
                                    <FileText className="h-4 w-4 text-blue-400" />
                                    <span>.txt, .md, .html, .pdf</span>
                                </div>
                                <div className="flex items-center gap-2">
                                    <Subtitles className="h-4 w-4 text-yellow-400" />
                                    <span>.srt, .vtt</span>
                                </div>
                            </CardContent>
                        </Card>
                    </div>
                </div>
            </main>

            {/* Folder Browser Dialog */}
            <FolderBrowser
                open={browserOpen}
                onOpenChange={setBrowserOpen}
                onSelect={handleFolderSelect}
            />
        </div>
    );
}
