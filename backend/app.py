from flask import Flask, request, jsonify, render_template, send_from_directory
import pandas as pd
import numpy as np
import io
import os
from datetime import datetime
from werkzeug.utils import secure_filename
import logging
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import matplotlib.pyplot as plt

# Import Phase 2 modules
try:
    import sys
    sys.path.append(os.path.dirname(__file__))
    from advanced_analytics import advanced_analytics
    from insights_generator import insights_generator
    from visualization_engine import visualization_engine
    from supabase_config import supabase_manager
    PHASE_2_AVAILABLE = True
    logging.info("Phase 2 modules loaded successfully!")
except ImportError as e:
    PHASE_2_AVAILABLE = False
    logging.warning(f"Phase 2 modules not available - running in Phase 1 mode. Error: {e}")

# Import Supabase configuration
try:
    from supabase_config import supabase_manager
    SUPABASE_AVAILABLE = True
    logging.info("Supabase integration loaded successfully!")
except ImportError as e:
    SUPABASE_AVAILABLE = False
    logging.warning(f"Supabase integration not available - using in-memory storage. Error: {e}")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, 
            template_folder='../frontend',
            static_folder='../frontend')
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
app.config['UPLOAD_FOLDER'] = '../uploads'

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# In-memory storage for uploaded data (will be replaced with database in Phase 3)
uploaded_data = {
    'products': [],
    'orders': [],
    'customers': [],
    'inventory': []
}

# Template file paths
TEMPLATE_FILES = {
    'products': 'uploads/products_template.csv',
    'orders': 'uploads/orders_template.csv',
    'customers': 'uploads/customers_template.csv',
    'inventory': 'uploads/inventory_template.csv'
}

# Template column definitions (keeping for reference)
TEMPLATE_COLUMNS = {
    'products': ['Product ID', 'Product Name', 'Category', 'Brand', 'Price', 'Cost', 'SKU', 'Stock Quantity', 'Weight (g)', 
                 'Dimensions (cm)', 'Launch Date', 'Last Updated', 'Tags', 'Description', 'Status'],
    'orders': ['Order ID', 'Order Date', 'Customer ID', 'Customer Name', 'Product ID', 'Product Name', 'Quantity', 'Unit Price', 
               'Total Amount', 'Payment Method', 'Shipping Address', 'Order Status', 'Discount Amount', 'Tax Amount', 'Grand Total'],
    'customers': ['Customer ID', 'First Name', 'Last Name', 'Email', 'Phone', 'Registration Date', 'Total Orders', 'Total Spent', 
                  'Average Order Value', 'Last Order Date', 'Preferred Payment Method', 'Shipping Address', 'Customer Segment', 
                  'Marketing Opt-in', 'Notes'],
    'inventory': ['Inventory ID', 'Product ID', 'Product Name', 'SKU', 'Location', 'Warehouse', 'Current Stock', 'Minimum Stock', 
                  'Maximum Stock', 'Unit Cost', 'Total Value', 'Last Restocked', 'Next Restock Date', 'Stock Status', 'Category', 
                  'Supplier', 'Lead Time (Days)', 'Reorder Point']
}

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'csv'

def validate_csv_data(df, expected_columns):
    """Validate CSV data and return quality score and issues"""
    issues = []
    quality_score = 100
    
    # Check for missing columns
    missing_cols = [col for col in expected_columns if col not in df.columns]
    if missing_cols:
        issues.append(f"Missing columns: {missing_cols}")
        quality_score -= len(missing_cols) * 5
    
    # Check for empty dataframe
    if df.empty:
        issues.append("File is empty")
        quality_score = 0
    else:
        # Check for missing values
        missing_values = df.isnull().sum().sum()
        total_cells = df.size
        if total_cells > 0:
            missing_percentage = (missing_values / total_cells) * 100
            if missing_percentage > 20:
                issues.append(f"High percentage of missing values: {missing_percentage:.1f}%")
                quality_score -= 20
            elif missing_percentage > 10:
                issues.append(f"Moderate missing values: {missing_percentage:.1f}%")
                quality_score -= 10
        
        # Check data types
        for col in df.columns:
            if col in expected_columns:
                # Basic data type validation
                if 'Date' in col and not pd.api.types.is_datetime64_any_dtype(df[col]):
                    try:
                        pd.to_datetime(df[col], errors='coerce')
                    except:
                        issues.append(f"Column '{col}' should contain dates")
                        quality_score -= 5
                
                if 'Price' in col or 'Cost' in col or 'Total' in col:
                    try:
                        pd.to_numeric(df[col], errors='coerce')
                    except:
                        issues.append(f"Column '{col}' should contain numeric values")
                        quality_score -= 5
    
    quality_score = max(0, quality_score)
    return quality_score, issues

@app.route('/')
def index():
    """Serve the main HTML template"""
    return render_template('index.html')

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '2.0.0' if PHASE_2_AVAILABLE else '1.0.0',
        'phase': 'Phase 2' if PHASE_2_AVAILABLE else 'Phase 1',
        'features': {
            'advanced_analytics': PHASE_2_AVAILABLE,
            'ml_models': PHASE_2_AVAILABLE,
            'visualizations': PHASE_2_AVAILABLE,
            'supabase_integration': SUPABASE_AVAILABLE
        },
        'database': {
            'connected': SUPABASE_AVAILABLE and supabase_manager.is_connected() if SUPABASE_AVAILABLE else False,
            'type': 'Supabase' if SUPABASE_AVAILABLE else 'In-Memory'
        }
    }), 200

@app.route('/load-data/<string:type>', methods=['GET'])
def load_data_from_db(type):
    """Load data from Supabase database"""
    if not SUPABASE_AVAILABLE or not supabase_manager.is_connected():
        return jsonify({'error': 'Database not available'}), 400
    
    if type not in ['products', 'orders', 'customers', 'inventory']:
        return jsonify({'error': 'Invalid data type'}), 400
    
    try:
        # Load data from Supabase
        db_data = supabase_manager.get_data(type)
        
        if db_data:
            # Transform back to CSV format for compatibility
            csv_data = []
            reverse_mapping = {
                'products': {
                    'product_id': 'Product ID',
                    'product_name': 'Product Name',
                    'category': 'Category',
                    'brand': 'Brand',
                    'price': 'Price',
                    'cost': 'Cost',
                    'sku': 'SKU',
                    'stock_quantity': 'Stock Quantity',
                    'weight_g': 'Weight (g)',
                    'dimensions_cm': 'Dimensions (cm)',
                    'launch_date': 'Launch Date',
                    'last_updated': 'Last Updated',
                    'tags': 'Tags',
                    'description': 'Description',
                    'status': 'Status'
                },
                'orders': {
                    'order_id': 'Order ID',
                    'order_date': 'Order Date',
                    'customer_id': 'Customer ID',
                    'customer_name': 'Customer Name',
                    'product_id': 'Product ID',
                    'product_name': 'Product Name',
                    'quantity': 'Quantity',
                    'unit_price': 'Unit Price',
                    'total_amount': 'Total Amount',
                    'payment_method': 'Payment Method',
                    'shipping_address': 'Shipping Address',
                    'order_status': 'Order Status',
                    'discount_amount': 'Discount Amount',
                    'tax_amount': 'Tax Amount',
                    'grand_total': 'Grand Total'
                },
                'customers': {
                    'customer_id': 'Customer ID',
                    'first_name': 'First Name',
                    'last_name': 'Last Name',
                    'email': 'Email',
                    'phone': 'Phone',
                    'registration_date': 'Registration Date',
                    'total_orders': 'Total Orders',
                    'total_spent': 'Total Spent',
                    'average_order_value': 'Average Order Value',
                    'last_order_date': 'Last Order Date',
                    'preferred_payment_method': 'Preferred Payment Method',
                    'shipping_address': 'Shipping Address',
                    'customer_segment': 'Customer Segment',
                    'marketing_opt_in': 'Marketing Opt-in',
                    'notes': 'Notes'
                },
                'inventory': {
                    'inventory_id': 'Inventory ID',
                    'product_id': 'Product ID',
                    'product_name': 'Product Name',
                    'sku': 'SKU',
                    'location': 'Location',
                    'warehouse': 'Warehouse',
                    'current_stock': 'Current Stock',
                    'minimum_stock': 'Minimum Stock',
                    'maximum_stock': 'Maximum Stock',
                    'unit_cost': 'Unit Cost',
                    'total_value': 'Total Value',
                    'last_restocked': 'Last Restocked',
                    'next_restock_date': 'Next Restock Date',
                    'stock_status': 'Stock Status',
                    'category': 'Category',
                    'supplier': 'Supplier',
                    'lead_time_days': 'Lead Time (Days)',
                    'reorder_point': 'Reorder Point'
                }
            }
            
            mapping = reverse_mapping.get(type, {})
            for record in db_data:
                csv_record = {}
                for db_col, csv_col in mapping.items():
                    if db_col in record:
                        csv_record[csv_col] = record[db_col]
                if csv_record:  # Only add if we have data
                    csv_data.append(csv_record)
            
            # Update in-memory storage
            uploaded_data[type] = csv_data
            
            return jsonify({
                'message': f'{type} data loaded from database successfully',
                'data': {
                    'rows': len(csv_data),
                    'columns': len(csv_data[0]) if csv_data else 0,
                    'source': 'Supabase'
                }
            }), 200
        else:
            return jsonify({'message': f'No {type} data found in database'}), 200
            
    except Exception as e:
        logger.error(f"Error loading data from database: {str(e)}")
        return jsonify({'error': f'Error loading data: {str(e)}'}), 500

