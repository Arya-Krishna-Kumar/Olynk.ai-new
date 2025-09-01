#!/usr/bin/env python3
"""
Test Supabase Integration for OLynk AI MVP
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

try:
    from backend.supabase_config import supabase_manager
    print("✅ Supabase configuration imported successfully")
except ImportError as e:
    print(f"❌ Failed to import Supabase configuration: {e}")
    sys.exit(1)

def test_supabase_connection():
    """Test basic Supabase connectivity"""
    print("\n🔍 Testing Supabase Connection...")
    
    if not supabase_manager.is_connected():
        print("❌ Supabase client not connected")
        return False
    
    print("✅ Supabase client connected")
    
    # Test basic operations
    try:
        # Test getting data from products table
        print("\n📊 Testing data retrieval...")
        products = supabase_manager.get_data('products', limit=5)
        print(f"✅ Retrieved {len(products)} products from database")
        
        # Test getting data from other tables
        orders = supabase_manager.get_data('orders', limit=5)
        customers = supabase_manager.get_data('customers', limit=5)
        inventory = supabase_manager.get_data('inventory', limit=5)
        
        print(f"✅ Retrieved {len(orders)} orders from database")
        print(f"✅ Retrieved {len(customers)} customers from database")
        print(f"✅ Retrieved {len(inventory)} inventory items from database")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing database operations: {e}")
        return False

def test_data_storage():
    """Test storing sample data"""
    print("\n💾 Testing data storage...")
    
    try:
        # Sample product data
        sample_product = {
            'product_id': 'TEST001',
            'product_name': 'Test Product',
            'category': 'Test Category',
            'brand': 'Test Brand',
            'price': 99.99,
            'cost': 50.00,
            'sku': 'TEST-SKU-001',
            'stock_quantity': 100,
            'status': 'Active'
        }
        
        # Store sample data
        success = supabase_manager.store_data('products', [sample_product])
        
        if success:
            print("✅ Sample data stored successfully")
            
            # Retrieve and verify
            products = supabase_manager.get_data('products', limit=10)
            test_product = next((p for p in products if p.get('product_id') == 'TEST001'), None)
            
            if test_product:
                print("✅ Sample data retrieved and verified")
                return True
            else:
                print("❌ Sample data not found after storage")
                return False
        else:
            print("❌ Failed to store sample data")
            return False
            
    except Exception as e:
        print(f"❌ Error testing data storage: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 OLynk AI MVP - Supabase Integration Test")
    print("=" * 50)
    
    # Test connection
    if not test_supabase_connection():
        print("\n❌ Supabase connection test failed")
        sys.exit(1)
    
    # Test data storage
    if not test_data_storage():
        print("\n❌ Data storage test failed")
        sys.exit(1)
    
    print("\n🎉 All Supabase tests passed!")
    print("✅ Your OLynk AI application is ready to use with Supabase!")
    
    # Show database status
    print("\n📊 Database Status:")
    print(f"   Connected: {supabase_manager.is_connected()}")
    print(f"   URL: https://cyrdngsfjnufzwfghbrs.supabase.co")
    print(f"   Tables: {list(supabase_manager.tables.keys())}")

if __name__ == "__main__":
    main()

