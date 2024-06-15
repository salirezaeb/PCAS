import threading

from apps.cluster import routes, cluster_manager
from config import Config

from flask import Flask


app = Flask(__name__)
app.config.from_object(Config)

app.register_blueprint(routes.routes_bp)

with app.app_context():
    thread = threading.Thread(target=cluster_manager.scrape_workers)
    thread.start()