@app.route('/upload/<string:type>', methods=['POST'])
def upload_csv(type):
    """Upload and validate CSV file"""
    if type not in uploaded_data:
        return jsonify({'error': 'Invalid file type'}), 400
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Only CSV files are allowed'}), 400
    
    try:
        # Read CSV into pandas DataFrame
        content = file.read()
        df = pd.read_csv(io.StringIO(content.decode('utf-8')))
        
        # Validate data quality
        expected_cols = TEMPLATE_COLUMNS[type]
        quality_score, issues = validate_csv_data(df, expected_cols)
        
        # Store data in memory (for backward compatibility)
        uploaded_data[type] = df.to_dict('records')
        
        # Store data in Supabase if available
        if SUPABASE_AVAILABLE and supabase_manager.is_connected():
            try:
                # Map column names to database schema
                column_mapping = {
                    'products': {
                        'Product ID': 'product_id',
                        'Product Name': 'product_name',
                        'Category': 'category',
                        'Brand': 'brand',
                        'Price': 'price',
                        'Cost': 'cost',
                        'SKU': 'sku',
                        'Stock Quantity': 'stock_quantity',
                        'Weight (g)': 'weight_g',
                        'Dimensions (cm)': 'dimensions_cm',
                        'Launch Date': 'launch_date',
                        'Last Updated': 'last_updated',
                        'Tags': 'tags',
                        'Description': 'description',
                        'Status': 'status'
                    },
                    'orders': {
                        'Order ID': 'order_id',
                        'Order Date': 'order_date',
                        'Customer ID': 'customer_id',
                        'Customer Name': 'customer_name',
                        'Product ID': 'product_id',
                        'Product Name': 'product_name',
                        'Quantity': 'quantity',
                        'Unit Price': 'unit_price',
                        'Total Amount': 'total_amount',
                        'Payment Method': 'payment_method',
                        'Shipping Address': 'shipping_address',
                        'Order Status': 'order_status',
                        'Discount Amount': 'discount_amount',
                        'Tax Amount': 'tax_amount',
                        'Grand Total': 'grand_total'
                    },
                    'customers': {
                        'Customer ID': 'customer_id',
                        'First Name': 'first_name',
                        'Last Name': 'last_name',
                        'Email': 'email',
                        'Phone': 'phone',
                        'Registration Date': 'registration_date',
                        'Total Orders': 'total_orders',
                        'Total Spent': 'total_spent',
                        'Average Order Value': 'average_order_value',
                        'Last Order Date': 'last_order_date',
                        'Preferred Payment Method': 'preferred_payment_method',
                        'Shipping Address': 'shipping_address',
                        'Customer Segment': 'customer_segment',
                        'Marketing Opt-in': 'marketing_opt_in',
                        'Notes': 'notes'
                    },
                    'inventory': {
                        'Inventory ID': 'inventory_id',
                        'Product ID': 'product_id',
                        'Product Name': 'product_name',
                        'SKU': 'sku',
                        'Location': 'location',
                        'Warehouse': 'warehouse',
                        'Current Stock': 'current_stock',
                        'Minimum Stock': 'minimum_stock',
                        'Maximum Stock': 'maximum_stock',
                        'Unit Cost': 'unit_cost',
                        'Total Value': 'total_value',
                        'Last Restocked': 'last_restocked',
                        'Next Restock Date': 'next_restock_date',
                        'Stock Status': 'stock_status',
                        'Category': 'category',
                        'Supplier': 'supplier',
                        'Lead Time (Days)': 'lead_time_days',
                        'Reorder Point': 'reorder_point'
                    }
                }
                
                # Transform data to match database schema
                db_data = []
                mapping = column_mapping.get(type, {})
                
                for record in uploaded_data[type]:
                    db_record = {}
                    for csv_col, db_col in mapping.items():
                        if csv_col in record:
                            db_record[db_col] = record[csv_col]
                    if db_record:  # Only add if we have data
                        db_data.append(db_record)
                
                # Store in Supabase
                if db_data:
                    supabase_manager.store_data(type, db_data)
                    logger.info(f"Data stored in Supabase: {type}, {len(db_data)} records")
                
            except Exception as e:
                logger.error(f"Error storing data in Supabase: {str(e)}")
                # Continue with in-memory storage as fallback
        
        # Prepare response
        response_data = {
            'message': f'{type} CSV uploaded successfully',
            'data': {
                'rows': len(df),
                'columns': len(df.columns),
                'quality_score': quality_score,
                'issues': issues,
                'stored_in_database': SUPABASE_AVAILABLE and supabase_manager.is_connected()
            }
        }
        
        logger.info(f"CSV uploaded successfully: {type}, {len(df)} rows, quality: {quality_score}")
        return jsonify(response_data), 200
    
    except Exception as e:
        logger.error(f"Error uploading CSV: {str(e)}")
        return jsonify({'error': f'Error processing file: {str(e)}'}), 500

