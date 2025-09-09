from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Dict, Optional
import uvicorn
import os
from food_ordering_agent import FoodOrderingAgent

app = FastAPI(title="Food Ordering Chatbot", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize the food ordering agent
food_agent = FoodOrderingAgent()

class ChatMessage(BaseModel):
    message: str
    session_id: Optional[str] = "default"

class ChatResponse(BaseModel):
    response: str
    cart_items: List[Dict]
    total_amount: float

@app.get("/")
async def root():
    return FileResponse("static/index.html")

@app.post("/chat", response_model=ChatResponse)
async def chat(chat_message: ChatMessage):
    try:
        session_id = chat_message.session_id or "default"
        response = await food_agent.process_message(
            chat_message.message, 
            session_id
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/cart/{session_id}")
async def get_cart(session_id: str = "default"):
    cart = food_agent.get_cart(session_id)
    return {"cart_items": cart["items"], "total_amount": cart["total"]}

@app.delete("/cart/{session_id}")
async def clear_cart(session_id: str = "default"):
    food_agent.clear_cart(session_id)
    return {"message": "Cart cleared successfully"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)