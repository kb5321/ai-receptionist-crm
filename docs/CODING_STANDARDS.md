# Coding Standards

**Version:** 2.0  
**Last Updated:** July 26, 2026  
**Purpose:** Establish consistent coding practices that promote readability, maintainability, security, and long-term scalability across the AI Business Assistant Platform.

---

# 1. Philosophy

Code is written for people first and computers second.

Every line of code should be easy to understand, easy to maintain, and easy to extend.

The platform values:

- Readability
- Simplicity
- Consistency
- Maintainability
- Security
- Testability
- Incremental Improvement

When multiple solutions exist, choose the solution that is easiest for another developer to understand.

---

# 2. General Engineering Principles

## Keep It Simple

Prefer simple solutions over unnecessary complexity.

Avoid premature optimization.

---

## Separation of Concerns

Each component should have a single responsibility.

Examples:

- Routers handle HTTP requests.
- Services contain business logic.
- Database code handles persistence.
- External integrations communicate with third-party APIs.

---

## Consistency

Follow existing project patterns whenever possible.

Consistent code is easier to maintain than individually "clever" code.

---

## Leave the Code Better

Every change should improve the codebase.

Fix small issues when appropriate rather than leaving them for someone else.

---

# 3. Python Standards

## Naming Conventions

### Variables

Use descriptive snake_case names.

Good:

```python
client_name
appointment_date
preferred_time
```

Avoid:

```python
x
tmp
data1
```

---

### Functions

Use verbs.

Examples:

```python
create_client()
send_sms()
validate_phone()
detect_language()
```

---

### Classes

Use PascalCase.

Examples:

```python
ClientService
SMSService
AppointmentManager
```

---

### Constants

Use uppercase.

```python
MAX_RETRIES = 3
SESSION_TIMEOUT = 30
```

---

# 4. Type Hints

Use type hints whenever practical.

Example:

```python
def create_client(name: str, phone: str) -> Client:
```

Type hints improve readability and tooling support.

---

# 5. Function Design

Functions should:

- Perform one responsibility.
- Have descriptive names.
- Remain reasonably small.
- Avoid excessive nesting.
- Return predictable values.

If a function becomes difficult to explain, consider splitting it into smaller functions.

---

# 6. FastAPI Standards

## Thin Routers

Routers should:

- Validate requests
- Call services
- Return responses

Business logic belongs in services.

Example:

```
Router
    ↓
Service
    ↓
Database
```

---

## Dependency Injection

Prefer dependency injection for reusable services and shared resources.

---

## Response Models

Use Pydantic models whenever possible.

Avoid returning unstructured dictionaries.

---

## Error Handling

Return appropriate HTTP status codes.

Provide meaningful error messages.

Avoid exposing internal implementation details.

---

# 7. Database Standards

## Parameterized Queries

Always use parameterized SQL.

Never concatenate user input into SQL statements.

---

## Transactions

Group related database operations into transactions.

Maintain data consistency.

---

## Naming

Use lowercase snake_case.

Examples:

```
client_notes
sms_messages
appointment_status
```

---

## Future Repository Pattern

As the platform grows, database operations should migrate into dedicated repository classes.

---

# 8. Artificial Intelligence Standards

AI-generated information must always be validated before being stored.

The AI should assist business workflows—not replace business rules.

Guidelines:

- Validate extracted data.
- Confirm missing information.
- Preserve conversation context.
- Store structured business records.
- Handle uncertainty gracefully.

AI responses should remain professional, helpful, and concise.

---

# 9. Security Standards

Passwords must always be hashed.

Never store plaintext passwords.

Never commit:

- API keys
- Passwords
- Secrets
- Tokens
- Credentials

Use environment variables for configuration.

Validate all user input.

Authorize access before performing protected operations.

---

# 10. Logging Standards

Avoid using `print()` for application logging.

Use Python's logging framework.

Logs should include meaningful context without exposing sensitive information.

Examples:

- Application startup
- Authentication events
- Errors
- External API failures
- Business workflow events

---

# 11. Testing Standards

New features should include appropriate tests.

Testing includes:

- Unit Tests
- Integration Tests
- Regression Tests

Tests should be:

- Independent
- Repeatable
- Easy to understand

---

# 12. Git Standards

Commits should represent one logical change.

Use meaningful commit messages.

Examples:

```
feat: add multilingual language detection

fix: correct SMS delivery status handling

docs: establish Version 2.0 software architecture
```

Commit early.

Commit often.

Avoid large unrelated commits.

---

# 13. Documentation Standards

Documentation is part of the software.

Update documentation whenever architecture, APIs, workflows, or user-facing behavior changes.

Relevant documents include:

- README.md
- ENGINEERING_CHARTER.md
- PRODUCT_VISION.md
- ROADMAP.md
- ARCHITECTURE.md
- API_GUIDE.md
- RELEASE_NOTES.md

---

# 14. Code Review Checklist

Before submitting code, verify:

- Code follows project structure.
- Naming is descriptive.
- Business logic is not duplicated.
- Type hints are included where appropriate.
- Errors are handled gracefully.
- Security requirements are met.
- Tests pass.
- Documentation is updated if necessary.

---

# 15. Engineering Rules

The following rules guide day-to-day development.

- Write code for humans first.
- Keep routers thin.
- Keep services focused.
- Prefer explicit behavior over implicit behavior.
- Minimize duplication.
- Optimize for maintainability before optimization.
- Every feature should be testable.
- Every bug fix should leave the codebase slightly better than before.
- Favor readability over cleverness.
- Small, consistent improvements lead to long-term success.

---

# 16. Continuous Improvement

Coding standards are living guidelines.

As the platform evolves, these standards should evolve as well.

Improvements should be discussed, documented, and adopted consistently across the project.

---

# Conclusion

The AI Business Assistant Platform is built on the belief that high-quality software is the result of disciplined engineering practices, thoughtful design, and continuous learning.

These coding standards establish a common language for development and ensure that future contributors can build upon a consistent, maintainable, and scalable foundation.