from app.models import db
from app import create_app


app = create_app("ProductionConfig")


# Create the table
with app.app_context():
    # db.drop_all()
    db.create_all()


if __name__ == "__main__":
    app.run(debug=True)

# seeding database
# curl -X POST http://127.0.0.1:5000/fakedata/seed-database
