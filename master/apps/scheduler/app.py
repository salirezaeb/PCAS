import threading

from apps.scheduler import routes, scheduler
from config import Config

from flask import Flask


app = Flask(__name__)
app.config.from_object(Config)

app.register_blueprint(routes.routes_bp)

with app.app_context():
    thread = threading.Thread(target=scheduler.daemon)
    thread.start()
