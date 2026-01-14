Webhook Ingestion Service
A production-style FastAPI service designed to ingest WhatsApp-like messages exactly once, featuring HMAC-based security, structured logging, and Prometheus monitoring.

Setup Used
Editor: VSCode

AI Assistant: Gemini (Google)

OS: Windows 11 (PowerShell)

How to Run
The service is fully containerized. Use the following commands (PowerShell):

Set Environment Variables:

PowerShell

$env:WEBHOOK_SECRET="testsecret"
$env:DATABASE_URL="sqlite:////data/app.db"
Build and Start:

PowerShell

docker compose up -d --build
Shutdown:

PowerShell

docker compose down -v