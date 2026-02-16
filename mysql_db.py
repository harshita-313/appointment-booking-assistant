from datetime import date, time
import mysql.connector
from typing import Any
from datetime import date, time
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import HumanMessage, AIMessage

# Connect to server
def get_db():
  return mysql.connector.connect(
    host="127.0.0.1",
    port=3307,
    user="root",
    password="",
    database="book_appointment"
)

###### FOR BOOKING ######
# Function to check for the availability of slot
def check_slot(date: date, time: time) -> None:
  db = get_db()
  cur = db.cursor()

  cur.execute("SELECT * FROM bookings WHERE date=%s and time=%s",(date, time))
  result = cur.fetchone()

  cur.close()
  db.close()
  return result

def fetch_id(id) -> None:
  db = get_db()
  cur = db.cursor()

  cur.execute("SELECT date, time FROM bookings WHERE id=%s",(id,))
  result = cur.fetchall()
  
  cur.close()
  db.close()
  return result

def insert_slot(session_id, name, email, date, time):
  db = get_db()
  cur = db.cursor()
  
  # Insert the row without id
  cur.execute("""
  INSERT INTO bookings (session_id, name, email, date, time)
  VALUES (%s, %s, %s, %s, %s)
  """, (session_id, name, email, date, time))
  db.commit()
  
  # Get last inserted auto_id
  cur.execute("SELECT LAST_INSERT_ID()")
  auto_id = cur.fetchone()[0]
  
  # Update id with prefix
  booking_id = f"CH{auto_id:04d}"
  cur.execute("UPDATE bookings SET id = %s WHERE auto_id = %s", (booking_id, auto_id))
  db.commit()
  
  cur.close()
  db.close()
  return f"Slot booked successfully! Your ID is {booking_id}"

###### FOR RESCHEDULING ######
def reschedule_slot(id, new_date, new_time, note):
  db = get_db()
  cur = db.cursor()

  # Check slot conflict
  cur.execute("""
    SELECT 1 FROM bookings
    WHERE date = %s AND time = %s AND id != %s
  """, (new_date, new_time, id))

  if cur.fetchone():
    cur.close()
    db.close()
    return "That time slot is already booked."

  # Update
  cur.execute("""
    UPDATE bookings
    SET date = %s, time = %s, note = %s
    WHERE id = %s
  """, (new_date, new_time, note, id))

  db.commit()

  if cur.rowcount==0:
    message = f"ID {id} does not exist"
  else:
    message =  f"Rescheduled successfully!"

  cur.close()
  db.close()
  return message

###### FOR CANCELLING ######
def cancel_slot(id, date, time):
  db = get_db()
  cur = db.cursor()

  query = """
  delete from bookings
  where id = %s and date = %s and time = %s
  """
  values = (id, date, time)
  cur.execute(query, values)

  db.commit()

  if cur.rowcount==0:
    message = f"Sorry, won't be able to cancel as either the ID or date or time does not exist."
  else:
    message = f"Slot cancelled successfully!"

  cur.close()
  db.close()
  return message

class MySQLChats(BaseChatMessageHistory):
  db = get_db()
  def __init__(self, session_id):
    self.session_id = session_id
    self.conn = get_db()
    self.cursor = self.conn.cursor()

  def add_message(self, message):
    role = "assistant" if isinstance (message, AIMessage) else "user"

    self.cursor.execute ("INSERT INTO chat_history (session_id, role, message) VALUES (%s, %s, %s)",
    (self.session_id, role, message.content))

    self.conn.commit()

  # Required by BaseChatMessageHistory
  def add_user_message(self, text: str):
    self.add_message(HumanMessage(content=text))

  # Required by BaseChatMessageHistory
  def add_ai_message(self, text: str):
    self.add_message(AIMessage(content=text))

  @property
  def messages(self):
    """LangChain reads chat history from here"""
    self.cursor.execute(
        "SELECT role, message FROM chat_history WHERE session_id = %s ORDER BY id ASC",
        (self.session_id,)
    )
    rows = self.cursor.fetchall()

    all_messages = []
    for role, text in rows:
      if role == "user":
          all_messages.append(HumanMessage(content=text))
      else:
          all_messages.append(AIMessage(content=text))

    return all_messages
  
  def clear(self):
    self.cursor.execute(
      "DELETE FROM chat_history WHERE session_id = %s",
      (self.session_id,)
    )
    self.conn.commit()

# TO CREATE TABLE CHAT HISTORY
# db = get_db()
# cur = db.cursor()
# query = """
# # CREATE TABLE chat_history (
# # id INT AUTO_INCREMENT PRIMARY KEY,
# # session_id VARCHAR(100) NOT NULL,
# # role CHAR(36),
# # message TEXT
# # );

# TO CREATE TABLE BOOKINGS
# create table bookings (
# auto_id INT AUTO_INCREMENT PRIMARY KEY,
# id CHAR(6) UNIQUE,
# session_id char(36),
# name varchar(255),
# email varchar(255) not null unique,
# date date,
# time time,
# note text
# )
# """
# cur.execute(query)
# db.commit()
# cur.close()
# db.close()


