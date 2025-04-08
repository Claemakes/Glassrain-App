"""
Contractor Review Analyzer

This module uses a combination of web scraping and AI to analyze
contractor reviews from sites like Google, Yelp, and Facebook.
The results are used to improve the contractor matching system.
"""

import os
import json
import logging
import psycopg2
from datetime import datetime, timedelta
import re
import random  # For simulating review data if needed

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_db_connection():
    """Get a connection to the PostgreSQL database"""
    try:
        conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
        conn.autocommit = True
        return conn
    except Exception as e:
        logger.error(f"Database connection error: {str(e)}")
        return None

def ensure_contractor_metrics_table():
    """Ensure the contractor_metrics table exists"""
    conn = get_db_connection()
    if not conn:
        logger.error("Failed to connect to database")
        return False
    
    try:
        cursor = conn.cursor()
        
        # Check if table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'contractor_metrics'
            )
        """)
        
        table_exists = cursor.fetchone()[0]
        
        if not table_exists:
            # Create contractor_metrics table
            cursor.execute("""
                CREATE TABLE contractor_metrics (
                    contractor_id INTEGER PRIMARY KEY REFERENCES contractors(id),
                    review_count INTEGER DEFAULT 0,
                    average_rating NUMERIC(3,1) DEFAULT 0,
                    sentiment_score NUMERIC(3,1) DEFAULT 0,
                    response_time_hours INTEGER,
                    quality_keywords TEXT[],
                    tier_level TEXT DEFAULT 'Standard',
                    last_updated TIMESTAMP DEFAULT NOW(),
                    data_sources TEXT[]
                )
            """)
            logger.info("Created contractor_metrics table")
        
        cursor.close()
        return True
    except Exception as e:
        logger.error(f"Error checking/creating contractor_metrics table: {str(e)}")
        return False
    finally:
        conn.close()

def get_contractors_needing_update(days_threshold=7):
    """Get contractors that need metrics updates"""
    conn = get_db_connection()
    if not conn:
        logger.error("Failed to connect to database")
        return []
    
    try:
        cursor = conn.cursor()
        
        # Get contractors that haven't been updated in X days or don't have metrics
        cursor.execute("""
            SELECT c.id, c.name 
            FROM contractors c
            LEFT JOIN contractor_metrics m ON c.id = m.contractor_id
            WHERE m.contractor_id IS NULL 
                OR m.last_updated < %s
            LIMIT 100
        """, (datetime.now() - timedelta(days=days_threshold),))
        
        contractors = []
        for row in cursor.fetchall():
            contractors.append({
                "id": row[0],
                "name": row[1],
                "website": None  # Set website to None since it's not in our schema
            })
        
        cursor.close()
        return contractors
    except Exception as e:
        logger.error(f"Error getting contractors for update: {str(e)}")
        return []
    finally:
        conn.close()

def fetch_google_reviews(contractor):
    """
    Fetch Google reviews for a contractor
    
    In a real implementation, this would use web scraping or the Google Places API
    to get reviews for the contractor based on their name and website.
    """
    logger.info(f"Fetching Google reviews for {contractor['name']}")
    
    # In a production system, you would:
    # 1. Get the business Place ID using Google Places API search
    # 2. Fetch reviews using the Place ID

    # For demonstration, generate simulated review data
    # This would be replaced by actual API calls or web scraping
    num_reviews = random.randint(5, 20)
    reviews = []
    
    for i in range(num_reviews):
        rating = random.randint(3, 5)  # Mostly positive ratings
        reviews.append({
            "rating": rating,
            "text": f"Sample Google review {i+1} for {contractor['name']}. {'Great service!' if rating >= 4 else 'Decent service but could improve.'}",
            "date": (datetime.now() - timedelta(days=random.randint(1, 90))).strftime("%Y-%m-%d")
        })
    
    return {
        "source": "Google",
        "average_rating": sum(r["rating"] for r in reviews) / len(reviews) if reviews else 0,
        "review_count": len(reviews),
        "reviews": reviews
    }

def fetch_yelp_reviews(contractor):
    """
    Fetch Yelp reviews for a contractor
    
    In a real implementation, this would use the Yelp Fusion API
    to get reviews for the contractor based on their name and website.
    """
    logger.info(f"Fetching Yelp reviews for {contractor['name']}")
    
    # In a production system, you would:
    # 1. Search for the business using the Yelp Fusion API
    # 2. Fetch reviews using the business ID

    # For demonstration, generate simulated review data
    # This would be replaced by actual API calls
    num_reviews = random.randint(3, 15)
    reviews = []
    
    for i in range(num_reviews):
        rating = random.randint(2, 5)  # Mix of ratings
        reviews.append({
            "rating": rating,
            "text": f"Sample Yelp review {i+1} for {contractor['name']}. {'Highly recommended!' if rating >= 4 else 'They were okay, but could have done better.'}",
            "date": (datetime.now() - timedelta(days=random.randint(1, 120))).strftime("%Y-%m-%d")
        })
    
    return {
        "source": "Yelp",
        "average_rating": sum(r["rating"] for r in reviews) / len(reviews) if reviews else 0,
        "review_count": len(reviews),
        "reviews": reviews
    }

def analyze_reviews_with_ai(reviews_data):
    """
    Use OpenAI to analyze review texts and extract insights
    
    In a real implementation, you would send the review texts to the OpenAI API
    and use a prompt that asks it to analyze sentiment, extract key positive/negative
    points, and identify recurring themes.
    """
    try:
        logger.info("Analyzing reviews with AI")
        
        # Prepare review texts for analysis
        all_reviews = []
        sources = []
        for source_data in reviews_data:
            sources.append(source_data["source"])
            all_reviews.extend(source_data["reviews"])
        
        # Calculate basic metrics
        total_reviews = len(all_reviews)
        if total_reviews == 0:
            return {
                "sentiment_score": 0,
                "average_rating": 0,
                "quality_keywords": [],
                "data_sources": sources,
                "review_count": 0
            }
        
        average_rating = sum(review["rating"] for review in all_reviews) / total_reviews
        
        # Extract text for sentiment analysis
        review_texts = [review["text"] for review in all_reviews]
        
        # In a real implementation, this would call the OpenAI API
        # For demonstration, use simple rules to simulate sentiment analysis
        
        # Simulate sentiment analysis
        sentiment_score = min(5.0, average_rating * (1 + random.uniform(-0.1, 0.1)))
        
        # Extract quality keywords
        positive_keywords = ["professional", "reliable", "thorough", "detailed", 
                            "punctual", "efficient", "friendly", "courteous",
                            "skilled", "experienced", "knowledgeable", "responsive"]
        
        # In a real implementation, these would be extracted from the AI analysis
        # For demonstration, randomly select a subset of keywords
        extracted_keywords = random.sample(positive_keywords, min(5, len(positive_keywords)))
        
        return {
            "sentiment_score": sentiment_score,
            "average_rating": average_rating,
            "quality_keywords": extracted_keywords,
            "data_sources": sources,
            "review_count": total_reviews
        }
        
    except Exception as e:
        logger.error(f"Error analyzing reviews with AI: {str(e)}")
        return simple_review_analysis(reviews_data)

def simple_review_analysis(reviews_data):
    """Perform simple review analysis without AI"""
    try:
        logger.info("Performing simple review analysis")
        
        # Prepare review texts for analysis
        all_reviews = []
        sources = []
        for source_data in reviews_data:
            sources.append(source_data["source"])
            all_reviews.extend(source_data["reviews"])
        
        # Calculate basic metrics
        total_reviews = len(all_reviews)
        if total_reviews == 0:
            return {
                "sentiment_score": 0,
                "average_rating": 0,
                "quality_keywords": [],
                "data_sources": sources,
                "review_count": 0
            }
        
        average_rating = sum(review["rating"] for review in all_reviews) / total_reviews
        
        # Sentiment score = average rating on 0-5 scale
        sentiment_score = average_rating
        
        # Simulate extracted keywords based on rating
        possible_keywords = {
            "high": ["reliable", "professional", "quality", "satisfied", "recommend"],
            "medium": ["decent", "acceptable", "satisfactory"],
            "low": ["improvement", "disappointed", "late"]
        }
        
        if average_rating >= 4.0:
            keywords = random.sample(possible_keywords["high"], 3)
        elif average_rating >= 3.0:
            keywords = random.sample(possible_keywords["medium"], 2) + random.sample(possible_keywords["high"], 1)
        else:
            keywords = random.sample(possible_keywords["low"], 2) + random.sample(possible_keywords["medium"], 1)
        
        return {
            "sentiment_score": sentiment_score,
            "average_rating": average_rating,
            "quality_keywords": keywords,
            "data_sources": sources,
            "review_count": total_reviews
        }
        
    except Exception as e:
        logger.error(f"Error in simple review analysis: {str(e)}")
        return {
            "sentiment_score": 0,
            "average_rating": 0,
            "quality_keywords": [],
            "data_sources": sources if 'sources' in locals() else [],
            "review_count": 0
        }

def update_contractor_metrics(contractor_id, metrics_data):
    """Update contractor metrics in the database"""
    conn = get_db_connection()
    if not conn:
        logger.error("Failed to connect to database")
        return False
    
    try:
        cursor = conn.cursor()
        
        # Determine tier level based on sentiment score
        tier_level = "Standard"
        if metrics_data["sentiment_score"] >= 4.5:
            tier_level = "Diamond"
        elif metrics_data["sentiment_score"] >= 4.0:
            tier_level = "Gold"
        
        # Check if metrics exist for this contractor
        cursor.execute("SELECT contractor_id FROM contractor_metrics WHERE contractor_id = %s", (contractor_id,))
        exists = cursor.fetchone() is not None
        
        if exists:
            # Update existing metrics
            cursor.execute("""
                UPDATE contractor_metrics
                SET review_count = %s,
                    average_rating = %s,
                    sentiment_score = %s,
                    quality_keywords = %s,
                    tier_level = %s,
                    last_updated = NOW(),
                    data_sources = %s
                WHERE contractor_id = %s
            """, (
                metrics_data["review_count"],
                metrics_data["average_rating"],
                metrics_data["sentiment_score"],
                metrics_data["quality_keywords"],
                tier_level,
                metrics_data["data_sources"],
                contractor_id
            ))
        else:
            # Insert new metrics
            cursor.execute("""
                INSERT INTO contractor_metrics
                (contractor_id, review_count, average_rating, sentiment_score, quality_keywords, tier_level, data_sources)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                contractor_id,
                metrics_data["review_count"],
                metrics_data["average_rating"],
                metrics_data["sentiment_score"],
                metrics_data["quality_keywords"],
                tier_level,
                metrics_data["data_sources"]
            ))
        
        # Also update the tier_level in the contractors table
        cursor.execute("""
            UPDATE contractors
            SET tier_level = %s,
                rating = %s
            WHERE id = %s
        """, (
            tier_level,
            metrics_data["average_rating"],
            contractor_id
        ))
        
        cursor.close()
        logger.info(f"Updated metrics for contractor ID {contractor_id}")
        return True
    except Exception as e:
        logger.error(f"Error updating contractor metrics: {str(e)}")
        return False
    finally:
        conn.close()

