# Loan Management System

## Table of Contents
- [Introduction](#introduction)
- [Features](#features)
- [Technologies Used](#technologies-used)
- [Installation](#installation)
- [API Endpoints](#api-endpoints)
  - [User Registration](#user-registration)
  - [Apply for Loan](#apply-for-loan)
  - [Make Payment](#make-payment)
  - [Get Statement](#get-statement)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Introduction
The Loan Management System is a Django-based application designed to facilitate the lending process for a loan service company. It allows users to register, apply for loans, manage repayments, and view their loan statements.

## Features
- User registration and credit score calculation.
- Apply for various types of loans (Car, Home, Education, Personal).
- EMI calculation and management.
- Payment processing and tracking.
- Statement generation for users to track payments and dues.

## Technologies Used
- **Django**: Web framework for building the application.
- **Django REST Framework**: For creating RESTful APIs.
- **Celery**: For asynchronous task management (credit score calculation).
- **SQLite**: Database to store user and loan data.
- **Pandas**: For processing user transaction data from CSV files.

## Installation
1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd loan-management-system
   ```

2. **Set up a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install requirements:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up your database:**
   - Configure your database settings in `settings.py`.
   - Run the migrations:
   ```bash
   python manage.py migrate
   ```

5. **Run the application:**
   ```bash
   python manage.py runserver
   ```

## API Endpoints
### User Registration
- **Endpoint**: `/api/register-user/`
- **Method**: `POST`
- **Request Body**:
  ```json
  {
      "name": "John Doe",
      "email": "john@example.com",
      "annual_income": 200000,
      "aadhar_id": "123456789012"
  }
  ```
- **Response**:
  ```json
  {
      "error": null,
      "unique_user_id": "some-uuid"
  }
  ```

### Apply for Loan
- **Endpoint**: `/api/apply-loan/`
- **Method**: `POST`
- **Request Body**:
  ```json
  {
      "unique_user_id": "some-uuid",
      "loan_type": "Car",
      "loan_amount": 500000,
      "interest_rate": 14,
      "term_period": 24,
      "disbursement_date": "2024-10-01"
  }
  ```
- **Response**:
  ```json
  {
      "message": "Loan application submitted successfully.",
      "loan_id": "loan-id"
  }
  ```

### Make Payment
- **Endpoint**: `/api/make-payment/`
- **Method**: `POST`
- **Request Body**:
  ```json
  {
      "loan_id": "loan-id",
      "amount": 25000
  }
  ```
- **Response**:
  ```json
  {
      "error": null
  }
  ```

### Get Statement
- **Endpoint**: `/api/get-statement/`
- **Method**: `GET`
- **Request Parameters**:
  - `loan_id`: "loan-id"
- **Response**:
  ```json
  {
      "error": null,
      "past_transactions": [
          {
              "date": "2024-10-01",
              "principal": 5000,
              "interest": 500,
              "amount_paid": 5500
          }
      ],
      "upcoming_transactions": [
          {
              "date": "2024-11-01",
              "amount_due": 5500
          }
      ]
  }
  ```

## Usage
After setting up the application and running the server, you can interact with the API using tools like Postman or cURL. Make sure to follow the request format outlined above for each endpoint.

## Contributing
Contributions are welcome! Please fork the repository and create a pull request for any enhancements or bug fixes.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.
