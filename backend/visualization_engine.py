"""
Visualization Engine for OLynk AI MVP
Phase 2: Week 7 - Interactive Charts and Visualizations
"""

# Set matplotlib to use non-interactive backend for server environment
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend

import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
# Temporarily disable seaborn import to avoid conflicts
# import seaborn as sns
import io
import base64

class VisualizationEngine:
    """Generate interactive charts and visualizations for the dashboard"""
    
    def __init__(self):
        # Set matplotlib style - use default style to avoid conflicts
        try:
            plt.style.use('default')
        except:
            pass  # Use default matplotlib style
        
        # Note: seaborn styling disabled to avoid import conflicts
    
    def generate_revenue_chart(self, orders_df, chart_type='line'):
        """Generate revenue visualization charts"""
        try:
            # Find revenue and date columns
            revenue_cols = [col for col in orders_df.columns if 'Total' in col or 'Value' in col or 'Amount' in col or 'Grand' in col]
            date_cols = [col for col in orders_df.columns if 'Date' in col or 'date' in col.lower()]
            
            if not revenue_cols or not date_cols:
                return {"error": "Missing required columns for revenue chart (need revenue and date columns)"}
            
            revenue_col = revenue_cols[0]
            date_col = date_cols[0]
            
            # Prepare data
            df = orders_df.copy()
            df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
            df[revenue_col] = pd.to_numeric(df[revenue_col], errors='coerce')
            df = df.dropna(subset=[date_col, revenue_col])
            
            if len(df) == 0:
                return {"error": "No valid data for revenue chart"}
            
            # Sort by date
            df = df.sort_values(date_col)
            
            if chart_type == 'line':
                return self._create_revenue_line_chart(df, date_col, revenue_col)
            elif chart_type == 'bar':
                return self._create_revenue_bar_chart(df, date_col, revenue_col)
            elif chart_type == 'trend':
                return self._create_revenue_trend_chart(df, date_col, revenue_col)
            else:
                return {"error": "Unsupported chart type"}
                
        except Exception as e:
            return {"error": f"Revenue chart generation failed: {str(e)}"}
    
    def _create_revenue_line_chart(self, df, date_col, revenue_col):
        """Create line chart for revenue over time"""
        try:
            # Group by date and sum revenue
            daily_revenue = df.groupby(df[date_col].dt.date)[revenue_col].sum().reset_index()
            daily_revenue[date_col] = pd.to_datetime(daily_revenue[date_col])
            
            # Create the plot
            plt.figure(figsize=(12, 6))
            plt.plot(daily_revenue[date_col], daily_revenue[revenue_col], 
                    marker='o', linewidth=2, markersize=4)
            
            plt.title('Daily Revenue Trend', fontsize=16, fontweight='bold')
            plt.xlabel('Date', fontsize=12)
            plt.ylabel('Revenue (₹)', fontsize=12)
            plt.grid(True, alpha=0.3)
            plt.xticks(rotation=45)
            
            # Add trend line
            if len(daily_revenue) > 1:
                z = np.polyfit(range(len(daily_revenue)), daily_revenue[revenue_col], 1)
                p = np.poly1d(z)
                trend_line = p(range(len(daily_revenue)))
                plt.plot(daily_revenue[date_col], trend_line, 
                        "--", alpha=0.8, color='red', label='Trend Line')
                plt.legend()
            
            plt.tight_layout()
            
            # Convert to base64
            img_buffer = io.BytesIO()
            plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight')
            img_buffer.seek(0)
            img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
            plt.close()
            
            return {
                "chart_type": "line",
                "title": "Daily Revenue Trend",
                "image": img_base64,
                "data_points": len(daily_revenue),
                "total_revenue": float(daily_revenue[revenue_col].sum()),
                "avg_daily_revenue": float(daily_revenue[revenue_col].mean())
            }
            
        except Exception as e:
            return {"error": f"Line chart creation failed: {str(e)}"}
    
    def _create_revenue_bar_chart(self, df, date_col, revenue_col):
        """Create bar chart for revenue by time period"""
        try:
            # Group by week using a more compatible method
            df['Week'] = df[date_col].dt.strftime('%Y-%U')  # Year-Week format
            weekly_revenue = df.groupby('Week')[revenue_col].sum().reset_index()
            
            # Create the plot
            plt.figure(figsize=(14, 6))
            bars = plt.bar(range(len(weekly_revenue)), weekly_revenue[revenue_col], 
                          color='skyblue', alpha=0.7)
            
            plt.title('Weekly Revenue Performance', fontsize=16, fontweight='bold')
            plt.xlabel('Week', fontsize=12)
            plt.ylabel('Revenue (₹)', fontsize=12)
            plt.grid(True, alpha=0.3)
            
            # Add value labels on bars
            for bar in bars:
                height = bar.get_height()
                plt.text(bar.get_x() + bar.get_width()/2., height,
                        f'₹{height:,.0f}', ha='center', va='bottom', fontsize=8)
            
            plt.tight_layout()
            
            # Convert to base64
            img_buffer = io.BytesIO()
            plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight')
            img_buffer.seek(0)
            img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
            plt.close()
            
            return {
                "chart_type": "bar",
                "title": "Weekly Revenue Performance",
                "image": img_base64,
                "data_points": len(weekly_revenue),
                "total_revenue": float(weekly_revenue[revenue_col].sum()),
                "avg_weekly_revenue": float(weekly_revenue[revenue_col].mean())
            }
            
        except Exception as e:
            return {"error": f"Bar chart creation failed: {str(e)}"}
    
    def _create_revenue_trend_chart(self, df, date_col, revenue_col):
        """Create trend analysis chart with moving averages"""
        try:
            # Calculate moving averages
            df = df.sort_values(date_col)
            df['MA_7'] = df[revenue_col].rolling(window=7, min_periods=1).mean()
            df['MA_30'] = df[revenue_col].rolling(window=30, min_periods=1).mean()
            
            # Create the plot
            plt.figure(figsize=(14, 7))
            
            # Plot daily revenue
            plt.plot(df[date_col], df[revenue_col], 'o-', alpha=0.6, 
                    label='Daily Revenue', markersize=3)
            
            # Plot moving averages
            plt.plot(df[date_col], df['MA_7'], 'r-', linewidth=2, 
                    label='7-Day Moving Average')
            plt.plot(df[date_col], df['MA_30'], 'g-', linewidth=2, 
                    label='30-Day Moving Average')
            
            plt.title('Revenue Trend with Moving Averages', fontsize=16, fontweight='bold')
            plt.xlabel('Date', fontsize=12)
            plt.ylabel('Revenue (₹)', fontsize=12)
            plt.legend()
            plt.grid(True, alpha=0.3)
            plt.xticks(rotation=45)
            
            plt.tight_layout()
            
            # Convert to base64
            img_buffer = io.BytesIO()
            plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight')
            img_buffer.seek(0)
            img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
            plt.close()
            
            return {
                "chart_type": "trend",
                "title": "Revenue Trend with Moving Averages",
                "image": img_base64,
                "data_points": len(df),
                "trend_analysis": {
                    "current_7d_avg": float(df['MA_7'].iloc[-1]),
                    "current_30d_avg": float(df['MA_30'].iloc[-1]),
                    "trend_direction": "increasing" if df['MA_7'].iloc[-1] > df['MA_30'].iloc[-1] else "decreasing"
                }
            }
            
        except Exception as e:
            return {"error": f"Trend chart creation failed: {str(e)}"}
    
    def generate_customer_segmentation_chart(self, customers_df):
        """Generate customer segmentation visualization"""
        try:
            # Find spending columns
            spending_cols = [col for col in customers_df.columns if 'Spent' in col or 'Value' in col or 'Amount' in col]
            if not spending_cols:
                return {"error": "Missing spending column for customer segmentation"}
            
            spending_col = spending_cols[0]
            
            # Prepare data
            df = customers_df.copy()
            df[spending_col] = pd.to_numeric(df[spending_col], errors='coerce')
            df = df.dropna(subset=[spending_col])
            
            if len(df) == 0:
                return {"error": "No valid data for customer segmentation"}
            
            # Create spending distribution
            plt.figure(figsize=(12, 6))
            
            # Histogram with KDE
            plt.hist(df[spending_col], bins=20, alpha=0.7, color='skyblue', edgecolor='black')
            plt.axvline(df[spending_col].mean(), color='red', linestyle='--', 
                       label=f'Mean: ₹{df[spending_col].mean():,.0f}')
            plt.axvline(df[spending_col].median(), color='green', linestyle='--', 
                       label=f'Median: ₹{df[spending_col].median():,.0f}')
            
            plt.title('Customer Spending Distribution', fontsize=16, fontweight='bold')
            plt.xlabel('Total Spent (₹)', fontsize=12)
            plt.ylabel('Number of Customers', fontsize=12)
            plt.legend()
            plt.grid(True, alpha=0.3)
            
            plt.tight_layout()
            
            # Convert to base64
            img_buffer = io.BytesIO()
            plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight')
            img_buffer.seek(0)
            img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
            plt.close()
            
            return {
                "chart_type": "distribution",
                "title": "Customer Spending Distribution",
                "image": img_base64,
                "data_points": len(df),
                "statistics": {
                    "mean_spending": float(df[spending_col].mean()),
                    "median_spending": float(df[spending_col].median()),
                    "std_spending": float(df[spending_col].std()),
                    "total_customers": len(df)
                }
            }
            
        except Exception as e:
            return {"error": f"Customer segmentation chart failed: {str(e)}"}
    
    def generate_inventory_heatmap(self, inventory_df):
        """Generate inventory heatmap visualization"""
        try:
            # Find stock columns
            stock_cols = [col for col in inventory_df.columns if 'Stock' in col or 'Quantity' in col or 'Current' in col]
            if not stock_cols:
                return {"error": "Missing stock column for inventory heatmap"}
            
            stock_col = stock_cols[0]
            
            # Prepare data
            df = inventory_df.copy()
            df[stock_col] = pd.to_numeric(df[stock_col], errors='coerce')
            df = df.dropna(subset=[stock_col])
            
            if len(df) == 0:
                return {"error": "No valid data for inventory heatmap"}
            
            # Create stock level categories
            def categorize_stock(quantity):
                if quantity == 0:
                    return 'Out of Stock'
                elif quantity < 10:
                    return 'Low Stock'
                elif quantity < 50:
                    return 'Medium Stock'
                else:
                    return 'High Stock'
            
            df['Stock Level'] = df[stock_col].apply(categorize_stock)
            
            # Create the plot
            plt.figure(figsize=(10, 6))
            
            # Stock level distribution
            stock_counts = df['Stock Level'].value_counts()
            colors = ['#ff6b6b', '#ffd93d', '#6bcf7f', '#4ecdc4']
            
            plt.pie(stock_counts.values, labels=stock_counts.index, autopct='%1.1f%%',
                   colors=colors, startangle=90)
            plt.title('Inventory Stock Level Distribution', fontsize=16, fontweight='bold')
            
            plt.tight_layout()
            
            # Convert to base64
            img_buffer = io.BytesIO()
            plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight')
            img_buffer.seek(0)
            img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
            plt.close()
            
            return {
                "chart_type": "pie",
                "title": "Inventory Stock Level Distribution",
                "image": img_base64,
                "data_points": len(df),
                "stock_summary": {
                    "out_of_stock": int((df[stock_col] == 0).sum()),
                    "low_stock": int((df[stock_col] < 10).sum()),
                    "medium_stock": int(((df[stock_col] >= 10) & (df[stock_col] < 50)).sum()),
                    "high_stock": int((df[stock_col] >= 50).sum())
                }
            }
            
        except Exception as e:
            return {"error": f"Inventory heatmap failed: {str(e)}"}
    
    def generate_correlation_matrix(self, df, numeric_columns):
        """Generate correlation matrix heatmap"""
        try:
            # Select numeric columns
            numeric_data = df[numeric_columns].select_dtypes(include=[np.number])
            
            if numeric_data.empty:
                return {"error": "No numeric columns found for correlation analysis"}
            
            # Calculate correlation matrix
            corr_matrix = numeric_data.corr()
            
            # Create the plot
            plt.figure(figsize=(10, 8))
            mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
            
            # Use matplotlib instead of seaborn for heatmap
            plt.imshow(corr_matrix, cmap='coolwarm', aspect='auto')
            plt.colorbar()
            
            # Add annotations
            for i in range(len(corr_matrix.columns)):
                for j in range(len(corr_matrix.columns)):
                    plt.text(j, i, f'{corr_matrix.iloc[i, j]:.2f}', 
                            ha='center', va='center', fontsize=8)
            
            plt.xticks(range(len(corr_matrix.columns)), corr_matrix.columns, rotation=45)
            plt.yticks(range(len(corr_matrix.columns)), corr_matrix.columns)
            
            plt.title('Feature Correlation Matrix', fontsize=16, fontweight='bold')
            plt.tight_layout()
            
            # Convert to base64
            img_buffer = io.BytesIO()
            plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight')
            img_buffer.seek(0)
            img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
            plt.close()
            
            return {
                "chart_type": "heatmap",
                "title": "Feature Correlation Matrix",
                "image": img_base64,
                "correlation_data": corr_matrix.to_dict(),
                "features": list(corr_matrix.columns)
            }
            
        except Exception as e:
            return {"error": f"Correlation matrix failed: {str(e)}"}
    
    def generate_summary_dashboard(self, data_dict):
        """Generate a comprehensive dashboard with multiple charts"""
        dashboard = {
            "charts": [],
            "summary": {},
            "generated_at": datetime.now().isoformat()
        }
        
        try:
            # Revenue chart
            if data_dict.get('orders'):
                orders_df = pd.DataFrame(data_dict['orders'])
                revenue_chart = self.generate_revenue_chart(orders_df, 'trend')
                if 'error' not in revenue_chart:
                    dashboard["charts"].append(revenue_chart)
            
            # Customer segmentation
            if data_dict.get('customers'):
                customers_df = pd.DataFrame(data_dict['customers'])
                customer_chart = self.generate_customer_segmentation_chart(customers_df)
                if 'error' not in customer_chart:
                    dashboard["charts"].append(customer_chart)
            
            # Inventory overview
            if data_dict.get('inventory'):
                inventory_df = pd.DataFrame(data_dict['inventory'])
                inventory_chart = self.generate_inventory_heatmap(inventory_df)
                if 'error' not in inventory_chart:
                    dashboard["charts"].append(inventory_chart)
            
            # Summary statistics
            dashboard["summary"] = self._generate_summary_stats(data_dict)
            
            return dashboard
            
        except Exception as e:
            return {"error": f"Dashboard generation failed: {str(e)}"}
    
    def _generate_summary_stats(self, data_dict):
        """Generate summary statistics for the dashboard"""
        summary = {}
        
        try:
            if data_dict.get('orders'):
                orders_df = pd.DataFrame(data_dict['orders'])
                if 'Total' in orders_df.columns:
                    total_revenue = pd.to_numeric(orders_df['Total'], errors='coerce').sum()
                    summary['total_revenue'] = float(total_revenue)
                    summary['total_orders'] = len(orders_df)
            
            if data_dict.get('customers'):
                customers_df = pd.DataFrame(data_dict['customers'])
                summary['total_customers'] = len(customers_df)
                if 'Total Spent' in customers_df.columns:
                    total_spent = pd.to_numeric(customers_df['Total Spent'], errors='coerce').sum()
                    summary['total_customer_spending'] = float(total_spent)
            
            if data_dict.get('inventory'):
                inventory_df = pd.DataFrame(data_dict['inventory'])
                if 'On Hand' in inventory_df.columns:
                    on_hand = pd.to_numeric(inventory_df['On Hand'], errors='coerce')
                    summary['low_stock_items'] = int((on_hand < 10).sum())
                    summary['out_of_stock_items'] = int((on_hand == 0).sum())
            
            if data_dict.get('products'):
                summary['total_products'] = len(data_dict['products'])
            
        except Exception as e:
            summary['error'] = str(e)
        
        return summary

# Global instance
visualization_engine = VisualizationEngine() 