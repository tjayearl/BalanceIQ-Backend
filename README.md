# BalanceIQ Backend

BalanceIQ is a robust backend service for a personal finance management application. It provides core functionalities for handling users, transactions, debts, and notifications through a set of modular Python scripts that interact with a PostgreSQL database.

## Features

*   **User Authentication**: Secure user registration and login using `bcrypt` for password hashing.
*   **Session Management**: Creation of persistent, expiring user sessions for stateful interactions.
*   **Transaction Management**: Add, edit, delete, and list income and expense transactions.
*   **Financial Calculations**: Automatically calculate user balance based on transactions and provide simple tax estimations.
*   **Debt Tracking**: Manage personal debts, including adding new debts, listing them by status (paid/unpaid), and flagging overdue debts.
*   **Notifications**: A simple system to create and retrieve user-specific notifications.

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