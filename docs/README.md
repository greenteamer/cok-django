# Project Documentation

This document is the SINGLE entry point to all project documentation.

❗ Do NOT read other documentation files without first consulting this file.

This file defines:

- what documentation exists
- where it lives
- which file to read for a given topic

---

## How to Use This Documentation

If you are:

- **new to the project** → read sections in order
- **looking for a specific topic** → use the navigation below
- **an AI assistant** → identify the relevant topic and load ONLY the linked file(s)

Loading all documentation at once is explicitly discouraged.

---

## Documentation Principles

- Each document covers ONE topic
- No document is authoritative outside its declared scope
- No duplication between documents
- This file is the only place that defines documentation navigation

---

## 1. High-Level Overview

Start here to understand WHAT the system is and WHY it exists.

- 📄 [`overview.md`](./overview.md)  
  Purpose, goals, non-goals, and mental model of the system

---

## 2. Architecture

Read these documents to understand HOW the system is structured.

- 📄 [`architecture/system.md`](./architecture/system.md)  
  High-level system architecture and component boundaries

- 📄 [`architecture/data-flow.md`](./architecture/data-flow.md)  
  Runtime data flow and interaction between components

- 📄 [`architecture/decisions.md`](./architecture/decisions.md)  
  Architecture Decision Records (ADRs) and trade-offs

---

## 3. APIs & Interfaces

Read these documents to understand HOW to integrate with the system.

- 📄 [`api/overview.md`](./api/overview.md)
  API philosophy, versioning, and compatibility guarantees (for future implementation)

- 📄 [`api/http.md`](./api/http.md)
  Current HTTP endpoints (Django Admin only)

---

## 4. Configuration & Environment

Read these documents to understand HOW the system is configured.

- 📄 [`config/environment.md`](./config/environment.md)
  Environment variables, configuration rules, and production setup

---

## 5. Runtime Behavior

Read these documents to understand WHAT happens at runtime.

- 📄 [`runtime/lifecycle.md`](./runtime/lifecycle.md)
  Container startup, shutdown, and application lifecycle

- 📄 [`runtime/error-handling.md`](./runtime/error-handling.md)
  Error handling strategies, logging, and failure modes

---

## 6. Development Guides

Read these documents to understand HOW to work with the codebase.

- 📄 [`guides/setup.md`](./guides/setup.md)
  Local development setup with Docker

- 📄 [`guides/testing.md`](./guides/testing.md)
  Testing strategy and tooling (framework for future tests)

- 📄 [`guides/deployment.md`](./guides/deployment.md)
  Production deployment on Ubuntu server

---

## 7. Application Modules

Read these documents to understand Django app responsibilities and interfaces.

- 📄 [`modules/blog.md`](./modules/blog.md)
  Blog application: models, admin interface, and content management

- 📄 [`modules/resume.md`](./modules/resume.md)
  Resume/CV application: professional profile, experience, skills, certifications, and achievements

- 📄 [`modules/resume-pdf-export.md`](./modules/resume-pdf-export.md)
  PDF resume export: ReportLab implementation, layout strategy, and generation pipeline

---

## 8. Security & Compliance

Read these documents to understand SECURITY boundaries.

- 📄 [`security/overview.md`](./security/overview.md)
  Security model, threat assumptions, and hardening measures

---

## 9. Observability & Operations

Read these documents to understand how the system is monitored.

- 📄 [`ops/logging.md`](./ops/logging.md)
  Logging strategy, configuration, and best practices

---

## 10. Frontend Architecture

Read these documents to understand frontend organization and build process.

- 📄 [`frontend/css-architecture.md`](./frontend/css-architecture.md)
  Component-based CSS architecture, BEM naming, PostCSS build system, and development workflow

---

## Documentation Ownership Rules

- Each document has a single owner (team or module)
- Changes MUST update the relevant document
- If ownership is unclear → document it here

---

## Adding New Documentation

When adding a new documentation file:

1. Decide which section it belongs to
2. Add a link in THIS file
3. Ensure it covers ONE topic only
4. Avoid duplication with existing docs

Documentation that is not linked here is considered NON-EXISTENT.

---

## Documentation for Future Implementation

As the project evolves, consider adding documentation for:

### Domain & Business Logic

When implementing business features:
- `domain/concepts.md` - Core domain concepts and terminology
- `domain/invariants.md` - Business rules and constraints

### Internal APIs

When building internal services:
- `api/internal.md` - Service-to-service communication protocols

### Metrics & Monitoring

When adding observability:
- `ops/metrics.md` - Application metrics, monitoring, and alerting

### Migrations & Deprecations

When evolving the API or architecture:
- `migrations/overview.md` - Deprecation policy and migration guides

---

## Last Updated

2025-12-23

This file MUST be updated whenever:

- a new documentation file is added
- document responsibilities change
- new sections are needed
