from flask import Flask

from offilineu.config import Config
from offilineu.routes.browse_routes import browse_bp
from offilineu.routes.dashboard_routes import dashboard_bp
from offilineu.routes.files_routes import files_bp
from offilineu.routes.lesson_routes import lesson_bp
from offilineu.routes.progress_routes import progress_bp
from offilineu.routes.api_routes import api_bp


class Setup:
    @staticmethod
    def create_app():
        app = Flask(__name__)
        app.config.from_object(Config)
        app.register_blueprint(browse_bp)
        app.register_blueprint(dashboard_bp)
        app.register_blueprint(lesson_bp)
        app.register_blueprint(files_bp)
        app.register_blueprint(progress_bp)
        app.register_blueprint(api_bp)  # New API routes for React frontend
        return app

create_app = Setup.create_app

