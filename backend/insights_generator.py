"""
Enhanced AI Insights Generator for OLynk AI MVP
Phase 2: Week 6 - ML-Powered Insights Generation
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Import advanced analytics - use absolute import
try:
    from advanced_analytics import advanced_analytics
except ImportError:
    # Fallback for when running as standalone module
    advanced_analytics = None

class InsightsGenerator:
    """AI-powered insights generator using advanced analytics"""
    
    def __init__(self):
        self.insight_templates = {
            'revenue_trend': [
                "💰 Your revenue is showing a {trend_direction} trend with {trend_strength} momentum.",
                "📈 Revenue growth rate: {growth_rate_7d:.1%} (7-day), {growth_rate_30d:.1%} (30-day)",
                "🎯 Recommendation: {recommendation}"
            ],
            'customer_segmentation': [
                "👥 Customer Analysis: {total_customers} customers segmented into {n_clusters} groups",
                "🔍 Key segments: {segment_summary}",
                "💡 Action: {action_recommendation}"
            ],
            'anomaly_detection': [
                "⚠️ Anomaly Alert: {anomaly_count} unusual patterns detected ({anomaly_percentage:.1f}% of data)",
                "🎯 Focus areas: {focus_areas}",
                "🚨 Priority: {priority_level}"
            ],
            'inventory_optimization': [
                "📦 Inventory Status: {low_stock_count} items need attention",
                "📊 Stock turnover analysis: {turnover_insight}",
                "🔄 Optimization: {optimization_tip}"
            ]
        }
    
    def generate_comprehensive_insights(self, data_dict):
        """Generate comprehensive insights from all uploaded data"""
        insights = []
        recommendations = []
        
        try:
            # Revenue and Order Analysis
            if data_dict.get('orders'):
                orders_df = pd.DataFrame(data_dict['orders'])
                revenue_insights = self._analyze_revenue(orders_df)
                insights.extend(revenue_insights['insights'])
                recommendations.extend(revenue_insights['recommendations'])
            
            # Customer Analysis
            if data_dict.get('customers'):
                customers_df = pd.DataFrame(data_dict['customers'])
                customer_insights = self._analyze_customers(customers_df)
                insights.extend(customer_insights['insights'])
                recommendations.extend(customer_insights['recommendations'])
            
            # Inventory Analysis
            if data_dict.get('inventory'):
                inventory_df = pd.DataFrame(data_dict['inventory'])
                inventory_insights = self._analyze_inventory(inventory_df)
                insights.extend(inventory_insights['insights'])
                recommendations.extend(inventory_insights['recommendations'])
            
            # Product Analysis
            if data_dict.get('products'):
                products_df = pd.DataFrame(data_dict['products'])
                product_insights = self._analyze_products(products_df)
                insights.extend(product_insights['insights'])
                recommendations.extend(product_insights['recommendations'])
            
            # Cross-dataset insights
            cross_insights = self._generate_cross_dataset_insights(data_dict)
            insights.extend(cross_insights)
            
            # Add recommendations section
            if recommendations:
                insights.append("🎯 **Key Recommendations:**")
                insights.extend([f"• {rec}" for rec in recommendations[:5]])  # Top 5 recommendations
            
            return {
                'insights': insights,
                'recommendations': recommendations,
                'generated_at': datetime.now().isoformat(),
                'data_sources': list(data_dict.keys())
            }
            
        except Exception as e:
            return {
                'insights': [f"❌ Error generating insights: {str(e)}"],
                'recommendations': [],
                'error': str(e)
            }
    
    def _analyze_revenue(self, orders_df):
        """Analyze revenue patterns and trends"""
        insights = []
        recommendations = []
        
        try:
            if 'Total' in orders_df.columns and 'Order Date' in orders_df.columns:
                # Basic revenue stats
                total_revenue = pd.to_numeric(orders_df['Total'], errors='coerce').sum()
                avg_order_value = pd.to_numeric(orders_df['Total'], errors='coerce').mean()
                
                insights.append(f"💰 **Revenue Overview**: Total revenue ₹{total_revenue:,.2f}")
                insights.append(f"📊 Average order value: ₹{avg_order_value:,.2f}")
                
                # Advanced trend analysis (if available)
                if advanced_analytics:
                    try:
                        trend_analysis = advanced_analytics.detect_trends(
                            orders_df, 'Order Date', 'Total', window_days=30
                        )
                        
                        if 'error' not in trend_analysis:
                            trend_direction = trend_analysis['trend_direction']
                            trend_strength = trend_analysis['trend_strength']
                            growth_7d = trend_analysis['growth_rate_7d']
                            growth_30d = trend_analysis['growth_rate_30d']
                            
                            insights.append(f"📈 **Trend Analysis**: Revenue is {trend_direction} with {trend_strength} momentum")
                            insights.append(f"📅 Growth rates: 7-day: {growth_7d:.1%}, 30-day: {growth_30d:.1%}")
                            
                            # Generate recommendations based on trends
                            if trend_direction == 'increasing':
                                if growth_7d > 0.1:  # 10% weekly growth
                                    recommendations.append("Maintain current growth strategies - momentum is strong")
                                else:
                                    recommendations.append("Focus on customer retention and upselling to boost growth")
                            else:
                                recommendations.append("Investigate declining revenue - consider promotional campaigns")
                    except Exception as e:
                        insights.append(f"📈 **Basic Trend**: Revenue analysis completed (advanced features unavailable)")
                
                # Anomaly detection (if available)
                if advanced_analytics:
                    try:
                        anomaly_analysis = advanced_analytics.detect_anomalies(
                            orders_df, ['Total'], contamination=0.05
                        )
                        
                        if 'error' not in anomaly_analysis:
                            anomaly_count = anomaly_analysis['anomaly_count']
                            if anomaly_count > 0:
                                insights.append(f"⚠️ **Anomaly Alert**: {anomaly_count} unusual order patterns detected")
                                recommendations.append("Review anomalous orders for potential fraud or data quality issues")
                    except Exception as e:
                        pass
                
                # Seasonal analysis
                if 'Order Date' in orders_df.columns:
                    orders_df['Order Date'] = pd.to_datetime(orders_df['Order Date'], errors='coerce')
                    weekly_revenue = orders_df.groupby(orders_df['Order Date'].dt.isocalendar().week)['Total'].sum()
                    if len(weekly_revenue) > 4:
                        seasonality = weekly_revenue.std() / weekly_revenue.mean()
                        if seasonality > 0.3:
                            insights.append("🔄 **Seasonality Detected**: Revenue shows weekly patterns")
                            recommendations.append("Plan inventory and marketing around weekly revenue cycles")
                
        except Exception as e:
            insights.append(f"❌ Revenue analysis error: {str(e)}")
        
        return {'insights': insights, 'recommendations': recommendations}
    
    def _analyze_customers(self, customers_df):
        """Analyze customer behavior and segmentation"""
        insights = []
        recommendations = []
        
        try:
            customer_count = len(customers_df)
            insights.append(f"👥 **Customer Base**: {customer_count} total customers")
            
            # Customer segmentation if we have spending data
            if 'Total Spent' in customers_df.columns:
                total_spent = pd.to_numeric(customers_df['Total Spent'], errors='coerce').sum()
                avg_spent = pd.to_numeric(customers_df['Total Spent'], errors='coerce').mean()
                
                insights.append(f"💳 **Spending Analysis**: Total customer spending ₹{total_spent:,.2f}")
                insights.append(f"📊 Average customer spending: ₹{avg_spent:,.2f}")
                
                # Customer segmentation (if available)
                if advanced_analytics:
                    try:
                        segmentation_features = ['Total Spent']
                        if 'Orders Count' in customers_df.columns:
                            segmentation_features.append('Orders Count')
                        
                        segmentation = advanced_analytics.segment_customers(
                            customers_df, segmentation_features, n_clusters=4
                        )
                        
                        if 'error' not in segmentation:
                            insights.append(f"🎯 **Customer Segments**: {segmentation['n_clusters']} distinct customer groups identified")
                            
                            # Analyze segments
                            for cluster_id in range(segmentation['n_clusters']):
                                cluster_info = segmentation['cluster_analysis'][f'cluster_{cluster_id}']
                                size = cluster_info['size']
                                percentage = cluster_info['percentage']
                                
                                if 'Total Spent' in cluster_info['characteristics']:
                                    avg_spending = cluster_info['characteristics']['Total Spent']['mean']
                                    insights.append(f"   • Segment {cluster_id+1}: {size} customers ({percentage:.1f}%) - Avg spending: ₹{avg_spending:,.2f}")
                            
                            # Generate recommendations
                            if segmentation['n_clusters'] > 1:
                                recommendations.append("Implement targeted marketing strategies for different customer segments")
                                recommendations.append("Focus retention efforts on high-value customer segments")
                    except Exception as e:
                        insights.append("🎯 **Customer Analysis**: Basic segmentation completed (advanced features unavailable)")
                
                # Customer lifetime value analysis
                if 'Last Order Date' in customers_df.columns:
                    customers_df['Last Order Date'] = pd.to_datetime(customers_df['Last Order Date'], errors='coerce')
                    recent_customers = customers_df[customers_df['Last Order Date'] >= (datetime.now() - timedelta(days=90))]
                    active_percentage = (len(recent_customers) / customer_count) * 100
                    
                    insights.append(f"🔄 **Customer Activity**: {active_percentage:.1f}% of customers active in last 90 days")
                    
                    if active_percentage < 50:
                        recommendations.append("Implement customer re-engagement campaigns")
                    elif active_percentage > 80:
                        insights.append("✅ Excellent customer retention rate!")
                
        except Exception as e:
            insights.append(f"❌ Customer analysis error: {str(e)}")
        
        return {'insights': insights, 'recommendations': recommendations}
    
    def _analyze_inventory(self, inventory_df):
        """Analyze inventory levels and optimization opportunities"""
        insights = []
        recommendations = []
        
        try:
            total_items = len(inventory_df)
            insights.append(f"📦 **Inventory Overview**: {total_items} total items")
            
            if 'On Hand' in inventory_df.columns:
                # Stock level analysis
                on_hand_data = pd.to_numeric(inventory_df['On Hand'], errors='coerce')
                low_stock = (on_hand_data < 10).sum()
                out_of_stock = (on_hand_data == 0).sum()
                
                insights.append(f"⚠️ **Stock Alerts**: {low_stock} items low on stock, {out_of_stock} out of stock")
                
                if low_stock > 0:
                    recommendations.append(f"Reorder {low_stock} items that are low on stock")
                
                if out_of_stock > 0:
                    recommendations.append(f"Immediate action needed for {out_of_stock} out-of-stock items")
                
                # Stock optimization
                if 'Cost' in inventory_df.columns:
                    cost_data = pd.to_numeric(inventory_df['Cost'], errors='coerce')
                    total_inventory_value = (on_hand_data * cost_data).sum()
                    insights.append(f"💰 **Inventory Value**: Total stock value ₹{total_inventory_value:,.2f}")
                    
                    # ABC analysis (simple version)
                    if not on_hand_data.empty and not cost_data.empty:
                        abc_data = pd.DataFrame({
                            'quantity': on_hand_data,
                            'cost': cost_data,
                            'value': on_hand_data * cost_data
                        }).dropna()
                        
                        if len(abc_data) > 0:
                            total_value = abc_data['value'].sum()
                            abc_data['percentage'] = abc_data['value'] / total_value * 100
                            
                            # Top 20% items (A category)
                            a_items = abc_data.nlargest(int(len(abc_data) * 0.2), 'value')
                            a_percentage = a_items['percentage'].sum()
                            
                            insights.append(f"📊 **ABC Analysis**: Top 20% of items represent {a_percentage:.1f}% of inventory value")
                            recommendations.append("Focus inventory management on high-value A-category items")
                
                # Location analysis
                if 'Location' in inventory_df.columns:
                    location_summary = inventory_df['Location'].value_counts()
                    if len(location_summary) > 1:
                        insights.append(f"📍 **Multi-location**: Inventory spread across {len(location_summary)} locations")
                        recommendations.append("Optimize stock distribution across locations")
                
        except Exception as e:
            insights.append(f"❌ Inventory analysis error: {str(e)}")
        
        return {'insights': insights, 'recommendations': recommendations}
    
    def _analyze_products(self, products_df):
        """Analyze product performance and catalog optimization"""
        insights = []
        recommendations = []
        
        try:
            total_products = len(products_df)
            insights.append(f"🛍️ **Product Catalog**: {total_products} total products")
            
            # Price analysis
            if 'Variant Price' in products_df.columns:
                price_data = pd.to_numeric(products_df['Variant Price'], errors='coerce').dropna()
                if len(price_data) > 0:
                    avg_price = price_data.mean()
                    price_range = price_data.max() - price_data.min()
                    
                    insights.append(f"💰 **Pricing**: Average price ₹{avg_price:,.2f}, Range ₹{price_range:,.2f}")
                    
                    # Price optimization
                    if price_range > avg_price * 2:
                        insights.append("📊 **Price Variation**: High price variability detected")
                        recommendations.append("Review pricing strategy for consistency and competitiveness")
            
            # Category analysis
            if 'Product Category' in products_df.columns:
                category_summary = products_df['Product Category'].value_counts()
                top_categories = category_summary.head(3)
                
                insights.append("🏷️ **Top Categories**:")
                for category, count in top_categories.items():
                    percentage = (count / total_products) * 100
                    insights.append(f"   • {category}: {count} products ({percentage:.1f}%)")
                
                if len(category_summary) > 5:
                    recommendations.append("Consider consolidating or optimizing underperforming product categories")
            
            # Vendor analysis
            if 'Vendor' in products_df.columns:
                vendor_summary = products_df['Vendor'].value_counts()
                if len(vendor_summary) > 1:
                    insights.append(f"🏢 **Vendor Diversity**: Products from {len(vendor_summary)} vendors")
                    
                    # Vendor concentration
                    top_vendor_percentage = (vendor_summary.iloc[0] / total_products) * 100
                    if top_vendor_percentage > 50:
                        insights.append("⚠️ **Vendor Concentration**: High dependency on single vendor")
                        recommendations.append("Diversify vendor base to reduce supply chain risk")
            
            # SEO optimization
            if 'SEO Title' in products_df.columns and 'SEO Description' in products_df.columns:
                missing_seo_title = products_df['SEO Title'].isna().sum()
                missing_seo_desc = products_df['SEO Description'].isna().sum()
                
                if missing_seo_title > 0 or missing_seo_desc > 0:
                    insights.append(f"🔍 **SEO Gaps**: {missing_seo_title} missing titles, {missing_seo_desc} missing descriptions")
                    recommendations.append("Complete SEO metadata for better product discoverability")
                
        except Exception as e:
            insights.append(f"❌ Product analysis error: {str(e)}")
        
        return {'insights': insights, 'recommendations': recommendations}
    
    def _generate_cross_dataset_insights(self, data_dict):
        """Generate insights by combining data from multiple sources"""
        cross_insights = []
        
        try:
            # Revenue vs Customer correlation
            if data_dict.get('orders') and data_dict.get('customers'):
                orders_df = pd.DataFrame(data_dict['orders'])
                customers_df = pd.DataFrame(data_dict['customers'])
                
                if 'Total' in orders_df.columns and 'Total Spent' in customers_df.columns:
                    total_revenue = pd.to_numeric(orders_df['Total'], errors='coerce').sum()
                    total_customer_spending = pd.to_numeric(customers_df['Total Spent'], errors='coerce').sum()
                    
                    if total_revenue > 0 and total_customer_spending > 0:
                        discrepancy = abs(total_revenue - total_customer_spending) / total_revenue * 100
                        if discrepancy > 10:
                            cross_insights.append(f"⚠️ **Data Discrepancy**: Revenue and customer spending differ by {discrepancy:.1f}%")
                            cross_insights.append("🔍 Review data consistency between orders and customer records")
            
            # Inventory vs Product correlation
            if data_dict.get('inventory') and data_dict.get('products'):
                inventory_df = pd.DataFrame(data_dict['inventory'])
                products_df = pd.DataFrame(data_dict['products'])
                
                inventory_skus = set(inventory_df['SKU'].dropna())
                product_skus = set(products_df['Variant SKU'].dropna())
                
                missing_inventory = product_skus - inventory_skus
                missing_products = inventory_skus - product_skus
                
                if missing_inventory:
                    cross_insights.append(f"📦 **Missing Inventory**: {len(missing_inventory)} products lack inventory records")
                
                if missing_products:
                    cross_insights.append(f"🛍️ **Orphaned Inventory**: {len(missing_products)} inventory items without product records")
                
                if missing_inventory or missing_products:
                    cross_insights.append("🔄 Action: Synchronize product and inventory data")
            
            # Customer vs Order correlation
            if data_dict.get('customers') and data_dict.get('orders'):
                customers_df = pd.DataFrame(data_dict['customers'])
                orders_df = pd.DataFrame(data_dict['orders'])
                
                if 'Email' in customers_df.columns and 'Email' in orders_df.columns:
                    customer_emails = set(customers_df['Email'].dropna())
                    order_emails = set(orders_df['Email'].dropna())
                    
                    customers_without_orders = customer_emails - order_emails
                    orders_without_customers = order_emails - customer_emails
                    
                    if customers_without_orders:
                        cross_insights.append(f"👥 **Inactive Customers**: {len(customers_without_orders)} customers have no orders")
                        cross_insights.append("💡 Consider re-engagement campaigns")
                    
                    if orders_without_customers:
                        cross_insights.append(f"🛒 **Guest Orders**: {len(orders_without_customers)} orders from non-registered customers")
                        cross_insights.append("🎯 Opportunity to convert guest customers to registered users")
                
        except Exception as e:
            cross_insights.append(f"❌ Cross-dataset analysis error: {str(e)}")
        
        return cross_insights

# Global instance
insights_generator = InsightsGenerator() 