import asyncio
import threading
from icecream import ic
from time import sleep
from services import ImportService
from dependency import injector


def run_on_start(*args, **argv):
    num_retry = 0
    max_retry = 5
    try:
        import_service = injector.get(ImportService)
        if import_service is not None:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(import_service.run_import_task())
    except Exception as ex:
        ic(f"Exception importing data {ex}")
        if num_retry < max_retry:
            sleep(10)
            run_on_start()


def run_background_import():
    try:
        thread = threading.Thread(target=run_on_start())
        thread.start()
    except Exception as ex:
        ic(f'Run exception on import')
        ic(ex)


if __name__ == '__main__':
    run_background_import()