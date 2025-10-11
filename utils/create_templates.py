from pathlib import Path


class CreateTemplates:
    @staticmethod
    def create():
        """Create basic template files if they don't exist"""
        templates_dir = Path('templates')
        templates_dir.mkdir(exist_ok=True)

        # Basic select course template
        select_template = '''<!DOCTYPE html>
    <html>
    <head>
        <title>OfflineU - Select Course</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .container { max-width: 800px; margin: 0 auto; }
            .directory { padding: 10px; border: 1px solid #ddd; margin: 5px 0; cursor: pointer; }
            .directory:hover { background-color: #f0f0f0; }
            .course-candidate { background-color: #e8f5e8; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>OfflineU - Course Selection</h1>
            <div id="browser"></div>
            <script>
                // Basic directory browser implementation
                function loadDirectories(path = '') {
                    fetch(`/browse?path=${encodeURIComponent(path)}`)
                        .then(r => r.json())
                        .then(data => {
                            const browser = document.getElementById('browser');
                            browser.innerHTML = `
                                <h3>Current: ${data.current_path}</h3>
                                ${data.parent_path ? `<div class="directory" onclick="loadDirectories('${data.parent_path}')">📁 .. (Parent)</div>` : ''}
                                ${data.directories.map(dir => `
                                    <div class="directory ${dir.is_course_candidate ? 'course-candidate' : ''}" 
                                         onclick="${dir.is_course_candidate ? `loadCourse('${dir.path}')` : `loadDirectories('${dir.path}')`}">
                                        📁 ${dir.name} ${dir.media_files > 0 ? `(${dir.media_files} media files)` : ''}
                                    </div>
                                `).join('')}
                            `;
                        });
                }
    
                function loadCourse(path) {
                    fetch('/load_course', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({course_path: path})
                    })
                    .then(r => r.json())
                    .then(data => {
                        if (data.success) {
                            location.reload();
                        } else {
                            alert('Error: ' + data.error);
                        }
                    });
                }
    
                loadDirectories();
            </script>
        </div>
    </body>
    </html>'''

        # Basic course dashboard template
        dashboard_template = '''<!DOCTYPE html>
    <html>
    <head>
        <title>OfflineU - {{ course.name }}</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .container { max-width: 1200px; margin: 0 auto; }
            .module { margin: 20px 0; border: 1px solid #ddd; padding: 15px; }
            .lesson { padding: 8px; margin: 5px 0; border-left: 4px solid #ddd; }
            .lesson.completed { border-left-color: #4CAF50; background-color: #f8fff8; }
            .lesson a { text-decoration: none; color: #333; }
            .lesson:hover { background-color: #f0f0f0; }
            .progress { background-color: #f0f0f0; height: 20px; border-radius: 10px; overflow: hidden; }
            .progress-bar { background-color: #4CAF50; height: 100%; transition: width 0.3s; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>{{ course.name }}</h1>
            <div class="progress">
                <div class="progress-bar" style="width: {{ stats.completion_percentage }}%"></div>
            </div>
            <p>Progress: {{ stats.completed_lessons }}/{{ stats.total_lessons }} lessons ({{ stats.completion_percentage }}%)</p>
    
            {% for module_idx, module in course.modules|enumerate %}
            <div class="module">
                <h2>{{ module.title }}</h2>
                {% for lesson_idx, lesson in module.lessons|enumerate %}
                <div class="lesson {% if lesson.completed %}completed{% endif %}">
                    <a href="/lesson/{{ module_idx }}/{{ lesson_idx }}">
                        {{ lesson.title }} 
                        <small>({{ lesson.lesson_type }})</small>
                        {% if lesson.completed %}✓{% endif %}
                    </a>
                </div>
                {% endfor %}
            </div>
            {% endfor %}
    
            <p><a href="/reset_course">Select Different Course</a></p>
        </div>
    </body>
    </html>'''

        # Basic lesson view template
        lesson_template = '''<!DOCTYPE html>
    <html>
    <head>
        <title>{{ lesson.title }} - {{ course.name }}</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .container { max-width: 1000px; margin: 0 auto; }
            video, audio { width: 100%; max-width: 800px; }
            .content { margin: 20px 0; }
            .navigation { margin: 20px 0; }
            button { padding: 10px 20px; margin: 5px; cursor: pointer; }
            .file-link { display: block; margin: 5px 0; padding: 5px; background: #f0f0f0; text-decoration: none; color: #333; }
            .file-link:hover { background: #e0e0e0; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>{{ lesson.title }}</h1>
            <div class="navigation">
                <a href="/">← Back to Course</a>
                <button onclick="markCompleted()">Mark as Completed</button>
            </div>
    
            <div class="content">
                {% if lesson.video_file %}
                <h3>Video</h3>
                <video controls preload="metadata" id="video-player">
                    <source src="/files/{{ lesson.video_file }}" type="video/mp4">
                    {% if lesson.subtitle_file %}
                    <track kind="subtitles" src="/files/{{ lesson.subtitle_file }}" srclang="en" label="English">
                    {% endif %}
                    Your browser does not support the video tag.
                </video>
                {% endif %}
    
                {% if lesson.audio_file %}
                <h3>Audio</h3>
                <audio controls preload="metadata" id="audio-player">
                    <source src="/files/{{ lesson.audio_file }}" type="audio/mp3">
                    Your browser does not support the audio tag.
                </audio>
                {% endif %}
    
                {% if lesson.text_files %}
                <h3>Additional Resources</h3>
                {% for text_file in lesson.text_files %}
                <a href="/files/{{ text_file }}" class="file-link" target="_blank">
                    📄 {{ text_file.split('/')[-1] }}
                </a>
                {% endfor %}
                {% endif %}
            </div>
    
            <script>
                function markCompleted() {
                    fetch('/api/progress', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({
                            lesson_path: '{{ lesson_path }}',
                            completed: true,
                            progress_seconds: getProgressSeconds()
                        })
                    })
                    .then(r => r.json())
                    .then(data => {
                        if (data.success) {
                            alert('lesson.py marked as completed!');
                            window.location.href = '/';
                        }
                    });
                }
    
                function getProgressSeconds() {
                    const video = document.getElementById('video-player');
                    const audio = document.getElementById('audio-player');
                    if (video && !video.paused) return Math.floor(video.currentTime);
                    if (audio && !audio.paused) return Math.floor(audio.currentTime);
                    return 0;
                }
    
                // Auto-save progress periodically
                setInterval(() => {
                    const seconds = getProgressSeconds();
                    if (seconds > 0) {
                        fetch('/api/progress', {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify({
                                lesson_path: '{{ lesson_path }}',
                                completed: false,
                                progress_seconds: seconds
                            })
                        });
                    }
                }, 30000); // Save every 30 seconds
            </script>
        </div>
    </body>
    </html>'''

        # Write templates to files
        template_files = {
            'select_course.html': select_template,
            'course_dashboard.html': dashboard_template,
            'lesson_view.html': lesson_template
        }

        for filename, content in template_files.items():
            template_path = templates_dir / filename
            if not template_path.exists():
                with open(template_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"Created template: {template_path}")