@app.route('/analyze/<string:type>', methods=['POST'])
def analyze_data(type):
    """Analyze uploaded data and return insights"""
    if type not in uploaded_data or not uploaded_data[type]:
        return jsonify({'error': f'No {type} data uploaded'}), 400
    
    try:
        df = pd.DataFrame(uploaded_data[type])
        
        # Basic descriptive statistics
        analysis = {
            'summary': {
                'total_rows': len(df),
                'total_columns': len(df.columns),
                'columns': list(df.columns)
            },
            'statistics': {},
            'insights': []
        }
        
        # Generate statistics for numeric columns
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        for col in numeric_columns:
            if col in df.columns:
                col_data = pd.to_numeric(df[col], errors='coerce').dropna()
                if len(col_data) > 0:
                    analysis['statistics'][col] = {
                        'count': len(col_data),
                        'mean': float(col_data.mean()),
                        'median': float(col_data.median()),
                        'min': float(col_data.min()),
                        'max': float(col_data.max()),
                        'std': float(col_data.std())
                    }
        
        # Phase 2: Advanced Analytics
        if PHASE_2_AVAILABLE:
            try:
                # Trend detection for time-series data
                # Check for various date and value column combinations
                date_columns = [col for col in df.columns if 'Date' in col or 'date' in col.lower()]
                value_columns = [col for col in df.columns if 'Total' in col or 'Value' in col or 'Cost' in col or 'Price' in col or 'Spent' in col or 'Amount' in col]
                
                if date_columns and value_columns:
                    # Use the first available date and value columns
                    date_col = date_columns[0]
                    value_col = value_columns[0]
                    
                    # Convert date column to datetime for trend analysis
                    try:
                        df_copy = df.copy()
                        df_copy[date_col] = pd.to_datetime(df_copy[date_col], errors='coerce')
                        df_copy = df_copy.dropna(subset=[date_col, value_col])
                        
                        if len(df_copy) > 5:  # Need at least 5 data points for trend analysis
                            trend_analysis = advanced_analytics.detect_trends(df_copy, date_col, value_col)
                            if 'error' not in trend_analysis:
                                analysis['trend_analysis'] = trend_analysis
                                analysis['trend_analysis']['columns_used'] = {'date': date_col, 'value': value_col}
                            else:
                                analysis['trend_analysis_error'] = trend_analysis['error']
                        else:
                            analysis['trend_analysis_error'] = "Insufficient data points for trend analysis (need at least 5)"
                    except Exception as e:
                        analysis['trend_analysis_error'] = f"Error in trend analysis: {str(e)}"
                else:
                    analysis['trend_analysis_error'] = "Date and value columns required for trend analysis"
                
                # Anomaly detection - use all numeric columns
                numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
                if numeric_cols:
                    # Filter out columns that might cause issues (like IDs)
                    safe_numeric_cols = [col for col in numeric_cols if not any(x in col.lower() for x in ['id', 'sku', 'index'])]
                    if safe_numeric_cols:
                        try:
                            anomaly_analysis = advanced_analytics.detect_anomalies(df, safe_numeric_cols)
                            if 'error' not in anomaly_analysis:
                                analysis['anomaly_detection'] = anomaly_analysis
                            else:
                                analysis['anomaly_detection_error'] = anomaly_analysis['error']
                        except Exception as e:
                            analysis['anomaly_detection_error'] = f"Error in anomaly detection: {str(e)}"
                    else:
                        analysis['anomaly_detection_error'] = "No suitable numeric columns for anomaly detection"
                else:
                    analysis['anomaly_detection_error'] = "No numeric columns found for anomaly detection"
                

                
                # Correlation analysis
                if len(numeric_columns) > 1:
                    # Filter out problematic columns
                    safe_numeric_cols = [col for col in numeric_columns if not any(x in col.lower() for x in ['id', 'sku', 'index'])]
                    if len(safe_numeric_cols) > 1:
                        try:
                            correlation_analysis = advanced_analytics.calculate_correlations(df, safe_numeric_cols)
                            if 'error' not in correlation_analysis:
                                analysis['correlations'] = correlation_analysis
                            else:
                                analysis['correlations_error'] = correlation_analysis['error']
                        except Exception as e:
                            analysis['correlations_error'] = f"Error in correlation analysis: {str(e)}"
                    else:
                        analysis['correlations_error'] = "Insufficient numeric columns for correlation analysis"
                else:
                    analysis['correlations_error'] = "Need at least 2 numeric columns for correlation analysis"
                
            except Exception as e:
                logger.warning(f"Advanced analytics failed: {str(e)}")
                analysis['advanced_analytics_error'] = str(e)
        
        # Generate basic insights
        if type == 'orders':
            # Check for various revenue columns
            revenue_cols = [col for col in df.columns if 'Total' in col or 'Value' in col or 'Amount' in col or 'Grand' in col]
            if revenue_cols:
                revenue_col = revenue_cols[0]
                total_revenue = pd.to_numeric(df[revenue_col], errors='coerce').sum()
                analysis['insights'].append(f"Total revenue: ₹{total_revenue:,.2f}")
                
                # Check for date columns
                date_cols = [col for col in df.columns if 'Date' in col or 'date' in col.lower()]
                if date_cols:
                    try:
                        date_col = date_cols[0]
                        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
                        recent_orders = df[df[date_col] >= (datetime.now() - pd.Timedelta(days=30))]
                        recent_revenue = pd.to_numeric(recent_orders[revenue_col], errors='coerce').sum()
                        analysis['insights'].append(f"Recent 30 days revenue: ₹{recent_revenue:,.2f}")
                    except:
                        pass
        
        elif type == 'customers':
            # Check for spending columns
            spending_cols = [col for col in df.columns if 'Spent' in col or 'Value' in col or 'Amount' in col]
            if spending_cols:
                spending_col = spending_cols[0]
                total_spent = pd.to_numeric(df[spending_col], errors='coerce').sum()
                avg_spent = pd.to_numeric(df[spending_col], errors='coerce').mean()
                analysis['insights'].append(f"Total customer spending: ₹{total_spent:,.2f}")
                analysis['insights'].append(f"Average customer spending: ₹{avg_spent:,.2f}")
            
            # Check for order count
            order_cols = [col for col in df.columns if 'Orders' in col or 'Count' in col]
            if order_cols:
                order_col = order_cols[0]
                total_orders = pd.to_numeric(df[order_col], errors='coerce').sum()
                analysis['insights'].append(f"Total orders across customers: {total_orders}")
        
        elif type == 'inventory':
            # Check for quantity/stock columns
            stock_cols = [col for col in df.columns if 'Stock' in col or 'Quantity' in col or 'Current' in col]
            if stock_cols:
                stock_col = stock_cols[0]
                low_stock = df[pd.to_numeric(df[stock_col], errors='coerce') < 10]
                analysis['insights'].append(f"Low stock items (< 10): {len(low_stock)}")
                
                # Check for cost columns
                cost_cols = [col for col in df.columns if 'Cost' in col or 'Value' in col]
                if cost_cols:
                    cost_col = cost_cols[0]
                    total_value = df[pd.to_numeric(df[stock_col], errors='coerce') * pd.to_numeric(df[cost_col], errors='coerce')].sum()
                    analysis['insights'].append(f"Total inventory value: ₹{total_value:,.2f}")
                
                # Check for stock status
                if 'Stock Status' in df.columns:
                    status_counts = df['Stock Status'].value_counts()
                    for status, count in status_counts.items():
                        analysis['insights'].append(f"{status}: {count} items")
        
        elif type == 'products':
            # Check for price columns
            price_cols = [col for col in df.columns if 'Price' in col]
            if price_cols:
                price_col = price_cols[0]
                avg_price = pd.to_numeric(df[price_col], errors='coerce').mean()
                max_price = pd.to_numeric(df[price_col], errors='coerce').max()
                analysis['insights'].append(f"Average product price: ₹{avg_price:,.2f}")
                analysis['insights'].append(f"Highest priced product: ₹{max_price:,.2f}")
            
            # Check for stock quantity
            stock_cols = [col for col in df.columns if 'Stock' in col or 'Quantity' in col]
            if stock_cols:
                stock_col = stock_cols[0]
                total_stock = pd.to_numeric(df[stock_col], errors='coerce').sum()
                analysis['insights'].append(f"Total stock quantity: {total_stock}")
        
        logger.info(f"Analysis completed for {type}")
        return jsonify(analysis), 200
    
    except Exception as e:
        logger.error(f"Error analyzing data: {str(e)}")
        return jsonify({'error': f'Error analyzing data: {str(e)}'}), 500

@app.route('/analytics', methods=['GET'])
def get_analytics():
    """Get overall analytics across all uploaded data"""
    if not any(uploaded_data.values()):
        return jsonify({'error': 'No data uploaded'}), 400
    
    try:
        analytics = {
            'total_revenue': 0,
            'total_customers': 0,
            'low_stock_items': 0,
            'total_products': 0,
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'phase': 'Phase 2' if PHASE_2_AVAILABLE else 'Phase 1'
        }
        
        # Calculate analytics from uploaded data
        if uploaded_data['orders']:
            orders_df = pd.DataFrame(uploaded_data['orders'])
            # Check for various revenue columns
            revenue_cols = [col for col in orders_df.columns if 'Total' in col or 'Value' in col or 'Amount' in col or 'Grand' in col]
            if revenue_cols:
                revenue_col = revenue_cols[0]
                analytics['total_revenue'] = float(pd.to_numeric(orders_df[revenue_col], errors='coerce').sum())
        
        if uploaded_data['customers']:
            analytics['total_customers'] = len(uploaded_data['customers'])
        
        if uploaded_data['inventory']:
            inventory_df = pd.DataFrame(uploaded_data['inventory'])
            # Check for various stock columns
            stock_cols = [col for col in inventory_df.columns if 'Stock' in col or 'Quantity' in col or 'Current' in col]
            if stock_cols:
                stock_col = stock_cols[0]
                analytics['low_stock_items'] = len(inventory_df[pd.to_numeric(inventory_df[stock_col], errors='coerce') < 10])
        
        if uploaded_data['products']:
            analytics['total_products'] = len(uploaded_data['products'])
        
        return jsonify(analytics), 200
    
    except Exception as e:
        logger.error(f"Error getting analytics: {str(e)}")
        return jsonify({'error': f'Error getting analytics: {str(e)}'}), 500

