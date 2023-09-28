import threading
import nest_asyncio
from gevent.pywsgi import WSGIServer
from flask import Flask, jsonify
from flask_cors import CORS
from flask_injector import FlaskInjector
from dependency import injector
from import_task import run_on_start
from flask_swagger import swagger
from flask_swagger_ui import get_swaggerui_blueprint
from icecream import ic

from routes import routes_api

nest_asyncio.apply()

SWAGGER_URL = '/apidocs'
SWAGGER_JSON = '/swagger.json'

class HBPBackend(Flask):
    def run(self, host=None, port=None, debug=None, load_dotenv=True, **options):
        super(HBPBackend, self).run(host=host, port=port, debug=debug, load_dotenv=load_dotenv, **options)


def create_app():
    app = HBPBackend(__name__, static_url_path='')
    create_cron_tab()
    try:
        thread = threading.Thread(target=run_on_start)
        thread.start()
    except Exception as ex:
        ic(f'Run exception')
        ic(ex)
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


@routes_api.route('/swagger.json', methods=['GET'])
def openapi():
    try:
        swagger_definitions = swagger(app)
        swagger_definitions['title'] = 'The HippocampusHub API Documentation'
        swagger_definitions['version'] = '1.0.0'
        swagger_definitions['info'] = {
            'title': 'The HippocampusHub API Documentation',
            'version': '1.0.0'
        }
        return jsonify(swagger_definitions)
    except Exception as ex:
        ic(f'Run swagger exception {ex}')

        

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,  # Swagger UI static files will be mapped to '{SWAGGER_URL}/dist/'
    SWAGGER_JSON,
    config={  # Swagger UI config overrides
        'app_name': "HBP Backend"
    },
)



app.register_blueprint(routes_api)
app.register_blueprint(swaggerui_blueprint)

try:
    ic(f'*******************')
    ic(f'RUN APP')
    ic(f'*******************')
    http_server = WSGIServer(('', 5000), app)
    http_server.serve_forever()

except Exception as ex:
    ic(f'*******************')
    ic(f'RUN EXCEPTION {ex}')
    ic(f'*******************')
