# ProcureAI --- AI Purchasing Agent

ProcureAI is an AI-assisted purchasing decision system built for retail
procurement workflows.

The system investigates a purchasing situation, evaluates the proposed
purchase against business constraints, makes a decision using Gemini,
validates that decision deterministically, executes the purchase action
when safe, and validates the result after execution.

The project focuses on **decision quality and safe execution rather than
simply generating a chatbot response**.

------------------------------------------------------------------------

## Problem

Purchasing recommendations can be incorrect when they do not consider
the complete purchasing situation.

A buyer may need to consider:

-   Current inventory
-   Expected demand
-   Existing open purchase orders
-   Supplier availability
-   Supplier MOQ
-   Supplier lead time
-   Unit price
-   Budget
-   Storage capacity
-   Supplier failures and alternative sourcing options

ProcureAI combines AI reasoning with deterministic business validation
so that an AI recommendation cannot directly bypass hard purchasing
constraints.

------------------------------------------------------------------------

## Core Workflow

``` text
                    ┌──────────────────┐
                    │    React UI      │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │   FastAPI API    │
                    └────────┬─────────┘
                             │
              ┌──────────────┴──────────────┐
              │                             │
              ▼                             ▼
      ┌────────────────┐            ┌────────────────┐
      │  Gemini Agent  │            │  SQLite DB     │
      │  Investigation │            │  Procurement   │
      │  & Decision    │            │  Data          │
      └────────┬───────┘            └────────────────┘
               │
               ▼
      ┌────────────────────┐
      │ Deterministic      │
      │ Business Validator │
      └──────────┬─────────┘
                 │
                 ▼
      ┌────────────────────┐
      │ Purchase Execution │
      └──────────┬─────────┘
                 │
                 ▼
      ┌────────────────────┐
      │ Post-Execution     │
      │ Validation         │
      └────────────────────┘
```

### Design principle

The LLM is responsible for **investigation and reasoning**.

The backend is responsible for **hard business rules and execution
safety**.

This prevents the AI from directly making an unchecked purchasing
decision.

------------------------------------------------------------------------

## Scenarios Implemented

### Scenario 1 --- Purchase Recommendation Review

The system receives a recommendation to purchase **800 units**.

Purchasing data:

-   Current inventory: 300
-   Expected demand: 1000
-   Existing open PO: 400
-   Supplier MOQ: 100
-   Supplier availability: 1000
-   Unit price: 40
-   Budget: 20,000
-   Storage capacity: 1000

The actual requirement is:

``` text
1000 demand - 300 inventory - 400 open PO
= 300 additional units
```

The proposed 800-unit purchase would:

-   Cost 32,000, exceeding the 20,000 budget
-   Increase projected inventory beyond the 1000-unit storage capacity

The agent therefore modifies the recommendation to **300 units**.

The backend validates the decision before creating the purchase order.

Expected flow:

``` text
800 proposed
      ↓
AI investigates
      ↓
MODIFY → 300
      ↓
Business validation
      ↓
Create PO
      ↓
Post-execution validation
      ↓
SUCCESS
```

------------------------------------------------------------------------

### Scenario 2 --- Supplier Cannot Fulfil

The system has an open PO for **500 units** with the primary supplier.

Purchasing data:

-   Inventory: 100
-   Demand: 600
-   Open PO: 500
-   Primary supplier availability: 250
-   Backup supplier availability: 500
-   Primary supplier price: 50
-   Backup supplier price: 55
-   Budget: 30,000
-   Storage capacity: 800

The primary supplier can fulfill only 250 of the 500-unit PO, creating a
**250-unit shortfall**.

The agent investigates the available suppliers and recommends a recovery
purchase of 250 units from the backup supplier.

The recovery purchase is then validated and executed.

Expected flow:

``` text
500-unit open PO
      ↓
Primary supplier can provide only 250
      ↓
250-unit shortfall detected
      ↓
Backup supplier investigated
      ↓
250-unit recovery purchase
      ↓
Business validation
      ↓
Recovery PO created
      ↓
Post-execution validation
      ↓
SUCCESS
```

