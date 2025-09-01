"""
Supabase Configuration for OLynk AI MVP
Database integration for persistent data storage
"""

import os
from supabase import create_client, Client
from datetime import datetime
import logging

# Supabase credentials
SUPABASE_URL = "https://cyrdngsfjnufzwfghbrs.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImN5cmRuZ3Nmam51Znp3ZmdoYnJzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTY2NzAzNTcsImV4cCI6MjA3MjI0NjM1N30.lJvMbcwM03zJpJ_dw4Z6BoQHuucEHCyNiLWMIadBhjo"

# Initialize Supabase client
try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
    logging.info("Supabase client initialized successfully")
except Exception as e:
    logging.error(f"Failed to initialize Supabase client: {str(e)}")
    supabase = None

class SupabaseManager:
    """Manages Supabase database operations for OLynk AI"""
    
    def __init__(self):
        self.client = supabase
        self.tables = {
            'products': 'products',
            'orders': 'orders', 
            'customers': 'customers',
            'inventory': 'inventory',
            'analytics': 'analytics',
            'insights': 'insights'
        }
    
    def is_connected(self):
        """Check if Supabase connection is available"""
        return self.client is not None
    
    def create_tables(self):
        """Create necessary tables if they don't exist"""
        if not self.is_connected():
            return False
        
        try:
            # Note: In Supabase, tables are typically created via SQL migrations
            # For now, we'll assume tables exist or create them via SQL
            logging.info("Tables should be created via Supabase SQL editor")
            return True
        except Exception as e:
            logging.error(f"Error creating tables: {str(e)}")
            return False
    
    def store_data(self, table_name, data):
        """Store data in Supabase table"""
        if not self.is_connected():
            return False
        
        try:
            if table_name not in self.tables:
                logging.error(f"Invalid table name: {table_name}")
                return False
            
            # Add timestamp
            for record in data:
                record['created_at'] = datetime.now().isoformat()
                record['updated_at'] = datetime.now().isoformat()
            
            # Insert data
            result = self.client.table(self.tables[table_name]).insert(data).execute()
            logging.info(f"Stored {len(data)} records in {table_name}")
            return True
            
        except Exception as e:
            logging.error(f"Error storing data in {table_name}: {str(e)}")
            return False
    
    def get_data(self, table_name, limit=1000):
        """Retrieve data from Supabase table"""
        if not self.is_connected():
            return []
        
        try:
            if table_name not in self.tables:
                logging.error(f"Invalid table name: {table_name}")
                return []
            
            result = self.client.table(self.tables[table_name]).select("*").limit(limit).execute()
            return result.data
            
        except Exception as e:
            logging.error(f"Error retrieving data from {table_name}: {str(e)}")
            return []
    
    def update_data(self, table_name, data, record_id):
        """Update data in Supabase table"""
        if not self.is_connected():
            return False
        
        try:
            if table_name not in self.tables:
                logging.error(f"Invalid table name: {table_name}")
                return False
            
            # Add updated timestamp
            data['updated_at'] = datetime.now().isoformat()
            
            result = self.client.table(self.tables[table_name]).update(data).eq('id', record_id).execute()
            logging.info(f"Updated record {record_id} in {table_name}")
            return True
            
        except Exception as e:
            logging.error(f"Error updating data in {table_name}: {str(e)}")
            return False
    
    def delete_data(self, table_name, record_id):
        """Delete data from Supabase table"""
        if not self.is_connected():
            return False
        
        try:
            if table_name not in self.tables:
                logging.error(f"Invalid table name: {table_name}")
                return False
            
            result = self.client.table(self.tables[table_name]).delete().eq('id', record_id).execute()
            logging.info(f"Deleted record {record_id} from {table_name}")
            return True
            
        except Exception as e:
            logging.error(f"Error deleting data from {table_name}: {str(e)}")
            return False
    
    def store_analytics(self, analytics_data):
        """Store analytics results"""
        if not self.is_connected():
            return False
        
        try:
            analytics_data['created_at'] = datetime.now().isoformat()
            result = self.client.table('analytics').insert(analytics_data).execute()
            logging.info("Stored analytics data")
            return True
            
        except Exception as e:
            logging.error(f"Error storing analytics: {str(e)}")
            return False
    
    def store_insights(self, insights_data):
        """Store AI-generated insights"""
        if not self.is_connected():
            return False
        
        try:
            insights_data['created_at'] = datetime.now().isoformat()
            result = self.client.table('insights').insert(insights_data).execute()
            logging.info("Stored insights data")
            return True
            
        except Exception as e:
            logging.error(f"Error storing insights: {str(e)}")
            return False

# Global instance
supabase_manager = SupabaseManager()

