import asyncio
import nest_asyncio
import threading
from gevent.pywsgi import WSGIServer
from time import sleep
from flask import Flask
from flask_cors import CORS
from flask_injector import FlaskInjector
from helpers import import_data

from routes import routes_api
from dependency import injector

nest_asyncio.apply()


class HBPBackend(Flask):
    def run(self, host=None, port=None, debug=None, load_dotenv=True, **options):
        super(HBPBackend, self).run(host=host, port=port, debug=debug, load_dotenv=load_dotenv, **options)


def create_app():
    app = HBPBackend(__name__)
    num_retry = 0
    max_retry = 5

    def run_on_start(*args, **argv):
        try:
            import_data()
        except Exception as ex:
            print(f"Exception importing data {ex}")
            if num_retry < max_retry:
                sleep(10)
                run_on_start()

    try:
        thread = threading.Thread(target=run_on_start)
        thread.start()
    except Exception as ex:
        print(f'Run exception')
        print(ex)
    return app


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