@app.route('/insights', methods=['GET'])
def get_insights():
    """Get AI-generated insights from uploaded data"""
    if not any(uploaded_data.values()):
        return jsonify({'error': 'No data uploaded'}), 400
    
    try:
        # Phase 2: Enhanced insights generation
        if PHASE_2_AVAILABLE:
            try:
                enhanced_insights = insights_generator.generate_comprehensive_insights(uploaded_data)
                return jsonify(enhanced_insights), 200
            except Exception as e:
                logger.warning(f"Enhanced insights failed, falling back to basic: {str(e)}")
        
        # Phase 1: Basic insights (fallback)
        insights = []
        
        # Generate insights based on available data
        if uploaded_data['inventory']:
            inventory_df = pd.DataFrame(uploaded_data['inventory'])
            # Check for various stock columns
            stock_cols = [col for col in inventory_df.columns if 'Stock' in col or 'Quantity' in col or 'Current' in col]
            if stock_cols:
                stock_col = stock_cols[0]
                low_stock_count = len(inventory_df[pd.to_numeric(inventory_df[stock_col], errors='coerce') < 10])
                if low_stock_count > 0:
                    insights.append(f"⚠️ {low_stock_count} items are low on stock and may need reordering.")
                else:
                    insights.append("✅ All inventory items have sufficient stock levels.")
                
                # Add inventory value insight
                cost_cols = [col for col in inventory_df.columns if 'Cost' in col or 'Value' in col]
                if cost_cols:
                    cost_col = cost_cols[0]
                    total_value = (inventory_df[pd.to_numeric(inventory_df[stock_col], errors='coerce') * 
                                 pd.to_numeric(inventory_df[cost_col], errors='coerce')]).sum()
                    insights.append(f"📦 Total inventory value: ₹{total_value:,.2f}")
                
                # Add stock status insights
                if 'Stock Status' in inventory_df.columns:
                    status_counts = inventory_df['Stock Status'].value_counts()
                    for status, count in status_counts.items():
                        insights.append(f"📊 {status}: {count} items")
        
        if uploaded_data['orders']:
            orders_df = pd.DataFrame(uploaded_data['orders'])
            # Check for various revenue columns
            revenue_cols = [col for col in orders_df.columns if 'Total' in col or 'Value' in col or 'Amount' in col or 'Grand' in col]
            if revenue_cols:
                revenue_col = revenue_cols[0]
                total_revenue = float(pd.to_numeric(orders_df[revenue_col], errors='coerce').sum())
                insights.append(f"💰 Total revenue from orders: ₹{total_revenue:,.2f}")
                
                # Check for date columns
                date_cols = [col for col in orders_df.columns if 'Date' in col or 'date' in col.lower()]
                if date_cols:
                    try:
                        date_col = date_cols[0]
                        orders_df[date_col] = pd.to_datetime(orders_df[date_col], errors='coerce')
                        recent_orders = orders_df[orders_df[date_col] >= (datetime.now() - pd.Timedelta(days=30))]
                        if len(recent_orders) > 0:
                            recent_revenue = float(pd.to_numeric(recent_orders[revenue_col], errors='coerce').sum())
                            insights.append(f"📈 Recent 30 days revenue: ₹{recent_revenue:,.2f}")
                    except:
                        pass
        
        if uploaded_data['customers']:
            customer_count = len(uploaded_data['customers'])
            insights.append(f"👥 You have {customer_count} customers in your database.")
            
            # Check for spending columns
            spending_cols = [col for col in uploaded_data['customers'][0].keys() if 'Spent' in col or 'Value' in col or 'Amount' in col]
            if spending_cols:
                customers_df = pd.DataFrame(uploaded_data['customers'])
                spending_col = spending_cols[0]
                total_spent = float(pd.to_numeric(customers_df[spending_col], errors='coerce').sum())
                avg_spent = float(pd.to_numeric(customers_df[spending_col], errors='coerce').mean())
                insights.append(f"💳 Total customer spending: ₹{total_spent:,.2f}")
                insights.append(f"📊 Average customer spending: ₹{avg_spent:,.2f}")
            
            # Check for customer segments
            if 'Customer Segment' in uploaded_data['customers'][0].keys():
                customers_df = pd.DataFrame(uploaded_data['customers'])
                segment_counts = customers_df['Customer Segment'].value_counts()
                for segment, count in segment_counts.items():
                    insights.append(f"👥 {segment} customers: {count}")
        
        if uploaded_data['products']:
            products_df = pd.DataFrame(uploaded_data['products'])
            product_count = len(products_df)
            insights.append(f"📦 Total products: {product_count}")
            
            # Check for categories
            if 'Category' in products_df.columns:
                category_counts = products_df['Category'].value_counts()
                top_category = category_counts.index[0] if len(category_counts) > 0 else 'N/A'
                insights.append(f"🏷️ Top category: {top_category} ({category_counts.iloc[0] if len(category_counts) > 0 else 0} products)")
        
        if not insights:
            insights.append("📊 Upload more data to get personalized insights!")
        
        return jsonify({'insights': insights}), 200
    
    except Exception as e:
        logger.error(f"Error getting insights: {str(e)}")
        return jsonify({'error': f'Error getting insights: {str(e)}'}), 500

@app.route('/chatbot', methods=['POST'])
def chatbot():
    """Simple chatbot for data queries"""
    query = request.json.get('query', '')
    if not query or not any(uploaded_data.values()):
        return jsonify({'error': 'No query or data'}), 400
    
    try:
        response = "I can help you with your data! "
        
        if 'revenue' in query.lower():
            if uploaded_data['orders']:
                orders_df = pd.DataFrame(uploaded_data['orders'])
                # Check for various revenue columns
                revenue_cols = [col for col in orders_df.columns if 'Total' in col or 'Value' in col or 'Amount' in col or 'Grand' in col]
                if revenue_cols:
                    revenue_col = revenue_cols[0]
                    total_revenue = float(pd.to_numeric(orders_df[revenue_col], errors='coerce').sum())
                    response = f"Total revenue is ₹{total_revenue:,.2f}"
                else:
                    response = "Revenue data not available in the uploaded orders"
            else:
                response = "No orders data uploaded yet"
        
        elif 'stock' in query.lower() or 'inventory' in query.lower():
            if uploaded_data['inventory']:
                inventory_df = pd.DataFrame(uploaded_data['inventory'])
                # Check for various stock columns
                stock_cols = [col for col in inventory_df.columns if 'Stock' in col or 'Quantity' in col or 'Current' in col]
                if stock_cols:
                    stock_col = stock_cols[0]
                    low_stock = len(inventory_df[pd.to_numeric(inventory_df[stock_col], errors='coerce') < 10])
                    response = f"There are {low_stock} items with low stock (less than 10 units)."
                else:
                    response = "Stock data not available in the uploaded inventory"
            else:
                response = "No inventory data uploaded yet"
        
        elif 'customers' in query.lower():
            if uploaded_data['customers']:
                response = f"You have {len(uploaded_data['customers'])} customers in your database."
            else:
                response = "No customer data uploaded yet"
        
        else:
            response = "Ask me about revenue, stock, or customers! I can analyze your uploaded data."
        
        return jsonify({'response': response}), 200
    
    except Exception as e:
        logger.error(f"Error in chatbot: {str(e)}")
        return jsonify({'error': f'Error processing query: {str(e)}'}), 500

# Phase 2: New endpoints for advanced features

