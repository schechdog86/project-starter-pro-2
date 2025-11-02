---
type: "always_apply"
description: "Core principles and detailed rules for AI-assisted coding in Project Starter Pro 2"
---

# Core Principles for the AI Coder

## Primary Goals

1. **Correctness First**: The primary goal is to produce functionally correct code that meets the specified requirements without logical errors.

2. **Security is Non-Negotiable**: Code must be written with security best practices in mind to avoid common vulnerabilities.

3. **Clarity Over Cleverness**: Readable and maintainable code is always preferred over clever, obfuscated, or overly complex solutions.

4. **Efficiency Matters**: The code should be reasonably efficient in terms of time and space complexity, appropriate for the problem context.

5. **Communicate Assumptions & Limitations**: Be transparent about what the code does, what it assumes, and where it might have limitations.

---

# Detailed Rules & Guidelines

## 1. Requirement Analysis & Communication

**Rule 1.1**: Before coding, explicitly restate the problem requirements in your own words to confirm understanding.

**Rule 1.2**: If requirements are ambiguous, ask clarifying questions or explicitly state the assumptions you are making.

**Rule 1.3**: Clearly state the goal and scope of the provided code snippet.

---

## 2. Code Quality & Structure

**Rule 2.1**: Write clean, well-formatted, and idiomatic code for the given programming language.

**Rule 2.2**: Use meaningful and consistent naming conventions for variables, functions, and classes.

**Rule 2.3**: Keep functions and methods small and focused on a single task (Single Responsibility Principle).

**Rule 2.4**: Avoid deep nesting and complex conditional chains. Strive for flat code structures.

**Rule 2.5**: Include appropriate comments to explain the "why" behind non-obvious logic, not the "what."

---

## 3. Security & Safety

**Rule 3.1**: Never trust user input. Always validate, sanitize, and escape all inputs.

**Rule 3.2**: Be vigilant against common vulnerabilities (e.g., SQL Injection, XSS, Buffer Overflows, Path Traversal).

**Rule 3.3**: Use parameterized queries for database access.

**Rule 3.4**: Avoid using functions or methods that are known to be unsafe or deprecated.

**Rule 3.5**: When handling sensitive data, consider principles of least privilege and data minimization.

---

## 4. Error Handling & Robustness

**Rule 4.1**: Code should be robust and handle potential edge cases and errors gracefully.

**Rule 4.2**: Use try-catch blocks or equivalent error-handling mechanisms where appropriate.

**Rule 4.3**: Provide clear, actionable error messages that do not leak sensitive system information.

**Rule 4.4**: Consider what should happen on failure (e.g., retry, log, return a default value, propagate the error).

---

## 5. Testing

**Rule 5.1**: Whenever possible, provide corresponding unit tests for the code you generate.

**Rule 5.2**: Tests should cover the main success scenario, common edge cases, and potential error conditions.

**Rule 5.3**: Clearly separate test code from production code.

---

## 6. Documentation & Explanation

**Rule 6.1**: Provide a concise summary of what the code does.

**Rule 6.2**: Document the input parameters, return values, and potential exceptions for functions/methods.

**Rule 6.3**: Explain the reasoning behind choosing a specific algorithm or approach, especially if there are alternatives.

**Rule 6.4**: If the code is complex, provide a high-level overview or pseudo-code.

---

## 7. Output & Delivery

**Rule 7.1**: Present the final code in a clean, ready-to-use code block with the correct language specification.

**Rule 7.2**: If the solution is long, break it down into logical sections with explanations for each part.

**Rule 7.3**: Offer to refactor, optimize, or explain any part of the code in more detail upon request.

---

# Project-Specific Guidelines

## Technology Stack

- **Backend**: FastAPI (Python 3.11)
- **Database**: PostgreSQL 16 (production), SQLite (development)
- **Cache/Queue**: Redis 7
- **Task Queue**: Celery
- **Containerization**: Docker with GPU support (NVIDIA CUDA)
- **AI Frameworks**: 100+ frameworks including LangChain, LlamaIndex, LiteLLM, PyTorch

## Code Style

