from flask import Flask
from helpers import import_data


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

@app.route('/')
def hello_world():
    return 'Hello World!'


if __name__ == '__main__':
    app.run()
