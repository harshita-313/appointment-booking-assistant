import os
import re
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_community.tools import tool
from mysql_db import insert_slot, check_slot, MySQLChats, reschedule_slot, cancel_slot, fetch_id
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, AIMessageChunk, BaseMessage, ToolMessage
from datetime import datetime
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from typing import TypedDict, List, Annotated
from langchain_core.messages import BaseMessage
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.graph.message import add_messages

current_dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

load_dotenv()
openai_api = os.getenv('OPENAI_API_KEY')
openai_model = os.getenv('OPENAI_MODEL')
temperature = os.getenv('TEMPERATURE')

template = open('prompt.md','r',encoding='utf-8').read()

prompt = PromptTemplate (
    input_variables=["chat_history","input","current_dt"],
    template=template   
)

llm = ChatOpenAI(
    model = openai_model,
    streaming=True,
    temperature= temperature
)

def is_weekend(date_str):
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    return dt.weekday() >= 5 
    
@tool
def check_time_slot(input: str) -> str:
    """
    Use this tool to check if the date and time given by the user is already present in the database.
    If not already, then the slot is available. Weekends are not available.

    Date must be in YYYY-MM-DD format and time in HH:MM format.
    Example: 2025-12-12, 03:00
    """

    try:
        date_str, time_str = [msg.strip() for msg in input.split(",")]

        booking_dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
        current_dt = datetime.now()

        # Block past bookings
        if booking_dt < current_dt:
            return "Cannot book in the past!"
        
        if time_str not in ['10:00','12:00','14:00','16:00']:
            return """Time not available \nAvailable time slots - '10:00','12:00','14:00','16:00'"""
        
        if is_weekend(date_str):
            return f"{date_str} is a weekend. Appointments are not available on weekends."

        existing_slot = check_slot(date_str, time_str)
        if existing_slot:
            return f"Slot on {date_str} at {time_str} is not available."
        else:
            return f"Slot on {date_str} at {time_str} is available for booking."

    except Exception as e:
        return f"""Error! Please use the format: YYYY-MM-DD, HH:MM\nDetails: {str(e)}"""

@tool
def fetch_data(input: str) -> str:
    """
    Call this tool if user is asking for slots booked for a particluar id 

    Expected user input: booking ID
    Example: CH0001 
    """

    booking_id = input.strip()

    try:
        result = fetch_id(booking_id)
        if not result:
            return f"No bookings found for ID {booking_id}."
        # Convert DB rows into a human-readable response
        response_lines = [
            f"Date: {row[0]}, Time: {row[1]}"
            for row in result
        ]
        return (
            f"Here are the bookings for ID {booking_id}:\n"
            + "\n".join(response_lines)
        )
    except Exception as e:
        return f"Error fetching bookings for ID {booking_id}. Details: {str(e)}"

SESSION_CONTEXT = {}

@tool
def insert_data(input: str) -> str:
    """
    Use this tool to book a slot AFTER availability has been confirmed.

    Expected user input format: "name, email, date, time"
    Example: Harshita, harshita@gmail.com, 2025-10-03, 07:45
    """
    try:
        session_id = SESSION_CONTEXT.get("session_id")
        if not session_id:
            return "Error: No session ID found. Try again."

        parts = [p.strip() for p in input.split(",")]
        if len(parts) != 4:
            return "Invalid format. Please provide: name, email, date(YYYY-MM-DD), time(HH:MM)"

        name, email, date_str, time_str = parts

        if is_weekend(date_str):
            return f"{date_str} is a weekend. Appointments are not available on weekends."
        
        if not name or not email:
            return f"Name or email not given."

        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

        if not re.match(email_pattern, email):
            return f"Please provide a valid email"
        
        if time_str not in ['10:00','12:00','14:00','16:00']:
            return """Time not available. Available time slots - '10:00','12:00','14:00','16:00'"""
        
        return insert_slot(session_id, name, email, date_str, time_str)

    except Exception as e:
        return f"Booking failed due to a system error: {str(e)}"
    
@tool
def reschedule(input:str) -> str:
    """
    Use this tool to reschedule an existing booking.

    Also asks for note/reason from the user for rescheduling (not compulsory for user to answer).

    Expected user input format: "id, new_date, new_time, note"
    Example: CH0001, 2025-12-15, 14:00, note from the user

    """
    try:
        parts = [p.strip() for p in input.split(",")]
        if len(parts) != 4:
            return "Error! Format: YYYY-MM-DD, HH:MM"

        booking_id, new_date, new_time, note = parts

        if is_weekend(new_date):
            return f"{new_date} is a weekend. Appointments are not available on weekends."

        if new_time not in ['10:00','12:00','14:00','16:00']:
            return """Time not available. Available time slots - '10:00','12:00','14:00','16:00'"""

        result = reschedule_slot(booking_id, new_date, new_time, note)

        return result

    except Exception as e:
        return f"Reschedule failed due to a system error: {str(e)}"
       
@tool
def cancel(input:str) -> str:
    """
    Use this tool to cancel/delete an existing booking.

    Expected user input format: "id, date, time"
    Example: CH0001, 2025-12-15, 14:00 
    """

    try:
        parts = [p.strip() for p in input.split(",")]
        if len(parts) != 3:
            return "Error! Format: YYYY-MM-DD, HH:MM"

        booking_id, date_str, time_str = parts
        result = cancel_slot(booking_id, date_str, time_str)
        return result

    except Exception as e:
        return f"Cancellation failed due to some a system error: {str(e)}"
    
@tool
def send_mail(input: str) -> str:
    """
    Sends a confirmation email.
    Input should be a short email payload or message.
    """

    return "EMAIL_SENT"

tools = [check_time_slot, fetch_data, insert_data, reschedule, cancel, send_mail]

# State
class ChatState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]

llm_with_tools = llm.bind_tools(tools)

def chat_node(state: ChatState):
    messages = state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": messages + [response]}

tool_node = ToolNode(tools)

graph = StateGraph(ChatState)

graph.add_node("chat_node", chat_node)
graph.add_node("tools", tool_node)

graph.add_edge(START, "chat_node")

graph.add_conditional_edges("chat_node", tools_condition)

graph.add_edge("tools", "chat_node")
app_graph = graph.compile()

def load_history(session_id: str):
    store = MySQLChats(session_id=session_id)
    return store.messages

def save_user_message(session_id: str, text: str):
    store = MySQLChats(session_id=session_id)
    store.add_user_message(text)

def save_ai_message(session_id: str, text: str):
    store = MySQLChats(session_id=session_id)
    store.add_ai_message(text)

# Building conversation
async def stream_chat(user_input: str, session_id: str):
    SESSION_CONTEXT["session_id"] = session_id

    # Load history
    history = load_history(session_id)

    # Save user message once
    save_user_message(session_id, user_input)

    # Build initial state
    initial_state = {
        "messages": history + [HumanMessage(content=user_input)]
    }

    assistant_text = ""

    # Stream tokens
    async for event in app_graph.astream_events(initial_state):
        if event["event"] == "on_chat_model_stream":
            chunk = event["data"]["chunk"]
            token = chunk.content or ""
            assistant_text += token
            yield token

    # Save assistant message once (AFTER streaming)
    if assistant_text.strip():
        save_ai_message(session_id, assistant_text)
