from apps.predictor import routes, cache_predictor
from config import Config

from flask import Flask


app = Flask(__name__)
app.config.from_object(Config)

app.register_blueprint(routes.routes_bp)
