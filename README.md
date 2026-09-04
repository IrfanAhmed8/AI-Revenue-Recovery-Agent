[▶ Watch Demo Video](https://www.youtube.com/watch?v=l7CChYgNmhc)
# 🤖 AI Revenue Recovery Agent

An AI-powered revenue recovery system that analyzes failed payments, evaluates customer transaction history, and automatically determines the best recovery action.

The system uses **Google Gemini** as its AI decision engine, **Razorpay** for payment recovery links and payment processing, **FastAPI** for the backend, **PostgreSQL** for data storage, and a **React/Vite dashboard** for monitoring recovery performance.

---

# 🧠 How It Works

When a payment fails, the AI Recovery Agent analyzes the failed transaction along with the customer's transaction history and payment context.
![High Level Architecture](./images/Architecture.png)

```text
Payment Failed
      ↓
Get Current Transaction + Customer History
      ↓
Build Recovery Context + Prompt
      ↓
Gemini AI
      ↓
Structured Decision
      ↓
Execute Recovery Action
      ↓
Update Database
      ↓
Dashboard
```

The AI returns a structured decision containing:

* Recovery action
* Recovery probability
* Confidence score
* Decision reason
* Personalized customer message

A key design choice of this project is that the required recovery information is generated using a **single LLM call**.

---

# 🚀 Setup & Installation

## 📥 Clone the Repository

```bash
git clone <your-repository-url>
cd AI-Revenue-Recovery-Agent
```

---

# 🐳 Database Setup Using Docker

The project uses **Docker Compose** to automatically create and run the PostgreSQL database.

Make sure Docker and Docker Compose are installed and running.

Start the PostgreSQL database:

```bash
docker compose up -d
```

If your Docker version uses the older Compose command:

```bash
docker-compose up -d
```

This will automatically create a PostgreSQL container with the following configuration:

```text
Container Name: razorpay-postgres
PostgreSQL Version: 16
Username: postgres
Password: postgres
Database: ai-recovery-system
Port: 5432
```

The database data is stored in a Docker volume, so it persists even when the container is restarted.

---

# 🐍 Backend Setup

Navigate to the backend directory:

```bash
cd backend
```

## Create a Virtual Environment

```bash
python -m venv venv
```

## Activate the Virtual Environment

### Windows

```bash
venv\Scripts\activate
```

### macOS / Linux

```bash
source venv/bin/activate
```

## Install Backend Dependencies

All required Python packages are listed in `requirements.txt`.

Install them using:

```bash
pip install -r requirements.txt
```

This installs all required backend dependencies, including the packages needed for:

* FastAPI
* Uvicorn
* PostgreSQL database access
* Google Gemini integration
* Razorpay integration
* Environment variable management
* Other backend services

---

# 🗄️ Docker Compose Configuration

The project uses the following `docker-compose.yml` configuration to create the PostgreSQL database:

```yaml
services:
  postgres:
    image: postgres:16

    container_name: razorpay-postgres

    restart: unless-stopped

    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: ai-recovery-system

    ports:
      - "5432:5432"

    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

Start the database:

```bash
docker compose up -d
```

Check that the PostgreSQL container is running:

```bash
docker ps
```

You should see:

```text
razorpay-postgres
```

To stop the database:

```bash
docker compose down
```

To stop the database and remove all stored database data:

```bash
docker compose down -v
```

> ⚠️ Using `-v` removes the PostgreSQL Docker volume and permanently deletes the local database data.

---

# 🔐 Environment Variables

Create a `.env` file inside the `backend` directory:

```env
DATABASE_URL=postgresql://postgres:postgres@127.0.0.1:5432/ai-recovery-system

RAZORPAY_KEY_ID=your_razorpay_key_id
RAZORPAY_KEY_SECRET=your_razorpay_key_secret
RAZORPAY_WEBHOOK_SECRET=your_razorpay_webhook_secret

GEMINI_API_KEY=your_gemini_api_key
```

> ⚠️ Never commit your `.env` file or API keys to GitHub.

Add the following to your `.gitignore`:

```gitignore
.env
venv/
__pycache__/
node_modules/
```

---

# 🌱 Seed Database with Synthetic Data

After the PostgreSQL Docker container is running, insert the synthetic customer and payment data.

Make sure you are inside the `backend` directory and your virtual environment is activated.

Run:

```bash
python -m app.seed_data
```

The `seed_data.py` script inserts sample data into the PostgreSQL database.

The synthetic data is used to simulate:

* Customers
* Failed transactions
* Payment history
* Payment recovery scenarios
* Customer transaction patterns

This data allows the AI Recovery Agent to analyze realistic payment failure scenarios.

---

# ▶️ Start the Backend

From the `backend` directory, run:

```bash
uvicorn app.main:app --reload
```

The FastAPI server will start at:

```text
http://127.0.0.1:8000
```

You can access the FastAPI documentation at:

```text
http://127.0.0.1:8000/docs
```

---

# 🤖 Configure Google Gemini

The project uses **Google Gemini** as the AI decision engine.

Add your Gemini API key to the `.env` file:

```env
GEMINI_API_KEY=your_gemini_api_key
```

The AI receives:

* Current failed transaction information
* Customer transaction history
* Payment context
* Recovery instructions

Gemini returns a structured response containing:

* Recovery action
* Recovery probability
* Confidence score
* Decision reason
* Personalized customer message

The recovery decision is generated using a **single AI call**, reducing unnecessary API calls and simplifying the decision-making workflow.

---

# 💳 Configure Razorpay

Add your Razorpay API credentials to the `.env` file:

```env
RAZORPAY_KEY_ID=your_razorpay_key_id
RAZORPAY_KEY_SECRET=your_razorpay_key_secret
```

Razorpay is used to:

* Create payment recovery links
* Allow customers to complete failed payments
* Send payment status events through webhooks

---

# 🌐 Configure Razorpay Webhook Using ngrok

Since Razorpay requires a publicly accessible URL to send webhook events during local development, this project uses **ngrok**.

## Step 1: Start the Backend

Make sure FastAPI is running:

```bash
uvicorn app.main:app --reload
```

The backend runs on:

```text
http://127.0.0.1:8000
```

---

## Step 2: Start ngrok

Open another terminal and run:

```bash
ngrok http 8000
```

ngrok will generate a public URL similar to:

```text
https://abc123.ngrok-free.app
```

---

# 🌐 Configure Razorpay Webhooks

To receive payment status updates from Razorpay, you need to configure a webhook endpoint.

Since the application runs locally during development, **ngrok** is used to expose the FastAPI backend to the internet.

---

## Step 1 — Create a Razorpay Account

Go to Razorpay and create an account if you don't already have one.

After logging in, enable **Test Mode** for development and testing.

> ⚠️ Make sure Test Mode is enabled before creating test payments and configuring webhooks.

<!-- Add Razorpay Test Mode image here -->

![Enable Razorpay Test Mode](./images/razorpay_home.png)

---

## Step 2 — Open Account & Settings

From the Razorpay Dashboard:

1. Click on **Account & Settings**.
2. Navigate to **Website and App Settings**.

<!-- Add Account & Settings image here -->

![Account and Settings](./images/accounts.png)

---

## Step 3 — Open Webhooks

Under **Website and App Settings**, click on:

```text
Webhooks

# 🔒 Webhook Security

The Razorpay webhook endpoint verifies every incoming request using the `X-Razorpay-Signature` header.

The project:

1. Reads the raw webhook request body.
2. Retrieves the Razorpay signature.
3. Generates the expected HMAC SHA256 signature.
4. Compares the received and expected signatures.
5. Rejects invalid webhook requests.

This ensures that recovery events are processed only from verified Razorpay webhook requests.

---

# 🔄 Recovery Payment Webhook Flow

When a customer completes a payment using a recovery payment link:

```text
Customer Completes Payment
            ↓
Razorpay Captures Payment
            ↓
payment.captured Webhook
            ↓
ngrok Public URL
            ↓
/webhook/razorpay
            ↓
Verify Razorpay Signature
            ↓
Save Webhook Event
            ↓
Detect Recovery Payment
            ↓
Find Recovery Action
            ↓
Update Recovery Status
            ↓
Create Recovered Transaction
            ↓
Update Dashboard
```

The webhook handler also prevents duplicate webhook processing by checking existing payment and event records before creating a new webhook record.

---

# 🖥️ Frontend Setup

Navigate to the frontend dashboard directory:

```bash
cd frontend/dashboard
```

Install dependencies:

```bash
npm install
```

Start the frontend:

```bash
npm start
```

The React/Vite dashboard will start on the local URL displayed in your terminal.

---

# ▶️ Running the Complete Application

The application requires multiple services to run locally.

## Terminal 1 — PostgreSQL Database

From the project root:

```bash
docker compose up -d
```

This automatically starts PostgreSQL using the Docker Compose configuration.

---

## Terminal 2 — Backend Setup

```bash
cd backend

python -m venv venv
```

Activate the environment.

### Windows

```bash
venv\Scripts\activate
```

### macOS / Linux

```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Seed the database:

```bash
python app/seed_data.py
```

Start the backend:

```bash
uvicorn app.main:app --reload
```

---

## Terminal 3 — ngrok

```bash
ngrok http 8000
```

Copy the generated public URL and configure:

```text
https://your-ngrok-url.ngrok-free.app/webhook/razorpay
```

in the Razorpay webhook settings.

---

## Terminal 4 — Frontend

```bash
cd frontend/dashboard
npm install
npm start
```

---

# 🧪 Testing the AI Recovery Flow

At the moment, the project does **not use a queue-based system** for processing failed transactions.

Instead, you can manually trigger the AI recovery workflow using the API endpoint.
Endpoint to hit 
``` bash
http://localhost:8000/recovery/{Failed_id}/run
```

``` bash
SELECT id FROM failed_transactions;
```


The complete flow is:

```text
1. Payment Fails
        ↓
2. Failed Transaction is Identified
        ↓
3. Fetch Current Failed Transaction
        +
   Fetch Customer Transaction History
        ↓
4. Build Recovery Context + Prompt
        ↓
5. Send Context to Gemini
        ↓
6. Gemini Returns Structured Decision
        ↓
7. Execute Recovery Action
        ↓
8. Create Recovery Record
        ↓
9. Update Dashboard
```

For example, Gemini may return:

```json
{
  "success": true,
  "action": "PAYMENT_LINK",
  "amount": 52921,
  "currency": "INR",
  "failure_reason": "gateway_timeout",
  "recovery_probability": 0.65,
  "confidence": 0.85,
  "reason": "The payment failed due to a temporary gateway timeout, which is often a transient issue.",
  "message": "Your recent payment attempt was unsuccessful due to a temporary issue. Please try again using the new payment link.",
  "status": "payment_link_created"
}
```

---

# 💰 Payment Recovery Flow

When the AI selects `PAYMENT_LINK`:

```text
AI Decision: PAYMENT_LINK
            ↓
Create Razorpay Payment Link
            ↓
Send Recovery Message to Customer
            ↓
Customer Opens Payment Link
            ↓
Customer Completes Payment
            ↓
Razorpay Sends payment.captured Event
            ↓
Webhook Signature Verified
            ↓
Recovery Payment Detected
            ↓
Recovery Action Updated
            ↓
Recovered Transaction Created
            ↓
Dashboard Updated
```
![Transatcion](./images/tradnsaction.png)
---

# 📊 Dashboard

The dashboard provides visibility into the recovery agent's performance.

## 🏠 Home
![Home](./images/home.png)

Displays:

* Failed Transactions
* Revenue at Risk
* Recovered Transactions
* Revenue Recovered
* Recovery Rate
* AI Agent Status

---

## 📜 Recovery History
![Recovery History](./images/recovery_histroy.png)
Displays successfully recovered transactions, including:

* Transaction
* Amount
* Failure Reason
* Recovery Method
* Recovered At
* Razorpay Payment ID
* Status

---

## ⚙️ Currently Working On
![Currently Working on](./images/recovery_action.png)
Displays recovery actions executed by the AI agent, including:

* Action
* Transaction
* Recovery Probability
* Confidence
* Status
* Decision Reason
* Attempts
* Recovery Limit

---

# 🛠️ Tech Stack

| Technology    | Purpose                                     |
| ------------- | ------------------------------------------- |
| Python        | Backend development                         |
| FastAPI       | REST API and backend services               |
| Docker        | PostgreSQL container management             |
| PostgreSQL 16 | Database                                    |
| Google Gemini | AI recovery decision engine                 |
| Razorpay      | Payment links and payment processing        |
| ngrok         | Public webhook tunneling during development |
| React         | Frontend dashboard                          |
| Vite          | Frontend development tooling                |

---

# 🎯 Key Features

* 🤖 AI-powered payment recovery decisions
* 🧠 Single-call LLM decision workflow
* 🐳 Dockerized PostgreSQL database
* 🌱 Synthetic data seeding using `seed_data.py`
* 📊 Customer transaction history analysis
* 💳 Automated Razorpay payment link generation
* 🔐 Secure webhook signature verification
* 🔄 Duplicate webhook prevention
* 📈 Recovery performance dashboard
* 🗄️ PostgreSQL transaction and recovery tracking

---

# 🔁 Complete Recovery Lifecycle

```text
Failed Payment
      ↓
AI Analyzes Transaction
      ↓
AI Selects Recovery Strategy
      ↓
Recovery Action Created
      ↓
Payment Link Generated
      ↓
Customer Completes Payment
      ↓
Razorpay Webhook Received
      ↓
Webhook Signature Verified
      ↓
Recovery Identified
      ↓
Database Updated
      ↓
Recovered Revenue Displayed on Dashboard
```

---

# ⚠️ Development Note

The project uses **synthetic customer and payment data** inserted through the `seed_data.py` script to simulate payment failures and recovery scenarios.

The complete demonstration flow is:

> **Docker Database → Seed Synthetic Data → Failed Payment → AI Decision → Recovery Action → Customer Payment → Verified Recovery**

---

## ⭐ If you found this project useful, consider giving it a star!
