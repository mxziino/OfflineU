import { useState, useEffect, useCallback } from 'react';
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Breadcrumb, BreadcrumbItem, BreadcrumbLink, BreadcrumbList, BreadcrumbSeparator } from '@/components/ui/breadcrumb';
import { Badge } from '@/components/ui/badge';
import { browseFolders } from '@/lib/api';
import type { DirectoryInfo } from '@/types/api';
import { Folder, FolderOpen, Monitor, ArrowUp, BookOpen, Library } from 'lucide-react';

export type LoadMode = 'course' | 'learning_path';

interface FolderBrowserProps {
    open: boolean;
    onOpenChange: (open: boolean) => void;
    onSelect: (path: string, mode: LoadMode) => void;
}

export function FolderBrowser({ open, onOpenChange, onSelect }: FolderBrowserProps) {
    const [currentPath, setCurrentPath] = useState('');
    const [parentPath, setParentPath] = useState<string | null>(null);
    const [directories, setDirectories] = useState<DirectoryInfo[]>([]);
    const [loading, setLoading] = useState(false);
    const [loadingCourse, setLoadingCourse] = useState<'course' | 'learning_path' | null>(null);
    const [error, setError] = useState<string | null>(null);

    const loadFolder = useCallback(async (path: string) => {
        setLoading(true);
        setError(null);
        try {
            const data = await browseFolders(path);
            if (data.error) {
                setError(data.error);
            } else {
                setCurrentPath(data.current_path);
                setParentPath(data.parent_path);
                setDirectories(data.directories);
            }
        } catch (err) {
            setError('Failed to load folders');
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        if (open) {
            loadFolder('');
        }
    }, [open, loadFolder]);

    const handleSelectAsCourse = async () => {
        if (currentPath && currentPath !== 'Select a Drive') {
            setLoadingCourse('course');
            onSelect(currentPath, 'course');
            // Don't close immediately, parent will handle navigation
        }
    };

    const handleSelectAsLearningPath = async () => {
        if (currentPath && currentPath !== 'Select a Drive') {
            setLoadingCourse('learning_path');
            onSelect(currentPath, 'learning_path');
            // Don't close immediately, parent will handle navigation
        }
    };

    // Parse path into breadcrumb parts
    const pathParts = currentPath && currentPath !== 'Select a Drive'
        ? currentPath.split(/[\\\/]/).filter(Boolean)
        : [];

    const canSelect = currentPath && currentPath !== 'Select a Drive';

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="max-w-2xl max-h-[80vh] flex flex-col">
                <DialogHeader>
                    <DialogTitle className="flex items-center gap-2">
                        <FolderOpen className="h-5 w-5" />
                        Browse Folders
                    </DialogTitle>
                </DialogHeader>

                {/* Manual Path Input */}
                <div className="flex gap-2">
                    <input
                        type="text"
                        value={currentPath === 'Select a Drive' ? '' : currentPath}
                        onChange={(e) => setCurrentPath(e.target.value)}
                        onKeyDown={(e) => {
                            if (e.key === 'Enter' && currentPath) {
                                loadFolder(currentPath);
                            }
                        }}
                        placeholder="Paste path here, e.g., C:\Courses\MyLearningPath"
                        className="flex-1 px-3 py-2 rounded-md border bg-background text-sm focus:outline-none focus:ring-2 focus:ring-primary"
                    />
                    <Button
                        variant="secondary"
                        size="sm"
                        onClick={() => currentPath && loadFolder(currentPath)}
                    >
                        Go
                    </Button>
                </div>

                {/* Breadcrumb */}
                <div className="bg-muted/50 rounded-md p-2">
                    <Breadcrumb>
                        <BreadcrumbList>
                            <BreadcrumbItem>
                                <BreadcrumbLink
                                    href="#"
                                    onClick={(e) => { e.preventDefault(); loadFolder(''); }}
                                    className="flex items-center gap-1"
                                >
                                    <Monitor className="h-4 w-4" />
                                    Drives
                                </BreadcrumbLink>
                            </BreadcrumbItem>
                            {pathParts.map((part, index) => {
                                const pathToHere = pathParts.slice(0, index + 1).join('\\');
                                const fullPath = index === 0 && currentPath.includes(':')
                                    ? part + '\\'
                                    : pathToHere;
                                return (
                                    <span key={index} className="contents">
                                        <BreadcrumbSeparator />
                                        <BreadcrumbItem>
                                            <BreadcrumbLink
                                                href="#"
                                                onClick={(e) => { e.preventDefault(); loadFolder(fullPath); }}
                                            >
                                                {part}
                                            </BreadcrumbLink>
                                        </BreadcrumbItem>
                                    </span>
                                );
                            })}
                        </BreadcrumbList>
                    </Breadcrumb>
                </div>

                {/* Folder List */}
                <ScrollArea className="flex-1 min-h-0">
                    <div className="space-y-2 pr-4">
                        {loading && (
                            <div className="text-center py-8 text-muted-foreground">
                                Loading folders...
                            </div>
                        )}

                        {error && (
                            <div className="text-center py-8 text-destructive">
                                ⚠️ {error}
                            </div>
                        )}

                        {!loading && !error && (
                            <>
                                {parentPath && (
                                    <button
                                        onClick={() => loadFolder(parentPath)}
                                        className="w-full flex items-center gap-3 p-3 rounded-lg bg-muted/30 hover:bg-muted/50 transition-colors border-l-2 border-primary"
                                    >
                                        <ArrowUp className="h-5 w-5 text-primary" />
                                        <div className="text-left">
                                            <div className="font-medium">..</div>
                                            <div className="text-sm text-muted-foreground">Go to parent folder</div>
                                        </div>
                                    </button>
                                )}

                                {directories.map((dir) => (
                                    <button
                                        key={dir.path}
                                        onClick={() => loadFolder(dir.path)}
                                        className={`w-full flex items-center gap-3 p-3 rounded-lg transition-all hover:translate-x-1 ${dir.is_course_candidate
                                            ? 'bg-green-500/10 border-l-2 border-green-500 hover:bg-green-500/20'
                                            : 'bg-muted/30 hover:bg-muted/50 border-l-2 border-transparent'
                                            }`}
                                    >
                                        {dir.is_course_candidate ? (
                                            <BookOpen className="h-5 w-5 text-green-500" />
                                        ) : (
                                            <Folder className="h-5 w-5 text-muted-foreground" />
                                        )}
                                        <div className="flex-1 text-left">
                                            <div className="font-medium">{dir.name}</div>
                                            {dir.media_files > 0 && (
                                                <div className="text-sm text-muted-foreground">
                                                    {dir.media_files} media file{dir.media_files > 1 ? 's' : ''}
                                                </div>
                                            )}
                                        </div>
                                        {dir.is_course_candidate && (
                                            <Badge variant="secondary" className="bg-green-500/20 text-green-400">
                                                Course
                                            </Badge>
                                        )}
                                    </button>
                                ))}

                                {directories.length === 0 && !parentPath && (
                                    <div className="text-center py-8 text-muted-foreground">
                                        No folders found
                                    </div>
                                )}
                            </>
                        )}
                    </div>
                </ScrollArea>

                {/* Footer with two load options */}
                <DialogFooter className="flex-col gap-3 border-t pt-4 sm:flex-col">
                    <code className="text-sm text-muted-foreground truncate w-full text-center">
                        {currentPath || 'Select a folder'}
                    </code>

                    <div className="flex gap-3 w-full">
                        <Button
                            onClick={handleSelectAsCourse}
                            disabled={!canSelect || loadingCourse !== null}
                            variant="default"
                            className="flex-1 gap-2"
                        >
                            <BookOpen className="h-4 w-4" />
                            {loadingCourse === 'course' ? 'Loading...' : 'Load as Course'}
                        </Button>
                        <Button
                            onClick={handleSelectAsLearningPath}
                            disabled={!canSelect || loadingCourse !== null}
                            variant="secondary"
                            className="flex-1 gap-2 bg-purple-600 hover:bg-purple-700 text-white"
                        >
                            <Library className="h-4 w-4" />
                            {loadingCourse === 'learning_path' ? 'Loading...' : 'Load as Learning Path'}
                        </Button>
                    </div>

                    <p className="text-xs text-muted-foreground text-center">
                        <strong>Course:</strong> Single folder with lessons &nbsp;|&nbsp;
                        <strong>Learning Path:</strong> Folder with multiple sub-courses
                    </p>
                </DialogFooter>
            </DialogContent>
        </Dialog>
    );
}
