

"""
GlassRain API Server - Unified Solution

This is a fully contained Flask application for GlassRain that combines all features:
- Service discovery and contractor matching
- Product browsing and shopping cart
- Checkout tracking with retailer deeplinks
- 3D room visualization
"""

import os
import json
import logging
import psycopg2
from decimal import Decimal
from flask import Flask, jsonify, request, render_template, redirect, send_from_directory
from psycopg2.extras import RealDictCursor
from api_endpoint_for_checkout import add_retailer_checkout_endpoint
app = Flask(__name__)

@app.route("/")
def index():
    return "GlassRain is running!"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='glassrain_unified.log', 
    filemode='a'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'glassrain-dev-secret-key')

# JSON encoder for Decimal
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            return float(o)
        return super(DecimalEncoder, self).default(o)

app.json_encoder = DecimalEncoder

def get_db_connection():
    """Get a connection to the PostgreSQL database"""
    try:
        conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
        conn.autocommit = True
        return conn
    except Exception as e:
        logger.error(f"Database connection error: {str(e)}")
        return None

def add_headers(response):
    """Add headers to allow iframe embedding and CORS"""
    response.headers['X-Frame-Options'] = 'ALLOWALL'
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    return response

# Apply CORS headers to all responses
app.after_request(add_headers)

@app.route('/')
def index():
    """Simple HTML status page for GlassRain"""
    return render_template('landing.html')

@app.route('/api/status')
def status():
    """Returns server status"""
    conn = get_db_connection()
    db_status = "connected" if conn else "disconnected"
    
    if conn:
        conn.close()
    
    return jsonify({
        "status": "online",
        "version": "1.0.0",
        "database": db_status,
        "name": "GlassRain Unified API",
        "features": [
            "service_categories",
            "services",
            "service_tiers",
            "products",
            "stores",
            "contractors",
            "checkout_tracking"
        ]
    })

