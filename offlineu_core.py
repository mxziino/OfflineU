#!/usr/bin/env python3
"""
OfflineU - Self-hosted Course Viewer & Tracker
Enhanced version with dynamic subdirectory navigation
"""

import argparse
import os
import sys
from pathlib import Path

from offilineu import Setup
from offilineu.services.dynamic_course_parser import DynamicCourseParser
from offilineu.utils.create_templates import CreateTemplates

app = Setup.create_app()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='OfflineU Course Viewer & Tracker')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=5000, help='Port to bind to')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--create-templates', action='store_true', help='Create basic templates')
    parser.add_argument('course_path', nargs='?', help='Path to course directory')
    args = parser.parse_args()

    # Create templates if requested
    if args.create_templates:
        CreateTemplates.create()
        print("Templates created successfully!")
        if not args.course_path:
            sys.exit(0)

    # Autoload course if provided
    if args.course_path or os.environ.get('AUTO_LOAD_COURSE'):
        course_path = args.course_path or os.environ.get('AUTO_LOAD_COURSE')

        if not os.path.exists(course_path):
            print(f"Error: Course path does not exist: {course_path}", file=sys.stderr)
            sys.exit(1)

        try:
            current_course = DynamicCourseParser.scan_directory(course_path)
            print(f"Auto-loaded course: {current_course.name}")
            print(f"Built dynamic directory tree with {len(current_course.root_node.children)} top-level items")
        except Exception as e:
            print(f"Error loading course: {e}", file=sys.stderr)
            if args.debug:
                import traceback
                traceback.print_exc()
            sys.exit(1)

    # Create templates directory if it doesn't exist
    if not Path('offilineu/templates').exists():
        print("Templates directory not found. Creating basic templates...")
        CreateTemplates.create()

    print(f"Starting OfflineU on http://{args.host}:{args.port}")
    print("Use --create-templates to regenerate template files")

    try:
        app.run(debug=args.debug, host=args.host, port=args.port)
    except KeyboardInterrupt:
        print("\nShutting down OfflineU...")
    except Exception as e:
        print(f"Error starting server: {e}")
        if args.debug:
            import traceback

            traceback.print_exc()
        sys.exit(1)