------------------------------------------------------------------------

## Technology Stack

### Backend

-   Python
-   FastAPI
-   SQLAlchemy
-   SQLite
-   Pydantic
-   Google Gemini API

### Frontend

-   React
-   Vite
-   Axios
-   CSS

### Testing

-   Pytest

------------------------------------------------------------------------

## Project Structure

``` text
procure-ai/
│
├── backend/
│   ├── agent/
│   │   ├── agent.py
│   │   ├── prompts.py
│   │   ├── tools.py
│   │   └── workflow.py
│   │
│   ├── services/
│   │   ├── execution_validator.py
│   │   └── purchase_orders.py
│   │
│   ├── database.py
│   ├── models.py
│   ├── scenarios.py
│   ├── validator.py
│   └── main.py
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── App.css
│   │   └── main.jsx
│   └── package.json
│
├── tests/
│   └── test_validator.py
│
├── .env.example
├── .gitignore
└── README.md
```

------------------------------------------------------------------------

## Setup

### 1. Clone the repository

``` bash
git clone <your-repository-url>
cd procure-ai
```

### 2. Backend setup

Install the required Python packages:

``` bash
pip install fastapi uvicorn sqlalchemy pydantic python-dotenv google-genai pytest
```

Create a `.env` file in the backend/project environment:

``` env
GEMINI_API_KEY=your_gemini_api_key
```

Do not commit `.env`.

The repository includes `.env.example` for configuration reference.

### 3. Start the backend

From the backend directory:

``` bash
uvicorn main:app --reload
```

The API will run at:

``` text
http://localhost:8000
```

FastAPI documentation is available at:

``` text
http://localhost:8000/docs
```

### 4. Frontend setup

From the frontend directory:

``` bash
npm install
npm run dev
```

The frontend will normally run at:

``` text
http://localhost:5173
```

------------------------------------------------------------------------

## API Endpoints

### Get purchasing data

``` http
GET /purchasing/{sku}
```

Returns inventory, forecast, suppliers, open purchase orders and
purchasing constraints.

Example:

``` http
GET /purchasing/MILK-001
```

------------------------------------------------------------------------

### Validate a purchase

``` http
POST /purchasing/{sku}/validate?purchase_quantity=300
```

Runs deterministic business validation.

Checks include:

-   Required quantity
-   Supplier MOQ
-   Supplier availability
-   Budget
-   Storage capacity

------------------------------------------------------------------------

### Review a purchase with AI

``` http
POST /agent/review/{sku}?purchase_quantity=800
```

The Gemini agent investigates the purchasing context and returns a
structured decision.

Possible decisions:

``` text
ACCEPT
MODIFY
REJECT
ESCALATE
```

------------------------------------------------------------------------

### Execute an AI purchasing workflow

``` http
POST /agent/purchase/{sku}?purchase_quantity=800
```

This performs the complete workflow:

``` text
AI decision
    ↓
Business validation
    ↓
Purchase execution
    ↓
Post-execution validation
```

------------------------------------------------------------------------

### Reset Scenario 1

``` http
POST /scenarios/reset/1
```

------------------------------------------------------------------------

### Reset Scenario 2

``` http
POST /scenarios/reset/2
```

Scenario reset endpoints make the demo deterministic and prevent
previous test executions from affecting subsequent runs.

------------------------------------------------------------------------

## Decision and Validation Model

The agent returns a structured decision similar to:

``` json
{
  "decision": "MODIFY",
  "recommended_quantity": 300,
  "supplier_id": 1,
  "reason": "The proposed purchase is higher than required...",
  "evidence": [
    "Expected demand is 1000 units.",
    "Current inventory is 300 units.",
    "Open purchase orders total 400 units."
  ]
}
```

The backend then independently validates the recommendation.

For example:

