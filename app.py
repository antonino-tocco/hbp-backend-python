from flask import Flask
from flask_injector import FlaskInjector
from injector import inject
from helpers import import_data
from dependencies import configure

from routes import routes_api


class HBPBackend(Flask):
    def run(self, *args):
        super(HBPBackend, self).run(*args)


def create_app():
    app = HBPBackend(__name__)
    def run_on_start(*args, **argv):
        import_data()
    run_on_start()
    return app

app = create_app()

FlaskInjector(app=app, modules=[configure])

app.register_blueprint(routes_api)

@app.route('/')
def hello_world():
    return 'Server up!'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
