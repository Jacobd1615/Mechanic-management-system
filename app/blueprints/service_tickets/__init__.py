from flask import Blueprint

service_tickets_bp = Blueprint("service_tickets", __name__)

from . import routes #import routes to register them with the blueprint
