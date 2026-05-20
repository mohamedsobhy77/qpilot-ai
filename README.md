# QPilot AI

AI-Powered QA Automation Platform

QPilot AI is an end-to-end intelligent QA platform that transforms software requirements into structured QA assets using AI.

The platform allows QA engineers and teams to:

* Submit software requirements
* Generate test scenarios automatically
* Generate structured test cases
* Generate Playwright automation scripts
* Manage approval workflows
* Integrate with external systems such as GitHub and Slack

---

# Project Overview

Traditional QA workflows often require significant manual effort to:

* Analyze requirements
* Design test scenarios
* Write test cases
* Create automation scripts

QPilot AI accelerates this workflow by leveraging Large Language Models (LLMs) to automate large portions of the QA lifecycle.

The system provides a clean workflow:

Requirement → Scenarios → Test Cases → Automation Scripts

---

# Key Features

## Authentication System

* JWT Authentication
* Secure login system
* Protected API routes
* Session persistence

## Requirement Management

* Create and manage software requirements
* Store requirement metadata
* Requirement status tracking

## AI Scenario Generation

Generate intelligent test scenarios directly from business requirements.

Supported scenario types:

* Positive scenarios
* Negative scenarios
* Edge cases

## AI Test Case Generation

Generate structured test cases from scenarios.

Includes:

* Preconditions
* Test steps
* Expected results
* Priorities

## AI Automation Script Generation

Generate Playwright automation scripts automatically.

Generated scripts include:

* Assertions
* Dynamic test data
* Page interactions
* Validation logic

## Approval Workflow

* Approve generated test assets
* Reject or regenerate content
* QA review workflow

## Integrations

### GitHub Integration

* Push generated automation scripts to repositories

### Slack Integration

* Send notifications when automation scripts are generated

---

# Tech Stack

## Backend

* FastAPI
* SQLAlchemy
* AsyncIO
* Pydantic
* JWT Authentication
* SQLite / PostgreSQL

## Frontend

* Next.js 14
* TypeScript
* Tailwind CSS
* Zustand
* React Hook Form
* Zod
* Axios

## AI & Automation

* OpenRouter API
* LLM-based generation
* Playwright

---

# System Architecture

```text
Frontend (Next.js)
        ↓
FastAPI Backend
        ↓
AI Services Layer
        ↓
OpenRouter / LLM Models
        ↓
Generated QA Assets
```

---

# AI Workflow

## 1. Submit Requirement

The user submits a software requirement.

Example:

```text
Users should be able to register using email and password.
```

## 2. Generate Scenarios

The AI generates multiple testing scenarios.

Example:

* Successful registration
* Duplicate email registration
* Invalid password format
* Empty fields validation

## 3. Generate Test Cases

Structured test cases are generated for each scenario.

## 4. Generate Automation Script

The platform generates a Playwright automation script automatically.

---

# Example Generated Automation Script

```ts
import { test, expect } from '@playwright/test';

test('Successful registration', async ({ page }) => {
  await page.goto('/register');

  await page.fill('[data-testid="email"]', 'test@example.com');
  await page.fill('[data-testid="password"]', 'Test@123');

  await page.click('[data-testid="register-button"]');

  await expect(page).toHaveURL('/dashboard');
});
```

---

# Project Structure

```text
qpilot/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── services/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── db/
│   │   └── core/
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   ├── components/
│   │   ├── services/
│   │   ├── store/
│   │   └── lib/
│   └── package.json
│
└── README.md
```

---

# API Endpoints

## Authentication

* `POST /api/v1/auth/register`
* `POST /api/v1/auth/login`
* `GET /api/v1/auth/profile`

## Requirements

* `POST /api/v1/requirements`
* `GET /api/v1/requirements`

## Scenarios

* `POST /api/v1/scenarios/generate`
* `GET /api/v1/scenarios/{requirement_id}`

## Test Cases

* `POST /api/v1/test-cases/generate`
* `GET /api/v1/test-cases/{scenario_id}`

## Automation

* `POST /api/v1/automation/generate`
* `GET /api/v1/automation/{script_id}`

---

# Installation & Setup

## Backend Setup

```bash
cd backend

python -m venv venv

venv\Scripts\activate

pip install -r requirements.txt

python -m uvicorn app.main:app --reload
```

Backend runs on:

```text
http://localhost:8000
```

---

## Frontend Setup

```bash
cd frontend

npm install

npm run dev
```

Frontend runs on:

```text
http://localhost:3000
```

---

# Environment Variables

Create a `.env` file inside the backend directory.

Example:

```env
OPENAI_API_KEY=your_api_key
OPENAI_BASE_URL=https://openrouter.ai/api/v1
OPENAI_MODEL=deepseek/deepseek-v4-flash:free
DATABASE_URL=sqlite+aiosqlite:///./qpilot.db
JWT_SECRET=your_secret
```

---

# Current Capabilities

* Requirement management
* AI scenario generation
* AI test case generation
* AI Playwright generation
* JWT authentication
* Async backend architecture
* OpenRouter integration
* Frontend dashboard
* Approval workflow

---

# Future Enhancements

Planned improvements:

* Selenium support
* Cypress support
* Real Playwright execution
* Jira synchronization
* Excel export
* Test analytics dashboard
* AI bug prediction
* Multi-project workspace support
* CI/CD integration
* Docker deployment

---

# Challenges Solved

During development, several engineering challenges were addressed:

* AI invalid JSON handling
* Retry handling for rate limits
* Authentication token management
* GitHub push protection
* Large file cleanup from Git history
* Async database configuration
* Frontend/backend integration
* AI response parsing and validation

---

# Screenshots

Add screenshots here:

* Dashboard
* Requirement creation
* Scenario generation
* Test case generation
* Automation script generation

---

# Author

Mohamed Sobhy

Computer Science Graduate | QA Engineer | AI-Powered Testing Enthusiast

GitHub:
[https://github.com/mohamedsobhy77](https://github.com/mohamedsobhy77)

LinkedIn:
[https://www.linkedin.com/in/mohamed-sobhy](https://www.linkedin.com/in/mohamed-sobhy)

---

# License

This project is licensed under the MIT License.
