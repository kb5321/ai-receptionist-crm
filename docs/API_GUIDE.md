# API Guide

**Version:** 2.0  
**Last Updated:** July 27, 2026  
**Purpose:** Provide developers with a comprehensive reference for integrating with the AI Business Assistant Platform APIs.

---

# 1. API Overview

The AI Business Assistant Platform exposes RESTful APIs that enable intelligent customer engagement, CRM management, AI-powered conversations, SMS communications, and administrative operations.

The APIs are designed around modern REST principles, exchanging data using JSON and providing predictable, secure, and developer-friendly interfaces.

---

# 2. API Design Principles

The platform follows several API design principles.

## RESTful Design

Endpoints are organized around business resources and operations using standard HTTP methods.

## Stateless Communication

Each request contains all information necessary to complete the operation.

## JSON Communication

Requests and responses use JSON whenever applicable.

## Predictable Responses

APIs return consistent response formats and HTTP status codes.

## Secure by Default

Administrative endpoints require authentication and authorization.

## Backward Compatibility

Future API versions will evolve without unnecessarily breaking existing integrations.

---

# 3. Authentication

Administrative endpoints require authentication.

Current authentication is session-based using secure HTTP cookies.

Example login flow:

```
Administrator
        │
        ▼
POST /admin/login
        │
        ▼
Credentials Validated
        │
        ▼
Session Cookie Created
        │
        ▼
Access Granted
```

Future authentication options may include:

- JWT Tokens
- OAuth 2.0
- API Keys
- Service Accounts

---

# 4. Base URLs

## Development

```
http://localhost:8000
```

## Future Production

```
https://api.aibusinessassistant.com
```

---

# 5. Request Format

Requests should include appropriate HTTP headers.

Example:

```http
Content-Type: application/json
```

Example request body:

```json
{
    "client_name": "John Smith",
    "phone": "2105551234"
}
```

---

# 6. Response Format

Successful requests return JSON.

Example:

```json
{
    "success": true,
    "message": "Operation completed successfully."
}
```

---

# 7. HTTP Status Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 201 | Resource Created |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Resource Not Found |
| 422 | Validation Error |
| 500 | Internal Server Error |

---

# 8. Error Responses

Example:

```json
{
    "success": false,
    "error": "Phone number is required."
}
```

Error messages should be descriptive while avoiding disclosure of internal implementation details.

---

# 9. Public API Endpoints

## Health Check

### GET /health

Returns the health status of the platform.

Example Response

```json
{
    "status": "healthy",
    "database": "connected",
    "openai": "configured"
}
```

---

## Conversational AI

### POST /ask

Processes customer conversations through the Conversational AI.

### Request

```json
{
    "session_id": "abc123",
    "question": "I'd like to schedule a massage appointment."
}
```

### Response

```json
{
    "response": "I'd be happy to help schedule your appointment.",
    "lead_saved": false
}
```

### Features

- Multi-turn conversations
- Conversation history
- Intent detection
- Information extraction
- Lead creation
- Context awareness

---

## Leads

### POST /leads

Creates a CRM lead.

### GET /leads

Returns all leads.

---

## Appointments

### GET /appointments

Returns appointment records.

---

## Clients

### GET /clients

Returns client records.

---

# 10. Administrative Endpoints

Administrative endpoints require authentication.

Examples:

```
GET  /admin/login

POST /admin/login

GET  /admin/logout

GET  /admin/leads

GET  /admin/clients

GET  /admin/appointments

GET  /admin/sms
```

Administrative users can:

- Manage clients
- Review leads
- Send SMS
- View appointments
- View reporting dashboards

---

# 11. SMS API

## Send SMS

```
POST /clients/{client_id}/send-sms
```

Purpose:

Send an SMS message to an existing client.

Workflow

```
Administrator
        │
        ▼
Client Profile
        │
        ▼
Send SMS
        │
        ▼
RingCentral API
        │
        ▼
SMS Delivered
        │
        ▼
Message Logged
```

Each SMS record includes:

- Client ID
- Phone Number
- Message
- Status
- Direction
- Timestamp
- RingCentral Message ID

---

# 12. AI Workflow

```
Customer
        │
POST /ask
        │
        ▼
Conversation History
        │
        ▼
OpenAI Processing
        │
        ▼
Intent Detection
        │
        ▼
Information Extraction
        │
        ▼
Validation
        │
        ▼
Lead Creation
        │
        ▼
CRM Workflow
```

The Conversational AI supports:

- Multi-turn conversations
- Context retention
- Booking detection
- Lead generation
- Customer information collection
- Workflow automation

---

# 13. API Conventions

The API follows these conventions.

## Resource Naming

Use plural nouns.

Examples:

```
/clients
/leads
/appointments
```

---

## HTTP Methods

| Method | Purpose |
|---------|----------|
| GET | Retrieve resources |
| POST | Create resources |
| PUT | Update resources |
| DELETE | Remove resources |

---

## JSON Naming

Use lowercase snake_case field names.

Example:

```json
{
    "client_name": "John Smith",
    "preferred_time": "Afternoon"
}
```

---

# 14. Example Business Workflow

```
Customer

↓

POST /ask

↓

AI detects booking request

↓

Lead created

↓

Administrator reviews lead

↓

POST /clients/{client_id}/send-sms

↓

Customer receives confirmation
```

---

# 15. Future API Versioning

Current Version

```
POST /ask

GET /clients
```

Future Version

```
POST /api/v1/chat

GET /api/v1/clients

POST /api/v1/leads

GET /api/v1/appointments

POST /api/v1/sms
```

Introducing versioned APIs will allow future enhancements while maintaining compatibility with existing integrations.

---

# 16. Best Practices

Developers integrating with the platform should:

- Validate input before sending requests.
- Handle HTTP errors gracefully.
- Use HTTPS in production.
- Respect authentication requirements.
- Keep integrations stateless.
- Avoid exposing sensitive information.
- Log integration failures appropriately.

---

# 17. Planned Future APIs

The platform architecture supports future API expansion.

Planned capabilities include:

- Voice AI APIs
- Multilingual APIs
- Knowledge Base APIs
- Semantic Search APIs
- Business Analytics APIs
- Workflow Automation APIs
- SaaS Administration APIs

---

# Conclusion

The AI Business Assistant Platform API is designed to provide a consistent, secure, and developer-friendly interface for intelligent business automation.

As the platform evolves, the API will continue to expand while maintaining a commitment to reliability, simplicity, and backward compatibility.

Developers should be able to integrate with confidence, knowing that the platform follows modern engineering standards and clear API design principles.