# 🔧 Mechanic Shop Database API

[![Build Status](https://github.com/Jacobd1615/Mechanic-Database-advance-/actions/workflows/main.yaml/badge.svg)](https://github.com/Jacobd1615/Mechanic-Database-advance-/actions)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/flask-3.1.1-green.svg)](https://flask.palletsprojects.com/)
[![Tests](https://img.shields.io/badge/tests-43%2F43%20passing-brightgreen.svg)](#testing)

A professional REST API for managing a mechanic shop's operations, including customers, mechanics, service tickets, and inventory management. Built with Flask and featuring comprehensive test coverage, JWT authentication, and enterprise-level architecture.

## 🚀 Features

- **Complete CRUD Operations** for all entities (Customers, Mechanics, Service Tickets, Inventory)
- **JWT Authentication & Authorization** with role-based access control
- **Comprehensive Test Suite** with 43 tests and 100% pass rate
- **API Documentation** with Swagger/OpenAPI integration
- **Rate Limiting & Caching** for production performance
- **Professional Architecture** with Blueprint-based modular design
- **CI/CD Pipeline** with GitHub Actions
- **MySQL Database** with SQLAlchemy ORM

## 📋 Table of Contents

- [Quick Start](#quick-start)
- [Installation](#installation)
- [Configuration](#configuration)
- [API Documentation](#api-documentation)
- [Testing](#testing)
- [Architecture](#architecture)
- [Deployment](#deployment)
- [Contributing](#contributing)

## ⚡ Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/Jacobd1615/Mechanic-Database-advance-.git
   cd Mechanic-Database-advance-
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure database** (see [Configuration](#configuration))

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Access the API** at `http://localhost:5000`

## 🛠 Installation

### Prerequisites

- Python 3.11 or higher
- MySQL Server 8.0+
- Git

### Step-by-Step Installation

1. **Clone and Navigate**
   ```bash
   git clone https://github.com/Jacobd1615/Mechanic-Database-advance-.git
   cd Mechanic-Database-advance-
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   ```

3. **Activate Virtual Environment**
   - **Windows:**
     ```cmd
     venv\Scripts\activate
     ```
   - **macOS/Linux:**
     ```bash
     source venv/bin/activate
     ```

4. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## ⚙️ Configuration

### Database Setup

1. **Create MySQL Database**
   ```sql
   CREATE DATABASE mechanic_db;
   CREATE USER 'mechanic_user'@'localhost' IDENTIFIED BY 'your_password';
   GRANT ALL PRIVILEGES ON mechanic_db.* TO 'mechanic_user'@'localhost';
   FLUSH PRIVILEGES;
   ```

2. **Update Configuration**
   Edit `config.py` with your database credentials:
   ```python
   SQLALCHEMY_DATABASE_URI = "mysql+pymysql://mechanic_user:your_password@localhost/mechanic_db"
   ```

### Environment Variables

Create a `.env` file in the project root:
```env
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
DATABASE_URL=mysql+pymysql://mechanic_user:your_password@localhost/mechanic_db
```

## 📚 API Documentation

### Interactive Documentation

Visit `http://localhost:5000/swagger/` for interactive API documentation.

### Authentication

All endpoints (except `/fakedata/`) require JWT authentication:

```bash
# Get JWT token (implement your auth endpoint)
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "password"}'

# Use token in requests
curl -X GET http://localhost:5000/customers \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Main Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/customers` | List all customers | ✅ |
| `POST` | `/customers` | Create new customer | ✅ |
| `GET` | `/customers/{id}` | Get customer by ID | ✅ |
| `PUT` | `/customers/{id}` | Update customer | ✅ |
| `DELETE` | `/customers/{id}` | Delete customer | ✅ |
| `GET` | `/mechanics` | List all mechanics | ✅ |
| `POST` | `/mechanics` | Create new mechanic | ✅ |
| `GET` | `/service-tickets` | List service tickets | ✅ |
| `POST` | `/service-tickets` | Create service ticket | ✅ |
| `GET` | `/inventory` | List inventory items | ✅ |
| `POST` | `/inventory` | Create inventory item | ✅ |
| `GET` | `/fakedata/customers` | Generate test data | ❌ |

### Example API Calls

**Create a Customer:**
```bash
curl -X POST http://localhost:5000/customers \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@email.com",
    "phone": "555-0123"
  }'
```

**Create a Service Ticket:**
```bash
curl -X POST http://localhost:5000/service-tickets \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "customer_id": 1,
    "mechanic_id": 1,
    "description": "Oil change and tire rotation",
    "date_created": "2024-01-15"
  }'
```

## 🧪 Testing

This project includes a comprehensive test suite with **43 tests** and **100% pass rate**.

### Run All Tests
```bash
python -m pytest tests/ -v
```

### Run Specific Test Files
```bash
# Customer tests (10 tests)
python -m unittest tests.test_customer -v

# Mechanic tests (10 tests)  
python -m unittest tests.test_mechanic -v

# Service ticket tests (9 tests)
python -m unittest tests.test_tickets -v

# Inventory tests (14 tests)
python -m unittest tests.test_inventory -v
```

### Test Coverage Breakdown

- **Customer Management:** 10 tests covering CRUD operations, validation, authentication
- **Mechanic Management:** 10 tests covering mechanic-specific operations and relationships
- **Service Tickets:** 9 tests covering complex relationships and business logic
- **Inventory Management:** 14 tests covering stock management, service ticket integration

### Test Features

- **JWT Authentication Testing:** All tests include proper authentication
- **Database Isolation:** Each test runs in isolation with fresh data
- **Error Handling:** Comprehensive validation and error scenario testing
- **Relationship Testing:** Complex database relationships thoroughly tested
- **Business Logic Validation:** Real-world business rules verified

## 🏗 Architecture

### Project Structure
```
mechanic_shop_db/
├── app/
│   ├── __init__.py              # Flask app factory
│   ├── extensions.py            # Flask extensions
│   ├── models.py               # Database models
│   ├── blueprints/
│   │   ├── customers/          # Customer management
│   │   ├── mechanics/          # Mechanic management
│   │   ├── service_tickets/    # Service ticket management
│   │   ├── inventory/          # Inventory management
│   │   └── fakedata/          # Test data generation
│   ├── utils/
│   │   ├── roles.py           # Authentication utilities
│   │   └── util.py            # Helper functions
│   └── static/
│       └── swagger.yaml       # API documentation
├── tests/                     # Comprehensive test suite
├── .github/workflows/         # CI/CD pipeline
├── requirements.txt           # Production dependencies
└── README.md                 # This file
```

### Design Patterns

- **Blueprint Architecture:** Modular, scalable route organization
- **Factory Pattern:** Flask app factory for testing and deployment flexibility
- **Repository Pattern:** Clean data access layer with SQLAlchemy
- **Schema Validation:** Marshmallow for request/response validation
- **Dependency Injection:** Centralized extension management

### Database Schema

**Core Entities:**
- **Customers:** Personal information, contact details
- **Mechanics:** Staff information, specializations, work history
- **Service Tickets:** Work orders linking customers, mechanics, and services
- **Inventory:** Parts and supplies with stock management

**Relationships:**
- Customer → Service Tickets (One-to-Many)
- Mechanic → Service Tickets (One-to-Many)
- Service Tickets ↔ Inventory (Many-to-Many via association table)

## 🚀 Deployment

### Production Deployment with Gunicorn

1. **Install production dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set environment variables:**
   ```bash
   export FLASK_ENV=production
   export SECRET_KEY=your-production-secret-key
   ```

3. **Run with Gunicorn:**
   ```bash
   gunicorn -w 4 -b 0.0.0.0:8000 app:app
   ```

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "app:app"]
```

### CI/CD Pipeline

The project includes a GitHub Actions workflow (`.github/workflows/main.yaml`) that:

1. **Builds** the application
2. **Runs all 43 tests** with coverage reporting
3. **Deploys** to production (when configured)

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch:** `git checkout -b feature/amazing-feature`
3. **Run tests:** `python -m pytest tests/ -v`
4. **Commit changes:** `git commit -m 'Add amazing feature'`
5. **Push to branch:** `git push origin feature/amazing-feature`
6. **Open a Pull Request**

### Development Guidelines

- **Write Tests:** All new features must include comprehensive tests
- **Follow PEP 8:** Use consistent Python code style
- **Document Changes:** Update README.md and API documentation
- **Test Coverage:** Maintain 100% test pass rate

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👨‍💻 Author

**Jacob Davis**
- GitHub: [@Jacobd1615](https://github.com/Jacobd1615)
- Project: [Mechanic-Database-advance-](https://github.com/Jacobd1615/Mechanic-Database-advance-)

## 🙏 Acknowledgments

- Built with Flask and SQLAlchemy
- Comprehensive testing with Python unittest
- JWT authentication with python-jose
- API documentation with Swagger UI
- Professional architecture following industry best practices

---

*This project demonstrates enterprise-level API development with comprehensive testing, professional documentation, and production-ready deployment capabilities.*
