import os
import logging
from flask import Flask, jsonify
from flask_cors import CORS
from models.base import db
from routes.courses import bp as courses_bp
from routes.billing import bp as billing_bp
from routes.webhooks import bp as webhooks_bp
from routes.auth import bp as auth_bp
from routes.auth_cookie import bp as auth_cookie_bp
from routes.badges import bp as badges_bp
from routes.gamification import bp as gam_bp
from routes.admin import bp as admin_bp
from config import Config
from flask_caching import Cache
from flask_mail import Mail
from flask_babel import Babel
from dotenv import load_dotenv
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger = logging.getLogger("stemquest")

dsn = os.getenv("SENTRY_DSN")
if dsn:
    sentry_sdk.init(dsn=dsn, integrations=[FlaskIntegration()], traces_sample_rate=0.1)

cache = Cache()
mail = Mail()
babel = Babel()

def create_app():
    app = Flask(__name__, static_folder=None)
    app.config.from_object(Config)
    CORS(app, supports_credentials=True, origins=[app.config.get("FRONTEND_BASE")])
    db.init_app(app)
    cache.init_app(app)
    mail.init_app(app)
    babel.init_app(app)
    app.register_blueprint(auth_bp)
    app.register_blueprint(auth_cookie_bp)
    app.register_blueprint(courses_bp)
    app.register_blueprint(billing_bp)
    app.register_blueprint(webhooks_bp)
    app.register_blueprint(badges_bp)
    app.register_blueprint(gam_bp)
    app.register_blueprint(admin_bp)
    @app.route("/healthz")
    def health():
        return jsonify({"status":"ok"}), 200
    return app

app = create_app()

if __name__ == "__main__":
    port = int(os.getenv("PORT", "10000"))
    debug = os.getenv("FLASK_ENV", "production") != "production"
    app.run(host="0.0.0.0", port=port, debug=debug)
