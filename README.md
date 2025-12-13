# Project Nexus - E-Commerce Backend API

![Django](https://img.shields.io/badge/Django-5.1.4-green?style=for-the-badge&logo=django)
![DRF](https://img.shields.io/badge/DRF-3.16.1-red?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue?style=for-the-badge&logo=postgresql)
![Redis](https://img.shields.io/badge/Redis-7-red?style=for-the-badge&logo=redis)

![CI/CD](https://github.com/manuel-Igtm/alx-project-nexus/actions/workflows/ci-cd.yml/badge.svg?branch=main)
![Security Scanning](https://github.com/manuel-Igtm/alx-project-nexus/actions/workflows/security.yml/badge.svg?branch=main)
![Coverage](https://codecov.io/gh/manuel-Igtm/alx-project-nexus/branch/main/graph/badge.svg)

A powerful, secure, and scalable e-commerce backend API built with Django REST Framework. Features comprehensive security with IP tracking/blocking, interactive API documentation, and production-ready CI/CD pipelines.

## 📋 Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Quick Start](#quick-start)
- [API Documentation](#-api-documentation)
- [Security Features](#-security-features)
- [CI/CD Pipeline](#-cicd-pipeline)

---

## ✨ Features

### Core E-Commerce

- 🛍️ **Product Management** - Categories, products, variants with SKU
- 🛒 **Shopping Cart** - Guest & authenticated cart support
- 📦 **Order Management** - Full order lifecycle tracking
- 💳 **Payments** - Multi-provider support (Chapa, M-Pesa)
- 🔔 **Notifications** - Real-time order & payment updates

### Security

- 🛡️ **IP Blocking** - Automatic & manual IP blocking
- ⚡ **Rate Limiting** - Configurable rate limits per endpoint
- 🔐 **Brute Force Protection** - Auto-lockout after failed attempts
- 🛡️ **Security Dashboard** - Real-time monitoring & alerts
- 📝 **Audit Logging** - Comprehensive request logging

### Developer Experience

- 📚 **Interactive Docs** - Swagger UI & ReDoc
- 🔄 **GraphQL API** - Full GraphQL support
- 🧪 **Testing** - Comprehensive test suite
- 🐳 **Docker** - Production-ready containers
- 🚀 **CI/CD** - GitHub Actions & Jenkins pipelines

---

## 🛠️ Tech Stack

| Category | Technology |
|----------|------------|
| **Framework** | Django 5.2, Django REST Framework 3.16 |
| **Database** | PostgreSQL 16 |
| **Cache** | Redis 7 |
| **Task Queue** | Celery |
| **API Docs** | drf-yasg (Swagger/OpenAPI) |
| **GraphQL** | Graphene-Django |
| **Authentication** | JWT (SimpleJWT) |
| **Containerization** | Docker, Docker Compose |
| **CI/CD** | GitHub Actions, Jenkins |

---

## 🚀 Quick Start

### Option 1: Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/manuel-Igtm/alx-project-nexus.git
cd alx-project-nexus/project-nexus

# Start all services
docker-compose up -d

# Access the API
# Visit the API docs in your browser
xdg-open http://localhost:8000/swagger/ 2>/dev/null || echo "Open http://localhost:8000/swagger/"
```

### Option 2: Local Development

```bash
# Clone and setup
git clone https://github.com/manuel-Igtm/alx-project-nexus.git
cd alx-project-nexus/project-nexus

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env

# Run migrations
python manage.py migrate

# Start the server
python manage.py runserver
```

---

## 📚 API Documentation

| Interface | URL | Description |
|-----------|-----|-------------|
| **Swagger UI** | `/swagger/` | Interactive API explorer |
| **ReDoc** | `/redoc/` | Beautiful API reference |
| **GraphQL** | `/graphql/` | GraphQL playground |

### API Endpoints Overview

```text
📁 /api/
├── 🔐 /auth/           - Authentication
├── 🛍️ /products/        - Product CRUD
├── 📂 /categories/      - Category CRUD
├── 🛒 /carts/           - Cart management
├── 📦 /orders/          - Order management
├── 💳 /payments/        - Payment processing
├── 🔔 /notifications/   - User notifications
└── 🛡️ /security/        - Security management
```

---

## 🛡️ Security Features

### Rate Limiting

| Endpoint Type | Limit | Window |
|--------------|-------|--------|
| Default | 100 requests | 1 minute |
| Authentication | 10 requests | 1 minute |
| API endpoints | 200 requests | 1 minute |

### IP Blocking Triggers

- Rate limit exceeded (5+ violations)
- Brute force attacks (5+ failed logins)
- Suspicious request patterns

---

## 🚀 CI/CD Pipeline

### GitHub Actions

**GitHub Actions Workflows**
- **Lint & Code Quality**: Flake8, Black, isort, Bandit, Safety
- **Tests**: Pytest with coverage, Postgres + Redis services
- **Security Scan**: Dependency scanning, SAST, secrets, container scan
- **Build**: Docker image build on `main` and `develop`
- **Deploy**:
	- Staging: on `develop` (Render API)
	- Production: on `main` (Render API)

**Required Secrets (GitHub Repository → Settings → Secrets and variables → Actions)**
- `DOCKER_USERNAME`, `DOCKER_PASSWORD` — Docker Hub login (optional; enables image push)
- `RENDER_API_KEY` — Render API token
- `RENDER_STAGING_SERVICE_ID` — Render service ID for staging
- `RENDER_PRODUCTION_SERVICE_ID` — Render service ID for production
- `SLACK_WEBHOOK_URL` — Slack notifications (optional)
- `CODECOV_TOKEN` — Codecov upload (optional)

**Branch Behavior**
- Build on: `main`, `develop`
- Deploy staging: `develop`
- Deploy production: `main`

### Jenkins

Full Jenkinsfile included with parallel testing, security scanning, and deployment stages.

---

## 📄 License

This project is licensed under the MIT License.

## 👨‍💻 Author

**Manuel Igtm** - [@manuel-Igtm](https://github.com/manuel-Igtm)

## 🤝 Contributing

Contributions are welcome! Please read our [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📞 Support

For issues and questions, please open an [issue](https://github.com/manuel-Igtm/alx-project-nexus/issues) or contact the maintainer.

## 🙏 Acknowledgments

Built as part of the ALX Software Engineering Program.

## Made with ❤️ for the ALX Project Nexus