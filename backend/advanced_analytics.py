"""
Advanced Analytics Engine for OLynk AI MVP
Phase 2: Week 5-6 - Advanced Analytics & ML Models
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.ensemble import IsolationForest
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

class AdvancedAnalytics:
    """Advanced analytics engine with ML-powered insights"""
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.anomaly_detector = IsolationForest(contamination=0.1, random_state=42)
        self.segmentation_model = KMeans(n_clusters=4, random_state=42)
    
    def detect_trends(self, df, date_column, value_column, window_days=30):
        """Detect trends in time-series data"""
        try:
            # Convert date column
            df_copy = df.copy()
            df_copy[date_column] = pd.to_datetime(df_copy[date_column], errors='coerce')
            df_copy = df_copy.dropna(subset=[date_column, value_column])
            
            if len(df_copy) < 2:
                return {"error": "Insufficient data for trend analysis"}
            
            # Sort by date
            df_copy = df_copy.sort_values(date_column)
            
            # Calculate moving averages
            df_copy['MA_7'] = df_copy[value_column].rolling(window=7, min_periods=1).mean()
            df_copy['MA_30'] = df_copy[value_column].rolling(window=30, min_periods=1).mean()
            
            # Calculate growth rates
            df_copy['Daily_Growth'] = df_copy[value_column].pct_change()
            df_copy['Weekly_Growth'] = df_copy[value_column].pct_change(periods=7)
            
            # Trend analysis
            recent_data = df_copy.tail(window_days)
            if len(recent_data) > 1:
                # Linear trend calculation
                x = np.arange(len(recent_data))
                y = recent_data[value_column].values
                slope = np.polyfit(x, y, 1)[0]
                
                # Trend classification
                if slope > 0:
                    trend_direction = "increasing"
                    trend_strength = "strong" if abs(slope) > np.std(y) else "moderate"
                else:
                    trend_direction = "decreasing"
                    trend_strength = "strong" if abs(slope) > np.std(y) else "moderate"
                
                # Seasonality detection (simple approach)
                weekly_avg = df_copy.groupby(df_copy[date_column].dt.dayofweek)[value_column].mean()
                seasonality_score = weekly_avg.std() / weekly_avg.mean() if weekly_avg.mean() > 0 else 0
                
                return {
                    "trend_direction": trend_direction,
                    "trend_strength": trend_strength,
                    "growth_rate_7d": float(df_copy['Weekly_Growth'].tail(7).mean()),
                    "growth_rate_30d": float(df_copy['Daily_Growth'].tail(30).mean()),
                    "seasonality_score": float(seasonality_score),
                    "moving_averages": {
                        "7_day": float(df_copy['MA_7'].iloc[-1]),
                        "30_day": float(df_copy['MA_30'].iloc[-1])
                    },
                    "data_points": len(df_copy)
                }
            else:
                return {"error": "Insufficient recent data for trend analysis"}
                
        except Exception as e:
            return {"error": f"Trend analysis failed: {str(e)}"}
    
    def detect_anomalies(self, df, columns, contamination=0.1):
        """Detect anomalies using Isolation Forest"""
        try:
            # Prepare numeric data
            numeric_data = df[columns].select_dtypes(include=[np.number])
            if numeric_data.empty:
                return {"error": "No numeric columns found for anomaly detection"}
            
            # Handle missing values
            numeric_data = numeric_data.fillna(numeric_data.mean())
            
            # Scale the data
            scaled_data = self.scaler.fit_transform(numeric_data)
            
            # Fit anomaly detection model
            self.anomaly_detector.set_params(contamination=contamination)
            anomaly_labels = self.anomaly_detector.fit_predict(scaled_data)
            
            # Get anomaly scores
            anomaly_scores = self.anomaly_detector.decision_function(scaled_data)
            
            # Identify anomalies
            anomalies = df[anomaly_labels == -1].copy()
            anomalies['anomaly_score'] = anomaly_scores[anomaly_labels == -1]
            
            # Calculate statistics
            total_records = len(df)
            anomaly_count = len(anomalies)
            anomaly_percentage = (anomaly_count / total_records) * 100
            
            # Get top anomalies by score
            top_anomalies = anomalies.nlargest(5, 'anomaly_score')
            
            return {
                "total_records": total_records,
                "anomaly_count": anomaly_count,
                "anomaly_percentage": float(anomaly_percentage),
                "anomaly_threshold": float(np.percentile(anomaly_scores, 90)),
                "top_anomalies": top_anomalies.to_dict('records'),
                "anomaly_scores": {
                    "mean": float(np.mean(anomaly_scores)),
                    "std": float(np.std(anomaly_scores)),
                    "min": float(np.min(anomaly_scores)),
                    "max": float(np.max(anomaly_scores))
                }
            }
            
        except Exception as e:
            return {"error": f"Anomaly detection failed: {str(e)}"}
    
    def segment_customers(self, df, features, n_clusters=4):
        """Customer segmentation using K-means clustering"""
        try:
            # Prepare features for clustering
            feature_data = df[features].select_dtypes(include=[np.number])
            if feature_data.empty:
                return {"error": "No numeric features found for segmentation"}
            
            # Handle missing values
            feature_data = feature_data.fillna(feature_data.mean())
            
            # Scale the data
            scaled_features = self.scaler.fit_transform(feature_data)
            
            # Perform clustering
            self.segmentation_model.set_params(n_clusters=n_clusters)
            cluster_labels = self.segmentation_model.fit_predict(scaled_features)
            
            # Add cluster labels to dataframe
            df_with_clusters = df.copy()
            df_with_clusters['cluster'] = cluster_labels
            
            # Analyze clusters
            cluster_analysis = {}
            for cluster_id in range(n_clusters):
                cluster_data = df_with_clusters[df_with_clusters['cluster'] == cluster_id]
                cluster_analysis[f"cluster_{cluster_id}"] = {
                    "size": len(cluster_data),
                    "percentage": (len(cluster_data) / len(df)) * 100,
                    "characteristics": {}
                }
                
                # Calculate cluster characteristics
                for feature in features:
                    if feature in cluster_data.columns:
                        feature_data = pd.to_numeric(cluster_data[feature], errors='coerce').dropna()
                        if len(feature_data) > 0:
                            cluster_analysis[f"cluster_{cluster_id}"]["characteristics"][feature] = {
                                "mean": float(feature_data.mean()),
                                "median": float(feature_data.median()),
                                "std": float(feature_data.std())
                            }
            
            # Get cluster centers
            cluster_centers = self.segmentation_model.cluster_centers_
            
            # Create more interpretable cluster details
            cluster_details = []
            for cluster_id in range(n_clusters):
                cluster_data = df_with_clusters[df_with_clusters['cluster'] == cluster_id]
                cluster_info = cluster_analysis[f"cluster_{cluster_id}"]
                
                # Create human-readable characteristics
                characteristics = []
                for feature in features:
                    if feature in cluster_info["characteristics"]:
                        feat_stats = cluster_info["characteristics"][feature]
                        if feat_stats["mean"] > 0:
                            characteristics.append(f"{feature}: ₹{feat_stats['mean']:.2f} avg")
                
                # Determine cluster type based on characteristics
                cluster_type = self._determine_cluster_type(cluster_info, features)
                
                cluster_details.append({
                    "size": cluster_info["size"],
                    "percentage": round(cluster_info["percentage"], 1),
                    "characteristics": ", ".join(characteristics[:3]),  # Show top 3
                    "type": cluster_type
                })
            
            # Add business insights
            business_insights = []
            if len(cluster_details) > 1:
                largest_cluster = max(cluster_details, key=lambda x: x["size"])
                smallest_cluster = min(cluster_details, key=lambda x: x["size"])
                
                business_insights.append(f"Largest segment: {largest_cluster['type']} ({largest_cluster['size']} items, {largest_cluster['percentage']}%)")
                business_insights.append(f"Smallest segment: {smallest_cluster['type']} ({smallest_cluster['size']} items, {smallest_cluster['percentage']}%)")
                
                # Check for high-value segments
                high_value_clusters = [c for c in cluster_details if any('high' in c['type'].lower() or 'premium' in c['type'].lower())]
                if high_value_clusters:
                    business_insights.append(f"High-value segments identified: {len(high_value_clusters)} premium groups")
            
            return {
                "n_clusters": n_clusters,
                "cluster_analysis": cluster_analysis,
                "cluster_details": cluster_details,
                "cluster_centers": cluster_centers.tolist(),
                "total_customers": len(df),
                "features_used": features,
                "segmentation_quality": float(self.segmentation_model.inertia_),
                "business_insights": business_insights
            }
            
        except Exception as e:
            return {"error": f"Customer segmentation failed: {str(e)}"}
    
    def _determine_cluster_type(self, cluster_info, features):
        """Determine the type of cluster based on its characteristics"""
        try:
            # Look for spending-related features
            spending_features = [f for f in features if any(x in f.lower() for x in ['spent', 'value', 'amount', 'revenue', 'total'])]
            
            if spending_features:
                # Calculate average spending for this cluster
                avg_spending = 0
                for feature in spending_features:
                    if feature in cluster_info["characteristics"]:
                        avg_spending += cluster_info["characteristics"][feature]["mean"]
                
                if avg_spending > 0:
                    if avg_spending > 10000:  # High threshold
                        return "High-Value Premium"
                    elif avg_spending > 5000:  # Medium threshold
                        return "Mid-Value Standard"
                    else:
                        return "Low-Value Basic"
            
            # Look for order-related features
            order_features = [f for f in features if any(x in f.lower() for x in ['order', 'count', 'frequency'])]
            if order_features:
                avg_orders = 0
                for feature in order_features:
                    if feature in cluster_info["characteristics"]:
                        avg_orders += cluster_info["characteristics"][feature]["mean"]
                
                if avg_orders > 0:
                    if avg_orders > 20:
                        return "High-Frequency Loyal"
                    elif avg_orders > 10:
                        return "Medium-Frequency Regular"
                    else:
                        return "Low-Frequency Occasional"
            
            # Default classification based on size
            if cluster_info["size"] > len(cluster_info) * 0.4:  # More than 40% of total
                return "Mainstream Majority"
            elif cluster_info["size"] < len(cluster_info) * 0.1:  # Less than 10% of total
                return "Niche Minority"
            else:
                return "Standard Segment"
                
        except Exception:
            return "Standard Segment"
    
    def calculate_correlations(self, df, columns=None):
        """Calculate correlations between numeric columns"""
        try:
            if columns is None:
                numeric_data = df.select_dtypes(include=[np.number])
            else:
                numeric_data = df[columns].select_dtypes(include=[np.number])
            
            if numeric_data.empty:
                return {"error": "No numeric columns found for correlation analysis"}
            
            # Calculate correlation matrix
            correlation_matrix = numeric_data.corr()
            
            # Find strong correlations
            strong_correlations = []
            for i in range(len(correlation_matrix.columns)):
                for j in range(i+1, len(correlation_matrix.columns)):
                    corr_value = correlation_matrix.iloc[i, j]
                    if abs(corr_value) > 0.7:  # Strong correlation threshold
                        strong_correlations.append({
                            "variable1": correlation_matrix.columns[i],
                            "variable2": correlation_matrix.columns[j],
                            "correlation": float(corr_value),
                            "strength": "strong positive" if corr_value > 0 else "strong negative"
                        })
            
            # Create more interpretable variable names
            variable_names = {}
            for col in correlation_matrix.columns:
                if 'total' in col.lower() or 'amount' in col.lower() or 'spent' in col.lower():
                    variable_names[col] = f"💰 {col}"
                elif 'date' in col.lower() or 'time' in col.lower():
                    variable_names[col] = f"📅 {col}"
                elif 'stock' in col.lower() or 'quantity' in col.lower():
                    variable_names[col] = f"📦 {col}"
                elif 'price' in col.lower() or 'cost' in col.lower():
                    variable_names[col] = f"💵 {col}"
                elif 'order' in col.lower() or 'count' in col.lower():
                    variable_names[col] = f"🛒 {col}"
                else:
                    variable_names[col] = f"📊 {col}"
            
            # Enhanced strong correlations with business context
            enhanced_correlations = []
            for corr in strong_correlations:
                var1 = corr["variable1"]
                var2 = corr["variable2"]
                corr_value = corr["correlation"]
                
                # Add business interpretation
                interpretation = self._interpret_correlation(var1, var2, corr_value)
                
                enhanced_correlations.append({
                    **corr,
                    "variable1_display": variable_names.get(var1, var1),
                    "variable2_display": variable_names.get(var2, var2),
                    "interpretation": interpretation
                })
            
            return {
                "correlation_matrix": correlation_matrix.to_dict(),
                "strong_correlations": enhanced_correlations,
                "variables_analyzed": len(correlation_matrix.columns),
                "summary": {
                    "total_variables": len(correlation_matrix.columns),
                    "strong_correlations_count": len(enhanced_correlations),
                    "mean_correlation": float(correlation_matrix.values[np.triu_indices_from(correlation_matrix.values, k=1)].mean())
                }
            }
            
        except Exception as e:
            return {"error": f"Correlation analysis failed: {str(e)}"}
    
    def _interpret_correlation(self, var1, var2, corr_value):
        """Interpret correlation in business terms"""
        try:
            # Define business relationships
            if 'total' in var1.lower() or 'amount' in var1.lower() or 'spent' in var1.lower():
                if 'total' in var2.lower() or 'amount' in var2.lower() or 'spent' in var2.lower():
                    if corr_value > 0.7:
                        return "High spending customers tend to have high total amounts"
                    else:
                        return "Spending patterns are independent"
            
            if 'stock' in var1.lower() or 'quantity' in var1.lower():
                if 'cost' in var2.lower() or 'price' in var2.lower():
                    if corr_value > 0.7:
                        return "Higher stock quantities correlate with higher costs"
                    elif corr_value < -0.7:
                        return "Higher stock quantities correlate with lower unit costs (bulk pricing)"
            
            if 'order' in var1.lower() or 'count' in var1.lower():
                if 'total' in var2.lower() or 'amount' in var2.lower():
                    if corr_value > 0.7:
                        return "More orders correlate with higher total amounts"
                    else:
                        return "Order frequency and amounts are independent"
            
            if 'date' in var1.lower() or 'time' in var1.lower():
                if 'total' in var2.lower() or 'amount' in var2.lower():
                    if corr_value > 0.7:
                        return "Time-based trends in spending/amounts detected"
                    elif corr_value < -0.7:
                        return "Inverse time-based trends detected"
            
            # Generic interpretation
            if corr_value > 0.9:
                return "Very strong positive relationship - these variables move together"
            elif corr_value > 0.7:
                return "Strong positive relationship - as one increases, the other tends to increase"
            elif corr_value < -0.9:
                return "Very strong negative relationship - these variables move in opposite directions"
            elif corr_value < -0.7:
                return "Strong negative relationship - as one increases, the other tends to decrease"
            else:
                return "Moderate relationship - some connection exists"
                
        except Exception:
            return "Business relationship detected"
    
    def generate_forecast(self, df, date_column, value_column, periods=30):
        """Simple forecasting using moving averages and trend extrapolation"""
        try:
            # Prepare time series data
            df_copy = df.copy()
            df_copy[date_column] = pd.to_datetime(df_copy[date_column], errors='coerce')
            df_copy = df_copy.dropna(subset=[date_column, value_column])
            
            if len(df_copy) < 10:
                return {"error": "Insufficient data for forecasting (minimum 10 data points required)"}
            
            # Sort by date
            df_copy = df_copy.sort_values(date_column)
            
            # Calculate moving averages
            df_copy['MA_7'] = df_copy[value_column].rolling(window=7, min_periods=1).mean()
            df_copy['MA_14'] = df_copy[value_column].rolling(window=14, min_periods=1).mean()
            
            # Simple trend extrapolation
            recent_values = df_copy[value_column].tail(14).values
            if len(recent_values) >= 2:
                # Calculate trend
                x = np.arange(len(recent_values))
                slope, intercept = np.polyfit(x, recent_values, 1)
                
                # Generate forecast
                future_x = np.arange(len(recent_values), len(recent_values) + periods)
                forecast_values = slope * future_x + intercept
                
                # Calculate confidence intervals (simple approach)
                std_error = np.std(recent_values - (slope * x + intercept))
                confidence_interval = 1.96 * std_error  # 95% confidence
                
                forecast_data = []
                for i, value in enumerate(forecast_values):
                    forecast_data.append({
                        "period": i + 1,
                        "forecast": float(value),
                        "lower_bound": float(value - confidence_interval),
                        "upper_bound": float(value + confidence_interval)
                    })
                
                return {
                    "forecast_periods": periods,
                    "trend_slope": float(slope),
                    "trend_direction": "increasing" if slope > 0 else "decreasing",
                    "confidence_interval": float(confidence_interval),
                    "forecast_data": forecast_data,
                    "last_actual_value": float(recent_values[-1]),
                    "forecast_accuracy": "moderate"  # Placeholder for more sophisticated accuracy metrics
                }
            else:
                return {"error": "Insufficient recent data for forecasting"}
                
        except Exception as e:
            return {"error": f"Forecasting failed: {str(e)}"}

# Global instance
advanced_analytics = AdvancedAnalytics() 