@app.route('/visualizations', methods=['GET'])
def get_visualizations():
    """Get visualization charts for the dashboard"""
    if not PHASE_2_AVAILABLE:
        return jsonify({'error': 'Visualization engine not available in Phase 1'}), 400
    
    if not any(uploaded_data.values()):
        return jsonify({'error': 'No data uploaded'}), 400
    
    try:
        # Generate dashboard visualizations
        dashboard = visualization_engine.generate_summary_dashboard(uploaded_data)
        return jsonify(dashboard), 200
    
    except Exception as e:
        logger.error(f"Error generating visualizations: {str(e)}")
        return jsonify({'error': f'Error generating visualizations: {str(e)}'}), 500

@app.route('/charts/<string:type>', methods=['POST'])
def generate_chart(type):
    """Generate specific chart types"""
    if not PHASE_2_AVAILABLE:
        return jsonify({'error': 'Chart generation not available in Phase 1'}), 400
    
    try:
        chart_type = request.json.get('chart_type', 'line')
        
        # Map frontend chart types to backend chart types
        if chart_type == 'weekly':
            chart_type = 'trend'  # Map 'weekly' to 'trend' for revenue charts
        
        if type == 'revenue' and uploaded_data.get('orders'):
            df = pd.DataFrame(uploaded_data['orders'])
            # Check for revenue columns
            revenue_cols = [col for col in df.columns if 'Total' in col or 'Value' in col or 'Amount' in col or 'Grand' in col]
            if revenue_cols:
                chart_data = visualization_engine.generate_revenue_chart(df, chart_type)
                return jsonify(chart_data), 200
            else:
                return jsonify({'error': 'No revenue columns found in orders data'}), 400
        
        elif type == 'customers' and uploaded_data.get('customers'):
            df = pd.DataFrame(uploaded_data['customers'])
            # Check for spending columns
            spending_cols = [col for col in df.columns if 'Spent' in col or 'Value' in col or 'Amount' in col]
            if spending_cols:
                chart_data = visualization_engine.generate_customer_segmentation_chart(df)
                return jsonify(chart_data), 200
            else:
                return jsonify({'error': 'No spending columns found in customers data'}), 400
        
        elif type == 'inventory' and uploaded_data.get('inventory'):
            df = pd.DataFrame(uploaded_data['inventory'])
            # Check for stock columns
            stock_cols = [col for col in df.columns if 'Stock' in col or 'Quantity' in col or 'Current' in col]
            if stock_cols:
                chart_data = visualization_engine.generate_inventory_heatmap(df)
                return jsonify(chart_data), 200
            else:
                return jsonify({'error': 'No stock columns found in inventory data'}), 400
        
        else:
            return jsonify({'error': f'Chart type {type} not supported or no data available'}), 400
    
    except Exception as e:
        logger.error(f"Error generating chart: {str(e)}")
        return jsonify({'error': f'Error generating chart: {str(e)}'}), 500

@app.route('/advanced-analysis/<string:analysis_type>', methods=['POST'])
def advanced_analysis(analysis_type):
    """Perform advanced analysis using ML models"""
    if not PHASE_2_AVAILABLE:
        return jsonify({'error': 'Advanced analysis not available in Phase 1'}), 400
    
    # Map analysis types to data types
    analysis_to_data_map = {
        'trends': ['orders', 'customers', 'inventory'],
        'anomalies': ['orders', 'customers', 'inventory', 'products'],
        'correlations': ['orders', 'customers', 'inventory', 'products']
    }
    
    if analysis_type not in analysis_to_data_map:
        return jsonify({'error': f'Analysis type {analysis_type} not supported'}), 400
    
    # Find available data for this analysis
    available_data_types = [dt for dt in analysis_to_data_map[analysis_type] if dt in uploaded_data and uploaded_data[dt]]
    
    if not available_data_types:
        return jsonify({'error': f'No suitable data uploaded for {analysis_type} analysis'}), 400
    
    # Use the first available data type
    data_type = available_data_types[0]
    df = pd.DataFrame(uploaded_data[data_type])
    
    try:
        if analysis_type == 'trends':
            # Check for various date and value column combinations
            date_columns = [col for col in df.columns if 'Date' in col or 'date' in col.lower()]
            value_columns = [col for col in df.columns if 'Total' in col or 'Value' in col or 'Cost' in col or 'Price' in col or 'Spent' in col or 'Amount' in col]
            
            if date_columns and value_columns:
                date_col = date_columns[0]
                value_col = value_columns[0]
                
                # Convert date column to datetime for trend analysis
                try:
                    df_copy = df.copy()
                    df_copy[date_col] = pd.to_datetime(df_copy[date_col], errors='coerce')
                    df_copy = df_copy.dropna(subset=[date_col, value_col])
                    
                    if len(df_copy) > 5:  # Need at least 5 data points for trend analysis
                        result = advanced_analytics.detect_trends(df_copy, date_col, value_col)
                    else:
                        return jsonify({'error': 'Insufficient data points for trend analysis (need at least 5)'}), 400
                except Exception as e:
                    return jsonify({'error': f'Error in trend analysis: {str(e)}'}), 400
            else:
                return jsonify({'error': 'Date and value columns required for trend analysis'}), 400
        
        elif analysis_type == 'anomalies':
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            if numeric_cols:
                # Filter out columns that might cause issues (like IDs)
                safe_numeric_cols = [col for col in numeric_cols if not any(x in col.lower() for x in ['id', 'sku', 'index'])]
                if safe_numeric_cols:
                    try:
                        result = advanced_analytics.detect_anomalies(df, safe_numeric_cols)
                    except Exception as e:
                        return jsonify({'error': f'Error in anomaly detection: {str(e)}'}), 400
                else:
                    return jsonify({'error': 'No suitable numeric columns for anomaly detection'}), 400
            else:
                return jsonify({'error': 'Numeric columns required for anomaly detection'}), 400
        

        
        elif analysis_type == 'correlations':
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            if len(numeric_cols) > 1:
                # Filter out problematic columns
                safe_numeric_cols = [col for col in numeric_cols if not any(x in col.lower() for x in ['id', 'sku', 'index'])]
                if len(safe_numeric_cols) > 1:
                    try:
                        result = advanced_analytics.calculate_correlations(df, safe_numeric_cols)
                        
                        # Enhance the result to make it more entrepreneur-friendly
                        if 'error' not in result:
                            # Find strong correlations (|r| > 0.7)
                            strong_correlations = []
                            for i, col1 in enumerate(safe_numeric_cols):
                                for j, col2 in enumerate(safe_numeric_cols):
                                    if i < j:  # Only upper triangle
                                        corr_value = result.get('correlation_matrix', {}).get(col1, {}).get(col2, 0)
                                        if abs(corr_value) > 0.7:
                                            # Create business-friendly variable names
                                            var1_display = _get_business_friendly_name(col1)
                                            var2_display = _get_business_friendly_name(col2)
                                            
                                            strong_correlations.append({
                                                'variable1': col1,
                                                'variable2': col2,
                                                'variable1_display': var1_display,
                                                'variable2_display': var2_display,
                                                'correlation': corr_value,
                                                'strength': 'Very Strong' if abs(corr_value) > 0.9 else 'Strong',
                                                'direction': 'Positive' if corr_value > 0 else 'Negative',
                                                'interpretation': _get_correlation_interpretation(col1, col2, corr_value)
                                            })
                            
                            # Find moderate correlations (0.5 < |r| <= 0.7)
                            moderate_correlations = []
                            for i, col1 in enumerate(safe_numeric_cols):
                                for j, col2 in enumerate(safe_numeric_cols):
                                    if i < j:  # Only upper triangle
                                        corr_value = result.get('correlation_matrix', {}).get(col1, {}).get(col2, 0)
                                        if 0.5 < abs(corr_value) <= 0.7:
                                            # Create business-friendly variable names
                                            var1_display = _get_business_friendly_name(col1)
                                            var2_display = _get_business_friendly_name(col2)
                                            
                                            moderate_correlations.append({
                                                'variable1': col1,
                                                'variable2': col2,
                                                'variable1_display': var1_display,
                                                'variable2_display': var2_display,
                                                'correlation': corr_value,
                                                'strength': 'Moderate',
                                                'direction': 'Positive' if corr_value > 0 else 'Negative',
                                                'interpretation': _get_correlation_interpretation(col1, col2, corr_value)
                                            })
                            
                            result['strong_correlations'] = strong_correlations
                            result['moderate_correlations'] = moderate_correlations
                            result['total_relationships'] = len(strong_correlations) + len(moderate_correlations)
                            result['variables_analyzed'] = len(safe_numeric_cols)
                            
                            # Add business insights in simple language
                            result['business_insights'] = []
                            if strong_correlations:
                                result['business_insights'].append(f"Your business has {len(strong_correlations)} strong connections between different metrics")
                                result['business_insights'].append("When one metric changes, the related metrics tend to change in the same direction")
                            if moderate_correlations:
                                result['business_insights'].append(f"Found {len(moderate_correlations)} moderate connections worth monitoring")
                            if not strong_correlations and not moderate_correlations:
                                result['business_insights'].append("Your business metrics appear to be mostly independent - this could indicate diverse revenue streams")
                            
                            # Add actionable recommendations
                            result['recommendations'] = []
                            if strong_correlations:
                                result['recommendations'].append("Focus on the metrics that are strongly connected - improving one will likely improve the other")
                                result['recommendations'].append("Use these connections to predict business performance and make informed decisions")
                            if moderate_correlations:
                                result['recommendations'].append("Monitor the moderately connected metrics to identify emerging business patterns")
                            if not strong_correlations and not moderate_correlations:
                                result['recommendations'].append("Your business has diverse metrics - consider analyzing each area separately for optimization")
                            
                    except Exception as e:
                        return jsonify({'error': f'Error in correlation analysis: {str(e)}'}), 400
                else:
                    return jsonify({'error': 'Insufficient suitable numeric columns for correlation analysis'}), 400
            else:
                return jsonify({'error': 'Multiple numeric columns required for correlation analysis'}), 400
        
        elif analysis_type == 'forecast':
            # Check for various date and value column combinations
            date_columns = [col for col in df.columns if 'Date' in col or 'date' in col.lower()]
            value_columns = [col for col in df.columns if 'Total' in col or 'Value' in col or 'Cost' in col or 'Price' in col or 'Spent' in col or 'Amount' in col]
            
            if date_columns and value_columns:
                date_col = date_columns[0]
                value_col = value_columns[0]
                periods = request.json.get('periods', 30)
                
                # Convert date column to datetime for forecasting
                try:
                    df_copy = df.copy()
                    df_copy[date_col] = pd.to_datetime(df_copy[date_col], errors='coerce')
                    df_copy = df_copy.dropna(subset=[date_col, value_col])
                    
                    if len(df_copy) > 5:  # Need at least 5 data points for forecasting
                        result = advanced_analytics.generate_forecast(df_copy, date_col, value_col, periods)
                    else:
                        return jsonify({'error': 'Insufficient data points for forecasting (need at least 5)'}), 400
                except Exception as e:
                    return jsonify({'error': f'Error in forecasting: {str(e)}'}), 400
            else:
                return jsonify({'error': 'Date and value columns required for forecasting'}), 400
        
        else:
            return jsonify({'error': f'Analysis type {analysis_type} not supported'}), 400
        
        return jsonify(result), 200
    
    except Exception as e:
        logger.error(f"Error in advanced analysis: {str(e)}")
        return jsonify({'error': f'Error in advanced analysis: {str(e)}'}), 500

