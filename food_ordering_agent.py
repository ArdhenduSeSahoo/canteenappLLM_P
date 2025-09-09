from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from typing import Dict, List, TypedDict, Annotated
import json
import os
from dataclasses import dataclass, asdict

@dataclass
class FoodItem:
    name: str
    price: float
    category: str
    description: str = ""

# Sample menu data
MENU_ITEMS = [
    FoodItem("Margherita Pizza", 12.99, "Pizza", "Classic pizza with tomato sauce, mozzarella, and fresh basil"),
    FoodItem("Pepperoni Pizza", 14.99, "Pizza", "Pizza with pepperoni, tomato sauce, and mozzarella cheese"),
    FoodItem("Chicken Burger", 9.99, "Burger", "Grilled chicken breast with lettuce, tomato, and mayo"),
    FoodItem("Beef Burger", 11.99, "Burger", "Juicy beef patty with cheese, lettuce, tomato, and onions"),
    FoodItem("Caesar Salad", 8.99, "Salad", "Fresh romaine lettuce with Caesar dressing, croutons, and parmesan"),
    FoodItem("Pasta Carbonara", 13.99, "Pasta", "Creamy pasta with bacon, eggs, and parmesan cheese"),
    FoodItem("Fish Tacos", 10.99, "Tacos", "Grilled fish with cabbage slaw and chipotle mayo"),
    FoodItem("Chocolate Cake", 6.99, "Dessert", "Rich chocolate cake with chocolate frosting"),
]

class AgentState(TypedDict):
    messages: List[dict]
    user_intent: str
    cart_items: List[Dict]
    session_id: str
    current_step: str

