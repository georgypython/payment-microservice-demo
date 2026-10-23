# Demo / FUN Payment API

An asynchronous payment processing service built with FastAPI, RabbitMQ, and PostgreSQL. It simulates payment gateway operations, tracks payment statuses, and delivers webhook notifications.

## Features

- **Async payment processing** — API accepts payments and delegates processing to background workers.
- **Transactional Outbox** — payment records and outgoing events are stored atomically, with direct publishing and a background recovery mechanism.
- **Webhook delivery** — automatic retries with exponential backoff and a Dead Letter Queue (DLQ) for failed deliveries.
- **Idempotency** — duplicate requests are rejected using `Idempotency-Key`.
- **SSRF protection** — basic validation of webhook URLs.
- **Dependency Injection** — application components are wired using Dishka.
- **Simulated payment gateway** — configurable infrastructure with artificial processing delays and failures.

## Stack

- **API:** FastAPI
- **Message Broker:** RabbitMQ
- **Database:** PostgreSQL
- **ORM:** SQLAlchemy (async)
- **Migrations:** Alembic
- **Worker:** FastStream
- **Dependency Injection:** Dishka
- **Configuration:** Pydantic Settings
- **Runtime:** Docker Compose

## Quick Start

### Requirements

- Docker
- Docker Compose

### 1. Configure environment

```bash
cp .env.example .env
```

Edit `.env` if needed. The default configuration uses local Docker Compose services and a development API key.

### 2. Start the service

```bash
docker compose up --build -d
```

Database migrations are applied automatically by the API container.

### 3. Verify the service

The API is available at:

- **Base URL:** `http://localhost:8000`
- **RabbitMQ Management UI:** [http://localhost:15672](http://localhost:15672) — `guest` / `guest`

Check the repository for the configured health-check endpoint and API documentation route.

## API Usage

All payment endpoints require the `X-API-Key` header. Payment creation also requires an `Idempotency-Key`.

### Create a payment

Replace the webhook URL with your endpoint from [webhook.site](https://webhook.site) to inspect delivery attempts.

```bash
curl -i -X POST "http://localhost:8000/api/v1/payments" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_secret_key" \
  -H "Idempotency-Key: pay_req_001" \
  -d '{
    "amount": 2500.75,
    "currency": "rub",
    "description": "Order #432",
    "meta_info": {
      "user_id": 99,
      "device": "mobile"
    },
    "webhook_url": "https://webhook.site/YOUR_WEBHOOK_ID"
  }'
```

A successful submission returns `202 Accepted`. Payment processing happens asynchronously.

### Get payment status

Replace `PAYMENT_ID` with the ID returned when creating the payment.

```bash
curl -i "http://localhost:8000/api/v1/payments/PAYMENT_ID" \
  -H "X-API-Key: your_secret_key"
```

### Test idempotency

Repeat the creation request with the same `Idempotency-Key`. The API returns `409 Conflict` instead of creating a duplicate payment.

### Test webhook retries and DLQ

Use an unreachable webhook endpoint, then inspect the worker logs and RabbitMQ Management UI. After the configured delivery retries are exhausted, the failed message is routed to `payments.new.dlq`.

### Test webhook URL validation

Try submitting a webhook URL pointing to a localhost or internal network address. The request should fail validation with `422 Unprocessable Entity`.

## Architecture

```text
Client
  |
  v
FastAPI -----> PostgreSQL
  |                |
  |                +-- payments
  |                +-- outbox_events
  |
  +----> RabbitMQ ----> Payment Worker
  |                          |
  |                          +--> Simulated gateway
  |                          +--> Webhook delivery
  |
  +----> Outbox Daemon
             |
             +--> Recovers unpublished events
```

The Outbox pattern ensures that payment creation and event persistence happen in a single database transaction. The API attempts to publish events immediately after committing, while a background daemon recovers events that could not be published.

The worker is independent of the Outbox implementation: it consumes messages from RabbitMQ, simulates payment processing, updates payment status, and delivers webhooks.

## Project Structure

- `src/api/` — FastAPI endpoints
- `src/consumers/` — RabbitMQ message consumers
- `src/core/` — application configuration and logging
- `src/dependencies/` — Dishka dependency injection
- `src/infrastructure/` — database and broker setup
- `src/models/` — SQLAlchemy ORM models
- `src/schemas/` — request and response schemas
- `src/services/` — payment and Outbox business logic
- `src/workers/` — worker and Outbox daemon entry points

## One thing

This is a demo project with a simulated payment gateway. It is intended for learning and experimentation, not for processing real payments or handling production financial data.

тесте.