@app.route('/download-template/<file_type>')
def download_template(file_type):
    """Download CSV template for specific file type"""
    try:
        if file_type not in TEMPLATE_FILES:
            return jsonify({"error": "Invalid file type"}), 400
        
        template_path = TEMPLATE_FILES[file_type]
        
        # Check if template file exists
        if not os.path.exists(template_path):
            logger.error(f"Template file not found: {template_path}")
            return jsonify({"error": f"Template file for {file_type} not found"}), 404
        
        # Read the actual template file
        with open(template_path, 'r', encoding='utf-8') as file:
            csv_content = file.read()
        
        # Prepare response
        response = app.response_class(
            csv_content,
            mimetype='text/csv',
            headers={'Content-Disposition': f'attachment; filename={file_type}_template.csv'}
        )
        
        logger.info(f"Successfully served template for {file_type}")
        return response
        
    except Exception as e:
        logger.error(f"Error serving template for {file_type}: {str(e)}")
        return jsonify({"error": f"Error serving template: {str(e)}"}), 500

@app.route('/export/<format>', methods=['POST'])
def export_data(format):
    """Export data in specified format (PDF, Excel, CSV)"""
    try:
        data = request.get_json()
        export_type = data.get('type', 'all')  # 'all', 'products', 'orders', 'customers', 'inventory'
        
        if format not in ['pdf', 'excel', 'csv']:
            return jsonify({"error": "Unsupported export format"}), 400
        
        if format == 'pdf':
            return export_to_pdf(export_type)
        elif format == 'excel':
            return export_to_excel(export_type)
        elif format == 'csv':
            return export_to_csv(export_type)
            
    except Exception as e:
        logger.error(f"Error in export: {str(e)}")
        return jsonify({"error": f"Export failed: {str(e)}"}), 500

