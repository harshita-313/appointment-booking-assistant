from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from main import stream_chat, SESSION_CONTEXT
from fastapi.middleware.cors import CORSMiddleware
from typing import Any
from langchain_core.messages import HumanMessage, AIMessage
from mysql_db import MySQLChats

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

class TakeInput(BaseModel):
    input: str
    session_id: str

class GetResponse(BaseModel):
    response: Any

@app.get("/history/{session_id}")
def get_history(session_id: str):
    history = MySQLChats(session_id).messages

    return [
        {
            "role": "🤖" if isinstance(msg, AIMessage) else "👤",
            "content": msg.content
        }
        for msg in history
    ]

@app.post("/chat/stream")
async def chat_stream(req: TakeInput):

    async def token_gen():
        async for event in stream_chat(req.input, req.session_id):
            yield event

    return StreamingResponse(token_gen(), media_type="text/plain")
