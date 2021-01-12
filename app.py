import asyncio
import nest_asyncio
import concurrent
from flask import Flask
from flask_cors import CORS, cross_origin
from flask_injector import FlaskInjector
from helpers import import_data
from threading import Timer

from routes import routes_api
from dependency import injector

nest_asyncio.apply()


class HBPBackend(Flask):
    def run(self, host=None, port=None, debug=None, load_dotenv=True, **options):
        super(HBPBackend, self).run(host=host, port=port, debug=debug, load_dotenv=load_dotenv, **options)


def create_app():
    app = HBPBackend(__name__)

    async def run_on_start(*args, **argv):
        t = Timer(30.0, lambda _ : await import_data())
        t.start()
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(run_on_start())
    except Exception as ex:
        print(f'Run exception')
        print(ex)
    return app

app = create_app()
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

FlaskInjector(app=app, injector=injector)

app.register_blueprint(routes_api)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
