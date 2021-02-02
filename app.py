import threading
import nest_asyncio
from crontab import CronTab
from gevent.pywsgi import WSGIServer
from flask import Flask
from flask_cors import CORS
from flask_injector import FlaskInjector
from dependency import injector
from import_task import run_on_start

from routes import routes_api

nest_asyncio.apply()


class HBPBackend(Flask):
    def run(self, host=None, port=None, debug=None, load_dotenv=True, **options):
        super(HBPBackend, self).run(host=host, port=port, debug=debug, load_dotenv=load_dotenv, **options)


def create_app():
    app = HBPBackend(__name__)
    create_cron_tab()
    try:
        thread = threading.Thread(target=run_on_start)
        thread.start()
    except Exception as ex:
        print(f'Run exception')
        print(ex)
    return app


def create_cron_tab():
    #cron = CronTab(user='root')
    #job = cron.new(command='python import_task.py')
    #job.hour.every(6)
    #cron.write()
    pass


app = create_app()
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

FlaskInjector(app=app, injector=injector)

app.register_blueprint(routes_api)

try:
    print(f'*******************')
    print(f'RUN APP')
    print(f'*******************')
    http_server = WSGIServer(('', 5000), app)
    http_server.serve_forever()

except Exception as ex:
    print(f'*******************')
    print(f'RUN EXCEPTION {ex}')
    print(f'*******************')
