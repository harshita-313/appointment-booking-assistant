# AI Appointment Booking Assistant

An AI-powered appointment booking assistant built using LangChain and LangGraph.
The system uses a structured, tool-driven architecture to handle booking, rescheduling, cancellation, and availability checks with strict validation and database-backed session history.

---

## Overview

This project demonstrates a deterministic, tool-based LLM agent designed for real-world appointment management.
Instead of relying on free-form AI responses, the assistant uses structured tools and a controlled prompt to ensure reliable, predictable, and accurate scheduling.

The assistant is restricted to appointment-related tasks to prevent hallucinations and maintain domain-specific behavior.

---

## Key Features

* Book new appointments
* Reschedule existing bookings
* Cancel appointments
* Check slot availability
* Retrieve booking details using booking ID
* Tool-driven LLM workflow (no fake bookings)
* MySQL-backed chat and booking history
* Real-time streaming responses

---

## Tech Stack

### Python

Core application logic and tool implementations.

### OpenAI

Provides the language model used to interpret user intent and drive the conversation.

### LangChain

Used for:

* LLM integration
* Tool creation
* Prompt management
* Message handling

### LangGraph

Used to:

* Build a deterministic agent workflow
* Control transitions between the chat model and tools
* Ensure structured execution instead of free-form agent behavior

### MySQL

Used for:

* Storing appointment bookings
* Maintaining session-based chat history
* Fetching, rescheduling, and canceling appointments

### FastAPI

Provides an API interface to interact with the assistant from a frontend or client.

### python-dotenv

Loads environment variables such as API keys and model configuration.

---

## System Architecture

1. User sends a message.
2. LangGraph routes the message to the chat node.
3. The LLM determines whether a tool is needed.
4. If required, the appropriate tool is executed:

   * Check availability
   * Insert booking
   * Reschedule
   * Cancel
   * Fetch data
5. Results are returned to the user.
6. Chat history is stored in MySQL.

---

## Project Structure

```
appointment-booking-assistant/
│
├── api.py              # API entry point
├── main.py             # Core assistant logic and LangGraph workflow
├── mysql_db.py         # Database operations
├── prompt.md           # System prompt and assistant rules
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

