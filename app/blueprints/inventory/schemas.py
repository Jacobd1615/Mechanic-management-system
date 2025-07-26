# Inventory schemas will be defined here
from marshmallow import validates, ValidationError
from app.extensions import ma
from app.models import Part


# Defining the Marshmallow schemas for serialization and deserialization
class PartSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Part
        load_instance = True
        include_fk = True

    @validates("price")
    def validate_price(self, value, **kwargs):
        if value <= 0:
            raise ValidationError("Price must be greater than zero.")

    @validates("quantity_in_stock")
    def validate_quantity_in_stock(self, value, **kwargs):
        if value < 0:
            raise ValidationError("Quantity in stock cannot be negative.")


# creating an instance of the schema
part_schema = PartSchema()
parts_schema = PartSchema(many=True)