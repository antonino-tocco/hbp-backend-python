from flask import Flask
from helpers import import_data

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

app.register_blueprint(routes_api)

@app.route('/')
def hello_world():
    return 'Server up!'


if __name__ == '__main__':
    app.run()
