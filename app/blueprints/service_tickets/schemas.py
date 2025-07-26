# Service ticket schemas will be defined here
import re
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from app.extensions import ma
from app.models import ServiceTicket, LaborLog
from marshmallow import fields, validates, ValidationError
from ..customers.schemas import CustomerSchema
from ..mechanics.schemas import MechanicSchema


# Defining the Marshmallow schemas for serialization and deserialization
class ServiceTicketSchema(SQLAlchemyAutoSchema):
    customer = fields.Nested(CustomerSchema, exclude=["service_tickets"])
    mechanics = fields.List(
        fields.Nested(MechanicSchema, exclude=["service_tickets", "labor_logs"])
    )
    labor_logs = fields.List(fields.Nested("LaborLogSchema"))

    class Meta:
        model = ServiceTicket
        include_fk = True
        load_instance = False
        fields = (
            "ticket_id",
            "customer_id",
            "service_date",
            "description",
            "VIN",
            "status",
            "date_created",
            "date_completed",
            "customer",
            "mechanics",
            "labor_logs",
        )

    @validates("VIN")
    def validate_vin(self, value, **kwargs):
        # Standard VIN is 17 characters, alphanumeric, no I, O, Q
        if not re.match(r"^[A-HJ-NPR-Z0-9]{17}$", value.upper()):
            raise ValidationError(
                "Invalid VIN format. Must be 17 alphanumeric characters (excluding I, O, Q)."
            )


class LaborLogSchema(SQLAlchemyAutoSchema):
    mechanic = fields.Nested(MechanicSchema, only=("id", "name"))

    class Meta:
        model = LaborLog
        include_fk = True
        load_instance = False
        fields = ("id", "hours_worked", "mechanic_id", "mechanic")


class EditTicketSchema(ma.Schema):
    add_mechanic_ids = fields.List(fields.Int(), required=False)
    remove_mechanic_ids = fields.List(fields.Int(), required=False)

    class Meta:
        fields = ("add_mechanic_ids", "remove_mechanic_ids")


# creating an instance of the schema
service_ticket_schema = ServiceTicketSchema()
service_tickets_schema = ServiceTicketSchema(many=True)
edit_service_ticket_schema = EditTicketSchema()

# Instances for the new schema
labor_log_schema = LaborLogSchema()
labor_logs_schema = LaborLogSchema(many=True)
