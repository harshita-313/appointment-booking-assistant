# AI Appointment Booking Assistant

An AI-powered appointment booking assistant built using LangChain and LangGraph.
The system uses a structured, tool-driven approach to handle booking, rescheduling, cancellation, and availability checks with strict validation and database-backed session history.

---

## Overview

This project demonstrates a deterministic, tool-based LLM agent designed for real-world appointment management.
It ensures reliable scheduling by validating time slots, preventing invalid bookings, and maintaining conversation history in a MySQL database.

The assistant is restricted to appointment-related tasks to maintain accuracy and predictable behavior.

---

## Key Features

* Book new appointments
* Reschedule existing bookings
* Cancel appointments
* Check slot availability
* Retrieve booking details using booking ID
* Tool-driven LLM workflow (no hallucinated bookings)
* MySQL-backed chat and booking history
* Real-time streaming responses

---

## Tech Stack

* **Language:** Python
* **LLM:** OpenAI
* **Frameworks:** LangChain, LangGraph
* **Database:** MySQL
* **API Layer:** FastAPI
* **Environment Management:** python-dotenv

---

## System Design Highlights

* Deterministic, tool-based agent workflow
* Strict prompt rules to control assistant behavior
* Database-backed session memory
* Slot validation before booking
* Modular tool architecture for each operation:

  * Check availability
  * Insert booking
  * Reschedule
  * Cancel
  * Fetch booking data

---

## Project Structure

```
appointment-booking-assistant/
│
├── api.py              # API entry point
├── main.py             # Core assistant logic
├── mysql_db.py         # Database operations
├── prompt.md           # System prompt and behavior rules
├── templates/          # Frontend templates
├── requirements.txt    # Dependencies
├── .gitignore
└── README.md
```

---

## Appointment Rules

* Weekdays only (Monday–Friday)
* Available time slots:

  * 10:00
  * 12:00
  * 14:00
  * 16:00
* No past bookings
* All slots validated via tools

---

## Example User Requests

* “Book an appointment tomorrow at 10:00”
* “Reschedule my appointment”
* “Cancel my booking”
* “Check availability for 2026-03-10 at 12:00”

---

