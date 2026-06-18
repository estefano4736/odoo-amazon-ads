import sys
import os

# Add parent path so we can import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.db import db

def test_connection():
    try:
        print("Connecting to Odoo...")
        uid, models = db.get_connection()
        print(f"✓ Connected to Odoo successfully. UID: {uid}")
        
        # Test reading rules
        rules = db.get_rules()
        print(f"Rules: {rules}")
        
        # Test reading campaigns
        campaigns = db.read_campaigns()
        print(f"Campaigns count: {len(campaigns)}")
        if campaigns:
            print(f"First campaign: {campaigns[0]}")
            
        # Test reading products
        products = db.read_products()
        print(f"Products count: {len(products)}")
        if products:
            print(f"First product: {products[0]}")
            
        # Test reading books
        books = db.read_books()
        print(f"Books count: {len(books)}")
        if books:
            print(f"First book: {books[0]}")
            
        # Test reading keywords
        keywords = db.read_keywords()
        print(f"Keywords count: {len(keywords)}")
        
        # Test reading search terms
        search_terms = db.read_search_terms()
        print(f"Search terms count: {len(search_terms)}")
        
    except Exception as e:
        print(f"✗ Connection error: {e}")

if __name__ == "__main__":
    test_connection()
