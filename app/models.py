# Import necessary libraries and modules
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Integer, Date, ForeignKey, Float
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from datetime import date


# Define the base model class
class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

#  Association table for many-to-many relationship between service tickets and mechanics
mechanic_association = db.Table(
    "mechanic_association",  # Explicitly name the table
    Base.metadata,
    db.Column(
        "service_ticket_id", db.Integer, db.ForeignKey("service_tickets.ticket_id")
    ),
    db.Column("mechanic_id", db.Integer, db.ForeignKey("mechanics.id")),
)

# Association table for many-to-many relationship between service tickets and parts
service_ticket_part_association = db.Table(
    "service_ticket_part_association",
    Base.metadata,
    db.Column(
        "service_ticket_id", db.Integer, db.ForeignKey("service_tickets.ticket_id")
    ),
    db.Column("part_id", db.Integer, db.ForeignKey("parts.part_id")),
)

# Define the models

# Customer model
class Customer(Base):
    __tablename__ = "customers"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(db.String(100), nullable=False)
    email: Mapped[str] = mapped_column(db.String(360), nullable=False, unique=True)
    phone: Mapped[str] = mapped_column(
        db.String(100),
        nullable=False,
    )
    password: Mapped[str] = mapped_column(db.String(255), nullable=False)
    
    # relationship with service tickets
    service_tickets: Mapped[list["ServiceTicket"]] = relationship(
        back_populates="customer"
    )


# Mechanic model
class Mechanic(Base):
    __tablename__ = "mechanics"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(db.String(100), nullable=False)
    email: Mapped[str] = mapped_column(db.String(360), nullable=False, unique=True)
    phone: Mapped[str] = mapped_column(db.String(100), nullable=False)
    password: Mapped[str] = mapped_column(db.String(255), nullable=False)
    salary: Mapped[float] = mapped_column(db.Float, nullable=False)

    # relationship with service tickets (existing)
    service_tickets: Mapped[list["ServiceTicket"]] = relationship(
        secondary=mechanic_association, back_populates="mechanics"
    )
    # relationship with labor logs (new)
    labor_logs: Mapped[list["LaborLog"]] = relationship(back_populates="mechanic")


class ServiceTicket(Base):
    __tablename__ = "service_tickets"
    ticket_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    customer_id: Mapped[int] = mapped_column(
        db.ForeignKey("customers.id"), nullable=False
    )
    service_date: Mapped[date] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(db.String(500), nullable=False)
    VIN: Mapped[str] = mapped_column(db.String(100), nullable=False, unique=True)
    status: Mapped[str] = mapped_column(db.String(50), default="Open")
    date_created: Mapped[date] = mapped_column(default=date.today)
    date_completed: Mapped[date] = mapped_column(nullable=True)

    # One-to-many relationship with customer
    customer: Mapped["Customer"] = relationship(back_populates="service_tickets")

    # Many-to-many relationship with mechanics (existing)
    mechanics: Mapped[list["Mechanic"]] = relationship(
        secondary=mechanic_association, back_populates="service_tickets"
    )
    # One-to-many relationship with labor logs (new)
    labor_logs: Mapped[list["LaborLog"]] = relationship(back_populates="ticket")
    # Many-to-many relationship with Parts
    parts: Mapped[list["Part"]] = relationship(
        secondary=service_ticket_part_association, back_populates="service_tickets"
    )


class LaborLog(Base):
    __tablename__ = "labor_logs"
    id: Mapped[int] = mapped_column(primary_key=True)
    hours_worked: Mapped[float] = mapped_column(db.Float, nullable=False)
    date_logged: Mapped[date] = mapped_column(default=date.today)

    # Foreign Keys
    ticket_id: Mapped[int] = mapped_column(
        db.ForeignKey("service_tickets.ticket_id"), nullable=False
    )
    mechanic_id: Mapped[int] = mapped_column(
        db.ForeignKey("mechanics.id"), nullable=False
    )

    # Relationships
    ticket: Mapped["ServiceTicket"] = relationship(back_populates="labor_logs")
    mechanic: Mapped["Mechanic"] = relationship(back_populates="labor_logs")


# Part model for inventory
class Part(Base):
    __tablename__ = "parts"
    part_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(db.String(100), nullable=False)
    description: Mapped[str] = mapped_column(db.String(500), nullable=True)
    price: Mapped[float] = mapped_column(db.Float, nullable=False)
    quantity_in_stock: Mapped[int] = mapped_column(db.Integer, nullable=False)

    # Many-to-many relationship with ServiceTickets
    service_tickets: Mapped[list["ServiceTicket"]] = relationship(
        secondary=service_ticket_part_association, back_populates="parts"
    )


