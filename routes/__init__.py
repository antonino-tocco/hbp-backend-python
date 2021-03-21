from flask import Blueprint

routes_api = Blueprint('routes', __name__)

from .auth import *
from .search import *
from .filters import *
from .main import *
from .proxy import *
from .download import *