import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { FolderBrowser, type LoadMode } from '@/components/FolderBrowser';
import { loadCourse, getLibrary, addToLibrary, removeFromLibrary, getAllTags, updateLibraryTags } from '@/lib/api';
import {
    Library, BookOpen, Plus, Trash2, CheckCircle2,
    FolderOpen, Play, BarChart3, Search, X
} from 'lucide-react';

interface LibraryItem {
    name: string;
    path: string;
    load_mode: 'course' | 'learning_path';
    total_lessons: number;
    completed_lessons: number;
    last_accessed: string;
    tags?: string[];
}

interface LibraryPageProps {
    onCourseSelected: (mode: LoadMode) => void;
    onShowStats?: () => void;
}

export function LibraryPage({ onCourseSelected, onShowStats }: LibraryPageProps) {
    const [library, setLibrary] = useState<LibraryItem[]>([]);
    const [browserOpen, setBrowserOpen] = useState(false);
    const [loading, setLoading] = useState(true);
    const [loadingPath, setLoadingPath] = useState<string | null>(null);
    const [searchQuery, setSearchQuery] = useState('');
    const [selectedTags, setSelectedTags] = useState<string[]>([]);
    const [allTags, setAllTags] = useState<string[]>([]);

    useEffect(() => {
        loadLibrary();
        loadTags();
    }, []);

    const loadLibrary = async () => {
        setLoading(true);
        const items = await getLibrary();
        setLibrary(items as LibraryItem[]);
        setLoading(false);
    };

    const loadTags = async () => {
        const tags = await getAllTags();
        setAllTags(tags);
    };

    const handleFolderSelect = async (path: string, mode: LoadMode) => {
        setLoadingPath(path);
        try {
            const result = await loadCourse(path, mode);
            if (result.success && result.course_name) {
                await addToLibrary(result.course_name, path, mode);
                setBrowserOpen(false);
                onCourseSelected(mode);
            } else {
                alert(result.error || 'Failed to load course');
                setBrowserOpen(false);
            }
        } catch (error) {
            console.error('Failed to load course:', error);
            alert('Failed to load course. Please check the path and try again.');
            setBrowserOpen(false);
        } finally {
            setLoadingPath(null);
        }
    };

    const handleItemClick = async (item: LibraryItem) => {
        setLoadingPath(item.path);
        try {
            const mode = item.load_mode || 'course';
            const result = await loadCourse(item.path, mode);
            if (result.success) {
                onCourseSelected(mode);
            }
        } catch (error) {
            console.error('Failed to load:', error);
        } finally {
            setLoadingPath(null);
        }
    };

    const handleRemove = async (path: string, e: React.MouseEvent) => {
        e.stopPropagation();
        await removeFromLibrary(path);
        await loadLibrary();
        await loadTags(); // Reload tags after removing an item
    };

    const toggleTagFilter = (tag: string) => {
        setSelectedTags(prev =>
            prev.includes(tag)
                ? prev.filter(t => t !== tag)
                : [...prev, tag]
        );
    };

    const handleTagsUpdate = async (path: string, tags: string[]) => {
        await updateLibraryTags(path, tags);
        await loadLibrary();
        await loadTags();
    };

    // Client-side filtering based on search and selected tags
    const filteredLibrary = library.filter(item => {
        // Filter by search query
        if (searchQuery && !item.name.toLowerCase().includes(searchQuery.toLowerCase())) {
            return false;
        }

        // Filter by selected tags ( OR logic - needs to match at least one)
        if (selectedTags.length > 0) {
            const itemTags = item.tags || [];
            if (!selectedTags.some(tag => itemTags.includes(tag))) {
                return false;
            }
        }

        return true;
    });

    const learningPaths = filteredLibrary.filter(i => i.load_mode === 'learning_path');
    const courses = filteredLibrary.filter(i => i.load_mode !== 'learning_path');

    const formatDate = (isoString: string) => {
        const date = new Date(isoString);
        const now = new Date();
        const diff = now.getTime() - date.getTime();
        const days = Math.floor(diff / (1000 * 60 * 60 * 24));

        if (days === 0) return 'Today';
        if (days === 1) return 'Yesterday';
        if (days < 7) return `${days} days ago`;
        return date.toLocaleDateString();
    };

    return (
        <div className="min-h-screen bg-background">
            {/* Header */}
            <header className="border-b bg-card sticky top-0 z-10">
                <div className="container py-4">
                    <div className="flex items-center justify-between mb-4">
                        <div className="flex items-center gap-3">
                            <Library className="h-6 w-6 text-primary" />
                            <h1 className="text-xl font-bold">OfflineU</h1>
                        </div>
                        <div className="flex items-center gap-2">
                            {onShowStats && (
                                <Button variant="outline" onClick={onShowStats} className="gap-2">
                                    <BarChart3 className="h-4 w-4" />
                                    Stats
                                </Button>
                            )}
                            <Button onClick={() => setBrowserOpen(true)} className="gap-2">
                                <Plus className="h-4 w-4" />
                                Add Course
                            </Button>
                        </div>
                    </div>

                    {/* Search Bar */}
                    <div className="relative mb-3">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                        <input
                            type="text"
                            placeholder="Search courses..."
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            className="w-full pl-10 pr-4 py-2 bg-background border border-input rounded-md focus:outline-none focus:ring-2 focus:ring-ring"
                        />
                        {searchQuery && (
                            <button
                                onClick={() => setSearchQuery('')}
                                className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                            >
                                <X className="h-4 w-4" />
                            </button>
                        )}
                    </div>

                    {/* Tag Filters */}
                    {allTags.length > 0 && (
                        <div className="flex flex-wrap gap-2">
                            {allTags.map(tag => (
                                <Badge
                                    key={tag}
                                    variant={selectedTags.includes(tag) ? "default" : "outline"}
                                    className="cursor-pointer"
                                    onClick={() => toggleTagFilter(tag)}
                                >
                                    {tag}
                                    {selectedTags.includes(tag) && (
                                        <X className="ml-1 h-3 w-3" />
                                    )}
                                </Badge>
                            ))}
                        </div>
                    )}
                </div>
            </header>

            {/* Main Content */}
            <main className="container py-8 max-w-5xl mx-auto space-y-8">
                {loading ? (
                    <div className="text-center py-16 text-muted-foreground">
                        Loading library...
                    </div>
                ) : library.length === 0 ? (
                    <div className="text-center py-16 space-y-4">
                        <FolderOpen className="h-16 w-16 text-muted-foreground mx-auto" />
                        <h2 className="text-xl font-semibold">No courses yet</h2>
                        <p className="text-muted-foreground">
                            Click "Add Course" to browse and select a course folder
                        </p>
                        <Button onClick={() => setBrowserOpen(true)} className="gap-2">
                            <Plus className="h-4 w-4" />
                            Add Your First Course
                        </Button>
                    </div>
                ) : (
                    <>
                        {/* Learning Paths Section */}
                        {learningPaths.length > 0 && (
                            <section>
                                <div className="flex items-center gap-2 mb-4">
                                    <Library className="h-5 w-5 text-purple-500" />
                                    <h2 className="text-lg font-semibold">Learning Paths</h2>
                                    <span className="text-sm text-muted-foreground">
                                        ({learningPaths.length})
                                    </span>
                                </div>
                                <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                                    {learningPaths.map((item) => (
                                        <LibraryCard
                                            key={item.path}
                                            item={item}
                                            loading={loadingPath === item.path}
                                            onClick={() => handleItemClick(item)}
                                            onRemove={(e) => handleRemove(item.path, e)}
                                            onTagsUpdate={(tags) => handleTagsUpdate(item.path, tags)}
                                            formatDate={formatDate}
                                        />
                                    ))}
                                </div>
                            </section>
                        )}

                        {/* Courses Section */}
                        {courses.length > 0 && (
                            <section>
                                <div className="flex items-center gap-2 mb-4">
                                    <BookOpen className="h-5 w-5 text-primary" />
                                    <h2 className="text-lg font-semibold">Courses</h2>
                                    <span className="text-sm text-muted-foreground">
                                        ({courses.length})
                                    </span>
                                </div>
                                <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                                    {courses.map((item) => (
                                        <LibraryCard
                                            key={item.path}
                                            item={item}
                                            loading={loadingPath === item.path}
                                            onClick={() => handleItemClick(item)}
                                            onRemove={(e) => handleRemove(item.path, e)}
                                            onTagsUpdate={(tags) => handleTagsUpdate(item.path, tags)}
                                            formatDate={formatDate}
                                        />
                                    ))}
                                </div>
                            </section>
                        )}
                    </>
                )}
            </main>

            {/* Folder Browser */}
            <FolderBrowser
                open={browserOpen}
                onOpenChange={setBrowserOpen}
                onSelect={handleFolderSelect}
            />
        </div>
    );
}

