# BalanceIQ Backend

BalanceIQ is a robust backend service for a personal finance management application. It provides core functionalities for handling users, transactions, debts, and notifications through a set of modular Python scripts that interact with a PostgreSQL database.

## BalanceIQ Backend Features

### 1️⃣ User Authentication & Sessions

*   **Register**: Users can create an account with email and password.
*   **Login / Logout**: Users can log in and log out.
*   **Session Management**:
    *   Session-based authentication (later upgrade to JWT for API).
    *   Users stay logged in until logout or session expiry.
    *   Session validation ensures only logged-in users can perform actions.

### 2️⃣ Transaction Management (Full CRUD)

*   **Add Transactions**: Income and expense transactions with amount, category, and description.
*   **List Transactions**: View all transactions for a user.
*   **Edit Transactions**: Update any transaction’s details.
*   **Delete Transactions**: Remove a transaction if needed.
*   **Filter / Summarize**:
    *   By date or category.
    *   Supports calculations like current balance and tax.
    *   Example: Track monthly salary, rent, groceries, etc., and compute net flow automatically.

### 3️⃣ Debt Management

*   **Add Debts**: Track debts with description, amount, and due date.
*   **Mark Debt as Paid**: Update debt status when settled.
*   **List Debts**: View paid vs unpaid debts.
*   **Overdue Detection**: Identify debts that are past due.

### 4️⃣ Notifications (Intelligent & Automatic)

*   Manual and automatic notifications.
*   **Alerts include**:
    *   Upcoming debt due dates.
    *   Overdue debts.
    *   Low balance warnings.
    *   Tax due reminders.
*   **Notification Tracking**: Marked as read/unread.

### 5️⃣ Reports & Analytics (Backend Only)

*   **Monthly, Weekly, Yearly Summaries**:
    *   Income, expenses, net flow, and debts due.
*   **Category Summaries**: Total spent by category (Food, Rent, etc.)
*   **Income vs Expense Analysis**: Quick overview of financial health.

### 6️⃣ API Layer (FastAPI)

*   Fully wrapped backend logic into a REST API.
*   **Endpoints include**:
    *   `/auth/register` — register user
    *   `/auth/login` — login user and generate JWT tokens
    *   `/transactions` — add, edit, delete, list transactions
    *   `/debts` — add, mark paid, list debts
    *   `/reports` — monthly, weekly, yearly summaries, spending by category
    *   `/notifications` — list notifications, mark as read
*   **JWT Authentication**: Protect routes and secure data.
*   **Security & Production Readiness**:
    *   Input validation
    *   Error handling
    *   Environment variables for sensitive info
    *   Logging and optional rate limiting

### 7️⃣ Integration Ready

*   Fully ready for frontend consumption (React, Vue, mobile apps).
*   CORS enabled to allow requests from your frontend domain.
*   All backend logic is reusable as Python functions, so you can test locally in the shell or via API calls.

### Example Use Cases

*   Track your income, expenses, and debts in real-time.
*   Receive automatic notifications when bills are due or your balance is low.
*   Generate monthly, weekly, and yearly summaries.
*   Connect to a web or mobile frontend to provide a full personal finance dashboard.

## Technology Stack

*   **Backend**: Python
*   **Database**: PostgreSQL
*   **DB Connector**: `psycopg2`
*   **Password Hashing**: `bcrypt`

## Project Structure

```
BalanceIQBackend/
├── auth.py             # Handles user registration, login, and session management.
├── finance.py          # Manages financial transactions, balance, and tax calculations.
├── debts.py            # Manages debt tracking.
├── notifications.py    # Handles user notifications.
├── db.py               # Database connection helper.
├── schema.sql          # SQL script to create the database schema.
├── test_flow.py        # Script to run a simple end-to-end test of core features.
└── README.md           # You are here!
```

## Getting Started

Follow these instructions to get the backend service running on your local machine.

### Prerequisites

*   Python 3.8+
*   PostgreSQL

### Installation

1.  **Clone the repository:**
    ```sh
    git clone <your-repository-url>
    cd BalanceIQBackend
    ```

2.  **Create a `requirements.txt` file:**
    Create a file named `requirements.txt` and add the following lines:
    ```
    psycopg2-binary
    bcrypt
    ```

3.  **Install Python dependencies:**
    ```sh
    pip install -r requirements.txt
    ```

4.  **Set up the PostgreSQL Database:**
    Open `psql` or your preferred PostgreSQL client and run the following commands to create the database and user. The credentials match those in `db.py`.

    ```sql
    CREATE DATABASE balanceiq;
    CREATE USER balanceuser WITH PASSWORD 'balancepass';
    GRANT ALL PRIVILEGES ON DATABASE balanceiq TO balanceuser;
    ```

5.  **Create the Database Schema:**
    Run the `schema.sql` script to create the necessary tables. You will also need to add the `sessions` table manually, as it is required by `auth.py`.

    First, run the main schema file:
    ```sh
    psql -U balanceuser -d balanceiq -f schema.sql
    ```

    Then, connect to the database and run the following command to create the `sessions` table:
    ```sql
    \c balanceiq balanceuser
    CREATE TABLE IF NOT EXISTS sessions (
        id SERIAL PRIMARY KEY,
        user_id INT REFERENCES users(id) ON DELETE CASCADE,
        token TEXT UNIQUE NOT NULL,
        expires_at TIMESTAMP NOT NULL
    );
    ```

## Running the Application

To verify that everything is set up correctly, you can run the test script. This script simulates a user registering, logging in, and performing several actions.

```sh
python test_flow.py
```

You should see output detailing the registration, login, transaction additions, and final balance.

## Acknowledgements

This project was developed with significant guidance and assistance from AI coding assistants, particularly **Gemini** and **ChatGPT**. Their contributions were invaluable for:

*   Outlining the overall project structure and behavior.
*   Providing clear patterns for database interactions.
*   Implementing robust error handling and security practices, such as password hashing.
*   Generating foundational code and suggesting improvements.

Their help accelerated the development process and improved the quality of the final codebase.