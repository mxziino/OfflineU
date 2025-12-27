# OfflineU - Project Documentation

## 📋 Overview

**OfflineU** is a self-hosted web application for viewing and tracking offline video, audio, and text-based training courses. It transforms any folder of course content into a fully navigable dashboard with automatic progress tracking—completely offline and private.

---

## 🏗️ Project Structure

```
OfflineU/
├── offlineu_core.py          # Main entry point & CLI
├── requirements.txt          # Python dependencies
├── Dockerfile               # Docker containerization
├── docker-compose.yml       # Docker orchestration
│
├── offilineu/               # Core application package
│   ├── __init__.py          # Flask app factory (Setup.create_app)
│   ├── config.py            # Configuration (SECRET_KEY, env vars)
│   │
│   ├── models/              # Data structures
│   │   ├── course.py        # Course dataclass (name, path, root_node, progress)
│   │   ├── lesson.py        # Lesson dataclass (video/audio/text files, progress)
│   │   └── directory_node.py # Tree structure node for directories
│   │
│   ├── routes/              # Flask blueprints (API endpoints)
│   │   ├── browse_routes.py    # /browse, /load_course - file system navigation
│   │   ├── dashboard_routes.py # / - main dashboard view
│   │   ├── files_routes.py     # /files/<path> - static file serving
│   │   ├── lesson_routes.py    # /lesson/<path> - lesson viewing
│   │   └── progress_routes.py  # /api/progress - progress updates
│   │
│   ├── services/            # Business logic
│   │   ├── dynamic_course_parser.py  # Scans folders → Course tree
│   │   ├── lesson_service.py         # Lesson retrieval helpers
│   │   └── progress_tracker.py       # JSON-based progress persistence
│   │
│   ├── templates/           # Jinja2 HTML templates
│   │   ├── select_course.html    # Course folder browser
│   │   ├── course_dashboard.html # Main course view
│   │   └── lesson_view.html      # Media/content player
│   │
│   └── utils/               # Utilities
│       ├── current_course.py      # Global course state
│       ├── supported_extensions.py # File type definitions
│       └── create_templates.py    # Template generator
│
└── templates/               # Duplicate templates (root level)
```

---

## 🔧 Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Backend** | Python 3.x + Flask 3.1.1 | Web server & API |
| **Templating** | Jinja2 | Dynamic HTML rendering |
| **Data Storage** | JSON (`.offlineu_progress.json`) | Local progress persistence |
| **Frontend** | Vanilla HTML/CSS/JS | Simple, zero-build UI |
| **Containerization** | Docker + Compose | Deployment options |

### Key Dependencies
- `flask==3.1.1` - Web framework
- `werkzeug==3.1.3` - WSGI utilities
- `jinja2==3.1.6` - Template engine

---

## 📁 Supported File Types

| Category | Extensions |
|----------|------------|
| **Video** | `.mp4`, `.mkv`, `.avi`, `.mov`, `.webm`, `.m4v`, `.flv`, `.wmv` |
| **Audio** | `.mp3`, `.wav`, `.m4a`, `.aac`, `.ogg`, `.flac` |
| **Subtitles** | `.srt`, `.vtt`, `.ass`, `.sub`, `.sbv` |
| **Documents** | `.txt`, `.md`, `.html`, `.htm`, `.pdf`, `.docx`, `.doc`, `.rtf` |
| **Quizzes** | Auto-detected by keywords: `quiz`, `exam`, `test`, `assessment`, etc. |

---

## 🔄 Core Workflow

1. **Startup**: `offlineu_core.py` initializes Flask app
2. **Course Selection**: User browses filesystem via `/browse` endpoint
3. **Parsing**: `DynamicCourseParser` scans selected folder → builds tree structure
4. **Dashboard**: Renders navigable course view with progress bar
5. **Lesson View**: Serves media player with auto-resume capability
6. **Progress Tracking**: Updates saved to `.offlineu_progress.json` in course folder

---

## 🚀 Best Improvements & Quality of Life Features

### 🔴 High Priority (User-Identified Pain Points)

