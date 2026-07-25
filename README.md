# AI Business Assistant Platform

> Enterprise AI platform for customer engagement, CRM, workflow automation, and intelligent communication.

---

## Version

**2.0.0**


---

## Mission

Build an AI-powered business platform that helps service-based organizations automate customer engagement, customer relationship management, communications, scheduling, and business workflows through secure, scalable, and intelligent software.

---

## Vision

The AI Business Assistant Platform is designed to evolve into a reusable business automation platform for service-based businesses.

Rather than solving a single business problem, the platform provides a foundation that can support CRM, AI Receptionists, appointment scheduling, messaging, reporting, analytics, voice AI, and future SaaS capabilities.

Every feature is engineered with long-term scalability, maintainability, and customer value in mind.

---

# Product Philosophy

Every engineering decision is evaluated using two guiding principles:

> **Is this good engineering?**

> **Does this make the product more valuable?**

These principles drive every architectural decision, code review, feature implementation, and product enhancement.

---

# Overview

The AI Business Assistant Platform transforms customer conversations into structured business workflows.

Current capabilities include:

- AI Receptionist
- Customer Relationship Management (CRM)
- Appointment Tracking
- Client Management
- SMS Communication
- Workflow Automation
- AI-assisted Customer Engagement

The platform combines conversational AI with enterprise backend architecture to automate customer interactions while maintaining structured business records and operational workflows.

This repository serves both as a production-oriented business platform and as a software engineering portfolio demonstrating modern Python backend development, cloud deployment, testing, DevOps, and AI integration.

---

# Screenshots

## Login Page

Administrator login.

![Login](screenshots/01-login-page.png)

---

## Dashboard

Administrative overview of the platform.

![Dashboard](screenshots/02-dashboard.png)

---

## AI Receptionist

Conversational AI capable of:

- Multi-turn conversations
- Customer engagement
- Lead qualification
- Structured data extraction
- CRM automation

![Chat](screenshots/03-ai-receptionist-chat.png)

---

## Lead Management

Manage customer leads captured by AI conversations.

![Leads](screenshots/04-leads.png)

---

## Appointment Management

Scheduling and appointment tracking.

![Appointments](screenshots/05-appointments.png)

---

## Client Management

Centralized customer database.

![Clients](screenshots/06-clients.png)

---

## Client Profile

Customer profile including:

- Contact Information
- Appointments
- SMS History
- Internal Notes

![Client Profile](screenshots/07-client-profile-overview.png)

---

## Conversation History

Persistent AI conversation history.

![Conversation History](screenshots/08-conversation-history.png)

---

## SMS Message Center

RingCentral SMS integration.

![SMS](screenshots/09-sms-messages.png)

---

# Features

## CRM

- Lead Management
- Client Management
- Appointment Tracking
- Client Notes
- SMS History

---

## AI Receptionist

- Conversational AI
- Lead Qualification
- Business Workflow Automation
- Semantic Information Extraction
- Customer Engagement

---

## Communications

- RingCentral SMS
- Appointment Reminders
- Follow-up Messaging
- Delivery Status Tracking

---

## Security

- User Authentication
- Role-Based Access Control
- Password Hashing
- Audit Logging

---

## Platform

- Docker
- Docker Compose
- PostgreSQL
- GitHub Actions
- Azure Deployment

---

# Technology Stack

## Backend

- Python
- FastAPI
- PostgreSQL

## Artificial Intelligence

- OpenAI API
- Conversational AI
- Semantic Information Extraction

## Communications

- RingCentral SMS API

## DevOps

- Docker
- Docker Compose
- GitHub Actions
- Git
- Ubuntu (WSL2)
- Microsoft Azure

## Testing

- Pytest
- Unit Testing
- Integration Testing

Run all tests:

```bash
pytest
```

Coverage report:

```bash
pytest --cov=. --cov-report=term-missing
```

---

# Architecture

```
                     Web Interface
                           │
          ┌────────────────┴────────────────┐
          │                                 │
   AI Receptionist API              Admin Portal
          │                                 │
          └────────────────┬────────────────┘
                           │
                     FastAPI Backend
                           │
                     Service Layer
          ┌──────────────┬──────────────┐
          │              │              │
      Repository     AI Service     SMS Service
          │              │              │
     PostgreSQL      OpenAI API   RingCentral
```

Detailed architecture:

```
docs/ARCHITECTURE.md
```

---

# Project Structure

```
app/
docs/
tests/
screenshots/

Dockerfile
docker-compose.yml
README.md
requirements.txt
```

---

# Automated Testing

Current Status

- 51+ Automated Tests
- 75% Code Coverage

Test Categories

- Unit Tests
- Integration Tests
- Authentication Tests
- Authorization Tests
- Service Layer Tests
- API Tests

---

# Running Locally

Start the application:

```bash
docker compose up --build
```

Application URL

```
http://127.0.0.1:8000
```

Useful Endpoints

```
/health
/admin/login
/admin/clients
/admin/leads
/admin/appointments
/admin/sms
```

---

# Environment Variables

Create a `.env` file:

```env
DATABASE_URL=
OPENAI_API_KEY=
TEST_SMS_TO_NUMBER=
```

Additional RingCentral credentials are also required.

---

# Engineering Principles

This project follows professional software engineering practices including:

- Clean Architecture
- Separation of Concerns
- SOLID Principles
- Secure-by-Design
- Test-Driven Development (where practical)
- Continuous Refactoring
- Documentation-Driven Development
- Cloud-Native Deployment
- Continuous Improvement

---

# Engineering Documentation

Additional documentation is available in the `docs` folder.

- PRODUCT_VISION.md
- ENGINEERING_CHARTER.md
- ROADMAP.md
- ARCHITECTURE.md
- API_GUIDE.md
- CODING_STANDARDS.md
- RELEASE_NOTES.md

---

# Roadmap

## Version 2.x

- React Front-End
- Enhanced Dashboard
- Reporting & Analytics
- Voice AI
- AI Knowledge Base

---

## Version 3.x

- Multi-Tenant SaaS
- Subscription Management
- Organization Management
- Customer Portal
- White-Label Platform

---

# Author

**Kouider Bakhti**

Software Engineer | Cloud | AI | Distributed Systems

GitHub

```
https://github.com/kb5321
```

LinkedIn

```
https://linkedin.com/in/kouiderbakhti
```

---

# Final Thought

The AI Business Assistant Platform is more than a software application.

It is an engineering journey, a continuously evolving software platform, and a demonstration of professional software engineering principles applied to real business problems.

Every release aims to improve both the product and the engineer building it.