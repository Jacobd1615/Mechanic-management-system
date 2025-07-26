from app.models import db
from app import create_app


app = create_app("ProductionConfig")


# Create the table
with app.app_context():
    # db.drop_all()
    db.create_all()


# seeding database
# curl -X POST https://mechanic-management-system.onrender.com/fakedata/seed-database

# swagger
# https://mechanic-management-system.onrender.com/api/docs

