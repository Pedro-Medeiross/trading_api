import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from connection import engine

# Import Base from models to create all tables
from models.bot_options import Base as BotOptionsBase
from models.brokerages import Base as BrokeragesBase
from models.trade_order_info import Base as TradeOrderInfoBase
from models.user import Base as UserBase
from models.user_brokerages import Base as UserBrokeragesBase

# Router imports
from routes.user_router import user_router
from routes.bot_options_router import bot_options_router
from routes.trade_order_info_router import trade_order_info_router
from routes.user_brokerages_router import user_brokerages_router
from routes.brokerages_router import brokerages_router
from routes.site_options_router import site_options_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def initialize_database() -> None:
    """
    Create all database tables if they don't exist.

    This function uses the Base classes from each model to create
    the corresponding database tables.
    """
    try:
        # Create tables for all models
        BotOptionsBase.metadata.create_all(engine)
        BrokeragesBase.metadata.create_all(engine)
        TradeOrderInfoBase.metadata.create_all(engine)
        UserBase.metadata.create_all(engine)
        UserBrokeragesBase.metadata.create_all(engine)

        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")


# Initialize the FastAPI application
app = FastAPI(
    title="Trading API",
    description="API for trading system with AI and automations",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Define allowed origins for CORS
origins = [
    "http://127.0.0.1:3000",
    "http://localhost:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "https://api.multitradingob.com",
    "https://multitradingob.com",
    "https://www.multitradingob.com",
    "https://bot.multitradingob.com",
]

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
initialize_database()

# Include routers
app.include_router(user_router, prefix='/user', tags=['Users'])
app.include_router(bot_options_router, prefix='/bot-options', tags=['Bot Options'])
app.include_router(trade_order_info_router, prefix='/trade-order-info', tags=['Trade Orders'])
app.include_router(user_brokerages_router, prefix='/user-brokerages', tags=['User Brokerages'])
app.include_router(brokerages_router, prefix='/brokerages', tags=['Brokerages'])
app.include_router(site_options_router, prefix='/site-options', tags=['Site Options'])


@app.get("/", tags=["Health Check"])
def health_check():
    """
    Health check endpoint to verify the API is running.

    Returns:
        Dict with status information
    """
    return {
        "status": "online",
        "message": "Trading API is running",
        "version": "1.0.0"
    }
