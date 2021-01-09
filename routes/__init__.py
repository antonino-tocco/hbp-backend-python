from flask import Blueprint

routes_api = Blueprint('routes', __name__)

from .search import *
from .filters import *
from .main import *