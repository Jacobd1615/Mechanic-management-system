# 🔧 Mechanic Shop Management API

[![Build Status](https://github.com/Jacobd1615/Mechanic-management-system/actions/workflows/main.yaml/badge.svg)](https://github.com/Jacobd1615/Mechanic-management-system/actions)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/flask-3.1.1-green.svg)](https://flask.palletsprojects.com/)
[![Tests](https://img.shields.io/badge/tests-43%2F43%20passing-brightgreen.svg)](#testing)
[![Live Demo](https://img.shields.io/badge/demo-live-success.svg)](https://mechanic-management-system.onrender.com/api/docs)

> **Created by Jacob Dyson** - Professional REST API for comprehensive mechanic shop operations management

A production-ready REST API built with Flask for managing mechanic shop operations including customers, mechanics, service tickets, and inventory. Features JWT authentication, comprehensive test coverage, and enterprise-level architecture.

## ✨ Key Features

- 🔐 **JWT Authentication** with role-based access control
- 📊 **Complete CRUD Operations** for all business entities
- 🧪 **100% Test Coverage** with 43 comprehensive tests
- 📚 **Interactive API Documentation** via Swagger UI
- 🚀 **Production Ready** with rate limiting & caching
- 🏗️ **Modular Architecture** using Flask Blueprints
- ⚡ **High Performance** with SQLAlchemy ORM
- 🔄 **CI/CD Pipeline** with automated deployment

## 🎯 Live Demo

**API Base URL:** https://mechanic-management-system.onrender.com  
**Documentation:** https://mechanic-management-system.onrender.com/api/docs

## 🚀 Quick Start

```bash
# Clone repository
git clone https://github.com/Jacobd1615/Mechanic-management-system.git
cd mechanic_shop_db

# Setup environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env  # Edit with your settings

# Run application
python flask_app.py
```

## 📋 API Endpoints

### 🔐 Authentication
- `POST /customers/login` - Customer authentication
- `POST /mechanics/login` - Mechanic authentication

### 👥 Customers
- `GET /customers/` - List all customers (Auth: Customer)
- `POST /customers/` - Create new customer
- `GET /customers/{id}` - Get customer details (Auth: Customer)
- `PUT /customers/{id}` - Update customer (Auth: Customer)
- `DELETE /customers/{id}` - Delete customer (Auth: Customer)

### 🔧 Mechanics  
- `GET /mechanics/` - List all mechanics (Auth: Mechanic)
- `POST /mechanics/` - Create new mechanic
- `GET /mechanics/{id}` - Get mechanic details (Auth: Mechanic)
- `PUT /mechanics/{id}` - Update mechanic (Auth: Mechanic)
- `DELETE /mechanics/{id}` - Delete mechanic (Auth: Mechanic)

### 🎫 Service Tickets
- `GET /service-tickets/` - List tickets (Auth: Role-based)
- `POST /service-tickets/` - Create ticket (Auth: Customer)
- `GET /service-tickets/{id}` - Get ticket details (Auth: Role-based)
- `PUT /service-tickets/{id}` - Update ticket (Auth: Role-based)

### 📦 Inventory
- `GET /inventory/` - List all parts
- `POST /inventory/` - Create part (Auth: Mechanic)
- `PUT /inventory/{id}` - Update part (Auth: Mechanic)
- `DELETE /inventory/{id}` - Delete part (Auth: Mechanic)

## 🧪 Testing

```bash
# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=app --cov-report=html

# Test specific module
python -m pytest tests/test_customer.py -v
```

**Test Results:** 43/43 tests passing ✅

## 🏗️ Architecture

```
app/
├── blueprints/           # Modular route definitions
│   ├── customers/        # Customer management
│   ├── mechanics/        # Mechanic management
│   ├── service_tickets/  # Service ticket operations
│   ├── inventory/        # Parts inventory
│   └── fakedata/         # Test data generation
├── utils/               # Utility functions
│   ├── roles.py         # JWT authentication & authorization
│   └── util.py          # Helper functions
├── models.py            # SQLAlchemy database models
├── extensions.py        # Flask extensions configuration
└── __init__.py          # Application factory

tests/                   # Comprehensive test suite
config.py               # Environment configurations
flask_app.py           # Application entry point
requirements.txt       # Python dependencies
```

## 🚀 Deployment

**Live Production:** https://mechanic-management-system.onrender.com

### Deploy to Render
1. Connect GitHub repository
2. Set environment variables
3. Deploy automatically on push

### Environment Variables for Production
```env
SQLALCHEMY_DATABASE_URI=postgresql://...
SECRET_KEY=your-production-secret
FLASK_ENV=production
```

## 👨‍� Author

**Jacob Dyson**
- GitHub: [@Jacobd1615](https://github.com/Jacobd1615)
- Project: [Mechanic Management System](https://github.com/Jacobd1615/Mechanic-management-system)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

*Built with ❤️ by Jacob Dyson*
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
