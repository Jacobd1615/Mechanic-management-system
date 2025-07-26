# Mechanic schemas will be defined here
import re
from marshmallow import validates, ValidationError, fields
from app.extensions import ma
from app.models import Mechanic


# Defining the Marshmallow schemas for serialization and deserialization
class MechanicSchema(ma.SQLAlchemyAutoSchema):
    password = fields.String(required=True, load_only=True)

    class Meta:
        model = Mechanic
        include_fk = True
        load_instance = True
        exclude = ("service_tickets", "labor_logs")

    @validates("email")
    def validate_email(self, value, **kwargs):
        if not re.match(r"[^@]+@[^@]+\.[^@]+", value):
            raise ValidationError("Invalid email format.")

    @validates("phone")
    def validate_phone(self, value, **kwargs):
        # US phone number format (e.g., 123-456-7890, (123) 456-7890, 1234567890)
        if not re.match(r"^\(?(\d{3})\)?[-. ]?(\d{3})[-. ]?(\d{4})$", value):
            raise ValidationError("Invalid US phone number format.")

    @validates("password")
    def validate_password(self, value, **kwargs):
        if len(value) < 8:
            raise ValidationError("Password must be at least 8 characters long.")


class MechanicUpdateSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Mechanic
        include_fk = True
        load_instance = True

    username = fields.String(dump_only=True)
    password = fields.String(load_only=True, required=False)

    @validates("email")
    def validate_email(self, value, **kwargs):
        if not re.match(r"[^@]+@[^@]+\.[^@]+", value):
            raise ValidationError("Invalid email format.")

    @validates("phone")
    def validate_phone(self, value, **kwargs):
        if not re.match(r"^\(?(\d{3})\)?[-. ]?(\d{3})[-. ]?(\d{4})$", value):
            raise ValidationError("Invalid US phone number format.")

    @validates("password")
    def validate_password(self, value, **kwargs):
        if value and len(value) < 8:
            raise ValidationError("Password must be at least 8 characters long.")


# creating an instance of the schema
mechanic_schema = MechanicSchema()
mechanics_schema = MechanicSchema(many=True)
login_schema = MechanicSchema(only=("email", "password"))
mechanic_update_schema = MechanicUpdateSchema()
