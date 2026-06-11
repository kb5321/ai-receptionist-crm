# AI Receptionist CRM Platform

A cloud-hosted customer engagement and workflow automation platform built with **FastAPI**, **PostgreSQL**, **OpenAI**, **RingCentral**, **Docker**, and **GitHub Actions**.

The platform combines conversational AI, customer relationship management (CRM), appointment tracking, SMS communication, and workflow automation into a unified business application.

---

# Overview

AI Receptionist CRM transforms customer conversations into structured business workflows.

The system captures leads, manages appointments, maintains client profiles, automates SMS communication, and supports AI-assisted customer engagement through OpenAI integration.

This project serves both as a production-oriented business platform and a software engineering portfolio project focused on modern backend development, cloud deployment, testing, containerization, and AI integration.

---

# Features

## CRM

* Lead Management
* Client Managements
* Appointment Tracking
* Client Notes
* SMS History

## AI Receptionist

* Conversational AI
* Lead Qualification
* Service Request Capture
* Customer Engagement Workflows
* Semantic Information Extraction

## Communications

* SMS Messaging via RingCentral
* Appointment Reminders
* Follow-Up Messaging
* Message Status Tracking

## Security

* User Authentication
* Role-Based Access Control
* Password Hashing
* Audit Logging

## Platform

* Docker Container Support
* Docker Compose Support
* PostgreSQL Database
* GitHub Actions CI/CD

---

# Technology Stack

## Backend

* Python
* FastAPI
* PostgreSQL

## AI

* OpenAI API
* Conversational AI
* Semantic Information Extraction

## Communications

* RingCentral SMS API

## DevOps

* Docker
* Docker Compose
* GitHub Actions
* Git
* Ubuntu (WSL2)

## Testing

* Pytest
* Unit Testing
* Integration Testing

---

# Architecture

```text
Customer
    ↓
AI Receptionist
    ↓
FastAPI API Layer
    ↓
Service Layer
    ↓
PostgreSQL

External Services:
    • OpenAI API
    • RingCentral SMS

Deployment:
    • Docker
    • Docker Compose
    • Azure (planned)
```

---

# Automated Testing

Current status:

* 51+ automated tests
* 75% code coverage

Test categories:

* Unit Tests
* Integration Tests
* Authentication Tests
* Authorization Tests
* Service Layer Tests
* API Route Tests

---

# Project Status

Active development.

## Completed Modules

* CRM Core
* User Management
* Security & Roles
* Audit Logging
* SMS Integration
* Docker Deployment
* GitHub Repository
* Automated Testing

## Current Focus

* Documentation
* Architecture Improvements
* Front-End Modernization
* Cloud Deployment

---

# Running Locally

## Build and Start

```bash
docker compose up --build
```

## Application URL

```text
http://127.0.0.1:8000
```

## Useful Endpoints

```text
/health
/admin/login
/admin/clients
/admin/leads
/admin/appointments
```

---

# Environment Variables

Create a `.env` file containing:

```env
DATABASE_URL=your_database_url
OPENAI_API_KEY=your_openai_api_key
TEST_SMS_TO_NUMBER=your_test_phone_number
```

Additional RingCentral credentials may also be required.

---

# Roadmap

## Phase 1

* CRM Core
* AI Receptionist
* SMS Integration

## Phase 2

* Modern React Front-End
* Enhanced Reporting
* Improved Dashboard UX

## Phase 3

* Voice AI Receptionist
* Call Transcription
* Semantic Client Profiles

## Phase 4

* Multi-Location SaaS Platform
* SpaRes AI

---

# Author

**Kouider Bakhti**

Senior Software Engineer | Cloud, Distributed Systems & AI-Powered Applications

LinkedIn:
linkedin.com/in/kouiderbakhti

GitHub:
github.com/kb5321