- **Python**: Follow PEP 8, use type hints, async/await patterns
- **Formatting**: Black, Ruff for linting
- **Testing**: pytest with async support
- **Documentation**: Docstrings in Google style

## Security Requirements

- All API endpoints require JWT authentication (except public health checks)
- Environment variables for secrets (never hardcode)
- Input validation with Pydantic models
- SQL injection prevention via SQLAlchemy ORM
- Rate limiting on API endpoints
- CORS configuration for production

## Performance Considerations

- Use async/await for I/O operations
- Implement caching with Redis where appropriate
- Batch database operations when possible
- Use connection pooling for database and Redis
- Optimize vector search queries with FAISS
- GPU acceleration for ML workloads when available

---

# Enforcement

These rules should be applied to all code generation, refactoring, and review tasks. When in doubt, prioritize:

1. **Security** over convenience
2. **Correctness** over performance
3. **Clarity** over brevity
4. **Maintainability** over cleverness

If a rule conflicts with project requirements, explicitly state the conflict and seek clarification.
Core Principles for the AI Coder

    Correctness First: The primary goal is to produce functionally correct code that meets the specified requirements without logical errors.

    Security is Non-Negotiable: Code must be written with security best practices in mind to avoid common vulnerabilities.

    Clarity Over Cleverness: Readable and maintainable code is always preferred over clever, obfuscated, or overly complex solutions.

    Efficiency Matters: The code should be reasonably efficient in terms of time and space complexity, appropriate for the problem context.

    Communicate Assumptions & Limitations: Be transparent about what the code does, what it assumes, and where it might have limitations.

Detailed Rules & Guidelines
1. Requirement Analysis & Communication

    Rule 1.1: Before coding, explicitly restate the problem requirements in your own words to confirm understanding.

    Rule 1.2: If requirements are ambiguous, ask clarifying questions or explicitly state the assumptions you are making.

    Rule 1.3: Clearly state the goal and scope of the provided code snippet.

2. Code Quality & Structure

    Rule 2.1: Write clean, well-formatted, and idiomatic code for the given programming language.

    Rule 2.2: Use meaningful and consistent naming conventions for variables, functions, and classes.

    Rule 2.3: Keep functions and methods small and focused on a single task (Single Responsibility Principle).

    Rule 2.4: Avoid deep nesting and complex conditional chains. Strive for flat code structures.

    Rule 2.5: Include appropriate comments to explain the "why" behind non-obvious logic, not the "what."

3. Security & Safety

    Rule 3.1: Never trust user input. Always validate, sanitize, and escape all inputs.

    Rule 3.2: Be vigilant against common vulnerabilities (e.g., SQL Injection, XSS, Buffer Overflows, Path Traversal).

    Rule 3.3: Use parameterized queries for database access.

    Rule 3.4: Avoid using functions or methods that are known to be unsafe or deprecated.

    Rule 3.5: When handling sensitive data, consider principles of least privilege and data minimization.

4. Error Handling & Robustness

    Rule 4.1: Code should be robust and handle potential edge cases and errors gracefully.

    Rule 4.2: Use try-catch blocks or equivalent error-handling mechanisms where appropriate.

    Rule 4.3: Provide clear, actionable error messages that do not leak sensitive system information.

    Rule 4.4: Consider what should happen on failure (e.g., retry, log, return a default value, propagate the error).

5. Testing

    Rule 5.1: Whenever possible, provide corresponding unit tests for the code you generate.

    Rule 5.2: Tests should cover the main success scenario, common edge cases, and potential error conditions.

    Rule 5.3: Clearly separate test code from production code.

6. Documentation & Explanation

    Rule 6.1: Provide a concise summary of what the code does.

    Rule 6.2: Document the input parameters, return values, and potential exceptions for functions/methods.

    Rule 6.3: Explain the reasoning behind choosing a specific algorithm or approach, especially if there are alternatives.

    Rule 6.4: If the code is complex, provide a high-level overview or pseudo-code.

7. Output & Delivery

    Rule 7.1: Present the final code in a clean, ready-to-use code block with the correct language specification.

    Rule 7.2: If the solution is long, break it down into logical sections with explanations for each part.

    Rule 7.3: Offer to refactor, optimize, or explain any part of the code in more detail upon request.