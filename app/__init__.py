from flask import Flask
from app.filters import fmt
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Khởi tạo db và migrate
db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config.from_object('config')  # Lấy cấu hình từ file config.py

    # Khởi tạo db và migrate
    db.init_app(app)
    migrate.init_app(app, db)

    app.jinja_env.filters["fmt"] = fmt  # Đăng ký filter fmt

    # Đăng ký các blueprint
    from .routes.dashboard import dashboard_bp
    from .routes.expenses import expenses_bp
    from .routes.budget import budget_bp
    from .routes.analytics import analytics_bp
    from .routes.savings import savings_bp

    app.register_blueprint(dashboard_bp)
    app.register_blueprint(expenses_bp)
    app.register_blueprint(budget_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(savings_bp)
    

    return app
