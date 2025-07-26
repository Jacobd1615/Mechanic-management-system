from flask import Blueprint

fakedata_bp = Blueprint("fakedata", __name__)

from . import routes

