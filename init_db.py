#!/usr/bin/env python3
"""
Database initialization script for GlassRain.
This script creates necessary tables if they don't exist.
"""

import os
import psycopg2
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("init_db.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def get_db_connection():
    """Get a connection to the PostgreSQL database"""
    try:
        conn = psycopg2.connect(
            os.environ.get('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/postgres')
        )
        return conn
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        return None

def init_db():
    """Initialize the database schema"""
    try:
        conn = get_db_connection()
        if not conn:
            logger.error("Failed to connect to database")
            sys.exit(1)
        
        with conn.cursor() as cur:
            # Create users table if it doesn't exist
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    updated_at TIMESTAMP
                )
            """)
            
            # Create homes table if it doesn't exist
            cur.execute("""
                CREATE TABLE IF NOT EXISTS homes (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL REFERENCES users(id),
                    address TEXT NOT NULL,
                    latitude NUMERIC(10, 6),
                    longitude NUMERIC(10, 6),
                    place_name TEXT,
                    square_feet INTEGER,
                    model_data JSONB,
                    created_at TIMESTAMP NOT NULL,
                    updated_at TIMESTAMP,
                    CONSTRAINT unique_user_address UNIQUE (user_id, address)
                )
            """)
            
            # Create service_categories table if it doesn't exist
            cur.execute("""
                CREATE TABLE IF NOT EXISTS service_categories (
                    id TEXT PRIMARY KEY,
                    name TEXT UNIQUE NOT NULL,
                    description TEXT,
                    icon TEXT
                )
            """)
            
            # Create services table if it doesn't exist
            cur.execute("""
                CREATE TABLE IF NOT EXISTS services (
                    id TEXT PRIMARY KEY,
                    category_id TEXT NOT NULL REFERENCES service_categories(id),
                    name TEXT NOT NULL,
                    description TEXT,
                    pricing_model TEXT NOT NULL,
                    base_price NUMERIC(10, 2) NOT NULL,
                    CONSTRAINT unique_category_service UNIQUE (category_id, name)
                )
            """)
            
            # Create service_tiers table if it doesn't exist
            cur.execute("""
                CREATE TABLE IF NOT EXISTS service_tiers (
                    id TEXT PRIMARY KEY,
                    name TEXT UNIQUE NOT NULL,
                    description TEXT,
                    multiplier NUMERIC(3, 2) NOT NULL
                )
            """)
            
            # Commit all changes
            conn.commit()
            
            logger.info("Database schema initialized successfully")
            
            # Check if basic service tiers exist, create them if not
            cur.execute("SELECT * FROM service_tiers")
            tiers = cur.fetchall()
            
            if not tiers:
                logger.info("Creating default service tiers...")
                
                cur.execute("""
                    INSERT INTO service_tiers (id, name, description, multiplier)
                    VALUES 
                        ('tier_silver', 'Silver', 'Solo contractors, affordable option', 1.0),
                        ('tier_gold', 'Gold', 'Small teams, quality service', 1.5),
                        ('tier_diamond', 'Diamond', 'Premium, experienced companies', 2.0)
                """)
                
                conn.commit()
                logger.info("Default service tiers created")
            
    except Exception as e:
        logger.error(f"Database initialization error: {e}")
        sys.exit(1)
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    logger.info("Starting database initialization...")
    init_db()
    logger.info("Database initialization complete")

def init_store_products():
    """Initialize store and product tables"""
    try:
        conn = get_db_connection()
        if not conn:
            logger.error("Failed to connect to database")
            sys.exit(1)
        
        with conn.cursor() as cur:
            # Create stores table if it doesn't exist
            cur.execute("""
                CREATE TABLE IF NOT EXISTS stores (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    logo_url TEXT,
                    website_url TEXT,
                    created_at TIMESTAMP NOT NULL
                )
            """)
            
            # Create products table if it doesn't exist
            cur.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    id TEXT PRIMARY KEY,
                    store_id TEXT NOT NULL REFERENCES stores(id),
                    name TEXT NOT NULL,
                    description TEXT,
                    price NUMERIC(10, 2) NOT NULL,
                    category TEXT,
                    image_url TEXT,
                    ar_model_url TEXT,
                    dimensions JSONB,
                    created_at TIMESTAMP NOT NULL,
                    CONSTRAINT unique_store_product UNIQUE (store_id, name)
                )
            """)
            
            # Commit changes
            conn.commit()
            logger.info("Store and product tables initialized successfully")
            
    except Exception as e:
        logger.error(f"Store and product initialization error: {e}")
    finally:
        if conn:
            conn.close()

# Update main function to call both initialization functions
if __name__ == "__main__":
    logger.info("Starting database initialization...")
    init_db()
    init_store_products()
    logger.info("Database initialization complete")