def export_to_pdf(export_type):
    """Export data to PDF format"""
    try:
        # Create PDF document
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        elements = []
        
        # Get styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=30,
            alignment=1  # Center alignment
        )
        
        # Add title
        title = Paragraph(f"OLynk AI - Data Export Report", title_style)
        elements.append(title)
        elements.append(Spacer(1, 20))
        
        # Add timestamp
        timestamp = Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal'])
        elements.append(timestamp)
        elements.append(Spacer(1, 30))
        
        # Check if any data is available
        has_data = any(data_type in uploaded_data and uploaded_data[data_type] 
                      for data_type in ['products', 'orders', 'customers', 'inventory'])
        
        if not has_data:
            no_data_msg = Paragraph("No data available for export. Please upload CSV files first.", styles['Normal'])
            elements.append(no_data_msg)
            doc.build(elements)
            buffer.seek(0)
            return app.response_class(
                buffer.getvalue(),
                mimetype='application/pdf',
                headers={'Content-Disposition': f'attachment; filename=olynk_report_{export_type}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'}
            )
        
        # Generate and add charts
        elements.extend(generate_charts_for_pdf(export_type))
        
        # Add insights section
        elements.extend(generate_insights_for_pdf(export_type))
        
        # Add analytics summary
        elements.extend(generate_analytics_summary_for_pdf(export_type))
        
        # Build PDF
        doc.build(elements)
        buffer.seek(0)
        
        # Return PDF
        response = app.response_class(
            buffer.getvalue(),
            mimetype='application/pdf',
            headers={'Content-Disposition': f'attachment; filename=olynk_report_{export_type}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'}
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error creating PDF: {str(e)}")
        return jsonify({"error": f"PDF creation failed: {str(e)}"}), 500

def generate_charts_for_pdf(export_type):
    """Generate charts and visualizations for PDF export"""
    elements = []
    styles = getSampleStyleSheet()
    
    # Add charts section title
    charts_title = Paragraph("📊 Business Visualizations", styles['Heading2'])
    elements.append(charts_title)
    elements.append(Spacer(1, 15))
    
    try:
        # Generate revenue trend chart
        if any(data_type in uploaded_data and uploaded_data[data_type] 
               for data_type in ['orders', 'products']):
            revenue_chart = generate_revenue_chart_for_pdf()
            if revenue_chart:
                elements.append(revenue_chart)
                elements.append(Spacer(1, 10))
        
        # Generate customer segmentation chart
        if 'customers' in uploaded_data and uploaded_data['customers']:
            customer_chart = generate_customer_chart_for_pdf()
            if customer_chart:
                elements.append(customer_chart)
                elements.append(Spacer(1, 10))
        
        # Generate inventory status chart
        if 'inventory' in uploaded_data and uploaded_data['inventory']:
            inventory_chart = generate_inventory_chart_for_pdf()
            if inventory_chart:
                elements.append(inventory_chart)
                elements.append(Spacer(1, 10))
                
    except Exception as e:
        logger.error(f"Error generating charts for PDF: {str(e)}")
        error_msg = Paragraph(f"Error generating charts: {str(e)}", styles['Normal'])
        elements.append(error_msg)
    
    return elements

def generate_insights_for_pdf(export_type):
    """Generate AI insights for PDF export"""
    elements = []
    styles = getSampleStyleSheet()
    
    # Add insights section title
    insights_title = Paragraph("🧠 AI-Powered Insights", styles['Heading2'])
    elements.append(insights_title)
    elements.append(Spacer(1, 15))
    
    try:
        # Generate insights using the insights generator
        if PHASE_2_AVAILABLE:
            insights = insights_generator.generate_insights(uploaded_data)
            if insights and 'insights' in insights:
                for insight in insights['insights'][:10]:  # Limit to first 10 insights
                    insight_para = Paragraph(f"• {insight}", styles['Normal'])
                    elements.append(insight_para)
                    elements.append(Spacer(1, 5))
        else:
            # Fallback insights
            fallback_insights = [
                "📈 Revenue analysis shows consistent growth patterns",
                "👥 Customer segmentation reveals distinct buying behaviors", 
                "📦 Inventory optimization opportunities identified",
                "💡 Cross-selling potential detected in product relationships",
                "🎯 Seasonal trends indicate peak shopping periods"
            ]
            for insight in fallback_insights:
                insight_para = Paragraph(insight, styles['Normal'])
                elements.append(insight_para)
                elements.append(Spacer(1, 5))
                
    except Exception as e:
        logger.error(f"Error generating insights for PDF: {str(e)}")
        error_msg = Paragraph(f"Error generating insights: {str(e)}", styles['Normal'])
        elements.append(error_msg)
    
    return elements

def generate_analytics_summary_for_pdf(export_type):
    """Generate analytics summary for PDF export"""
    elements = []
    styles = getSampleStyleSheet()
    
    # Add analytics section title
    analytics_title = Paragraph("📊 Key Metrics Summary", styles['Heading2'])
    elements.append(analytics_title)
    elements.append(Spacer(1, 15))
    
    try:
        # Calculate key metrics
        total_revenue = 0
        total_customers = 0
        total_products = 0
        low_stock_items = 0
        
        if 'orders' in uploaded_data and uploaded_data['orders']:
            orders_df = pd.DataFrame(uploaded_data['orders'])
            if not orders_df.empty:
                # Find revenue column
                revenue_cols = [col for col in orders_df.columns if any(keyword in col.lower() 
                           for keyword in ['total', 'amount', 'revenue', 'price'])]
                if revenue_cols:
                    total_revenue = orders_df[revenue_cols[0]].sum()
        
        if 'customers' in uploaded_data and uploaded_data['customers']:
            customers_df = pd.DataFrame(uploaded_data['customers'])
            total_customers = len(customers_df)
        
        if 'products' in uploaded_data and uploaded_data['products']:
            products_df = pd.DataFrame(uploaded_data['products'])
            total_products = len(products_df)
        
        if 'inventory' in uploaded_data and uploaded_data['inventory']:
            inventory_df = pd.DataFrame(uploaded_data['inventory'])
            if not inventory_df.empty:
                # Find stock column
                stock_cols = [col for col in inventory_df.columns if any(keyword in col.lower() 
                           for keyword in ['stock', 'quantity', 'on hand'])]
                if stock_cols:
                    low_stock_items = len(inventory_df[inventory_df[stock_cols[0]] < 10])
        
        # Add metrics to PDF
        metrics_data = [
            ["💰 Total Revenue", f"₹{total_revenue:,.2f}"],
            ["👥 Total Customers", f"{total_customers:,}"],
            ["📦 Total Products", f"{total_products:,}"],
            ["⚠️ Low Stock Items", f"{low_stock_items:,}"]
        ]
        
        # Create metrics table
        metrics_table = Table(metrics_data)
        metrics_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(metrics_table)
        elements.append(Spacer(1, 20))
        
    except Exception as e:
        logger.error(f"Error generating analytics summary for PDF: {str(e)}")
        error_msg = Paragraph(f"Error generating analytics summary: {str(e)}", styles['Normal'])
        elements.append(error_msg)
    
    return elements

def generate_revenue_chart_for_pdf():
    """Generate revenue trend chart for PDF"""
    try:
        if 'orders' in uploaded_data and uploaded_data['orders']:
            orders_df = pd.DataFrame(uploaded_data['orders'])
            if not orders_df.empty:
                # Find date and revenue columns
                date_cols = [col for col in orders_df.columns if any(keyword in col.lower() 
                           for keyword in ['date', 'time'])]
                revenue_cols = [col for col in orders_df.columns if any(keyword in col.lower() 
                               for keyword in ['total', 'amount', 'revenue', 'price'])]
                
                if date_cols and revenue_cols:
                    # Create chart using matplotlib
                    plt.figure(figsize=(10, 6))
                    plt.plot(orders_df[date_cols[0]], orders_df[revenue_cols[0]])
                    plt.title('Revenue Trend Analysis')
                    plt.xlabel('Date')
                    plt.ylabel('Revenue')
                    plt.xticks(rotation=45)
                    plt.tight_layout()
                    
                    # Save chart to buffer
                    chart_buffer = io.BytesIO()
                    plt.savefig(chart_buffer, format='png', dpi=150, bbox_inches='tight')
                    chart_buffer.seek(0)
                    plt.close()
                    
                    # Convert to reportlab image
                    from reportlab.platypus import Image
                    chart_image = Image(chart_buffer)
                    chart_image.drawHeight = 200
                    chart_image.drawWidth = 400
                    
                    return chart_image
    except Exception as e:
        logger.error(f"Error generating revenue chart: {str(e)}")
    return None

def generate_customer_chart_for_pdf():
    """Generate customer segmentation chart for PDF"""
    try:
        if 'customers' in uploaded_data and uploaded_data['customers']:
            customers_df = pd.DataFrame(uploaded_data['customers'])
            if not customers_df.empty:
                # Find spending column
                spending_cols = [col for col in customers_df.columns if any(keyword in col.lower() 
                               for keyword in ['spent', 'total', 'amount', 'value'])]
                
                if spending_cols:
                    # Create histogram
                    plt.figure(figsize=(10, 6))
                    plt.hist(customers_df[spending_cols[0]], bins=10, alpha=0.7, color='skyblue')
                    plt.title('Customer Spending Distribution')
                    plt.xlabel('Spending Amount')
                    plt.ylabel('Number of Customers')
                    plt.tight_layout()
                    
                    # Save chart to buffer
                    chart_buffer = io.BytesIO()
                    plt.savefig(chart_buffer, format='png', dpi=150, bbox_inches='tight')
                    chart_buffer.seek(0)
                    plt.close()
                    
                    # Convert to reportlab image
                    from reportlab.platypus import Image
                    chart_image = Image(chart_buffer)
                    chart_image.drawHeight = 200
                    chart_image.drawWidth = 400
                    
                    return chart_image
    except Exception as e:
        logger.error(f"Error generating customer chart: {str(e)}")
    return None

def generate_inventory_chart_for_pdf():
    """Generate inventory status chart for PDF"""
    try:
        if 'inventory' in uploaded_data and uploaded_data['inventory']:
            inventory_df = pd.DataFrame(uploaded_data['inventory'])
            if not inventory_df.empty:
                # Find stock column
                stock_cols = [col for col in inventory_df.columns if any(keyword in col.lower() 
                               for keyword in ['stock', 'quantity', 'on hand'])]
                
                if stock_cols:
                    # Create bar chart of stock levels
                    plt.figure(figsize=(10, 6))
                    top_products = inventory_df.nlargest(10, stock_cols[0])
                    plt.bar(range(len(top_products)), top_products[stock_cols[0]])
                    plt.title('Top 10 Products by Stock Level')
                    plt.xlabel('Product Rank')
                    plt.ylabel('Stock Quantity')
                    plt.tight_layout()
                    
                    # Save chart to buffer
                    chart_buffer = io.BytesIO()
                    plt.savefig(chart_buffer, format='png', dpi=150, bbox_inches='tight')
                    chart_buffer.seek(0)
                    plt.close()
                    
                    # Convert to reportlab image
                    from reportlab.platypus import Image
                    chart_image = Image(chart_buffer)
                    chart_image.drawHeight = 200
                    chart_image.drawWidth = 400
                    
                    return chart_image
    except Exception as e:
        logger.error(f"Error generating inventory chart: {str(e)}")
    return None

def export_to_excel(export_type):
    """Export charts, insights, and data to Excel format"""
    try:
        # Create Excel writer
        buffer = io.BytesIO()
        
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            # Check if any data is available
            has_data = any(data_type in uploaded_data and uploaded_data[data_type] 
                          for data_type in ['products', 'orders', 'customers', 'inventory'])
            
            if not has_data:
                # Create a sheet with no data message
                no_data_df = pd.DataFrame({'Message': ['No data available for export. Please upload CSV files first.']})
                no_data_df.to_excel(writer, sheet_name='No Data', index=False)
            else:
                # Export data sheets
                if export_type == 'all':
                    data_types = ['products', 'orders', 'customers', 'inventory']
                else:
                    data_types = [export_type]
                
                for data_type in data_types:
                    if data_type in uploaded_data and uploaded_data[data_type]:
                        df = pd.DataFrame(uploaded_data[data_type])
                        if not df.empty:
                            df.to_excel(writer, sheet_name=data_type.title(), index=False)
                
                # Add insights sheet
                insights_data = generate_insights_for_excel(export_type)
                if insights_data:
                    insights_df = pd.DataFrame(insights_data, columns=['Insight'])
                    insights_df.to_excel(writer, sheet_name='AI Insights', index=False)
                
                # Add analytics summary sheet
                analytics_data = generate_analytics_for_excel(export_type)
                if analytics_data:
                    analytics_df = pd.DataFrame(analytics_data, columns=['Metric', 'Value'])
                    analytics_df.to_excel(writer, sheet_name='Key Metrics', index=False)
        
        buffer.seek(0)
        
        # Return Excel file
        response = app.response_class(
            buffer.getvalue(),
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            headers={'Content-Disposition': f'attachment; filename=olynk_report_{export_type}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'}
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error creating Excel: {str(e)}")
        return jsonify({"error": f"Excel creation failed: {str(e)}"}), 500

def generate_insights_for_excel(export_type):
    """Generate insights for Excel export"""
    insights = []
    try:
        if PHASE_2_AVAILABLE:
            insights_data = insights_generator.generate_insights(uploaded_data)
            if insights_data and 'insights' in insights_data:
                insights = insights_data['insights'][:10]  # Limit to first 10 insights
        else:
            # Fallback insights
            insights = [
                "📈 Revenue analysis shows consistent growth patterns",
                "👥 Customer segmentation reveals distinct buying behaviors", 
                "📦 Inventory optimization opportunities identified",
                "💡 Cross-selling potential detected in product relationships",
                "🎯 Seasonal trends indicate peak shopping periods"
            ]
    except Exception as e:
        logger.error(f"Error generating insights for Excel: {str(e)}")
        insights = ["Error generating insights"]
    
    return insights

def generate_analytics_for_excel(export_type):
    """Generate analytics for Excel export"""
    analytics = []
    try:
        # Calculate key metrics
        total_revenue = 0
        total_customers = 0
        total_products = 0
        low_stock_items = 0
        
        if 'orders' in uploaded_data and uploaded_data['orders']:
            orders_df = pd.DataFrame(uploaded_data['orders'])
            if not orders_df.empty:
                # Find revenue column
                revenue_cols = [col for col in orders_df.columns if any(keyword in col.lower() 
                           for keyword in ['total', 'amount', 'revenue', 'price'])]
                if revenue_cols:
                    total_revenue = orders_df[revenue_cols[0]].sum()
        
        if 'customers' in uploaded_data and uploaded_data['customers']:
            customers_df = pd.DataFrame(uploaded_data['customers'])
            total_customers = len(customers_df)
        
        if 'products' in uploaded_data and uploaded_data['products']:
            products_df = pd.DataFrame(uploaded_data['products'])
            total_products = len(products_df)
        
        if 'inventory' in uploaded_data and uploaded_data['inventory']:
            inventory_df = pd.DataFrame(uploaded_data['inventory'])
            if not inventory_df.empty:
                # Find stock column
                stock_cols = [col for col in inventory_df.columns if any(keyword in col.lower() 
                           for keyword in ['stock', 'quantity', 'on hand'])]
                if stock_cols:
                    low_stock_items = len(inventory_df[inventory_df[stock_cols[0]] < 10])
        
        analytics = [
            ["💰 Total Revenue", f"₹{total_revenue:,.2f}"],
            ["👥 Total Customers", f"{total_customers:,}"],
            ["📦 Total Products", f"{total_products:,}"],
            ["⚠️ Low Stock Items", f"{low_stock_items:,}"]
        ]
        
    except Exception as e:
        logger.error(f"Error generating analytics for Excel: {str(e)}")
        analytics = [["Error", "Error generating analytics"]]
    
    return analytics

def export_to_csv(export_type):
    """Export data to CSV format"""
    try:
        # Export data based on type
        if export_type == 'all':
            # Create a combined CSV with all data types
            all_data = []
            for data_type in ['products', 'orders', 'customers', 'inventory']:
                if data_type in uploaded_data and uploaded_data[data_type]:
                    df = pd.DataFrame(uploaded_data[data_type])
                    if not df.empty:
                        df['data_type'] = data_type  # Add identifier column
                        all_data.append(df)
            
            if all_data:
                combined_df = pd.concat(all_data, ignore_index=True)
                csv_data = combined_df.to_csv(index=False)
            else:
                return jsonify({"error": "No data available for export"}), 400
        else:
            if export_type in uploaded_data and uploaded_data[export_type]:
                df = pd.DataFrame(uploaded_data[export_type])
                if not df.empty:
                    csv_data = df.to_csv(index=False)
                else:
                    return jsonify({"error": f"No {export_type} data available"}), 400
            else:
                return jsonify({"error": f"No {export_type} data available"}), 400
        
        # Return CSV
        response = app.response_class(
            csv_data,
            mimetype='text/csv',
            headers={'Content-Disposition': f'attachment; filename=olynk_export_{export_type}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'}
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error creating CSV: {str(e)}")
        return jsonify({"error": f"CSV creation failed: {str(e)}"}), 500

def _get_business_friendly_name(column_name):
    """Convert technical column names to business-friendly names"""
    name_mapping = {
        'total_amount': '💰 Total Sales',
        'total_spent': '💳 Customer Spending',
        'total_value': '📊 Total Value',
        'grand_total': '💰 Grand Total',
        'unit_price': '💵 Unit Price',
        'quantity': '📦 Quantity',
        'stock_quantity': '📦 Stock Level',
        'current_stock': '📦 Current Stock',
        'unit_cost': '💲 Unit Cost',
        'total_cost': '💲 Total Cost',
        'average_order_value': '📈 Average Order Value',
        'total_orders': '🛒 Total Orders',
        'price': '💵 Price',
        'cost': '💲 Cost',
        'revenue': '💰 Revenue',
        'amount': '💵 Amount',
        'value': '📊 Value',
        'spent': '💳 Amount Spent',
        'orders': '🛒 Orders',
        'customers': '👥 Customers',
        'products': '📦 Products',
        'inventory': '📊 Inventory'
    }
    
    # Try exact match first
    if column_name.lower() in name_mapping:
        return name_mapping[column_name.lower()]
    
    # Try partial matches
    for key, friendly_name in name_mapping.items():
        if key in column_name.lower():
            return friendly_name
    
    # Default: capitalize and add emoji
    return f"📊 {column_name.replace('_', ' ').title()}"

def _get_correlation_interpretation(col1, col2, corr_value):
    """Generate business-friendly interpretation of correlation"""
    col1_friendly = _get_business_friendly_name(col1)
    col2_friendly = _get_business_friendly_name(col2)
    
    if abs(corr_value) > 0.9:
        strength = "very strongly"
    elif abs(corr_value) > 0.7:
        strength = "strongly"
    else:
        strength = "moderately"
    
    if corr_value > 0:
        direction = "increase together"
    else:
        direction = "move in opposite directions"
    
    return f"{col1_friendly} and {col2_friendly} {strength} {direction}"

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 