// ============================================
// Library Card Component
// ============================================

interface LibraryCardProps {
    item: LibraryItem;
    loading: boolean;
    onClick: () => void;
    onRemove: (e: React.MouseEvent) => void;
    onTagsUpdate: (tags: string[]) => void;
    formatDate: (date: string) => string;
}

function LibraryCard({ item, loading, onClick, onRemove, onTagsUpdate, formatDate }: LibraryCardProps) {
    const progress = item.total_lessons > 0
        ? (item.completed_lessons / item.total_lessons) * 100
        : 0;
    const isComplete = progress === 100 && item.total_lessons > 0;

    const handleEditTags = (e: React.MouseEvent) => {
        e.stopPropagation();
        const currentTags = (item.tags || []).join(', ');
        const newTagsStr = prompt('Enter tags (comma separated):', currentTags);
        if (newTagsStr !== null) {
            const newTags = newTagsStr.split(',').map(t => t.trim()).filter(t => t.length > 0);
            onTagsUpdate(newTags);
        }
    };

    return (
        <Card
            className={`cursor-pointer transition-all hover:shadow-lg hover:scale-[1.02] group relative ${loading ? 'opacity-70 pointer-events-none' : ''
                } ${isComplete ? 'border-green-500/50' : ''}`}
            onClick={onClick}
        >
            <CardHeader className="pb-2">
                <CardTitle className="flex items-start gap-2">
                    {item.load_mode === 'learning_path' ? (
                        <Library className="h-5 w-5 text-purple-500 shrink-0 mt-0.5" />
                    ) : (
                        <BookOpen className="h-5 w-5 text-primary shrink-0 mt-0.5" />
                    )}
                    <span className="flex-1 line-clamp-2 leading-tight break-all">{item.name}</span>
                    {isComplete && (
                        <CheckCircle2 className="h-5 w-5 text-green-500 shrink-0" />
                    )}
                </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
                {item.total_lessons > 0 && (
                    <div className="space-y-1">
                        <div className="flex justify-between text-xs text-muted-foreground">
                            <span>{item.completed_lessons}/{item.total_lessons} lessons</span>
                            <span>{progress.toFixed(0)}%</span>
                        </div>
                        <Progress value={progress} className="h-1.5" />
                    </div>
                )}

                {/* Tags Display */}
                {item.tags && item.tags.length > 0 && (
                    <div className="flex flex-wrap gap-1">
                        {item.tags.map(tag => (
                            <Badge key={tag} variant="secondary" className="text-xs">
                                {tag}
                            </Badge>
                        ))}
                    </div>
                )}

                <div className="flex items-center justify-between">
                    <span className="text-xs text-muted-foreground">
                        {formatDate(item.last_accessed)}
                    </span>
                    <div className="flex gap-1">
                        <Button
                            variant="ghost"
                            size="sm"
                            className="h-7 px-2 opacity-0 group-hover:opacity-100 transition-opacity"
                            onClick={handleEditTags}
                            title="Edit Tags"
                        >
                            <Library className="h-3 w-3" />
                        </Button>
                        <Button
                            variant="ghost"
                            size="sm"
                            className="h-7 px-2 opacity-0 group-hover:opacity-100 transition-opacity"
                            onClick={onRemove}
                        >
                            <Trash2 className="h-3 w-3" />
                        </Button>
                        <Button variant="outline" size="sm" className="h-7 gap-1">
                            <Play className="h-3 w-3" />
                            {loading ? 'Loading...' : progress === 0 ? 'Start' : 'Continue'}
                        </Button>
                    </div>
                </div>
            </CardContent>
        </Card>
    );
}
