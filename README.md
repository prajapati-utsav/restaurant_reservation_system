# restaurant_reservation_system
Restaurant Table Reservation System

# Restaurant Reservation System (FastAPI)

## Overview
A FastAPI-based restaurant reservation system with features for:

- Customer management (preferences, dietary requirements, visit history)
- Table management (availability, combinable tables, locations)
- Reservation management (allocation, conflict prevention, merge/demerge tables)
- Daily reservation reports
- MySQL initialization script with dummy data
- Unit tests for allocation and conflict logic

---

## Requirements

- Python 3.10+
- MySQL server (8.0+ recommended)
- pip (Python package manager)

---

## Setup (Local)

### 1. Clone the repository
git clone <repo-url>
cd restaurant_reservation

### 2. Create a virtual environment and install dependencies
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

### 3. Configure MySQL Database
Create database and user:
CREATE DATABASE restaurant_db;
CREATE USER 'restaurant_user'@'localhost' IDENTIFIED BY 'password';
GRANT ALL PRIVILEGES ON restaurant_db.* TO 'restaurant_user'@'localhost';
FLUSH PRIVILEGES;

### Populate database with dummy data: Instead of running the SQL file manually, you can use the Python script:
python sql/run_sql_init.py

### You should see output like:
Connected to MySQL server.
SQL file executed successfully.
Connection closed.
### This script reads sql/init_mysql.sql and inserts tables, operating hours, and dummy customers.

### Update .env file in project root:
DB_USER=restaurant_user
DB_PASSWORD=password
DB_HOST=localhost
DB_PORT=3306
DB_NAME=restaurant_db

### 4. Run the Applicatione
uvicorn main:app --reload
Open http://127.0.0.1:8069/docs to view the interactive API documentation.

### 5. Run Tests
pytest tests/
Ensure your virtual environment is active.
Tests cover table allocation, reservation conflicts, customer conflicts, and utility functions.
daily_report endpoint generates daily reservation summaries.
Merge and demerge tables are supported for group reservations.

### Notes
Ensure MySQL server is running before initializing the database.
Python script run_sql_init.py ensures consistent dummy data for local testing.
All reservation conflicts are validated before creating or updating reservations.
Tables can be merged/demerged dynamically for group bookings.