"""
API Endpoint for Checkout Tracking

This module adds a new endpoint to the GlassRain API for tracking checkout events
and can be expanded to support actual API integration with retailers.
"""

import os
import json
import logging
import psycopg2
from flask import request, jsonify

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

def track_checkout_endpoint():
    """
    Endpoint to track checkout events and potentially
    integrate with retailer APIs for direct add-to-cart
    
    Expected JSON payload:
    {
        "store_id": 1,
        "store_name": "Store Name",
        "products": [
            {
                "id": 1,
                "name": "Product Name",
                "price": 19.99,
                "quantity": 2
            },
            ...
        ],
        "total_value": 39.98,
        "timestamp": "2025-04-07T14:30:15.123Z"
    }
    """
    try:
        # Get data from request
        data = request.get_json()
        if not data:
            return jsonify({'status': 'error', 'message': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['store_id', 'store_name', 'products', 'total_value']
        for field in required_fields:
            if field not in data:
                return jsonify({'status': 'error', 'message': f'Missing required field: {field}'}), 400
        
        # Log checkout event
        logger.info(f"Checkout event: {json.dumps(data)}")
        
        # Save to database
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                
                # Insert into checkout_events table
                cursor.execute("""
                    INSERT INTO checkout_events (store_id, store_name, products, total_value)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id
                """, (
                    data['store_id'],
                    data['store_name'],
                    json.dumps(data['products']),
                    data['total_value']
                ))
                
                event_id = cursor.fetchone()[0]
                
                cursor.close()
                logger.info(f"Checkout event saved with ID: {event_id}")
                
                # Integrate with retailer if needed
                if 'store_id' in data and data['store_id'] == 5:  # Amazon
                    # Example: Integrate with Amazon
                    amazon_url = integrate_with_amazon(data)
                    return jsonify({
                        'status': 'success',
                        'message': 'Checkout event tracked and integrated with Amazon',
                        'event_id': event_id,
                        'amazon_url': amazon_url
                    }), 200
                
                return jsonify({
                    'status': 'success',
                    'message': 'Checkout event tracked',
                    'event_id': event_id
                }), 200
                
            except Exception as e:
                logger.error(f"Error saving checkout event: {str(e)}")
                return jsonify({'status': 'error', 'message': 'Error saving checkout event'}), 500
            finally:
                conn.close()
        else:
            # Even if DB connection fails, acknowledge receipt of tracking data
            return jsonify({
                'status': 'partial',
                'message': 'Checkout event received but not saved to database'
            }), 200
            
    except Exception as e:
        logger.error(f"Error processing checkout event: {str(e)}")
        return jsonify({'status': 'error', 'message': 'Error processing checkout event'}), 500

def integrate_with_amazon(checkout_data):
    """
    Example function for Amazon API integration
    In a real implementation, this would use the Amazon Product Advertising API
    or Amazon Associates API to create a cart with the selected products
    """
    try:
        # Build an Amazon cart URL with the products
        base_url = "https://amazon.com/gp/aws/cart/add.html?"
        
        # Add each product to the URL
        params = []
        for i, product in enumerate(checkout_data['products']):
            product_id = f"B{str(product['id']).zfill(9)}"  # Example fake ASIN format
            params.append(f"ASIN.{i+1}={product_id}")
            params.append(f"Quantity.{i+1}={product['quantity']}")
        
        # Add tracking tag
        params.append("AssociateTag=glassrain-20")
        
        # Return the complete URL
        return base_url + "&".join(params)
        
    except Exception as e:
        logger.error(f"Error integrating with Amazon: {str(e)}")
        return None

def add_retailer_checkout_endpoint(app):
    """Add the retailer checkout endpoint to the Flask app"""
    app.add_url_rule('/api/track_checkout', 'track_checkout', track_checkout_endpoint, methods=['POST'])
    logger.info("Retailer checkout endpoint added to API")