| Feature | Description | Benefit |
|---------|-------------|---------|
| **🎨 Modern UI/UX Overhaul** | Replace basic styling with modern design (gradients, animations, cards, better typography) | Professional look, user engagement |
| **📂 Visual Folder Picker** | Native folder browser instead of pasting paths - click to navigate, select course folder | Easier course import, no copy/paste |
| **✅ Manual Lesson Completion** | "Mark as Complete" button for any lesson regardless of file states | Control over progress tracking |
| **🗂️ File Exclusion System** | Allow marking files as "not part of lesson" (extras, resources, etc.) | Accurate completion tracking |
| **📦 Multi-File Lesson Handling** | Smart grouping of related files, single completion for lesson bundle | Less clicking, intuitive progress |
| **Dark/Light Theme Toggle** | Add CSS theme switcher with localStorage persistence | User comfort, accessibility |
| **Search & Filter** | Global search across lessons, filter by type/completion | Navigation in large courses |
| **Keyboard Shortcuts** | `J/K` navigation, `Space` play/pause, `M` mark complete | Power user efficiency |
| **Mobile Responsive Design** | CSS media queries for tablet/phone layouts | Cross-device usage |
| **Playback Speed Control** | 0.5x - 2x video/audio speed | Faster learning |

#### 📋 Detailed Pain Point Solutions

**1. Visual Folder Picker**
- Replace text input with file browser dialog
- Show folder tree with expandable directories
- Highlight folders that contain media files (potential courses)
- "Select This Folder" button when in valid course directory

**2. Lesson Completion Control**
- Add "Mark Complete" / "Mark Incomplete" toggle button in lesson view
- Override automatic completion detection
- Save manual overrides to progress file

**3. File Management in Lessons**
- Show all files in lesson folder
- Checkboxes to mark "required" vs "supplementary" files
- Only required files count toward completion
- Option to hide non-essential files from view

### 🟡 Medium Priority

| Feature | Description | Benefit |
|---------|-------------|---------|
| **Multi-Course Management** | Library view showing all loaded courses with stats | Manage multiple courses |
| **Notes & Bookmarks** | Per-lesson notes saved to progress file | Active learning support |
| **Subtitle Integration** | Auto-load matching .srt/.vtt files | Accessibility |
| **Progress Export/Import** | JSON export for backup, cross-device sync | Data portability |
| **Watch Time Statistics** | Dashboard showing total time spent, daily streaks | Motivation/gamification |

### 🟢 Nice to Have

| Feature | Description | Benefit |
|---------|-------------|---------|
| **Multi-User Profiles** | Separate progress tracking per user | Family/team use |
| **Quiz Interactivity** | Parse and render interactive HTML quizzes | Engagement |
| **Auto-Advance** | Option to auto-play next lesson after completion | Binge-learning |
| **Thumbnail Generation** | FFmpeg-based video thumbnails | Visual navigation |
| **REST API Documentation** | OpenAPI/Swagger spec | Developer extensibility |

---

## 🛠️ Technical Improvements

### Code Quality
- [ ] Add type hints throughout codebase
- [ ] Implement proper error handling with user-friendly messages
- [ ] Add logging configuration (replace `print()` statements)
- [ ] Write unit tests for `DynamicCourseParser` and `ProgressTracker`

### Performance
- [ ] Async file scanning for large directories
- [ ] Lazy loading of subdirectories in browser
- [ ] Video streaming with range request support
- [ ] Cache parsed course structure in memory

### Security
- [ ] Sanitize file paths to prevent directory traversal
- [ ] Add CSRF protection
- [ ] Implement rate limiting on API endpoints
- [ ] Generate randomized SECRET_KEY on first run

### Architecture
- [ ] Separate frontend into dedicated static files (SPA-ready)
- [ ] Add WebSocket support for real-time progress sync
- [ ] Implement SQLite option for larger course libraries
- [ ] Create plugin system for custom content types

---

## 📝 Current Roadmap (from README)

- [x] Base function and testing
- [ ] Multi-user profile support
- [ ] Dark/light theme switcher
- [ ] Built-in quiz interactivity
- [ ] Import/export course metadata
- [ ] Mobile app wrapper
- [ ] Self hosted Docker Deployment

---

## 🚀 Quick Start

```bash
# Clone and install
git clone https://github.com/WhiskeyCoder/OfflineU.git
cd OfflineU
pip install -r requirements.txt

# Run
python offlineu_core.py --create-templates

# With specific course
python offlineu_core.py /path/to/your/course
```

**Access**: `http://127.0.0.1:5000`

---

## 📄 License

MIT License - Use freely, modify locally, share widely.

---

*Documentation generated on 2025-12-25*
