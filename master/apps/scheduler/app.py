from apps.scheduler import routes
from config import Config

from flask import Flask


app = Flask(__name__)
app.config.from_object(Config)

app.register_blueprint(routes.routes_bp)