class FoodOrderingAgent:
    def __init__(self):
        # Check for OpenAI API key
        if not os.getenv("OPENAI_API_KEY"):
            self.llm = None
            print("Warning: OPENAI_API_KEY not found. Using mock responses.")
        else:
            self.llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)
        
        self.menu_items = {item.name.lower(): item for item in MENU_ITEMS}
        self.carts = {}  # Session-based carts
        self.workflow = self._create_workflow()
    
    def _create_workflow(self):
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("understand_intent", self.understand_intent)
        workflow.add_node("show_menu", self.show_menu)
        workflow.add_node("add_to_cart", self.add_to_cart)
        workflow.add_node("view_cart", self.view_cart)
        workflow.add_node("confirm_order", self.confirm_order)
        workflow.add_node("general_chat", self.general_chat)
        
        # Set entry point
        workflow.set_entry_point("understand_intent")
        
        # Add conditional edges
        workflow.add_conditional_edges(
            "understand_intent",
            self.route_intent,
            {
                "menu": "show_menu",
                "add_item": "add_to_cart",
                "view_cart": "view_cart",
                "confirm_order": "confirm_order",
                "general": "general_chat"
            }
        )
        
        # All nodes end the conversation
        workflow.add_edge("show_menu", END)
        workflow.add_edge("add_to_cart", END)
        workflow.add_edge("view_cart", END)
        workflow.add_edge("confirm_order", END)
        workflow.add_edge("general_chat", END)
        
        return workflow.compile()
    
    def understand_intent(self, state: AgentState) -> AgentState:
        last_message = state["messages"][-1]["content"]
        
        # Simple intent classification
        message_lower = last_message.lower()
        
        if any(word in message_lower for word in ["menu", "items", "available", "what do you have"]):
            intent = "menu"
        elif any(word in message_lower for word in ["add", "order", "want", "get", "buy"]):
            intent = "add_item"
        elif any(word in message_lower for word in ["cart", "basket", "what's in", "show cart"]):
            intent = "view_cart"
        elif any(word in message_lower for word in ["confirm", "place order", "checkout", "confirm order"]):
            intent = "confirm_order"
        else:
            intent = "general"
        
        state["user_intent"] = intent
        return state
    
    def route_intent(self, state: AgentState) -> str:
        return state["user_intent"]
    
    def show_menu(self, state: AgentState) -> AgentState:
        menu_text = "🍽️ **Our Menu:**\n\n"
        
        categories = {}
        for item in MENU_ITEMS:
            if item.category not in categories:
                categories[item.category] = []
            categories[item.category].append(item)
        
        for category, items in categories.items():
            menu_text += f"**{category}:**\n"
            for item in items:
                menu_text += f"• {item.name} - ${item.price:.2f}\n  {item.description}\n\n"
        
        menu_text += "Just tell me what you'd like to add to your cart! 🛒"
        
        state["messages"].append({"role": "assistant", "content": menu_text})
        return state
    
    def add_to_cart(self, state: AgentState) -> AgentState:
        last_message = state["messages"][-1]["content"].lower()
        session_id = state["session_id"]
        
        if session_id not in self.carts:
            self.carts[session_id] = {"items": [], "total": 0.0}
        
        # Extract item names from the message
        added_items = []
        for item_name, item in self.menu_items.items():
            if item_name in last_message or any(word in last_message for word in item_name.split()):
                # Add to cart
                cart_item = {
                    "name": item.name,
                    "price": item.price,
                    "category": item.category,
                    "quantity": 1
                }
                self.carts[session_id]["items"].append(cart_item)
                self.carts[session_id]["total"] += item.price
                added_items.append(item.name)
        
        if added_items:
            response = f"Great! I've added {', '.join(added_items)} to your cart! 🛒\n\n"
            response += f"Current total: ${self.carts[session_id]['total']:.2f}\n\n"
            response += "Would you like to add anything else, view your cart, or confirm your order?"
        else:
            response = "I couldn't find that item on our menu. Would you like to see the menu again?"
        
        state["messages"].append({"role": "assistant", "content": response})
        return state
    
    def view_cart(self, state: AgentState) -> AgentState:
        session_id = state["session_id"]
        
        if session_id not in self.carts or not self.carts[session_id]["items"]:
            response = "Your cart is empty! 🛒 Would you like to see our menu?"
        else:
            cart = self.carts[session_id]
            response = "🛒 **Your Cart:**\n\n"
            for item in cart["items"]:
                response += f"• {item['name']} - ${item['price']:.2f}\n"
            response += f"\n**Total: ${cart['total']:.2f}**\n\n"
            response += "Would you like to add more items or confirm your order?"
        
        state["messages"].append({"role": "assistant", "content": response})
        return state
    
    def confirm_order(self, state: AgentState) -> AgentState:
        session_id = state["session_id"]
        
        if session_id not in self.carts or not self.carts[session_id]["items"]:
            response = "Your cart is empty! Please add some items before confirming your order."
        else:
            cart = self.carts[session_id]
            response = f"🎉 Order confirmed! Your total is ${cart['total']:.2f}\n\n"
            response += "**Order Summary:**\n"
            for item in cart["items"]:
                response += f"• {item['name']} - ${item['price']:.2f}\n"
            response += "\nYour order will be ready in 15-20 minutes. Thank you for ordering with us!"
            
            # Clear the cart after confirming
            self.carts[session_id] = {"items": [], "total": 0.0}
        
        state["messages"].append({"role": "assistant", "content": response})
        return state
    
    def general_chat(self, state: AgentState) -> AgentState:
        if self.llm:
            # Use OpenAI for general conversation
            system_prompt = """You are a friendly food ordering assistant. You help customers order food from a restaurant. 
            Be helpful and guide them towards ordering. Keep responses concise and friendly."""
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=state["messages"][-1]["content"])
            ]
            
            response = self.llm.invoke(messages)
            response_text = response.content
        else:
            # Fallback response when OpenAI is not available
            response_text = "Hello! I'm here to help you order food. Would you like to see our menu or do you have any questions about our offerings?"
        
        state["messages"].append({"role": "assistant", "content": response_text})
        return state
    
    async def process_message(self, message: str, session_id: str = "default"):
        # Initialize cart if it doesn't exist
        if session_id not in self.carts:
            self.carts[session_id] = {"items": [], "total": 0.0}
        
        # Create initial state
        state = {
            "messages": [{"role": "user", "content": message}],
            "user_intent": "",
            "cart_items": self.carts[session_id]["items"],
            "session_id": session_id,
            "current_step": "start"
        }
        
        # Run the workflow
        result = self.workflow.invoke(state)
        
        # Get the assistant's response
        assistant_message = result["messages"][-1]["content"]
        
        return {
            "response": assistant_message,
            "cart_items": self.carts[session_id]["items"],
            "total_amount": self.carts[session_id]["total"]
        }
    
    def get_cart(self, session_id: str = "default"):
        if session_id not in self.carts:
            self.carts[session_id] = {"items": [], "total": 0.0}
        return self.carts[session_id]
    
    def clear_cart(self, session_id: str = "default"):
        self.carts[session_id] = {"items": [], "total": 0.0}