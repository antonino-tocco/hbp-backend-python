from . import routes_api
from io import BytesIO
from flask import request, send_file
import requests


@routes_api.route('/proxy', methods=['GET'])
def proxy():
    return None
    url = request.args.get('url')
    if url is None or url.strip() == "":
        return None
    response = requests.get(url)
    image_name = url.split('/')[-1]
    buffer_image = BytesIO(response.content)
    buffer_image.seek(0)
    return send_file(buffer_image, attachment_filename=image_name)