@app.route('/api/service-categories')
def get_service_categories():
    """Return list of service categories"""
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
            SELECT id, name, description, icon as icon_url 
            FROM service_categories 
            ORDER BY name
        """)
        categories = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify(categories)
    except Exception as e:
        logger.error(f"Error fetching service categories: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/services')
def get_services():
    """Return list of available services with categories and subcategories"""
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get all categories
        cursor.execute("""
            SELECT id, name, description, icon as icon_url 
            FROM service_categories 
            ORDER BY name
        """)
        categories = cursor.fetchall()
        
        # For each category, get its services
        for category in categories:
            cursor.execute("""
                SELECT s.id, s.name, s.description, s.base_price, 
                       COALESCE(s.base_price_per_sqft, 0) as base_price_per_sqft,
                       COALESCE(s.min_price, 0) as min_price,
                       COALESCE(s.unit, '') as unit
                FROM services s
                WHERE s.category_id = %s
                ORDER BY s.name
            """, (category['id'],))
            services = cursor.fetchall()
            
            # For each service, get its sub-services if any
            for service in services:
                cursor.execute("""
                    SELECT id, name, description, price_adjustment, is_default
                    FROM service_options
                    WHERE service_id = %s
                    ORDER BY name
                """, (service['id'],))
                options = cursor.fetchall()
                service['options'] = options
            
            category['services'] = services
        
        cursor.close()
        conn.close()
        
        return jsonify(categories)
    except Exception as e:
        logger.error(f"Error fetching services: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/service-tiers')
def get_service_tiers():
    """Return service tiers with their multipliers"""
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
            SELECT id, name, description, multiplier as price_multiplier 
            FROM service_tiers 
            ORDER BY multiplier
        """)
        tiers = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify(tiers)
    except Exception as e:
        logger.error(f"Error fetching service tiers: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/contractors', methods=['GET'])
def get_contractors():
    """Return contractors, optionally filtered by service type"""
    service_id = request.args.get('service_id')
    zipcode = request.args.get('zipcode')
    
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        query = """
            SELECT c.id, c.name, c.description, c.contact_email, 
                  c.contact_phone, c.website, c.logo_url, c.rating,
                  c.tier_level, COUNT(cr.id) as review_count
            FROM contractors c
            LEFT JOIN contractor_reviews cr ON c.id = cr.contractor_id
        """
        
        params = []
        where_clauses = []
        
        if service_id:
            where_clauses.append("""
                c.id IN (
                    SELECT contractor_id FROM contractor_services 
                    WHERE service_id = %s
                )
            """)
            params.append(service_id)
            
        if zipcode:
            where_clauses.append("""
                c.id IN (
                    SELECT contractor_id FROM contractor_service_areas 
                    WHERE zipcode = %s
                )
            """)
            params.append(zipcode)
        
        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)
            
        query += " GROUP BY c.id ORDER BY c.tier_level DESC, c.rating DESC"
        
        cursor.execute(query, params)
        contractors = cursor.fetchall()
        
        # Get services for each contractor
        for contractor in contractors:
            cursor.execute("""
                SELECT s.id, s.name, s.description, s.base_price
                FROM services s
                JOIN contractor_services cs ON s.id = cs.service_id
                WHERE cs.contractor_id = %s
            """, (contractor['id'],))
            services = cursor.fetchall()
            contractor['services'] = services
            
        cursor.close()
        conn.close()
        
        return jsonify(contractors)
    except Exception as e:
        logger.error(f"Error fetching contractors: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/match-contractor', methods=['POST'])
def match_contractor():
    """Match the best contractor for a specific service and location"""
    if not request.json:
        return jsonify({"error": "No JSON data provided"}), 400
    
    service_id = request.json.get('service_id')
    zipcode = request.json.get('zipcode')
    
    if not service_id or not zipcode:
        return jsonify({"error": "service_id and zipcode are required"}), 400
    
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Find best matching contractor
        cursor.execute("""
            SELECT c.id, c.name, c.description, c.contact_email, 
                  c.contact_phone, c.website, c.logo_url, c.rating,
                  c.tier_level
            FROM contractors c
            JOIN contractor_services cs ON c.id = cs.contractor_id
            JOIN contractor_service_areas csa ON c.id = csa.contractor_id
            WHERE cs.service_id = %s
            AND csa.zipcode = %s
            ORDER BY 
                c.tier_level = 'Diamond' DESC,
                c.tier_level = 'Gold' DESC,
                c.tier_level = 'Standard' DESC,
                c.rating DESC
            LIMIT 1
        """, (service_id, zipcode))
        
        contractor = cursor.fetchone()
        
        if not contractor:
            return jsonify({
                "match_found": False,
                "message": "No matching contractor found for this service in your area"
            })
            
        # Get service details
        cursor.execute("""
            SELECT s.id, s.name, s.description, s.base_price
            FROM services s
            WHERE s.id = %s
        """, (service_id,))
        service = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "match_found": True,
            "contractor": contractor,
            "service": service
        })
    except Exception as e:
        logger.error(f"Error matching contractor: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/stores')
def get_stores():
    """Return list of stores"""
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
            SELECT id, name, description, logo_url, website
            FROM stores
            ORDER BY name
        """)
        stores = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify(stores)
    except Exception as e:
        logger.error(f"Error fetching stores: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/store-categories')
def get_store_categories():
    """Return list of store product categories"""
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
            SELECT id, name, description, icon as icon_url
            FROM store_categories
            ORDER BY name
        """)
        categories = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify(categories)
    except Exception as e:
        logger.error(f"Error fetching store categories: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/recommended_products')
def get_recommended_products():
    """Return recommended products for a room"""
    room_type = request.args.get('room')
    limit = request.args.get('limit', default=10, type=int)
    
    if not room_type:
        return jsonify({"error": "Room type is required"}), 400
    
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # First approach: Try direct text matching on products
        search_query = """
            SELECT p.id, p.name, p.description, p.price, 
                p.is_on_sale, p.sale_price, p.image_url,
                p.product_url, p.external_id,
                s.id as store_id, s.name as store_name, s.logo_url as store_logo,
                sc.name as category_name
            FROM products p
            JOIN stores s ON p.store_id = s.id
            JOIN store_categories sc ON p.category_id = sc.id
            WHERE sc.name ILIKE %s
            OR p.name ILIKE %s
            OR p.description ILIKE %s
            ORDER BY p.price DESC
            LIMIT %s
        """
        
        # Use room type as search parameter
        search_pattern = f"%{room_type}%"
        params = [search_pattern, search_pattern, search_pattern, limit]
        
        cursor.execute(search_query, params)
        recommended_products = cursor.fetchall()
        
        # If no direct matches, use room category mapping
        if len(recommended_products) == 0:
            logger.info(f"No direct matches for room type {room_type}, trying category mapping")
            
            # Map room types to categories that would be relevant for that room
            room_category_map = {
                'living': ['Furniture', 'Lighting', 'Decor', 'Entertainment'],
                'kitchen': ['Kitchen', 'Appliances', 'Dining'],
                'bedroom': ['Furniture', 'Bedding', 'Lighting', 'Decor'],
                'bathroom': ['Bath', 'Fixtures', 'Storage'],
                'office': ['Office', 'Furniture', 'Electronics'],
                'outdoor': ['Outdoor', 'Garden', 'Patio']
            }
            
            # Get categories relevant to this room type
            relevant_categories = room_category_map.get(room_type.lower(), ['Furniture', 'Lighting', 'Decor'])
            
            placeholders = ', '.join(['%s'] * len(relevant_categories))
            category_query = f"""
                SELECT p.id, p.name, p.description, p.price, 
                      p.is_on_sale, p.sale_price, p.image_url,
                      p.product_url, p.external_id,
                      s.id as store_id, s.name as store_name, s.logo_url as store_logo,
                      sc.name as category_name
                FROM products p
                JOIN stores s ON p.store_id = s.id
                JOIN store_categories sc ON p.category_id = sc.id
                WHERE sc.name ILIKE ANY(%s)
                ORDER BY p.price DESC
                LIMIT %s
            """
            
            # Build array of patterns for ILIKE ANY
            category_patterns = [f"%{cat}%" for cat in relevant_categories]
            cursor.execute(category_query, [category_patterns, limit])
            recommended_products = cursor.fetchall()
        
        # If still no results, return featured products
        if len(recommended_products) == 0:
            logger.info(f"No category matches for room type {room_type}, falling back to featured products")
            
            # Fallback to random products
            cursor.execute("""
                SELECT p.id, p.name, p.description, p.price, 
                    p.is_on_sale, p.sale_price, p.image_url,
                    p.product_url, p.external_id,
                    s.id as store_id, s.name as store_name, s.logo_url as store_logo,
                    sc.name as category_name
                FROM products p
                JOIN stores s ON p.store_id = s.id
                JOIN store_categories sc ON p.category_id = sc.id
                ORDER BY RANDOM()
                LIMIT %s
            """, [limit])
            recommended_products = cursor.fetchall()
        
        # Format the products for the response
        for product in recommended_products:
            # Format for JSON serialization
            if product['price'] is not None:
                product['price'] = float(product['price'])
            if product['sale_price'] is not None:
                product['sale_price'] = float(product['sale_price'])
            
            # Add formatted data
            product['image_url'] = product['image_url'] or '/static/img/product-placeholder.jpg'
            
            # Rename store_name to a more frontend-friendly property
            product['store'] = product['store_name']
        
        return jsonify({"products": recommended_products})
    
    except Exception as e:
        logger.error(f"Error retrieving recommended products: {str(e)}")
        return jsonify({"error": "Failed to retrieve recommended products"}), 500
    
    finally:
        if conn:
            conn.close()

@app.route('/api/products')
def get_products():
    """Return products, optionally filtered by store or category"""
    store_id = request.args.get('store_id')
    category_id = request.args.get('category_id')
    search_term = request.args.get('search')
    limit = request.args.get('limit', default=20, type=int)
    
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get all categories first
        cursor.execute("""
            SELECT sc.id, sc.name
            FROM store_categories sc
            ORDER BY sc.name
        """)
        categories = cursor.fetchall()
        
        # For each category, get its products (with filters applied)
        for category in categories:
            query = """
                SELECT p.id, p.name, p.description, p.price, 
                      p.is_on_sale, p.sale_price, p.image_url,
                      p.product_url, p.external_id,
                      s.id as store_id, s.name as store_name, s.logo_url as store_logo
                FROM products p
                JOIN stores s ON p.store_id = s.id
                WHERE p.category_id = %s
            """
            
            params = [category['id']]
            
            if store_id:
                query += " AND p.store_id = %s"
                params.append(store_id)
                
            if search_term:
                query += " AND (p.name ILIKE %s OR p.description ILIKE %s)"
                search_pattern = f"%{search_term}%"
                params.extend([search_pattern, search_pattern])
                
            query += f" ORDER BY p.name LIMIT {limit}"
            
            cursor.execute(query, params)
            products = cursor.fetchall()
            
            # Format the products for the response
            for product in products:
                # Format for JSON serialization
                if product['price'] is not None:
                    product['price'] = float(product['price'])
                if product['sale_price'] is not None:
                    product['sale_price'] = float(product['sale_price'])
                
                # Add formatted data
                product['image_url'] = product['image_url'] or '/static/img/product-placeholder.jpg'
                
            category['products'] = products
            
        # Filter out categories with no products
        categories = [cat for cat in categories if cat['products']]
        
        cursor.close()
        conn.close()
        
        return jsonify(categories)
    except Exception as e:
        logger.error(f"Error fetching products: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/mapbox-token')
def mapbox_token():
    """Return Mapbox API token"""
    token = os.environ.get('MAPBOX_API_KEY', 'pk.sample.key')
    return jsonify({"token": token})

@app.route('/address')
def address_entry():
    """Render the address entry page"""
    return render_template('address.html')

@app.route('/dashboard')
def dashboard():
    """Render the main dashboard page"""
    return render_template('dashboard.html')

@app.route('/elevate')
def elevate():
    """Render the Elevate tab (product browsing)"""
    return render_template('elevate.html')

@app.route('/services')
def services():
    """Render the Services tab"""
    return render_template('services.html')

@app.route('/diy')
def diy():
    """Render the DIY tab"""
    return render_template('diy.html')

@app.route('/settings')
def settings():
    """Render the Settings tab"""
    return render_template('settings.html')

@app.route('/api/process-address', methods=['POST'])
def process_address():
    """Process address data from the form, geocode using Mapbox, and save to database"""
    if not request.json:
        return jsonify({"error": "No JSON data provided"}), 400
    
    address_data = request.json
    
    # Check for the different format from updated template
    if 'address' in address_data:
        # This is from the updated template which just sends the full address string
        # We need to geocode it to get the details
        full_address = address_data['address']
        
        # Get geocoding from Mapbox
        mapbox_token = os.environ.get('MAPBOX_API_KEY')
        if not mapbox_token:
            return jsonify({"error": "Mapbox API key not configured"}), 500
            
        # Geocode the address using Mapbox
        try:
            import requests
            geocode_url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{full_address}.json?access_token={mapbox_token}&country=US&types=address"
            response = requests.get(geocode_url)
            geocode_data = response.json()
            
            if not geocode_data['features'] or len(geocode_data['features']) == 0:
                return jsonify({"error": "Could not geocode the address"}), 400
                
            # Get the first feature (most relevant match)
            feature = geocode_data['features'][0]
            
            # Extract components from the context and place_name
            context = feature.get('context', [])
            place_name_parts = feature.get('place_name', '').split(', ')
            
            street = feature.get('text', '')
            address_number = feature.get('address', '')
            if address_number:
                street = f"{address_number} {street}"
                
            city = ""
            state = ""
            country = "USA"
            postal_code = ""
            
            # Extract information from context
            for item in context:
                if item.get('id', '').startswith('place'):
                    city = item.get('text', '')
                elif item.get('id', '').startswith('region'):
                    state = item.get('text', '')
                elif item.get('id', '').startswith('country'):
                    country = item.get('text', '')
                elif item.get('id', '').startswith('postcode'):
                    postal_code = item.get('text', '')
            
            # Build standardized address_data
            coordinates = feature.get('center', [0, 0])
            address_data = {
                'street': street,
                'city': city,
                'state': state,
                'zip': postal_code,
                'country': country,
                'lat': coordinates[1],  # Mapbox returns [longitude, latitude]
                'lng': coordinates[0],
                'full_address': feature.get('place_name', full_address)
            }
            
        except Exception as e:
            logger.error(f"Error geocoding address: {str(e)}")
            return jsonify({"error": "Failed to process address information"}), 500
    else:
        # This is from the original template with individual fields
        # Validate required fields
        required_fields = ['street', 'city', 'state', 'zip', 'country']
        for field in required_fields:
            if field not in address_data or not address_data[field]:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Get geocoding from Mapbox
        mapbox_token = os.environ.get('MAPBOX_API_KEY')
        if not mapbox_token:
            return jsonify({"error": "Mapbox API key not configured"}), 500
    
    # Save address to database
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Add address
        cursor.execute("""
            INSERT INTO addresses (
                street, city, state, zip, country,
                lat, lng, full_address, created_at
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, NOW()
            ) RETURNING id
        """, (
            address_data['street'],
            address_data['city'],
            address_data['state'],
            address_data['zip'],
            address_data['country'],
            address_data.get('lat', 0),
            address_data.get('lng', 0),
            f"{address_data['street']}, {address_data['city']}, {address_data['state']} {address_data['zip']}, {address_data['country']}",
        ))
        
        address_id = cursor.fetchone()['id']
        
        # Link to user if user_id is provided
        if 'user_id' in address_data and address_data['user_id']:
            cursor.execute("""
                INSERT INTO user_addresses (
                    user_id, address_id, is_primary, created_at
                ) VALUES (
                    %s, %s, true, NOW()
                )
            """, (
                address_data['user_id'],
                address_id
            ))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "address_id": address_id,
            "message": "Address saved successfully"
        })
    except Exception as e:
        logger.error(f"Error saving address: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/addresses', methods=['GET'])
def get_addresses():
    """Get saved addresses for current user"""
    try:
        # In a real app, we would use user authentication to get only addresses
        # for the current user. For this demo, we'll return all addresses.
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("""
            SELECT 
                id, street, city, state, zip, country, 
                lat, lng, full_address, created_at
            FROM addresses
            ORDER BY created_at DESC
            LIMIT 5
        """)
        
        addresses = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify({"addresses": addresses})
    except Exception as e:
        logger.error(f"Error retrieving addresses: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files"""
    return send_from_directory('static', filename)



@app.route('/api/products/<int:product_id>')
def get_product(product_id):
    """Return a specific product by ID"""
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("""
            SELECT p.id, p.name, p.description, p.price, 
                p.is_on_sale, p.sale_price, p.image_url,
                p.product_url, p.external_id,
                s.id as store_id, s.name as store_name, s.logo_url as store_logo,
                sc.id as category_id, sc.name as category_name
            FROM products p
            JOIN stores s ON p.store_id = s.id
            JOIN store_categories sc ON p.category_id = sc.id
            WHERE p.id = %s
        """, [product_id])
        
        product = cursor.fetchone()
        
        if not product:
            return jsonify({"error": "Product not found"}), 404
        
        # Format the product for the response
        if product['price'] is not None:
            product['price'] = float(product['price'])
        if product['sale_price'] is not None:
            product['sale_price'] = float(product['sale_price'])
        
        # Add formatted data
        product['image_url'] = product['image_url'] or '/static/img/product-placeholder.jpg'
        
        return jsonify(product)
    
    except Exception as e:
        logger.error(f"Error getting product: {str(e)}")
        return jsonify({"error": f"Failed to get product: {str(e)}"}), 500
    
    finally:
        if conn:
            conn.close()

# Add retailer checkout endpoint
add_retailer_checkout_endpoint(app)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=port, debug=debug)
