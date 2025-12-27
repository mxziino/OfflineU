import { useState, useEffect, useCallback } from 'react';
import { Button } from '@/components/ui/button';
import { Save, FileText, Eye, Edit3 } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

interface MarkdownEditorProps {
    initialContent: string;
    onSave: (content: string) => void;
    onContentChange?: (content: string) => void;
}

export function MarkdownEditor({ initialContent, onSave, onContentChange }: MarkdownEditorProps) {
    const [content, setContent] = useState(initialContent);
    const [isSaving, setIsSaving] = useState(false);
    const [isPreview, setIsPreview] = useState(false);

    // Update content when initialContent changes (e.g., lesson change)
    useEffect(() => {
        setContent(initialContent);
    }, [initialContent]);

    const handleContentChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
        const newContent = e.target.value;
        setContent(newContent);
        onContentChange?.(newContent);
    };

    const handleSave = useCallback(async () => {
        setIsSaving(true);
        try {
            await onSave(content);
        } finally {
            setIsSaving(false);
        }
    }, [content, onSave]);

    // Keyboard shortcut for saving (Ctrl/Cmd + S)
    useEffect(() => {
        const handleKeyDown = (e: KeyboardEvent) => {
            if ((e.ctrlKey || e.metaKey) && e.key === 's') {
                e.preventDefault();
                handleSave();
            }
        };

        document.addEventListener('keydown', handleKeyDown);
        return () => document.removeEventListener('keydown', handleKeyDown);
    }, [handleSave]);

    return (
        <div className="flex flex-col h-full">
            {/* Toolbar */}
            <div className="flex items-center justify-between p-2 border-b bg-card">
                <div className="flex items-center gap-2">
                    <FileText className="h-4 w-4 text-muted-foreground" />
                    <span className="text-sm font-medium">Lesson Notes</span>
                </div>
                <div className="flex items-center gap-2">
                    {/* Edit/Preview Toggle */}
                    <div className="flex rounded-md border">
                        <Button
                            variant={!isPreview ? 'secondary' : 'ghost'}
                            size="sm"
                            onClick={() => setIsPreview(false)}
                            className="gap-1 rounded-r-none border-0"
                        >
                            <Edit3 className="h-3 w-3" />
                            Edit
                        </Button>
                        <Button
                            variant={isPreview ? 'secondary' : 'ghost'}
                            size="sm"
                            onClick={() => setIsPreview(true)}
                            className="gap-1 rounded-l-none border-0"
                        >
                            <Eye className="h-3 w-3" />
                            Preview
                        </Button>
                    </div>
                    <Button
                        variant="outline"
                        size="sm"
                        onClick={handleSave}
                        disabled={isSaving}
                        className="gap-2"
                    >
                        <Save className="h-3 w-3" />
                        {isSaving ? 'Saving...' : 'Save (Ctrl+S)'}
                    </Button>
                </div>
            </div>

            {/* Editor / Preview */}
            {isPreview ? (
                <div className="flex-1 overflow-auto p-6 bg-background prose prose-invert max-w-none">
                    {content ? (
                        <ReactMarkdown>{content}</ReactMarkdown>
                    ) : (
                        <p className="text-muted-foreground italic">No notes yet. Switch to Edit mode to start writing.</p>
                    )}
                </div>
            ) : (
                <textarea
                    value={content}
                    onChange={handleContentChange}
                    className="flex-1 w-full p-4 bg-background border-0 resize-none focus:outline-none focus:ring-0 font-mono text-sm"
                    placeholder="Write your markdown notes here...

Examples:
# Heading
## Subheading
- Bullet point
**bold** *italic*
`code`
"
                />
            )}
        </div>
    );
}

