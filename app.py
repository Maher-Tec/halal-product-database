from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import os
from pathlib import Path

app = Flask(__name__)
CORS(app)  # Allow your Flutter app to call this API

# Get the absolute path to the database file
DB_PATH = Path(__file__).parent / 'openfoodfacts_complete.db'

def get_db_connection():
    """Create a database connection"""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row  # This enables column access by name
    return conn

@app.route('/')
def home():
    return jsonify({
        'status': 'online',
        'service': 'Halal Product API',
        'version': '1.0',
        'endpoints': {
            '/product/<barcode>': 'Get product details by barcode',
            '/health': 'Health check'
        }
    })

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'database': str(DB_PATH.exists())})

@app.route('/product/<barcode>')
def get_product(barcode):
    """Get product by barcode"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Clean barcode (remove leading zeros)
        clean_barcode = barcode.lstrip('0')
        
        # Query both the original and cleaned barcode
        result = cursor.execute(
            'SELECT code, product_name, ingredients_text, categories, labels, allergens FROM products WHERE code = ? OR code = ?',
            (barcode, clean_barcode)
        ).fetchone()
        
        conn.close()
        
        if result:
            # Convert Row object to dictionary
            product = dict(result)
            return jsonify(product)
        else:
            return jsonify({'error': 'Product not found'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