``` text
Required quantity
= Demand - Inventory - Incoming PO
```

The validator also checks:

``` text
Purchase quantity >= MOQ

Purchase quantity <= Supplier availability

Purchase cost <= Budget

Projected inventory <= Storage capacity
```

If validation fails, the system does not execute the purchase and
returns an escalation result.

------------------------------------------------------------------------

## Why Use Deterministic Validation?

LLMs are useful for investigating a complex situation and reasoning over
multiple factors, but hard purchasing constraints should not depend
solely on generated text.

ProcureAI therefore separates:

### AI responsibility

-   Investigate the situation
-   Interpret supplier conditions
-   Compare alternatives
-   Identify shortfalls
-   Recommend an action
-   Explain the decision

### Backend responsibility

-   Calculate required quantities
-   Enforce MOQ
-   Check supplier availability
-   Check budget
-   Check storage capacity
-   Execute purchase actions
-   Verify execution results

This separation provides a safety layer between AI reasoning and real
purchasing actions.

------------------------------------------------------------------------

## Testing

Run the deterministic validator tests with:

``` bash
pytest
```

The tests cover cases such as:

-   Valid purchase
-   Budget violation
-   Storage violation
-   MOQ violation
-   Supplier availability violation

The workflow can also be manually evaluated through the two provided
scenario reset endpoints.

------------------------------------------------------------------------

## Demo

A typical Scenario 1 demo:

1.  Reset Scenario 1.
2.  Open the purchasing dashboard.
3.  Review the proposed 800-unit purchase.
4.  Observe the AI decision to modify it to 300 units.
5.  Observe deterministic validation passing.
6.  Execute the purchase.
7.  Observe the created purchase order.
8.  Observe post-execution validation succeeding.

Scenario 2:

1.  Reset Scenario 2.
2.  Review the 500-unit purchasing situation.
3.  Observe the primary supplier shortfall.
4.  Observe the AI selecting the backup supplier for the 250-unit
    recovery quantity.
5.  Execute the recovery purchase.
6.  Observe post-execution validation.

------------------------------------------------------------------------

## Failure Handling

ProcureAI does not execute a purchase when the AI decision cannot be
safely validated.

Examples include:

-   Supplier not found
-   Invalid supplier selected by the AI
-   Purchase exceeds budget
-   Purchase exceeds storage capacity
-   Supplier cannot provide the required quantity
-   Purchase order creation fails
-   Post-execution state does not match the expected result

These cases return an `ESCALATE` status instead of silently executing an
unsafe action.

------------------------------------------------------------------------

## Mock Data

The project uses SQLite and seeded scenario data rather than real
supplier or inventory integrations.

This keeps the assignment self-contained while still demonstrating the
complete purchasing workflow.

The mock database represents:

-   Products
-   Inventory
-   Forecasts
-   Suppliers
-   Purchase orders
-   Purchasing constraints

------------------------------------------------------------------------

## Limitations and Future Improvements

This implementation intentionally focuses on the core purchasing
workflow required for the assignment.

Potential future improvements include:

-   Human approval before high-value purchases
-   Real ERP/procurement integrations
-   Supplier reliability history
-   More sophisticated demand forecasting
-   Purchase order modification/cancellation workflows
-   Audit logs
-   Authentication and authorization
-   More purchasing scenarios
-   Production database
-   Background job processing
-   More comprehensive integration tests

------------------------------------------------------------------------

## Security

API keys are loaded from environment variables.

Do not commit:

``` text
.env
```

The repository should contain only:

``` text
.env.example
```

with the secret value omitted.

------------------------------------------------------------------------

## Summary

ProcureAI demonstrates an AI purchasing workflow where:

``` text
Investigate
    ↓
Reason
    ↓
Decide
    ↓
Validate
    ↓
Execute
    ↓
Validate outcome
```

The main design goal is to combine the flexibility of an LLM for
purchasing investigation with deterministic backend controls for safe
execution.