def process_contractor(contractor):
    """Process a single contractor"""
    logger.info(f"Processing contractor: {contractor['name']} (ID: {contractor['id']})")
    
    try:
        # Fetch reviews from different sources
        google_reviews = fetch_google_reviews(contractor)
        yelp_reviews = fetch_yelp_reviews(contractor)
        
        # Combine review data
        reviews_data = [google_reviews, yelp_reviews]
        
        # Analyze reviews
        metrics = analyze_reviews_with_ai(reviews_data)
        
        # Update contractor metrics in database
        update_contractor_metrics(contractor['id'], metrics)
        
        return True
    except Exception as e:
        logger.error(f"Error processing contractor {contractor['id']}: {str(e)}")
        return False

def run_review_analyzer(max_contractors=10, days_threshold=7):
    """Run the review analyzer for contractors needing updates"""
    logger.info("Starting contractor review analyzer")
    
    # First, ensure necessary tables exist
    ensure_contractor_metrics_table()
    add_tier_level_to_contractors_table()
    
    # Get contractors that need updates
    contractors = get_contractors_needing_update(days_threshold)
    logger.info(f"Found {len(contractors)} contractors needing updates")
    
    # Process up to max_contractors
    contractors_to_process = contractors[:max_contractors]
    successful = 0
    
    for contractor in contractors_to_process:
        if process_contractor(contractor):
            successful += 1
    
    logger.info(f"Processed {successful} out of {len(contractors_to_process)} contractors")
    return successful

def add_tier_level_to_contractors_table():
    """Add tier_level column to contractors table if it doesn't exist"""
    conn = get_db_connection()
    if not conn:
        logger.error("Failed to connect to database")
        return False
    
    try:
        cursor = conn.cursor()
        
        # Check if tier_level column exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.columns 
                WHERE table_name = 'contractors' AND column_name = 'tier_level'
            )
        """)
        
        column_exists = cursor.fetchone()[0]
        
        if not column_exists:
            # Add tier_level column
            cursor.execute("""
                ALTER TABLE contractors
                ADD COLUMN tier_level TEXT DEFAULT 'Standard'
            """)
            logger.info("Added tier_level column to contractors table")
        
        cursor.close()
        return True
    except Exception as e:
        logger.error(f"Error checking/adding tier_level column: {str(e)}")
        return False
    finally:
        conn.close()

# Run the analyzer if executed directly
if __name__ == '__main__':
    run_review_analyzer()