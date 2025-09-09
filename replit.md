# Food Ordering Chatbot

## Overview
A sophisticated food ordering chatbot built with FastAPI, LangGraph, and OpenAI integration. The chatbot helps customers browse menus, add items to cart, and complete orders through natural language conversations.

## Current State
- ✅ Fully functional chatbot with web interface
- ✅ Cart management (add items, view cart, confirm orders)
- ✅ LangGraph workflow for intelligent conversation flow
- ✅ OpenAI integration for natural language processing
- ✅ REST API endpoints for chat and cart management
- ✅ Responsive web interface

## Project Architecture
- **Backend**: FastAPI server with RESTful endpoints
- **AI Engine**: LangGraph workflow with OpenAI GPT-3.5-turbo
- **Frontend**: HTML/CSS/JavaScript chat interface
- **State Management**: Session-based cart storage

## Recent Changes (September 9, 2025)
- Created complete food ordering chatbot system
- Implemented LangGraph workflow with intent recognition
- Added cart management functionality
- Set up OpenAI integration with proper API key handling
- Created responsive web interface
- Configured FastAPI server with CORS and static file serving

## Features
1. **Menu Display**: Shows categorized food items with descriptions and prices
2. **Cart Management**: Add items, view cart contents, calculate totals
3. **Order Confirmation**: Complete order placement with cart clearing
4. **Natural Language**: Understands various ways of expressing food ordering intents
5. **Session Support**: Multiple users can maintain separate carts

## File Structure
- `main.py`: FastAPI application with API endpoints
- `food_ordering_agent.py`: LangGraph workflow and AI logic
- `static/index.html`: Web interface for the chatbot
- `replit.md`: Project documentation

## API Endpoints
- `GET /`: Serves the web interface
- `POST /chat`: Process chat messages and return responses
- `GET /cart/{session_id}`: Get cart contents for a session
- `DELETE /cart/{session_id}`: Clear cart for a session

## Menu Items
The system includes a sample menu with:
- Pizzas (Margherita, Pepperoni)
- Burgers (Chicken, Beef)
- Salads (Caesar)
- Pasta (Carbonara)
- Tacos (Fish)
- Desserts (Chocolate Cake)

## User Preferences
- Uses production-ready FastAPI setup
- Implements proper error handling and CORS
- Maintains clean, documented code structure
- Follows REST API conventions