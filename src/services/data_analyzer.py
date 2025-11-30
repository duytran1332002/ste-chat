"""
Data Analysis Service for Logistics AI Agent.
Handles all shipment data analysis operations.
"""

import pandas as pd
from typing import Optional, Dict, Any, Tuple
from dataclasses import dataclass


@dataclass
class AnalysisResult:
    """Container for analysis results."""
    data: str
    success: bool = True
    error: Optional[str] = None


class DataAnalyzer:
    """
    Service class for analyzing shipment data.
    Provides methods for various types of analysis on shipments.
    """
    
    def __init__(self, data_file: str):
        """
        Initialize the DataAnalyzer.
        
        Args:
            data_file: Path to the CSV file containing shipment data
        """
        self.data_file = data_file
        self.df = self._load_data()
    
    def _load_data(self) -> pd.DataFrame:
        """Load and prepare shipment data."""
        df = pd.read_csv(self.data_file)
        df['date'] = pd.to_datetime(df['date'])
        return df
    
    def get_dataset_summary(self) -> str:
        """Get a summary of the shipments dataset."""
        total_shipments = len(self.df)
        date_range = f"{self.df['date'].min().strftime('%Y-%m-%d')} to {self.df['date'].max().strftime('%Y-%m-%d')}"
        routes = self.df['route'].nunique()
        warehouses = self.df['warehouse'].nunique()
        
        summary = f"""Dataset Summary:
- Total Shipments: {total_shipments}
- Date Range: {date_range}
- Number of Routes: {routes} (Route A, B, C, D, E)
- Number of Warehouses: {warehouses} (WH1-WH5)
- Average Delivery Time: {self.df['delivery_time'].mean():.2f} days
- Median Delivery Time: {self.df['delivery_time'].median():.2f} days
- Average Delay (delayed shipments only): {self.df[self.df['delay_minutes'] > 0]['delay_minutes'].mean():.2f} minutes
- Median Delay (delayed shipments only): {self.df[self.df['delay_minutes'] > 0]['delay_minutes'].median():.2f} minutes
- Shipments with Delays: {(self.df['delay_minutes'] > 0).sum()} ({((self.df['delay_minutes'] > 0).sum() / total_shipments * 100):.1f}%)"""
        
        return summary

    def get_statistical_summary(self) -> str:
        """Get detailed statistical summary of shipment metrics."""
        result = f"""Statistical Summary:

Delivery Time Statistics:
- Mean: {self.df['delivery_time'].mean():.2f} days
- Median: {self.df['delivery_time'].median():.2f} days
- Min: {self.df['delivery_time'].min():.2f} days
- Max: {self.df['delivery_time'].max():.2f} days
- Standard Deviation: {self.df['delivery_time'].std():.2f} days

Delay Statistics (all shipments):
- Mean: {self.df[self.df['delay_minutes'] > 0]['delay_minutes'].mean():.2f} minutes
- Median: {self.df[self.df['delay_minutes'] > 0]['delay_minutes'].median():.2f} minutes
- Min: {self.df[self.df['delay_minutes'] > 0]['delay_minutes'].min():.0f} minutes
- Max: {self.df[self.df['delay_minutes'] > 0]['delay_minutes'].max():.0f} minutes
- Standard Deviation: {self.df[self.df['delay_minutes'] > 0]['delay_minutes'].std():.2f} minutes
"""
        
        # Statistics for only delayed shipments
        delayed = self.df[self.df['delay_minutes'] > 0]
        if len(delayed) > 0:
            result += f"""\nDelay Statistics (delayed shipments only):
- Mean: {delayed['delay_minutes'].mean():.2f} minutes
- Median: {delayed['delay_minutes'].median():.2f} minutes
- Min: {delayed['delay_minutes'].min():.0f} minutes
- Max: {delayed['delay_minutes'].max():.0f} minutes
- Standard Deviation: {delayed['delay_minutes'].std():.2f} minutes
- Count: {len(delayed)} shipments ({len(delayed)/len(self.df)*100:.1f}%)
"""
        
        return result

    def analyze_delays(self) -> str:
        """Analyze delays in shipments."""
        delayed = self.df[self.df['delay_minutes'] > 0]
        
        if len(delayed) == 0:
            return "No delays found above 0 minutes."
        
        # Top delay reasons
        delay_reasons = delayed[delayed['delay_reason'].notna()]['delay_reason'].value_counts()
        
        # Routes with most delays
        route_delays = delayed.groupby('route').size().sort_values(ascending=False)
        
        # Warehouses with most delays
        warehouse_delays = delayed.groupby('warehouse').size().sort_values(ascending=False)
        
        result = f"""Delay Analysis (> 0 minutes):
        
Total Delayed Shipments: {len(delayed)} ({len(delayed)/len(self.df)*100:.1f}%)
Average Delay: {delayed['delay_minutes'].mean():.1f} minutes
Maximum Delay: {delayed['delay_minutes'].max():.0f} minutes

Top Delay Reasons:
"""
        for reason, count in delay_reasons.head(5).items():
            result += f"- {reason}: {count} occurrences ({count/len(delayed)*100:.1f}%)\n"
        
        result += "\nRoutes with Most Delays:\n"
        for route, count in route_delays.head(3).items():
            result += f"- {route}: {count} delays\n"
        
        result += "\nWarehouses with Most Delays:\n"
        for warehouse, count in warehouse_delays.head(3).items():
            result += f"- {warehouse}: {count} delays\n"
        
        return result

    def analyze_route_performance(self, route: Optional[str] = None) -> str:
        """Analyze performance of routes."""
        if route:
            route_data = self.df[self.df['route'] == route]
            if len(route_data) == 0:
                return f"No data found for {route}. Available routes: {', '.join(self.df['route'].unique())}"
            
            avg_delivery = route_data['delivery_time'].mean()
            delayed_shipments = (route_data['delay_minutes'] > 0).sum()
            avg_delay = route_data[route_data['delay_minutes'] > 0]['delay_minutes'].mean() if delayed_shipments > 0 else 0.0
            total_shipments = len(route_data)
            
            result = f"""Performance Analysis for {route}:
            
Total Shipments: {total_shipments}
Delayed Shipments: {delayed_shipments} ({delayed_shipments/total_shipments*100:.1f}%)
Average Delivery Time: {avg_delivery:.2f} days
Average Delay (delayed only): {avg_delay:.1f} minutes

Warehouses Used:
"""
            warehouse_counts = route_data['warehouse'].value_counts()
            for wh, count in warehouse_counts.items():
                result += f"- {wh}: {count} shipments\n"
            
            return result
        else:
            # Compare all routes
            route_stats = self.df.groupby('route').agg({
                'delivery_time': 'mean',
                'id': 'count'
            }).round(2)
            
            # Calculate average delay only for delayed shipments
            delayed_df = self.df[self.df['delay_minutes'] > 0]
            avg_delays = delayed_df.groupby('route')['delay_minutes'].mean().round(2)
            
            route_stats['Avg Delay (min)'] = avg_delays
            route_stats.columns = ['Avg Delivery Time (days)', 'Total Shipments', 'Avg Delay (delayed only, min)']
            
            # Add delayed shipments count
            delayed_counts = self.df[self.df['delay_minutes'] > 0].groupby('route').size()
            route_stats['Delayed Shipments'] = delayed_counts
            route_stats['Delayed Shipments'] = route_stats['Delayed Shipments'].fillna(0).astype(int)
            
            route_stats = route_stats.sort_values('Avg Delivery Time (days)')
            
            result = "Route Performance Comparison:\n\n"
            result += route_stats.to_string()
            
            best_route = route_stats['Avg Delivery Time (days)'].idxmin()
            worst_route = route_stats['Avg Delivery Time (days)'].idxmax()
            
            result += f"\n\nBest Performing Route: {best_route} ({route_stats.loc[best_route, 'Avg Delivery Time (days)']} days avg)"
            result += f"\nWorst Performing Route: {worst_route} ({route_stats.loc[worst_route, 'Avg Delivery Time (days)']} days avg)"
            
            return result

    def analyze_warehouse_performance(self, warehouse: Optional[str] = None) -> str:
        """Analyze performance of warehouses."""
        if warehouse:
            wh_data = self.df[self.df['warehouse'] == warehouse]
            if len(wh_data) == 0:
                return f"No data found for {warehouse}. Available warehouses: {', '.join(self.df['warehouse'].unique())}"
            
            avg_delivery = wh_data['delivery_time'].mean()
            delayed_shipments = (wh_data['delay_minutes'] > 0).sum()
            avg_delay = wh_data[wh_data['delay_minutes'] > 0]['delay_minutes'].mean() if delayed_shipments > 0 else 0.0
            total_shipments = len(wh_data)
            
            # Delay reasons for this warehouse
            delay_reasons = wh_data[wh_data['delay_reason'] != 'None']['delay_reason'].value_counts()
            
            result = f"""Performance Analysis for {warehouse}:
            
Total Shipments: {total_shipments}
Delayed Shipments: {delayed_shipments} ({delayed_shipments/total_shipments*100:.1f}%)
Average Delivery Time: {avg_delivery:.2f} days
Average Delay (delayed only): {avg_delay:.1f} minutes

Routes Used:
"""
            route_counts = wh_data['route'].value_counts()
            for route, count in route_counts.items():
                result += f"- {route}: {count} shipments\n"
            
            if len(delay_reasons) > 0:
                result += "\nTop Delay Reasons:\n"
                for reason, count in delay_reasons.head(3).items():
                    result += f"- {reason}: {count} times\n"
            
            return result
        else:
            # Compare all warehouses
            wh_stats = self.df.groupby('warehouse').agg({
                'delivery_time': 'mean',
                'id': 'count'
            }).round(2)
            
            # Calculate average delay only for delayed shipments
            delayed_df = self.df[self.df['delay_minutes'] > 0]
            avg_delays = delayed_df.groupby('warehouse')['delay_minutes'].mean().round(2)
            
            wh_stats['Avg Delay (min)'] = avg_delays
            wh_stats.columns = ['Avg Delivery Time (days)', 'Total Shipments', 'Avg Delay (delayed only, min)']
            
            # Add delayed shipments count
            delayed_counts = self.df[self.df['delay_minutes'] > 0].groupby('warehouse').size()
            wh_stats['Delayed Shipments'] = delayed_counts
            wh_stats['Delayed Shipments'] = wh_stats['Delayed Shipments'].fillna(0).astype(int)
            
            wh_stats = wh_stats.sort_values('Avg Delivery Time (days)')
            
            result = "Warehouse Performance Comparison:\n\n"
            result += wh_stats.to_string()
            
            best_wh = wh_stats['Avg Delivery Time (days)'].idxmin()
            worst_wh = wh_stats['Avg Delivery Time (days)'].idxmax()
            
            result += f"\n\nBest Performing Warehouse: {best_wh} ({wh_stats.loc[best_wh, 'Avg Delivery Time (days)']} days avg)"
            result += f"\nWorst Performing Warehouse: {worst_wh} ({wh_stats.loc[worst_wh, 'Avg Delivery Time (days)']} days avg)"
            
            return result

    def get_recommendations(self) -> str:
        """Generate recommendations based on the data analysis."""
        recommendations = []
        
        # Analyze delay patterns
        delay_reasons = self.df[self.df['delay_reason'] != 'None']['delay_reason'].value_counts()
        top_reason = delay_reasons.idxmax() if len(delay_reasons) > 0 else None
        
        if top_reason:
            recommendations.append(f"🚨 Priority Issue: '{top_reason}' is the leading cause of delays ({delay_reasons[top_reason]} occurrences). Consider implementing mitigation strategies.")
        
        # Identify problematic routes
        delayed_df = self.df[self.df['delay_minutes'] > 0]
        route_delays = delayed_df.groupby('route')['delay_minutes'].mean().sort_values(ascending=False)
        worst_route = route_delays.idxmax()
        avg_delay_overall = delayed_df['delay_minutes'].mean()
        if route_delays[worst_route] > avg_delay_overall:
            recommendations.append(f"🛣️ Route Optimization: {worst_route} has the highest average delay ({route_delays[worst_route]:.1f} min). Review route planning and consider alternatives.")
        
        # Identify warehouse issues
        wh_delays = delayed_df.groupby('warehouse')['delay_minutes'].mean().sort_values(ascending=False)
        worst_wh = wh_delays.idxmax()
        if wh_delays[worst_wh] > avg_delay_overall:
            wh_delay_reasons = self.df[self.df['warehouse'] == worst_wh]['delay_reason'].value_counts()
            top_wh_reason = wh_delay_reasons.idxmax() if len(wh_delay_reasons) > 0 else 'Unknown'
            recommendations.append(f"🏭 Warehouse Focus: {worst_wh} has the highest average delay ({wh_delays[worst_wh]:.1f} min), mainly due to '{top_wh_reason}'. Address capacity or operational issues.")
        
        # Check for seasonal patterns
        df_recent = self.df[self.df['date'] >= self.df['date'].max() - pd.Timedelta(days=30)]
        recent_delay_rate = (df_recent['delay_minutes'] > 0).sum() / len(df_recent)
        overall_delay_rate = (self.df['delay_minutes'] > 0).sum() / len(self.df)
        
        if recent_delay_rate > overall_delay_rate * 1.2:
            recommendations.append(f"📈 Trend Alert: Recent delays are {((recent_delay_rate/overall_delay_rate - 1) * 100):.0f}% higher than average. Investigate recent changes in operations.")
        
        # Best practices
        best_route = delayed_df.groupby('route')['delay_minutes'].mean().idxmin()
        best_wh = delayed_df.groupby('warehouse')['delay_minutes'].mean().idxmin()
        recommendations.append(f"✅ Best Practices: Study {best_route} and {best_wh} performance to identify success factors for replication.")
        
        return "\n\n".join(recommendations)

    def analyze_by_time_period(self, month: Optional[str] = None, year: Optional[int] = None, 
                               start_date: Optional[str] = None, end_date: Optional[str] = None) -> str:
        """Analyze shipments for a specific time period."""
        filtered_df = self.df.copy()
        period_desc = ""
        
        # Filter by month and/or year
        if month:
            month_mapping = {
                'january': 1, 'jan': 1,
                'february': 2, 'feb': 2,
                'march': 3, 'mar': 3,
                'april': 4, 'apr': 4,
                'may': 5,
                'june': 6, 'jun': 6,
                'july': 7, 'jul': 7,
                'august': 8, 'aug': 8,
                'september': 9, 'sep': 9, 'sept': 9,
                'october': 10, 'oct': 10,
                'november': 11, 'nov': 11,
                'december': 12, 'dec': 12
            }
            month_num = month_mapping.get(month.lower(), None)
            if month_num:
                filtered_df = filtered_df[filtered_df['date'].dt.month == month_num]
                period_desc = month.capitalize()
            else:
                return f"Invalid month: {month}. Use full name or 3-letter abbreviation."
        
        if year:
            filtered_df = filtered_df[filtered_df['date'].dt.year == year]
            period_desc = f"{period_desc} {year}" if period_desc else str(year)
        
        # Filter by date range
        if start_date:
            filtered_df = filtered_df[filtered_df['date'] >= pd.to_datetime(start_date)]
            period_desc = f"from {start_date}"
        
        if end_date:
            filtered_df = filtered_df[filtered_df['date'] <= pd.to_datetime(end_date)]
            period_desc = f"{period_desc} to {end_date}" if period_desc else f"up to {end_date}"
        
        if len(filtered_df) == 0:
            return f"No shipments found for period: {period_desc}"
        
        # Calculate statistics
        total_shipments = len(filtered_df)
        avg_delivery = filtered_df['delivery_time'].mean()
        avg_delay = filtered_df[filtered_df['delay_minutes'] > 0]['delay_minutes'].mean()
        delayed_count = (filtered_df['delay_minutes'] > 0).sum()
        delayed_pct = (delayed_count / total_shipments * 100)
        
        result = f"""Time Period Analysis - {period_desc}:

Total Shipments: {total_shipments}
Average Delivery Time: {avg_delivery:.2f} days
Average Delay: {avg_delay:.1f} minutes
Shipments with Delays: {delayed_count} ({delayed_pct:.1f}%)
"""
        
        # Delay breakdown
        if delayed_count > 0:
            delay_reasons = filtered_df[filtered_df['delay_minutes'] > 0]['delay_reason'].value_counts()
            result += "\nTop Delay Reasons:\n"
            for reason, count in delay_reasons.head(5).items():
                result += f"- {reason}: {count} occurrences ({count/delayed_count*100:.1f}%)\n"
            
            # Route performance in this period
            route_stats = filtered_df[filtered_df['delay_minutes'] > 0].groupby('route').agg({
                'delay_minutes': ['mean', 'sum'],
                'id': 'count'
            }).round(1)
            route_stats.columns = ['Avg Delay (min)', 'Total Delay (min)', 'Total Shipments']
            
            # Calculate delayed shipments count for each route
            delayed_by_route = filtered_df[filtered_df['delay_minutes'] > 0].groupby('route').size()
            route_stats['Delayed Shipments'] = delayed_by_route
            route_stats['Delayed Shipments'] = route_stats['Delayed Shipments'].fillna(0).astype(int)
            
            route_stats = route_stats.sort_values('Total Delay (min)', ascending=False)
            
            result += "\nRoute Performance (sorted by total delay):\n"
            for route, row in route_stats.head(5).iterrows():
                result += f"- {route}: {int(row['Total Delay (min)'])} min total delay | {row['Avg Delay (min)']} min avg | {int(row['Total Shipments'])} total shipments | {row['Delayed Shipments']} delayed\n"
        
        return result

    def search_shipments(self, query: str) -> str:
        """Search for specific shipments based on query parameters."""
        query = query.lower()
        result_df = self.df.copy()
        
        # Parse query
        if 'route' in query:
            routes = ['Route A', 'Route B', 'Route C', 'Route D', 'Route E']
            for route in routes:
                if route.lower() in query:
                    result_df = result_df[result_df['route'] == route]
                    break
        
        if 'warehouse' in query or 'wh' in query:
            warehouses = ['WH1', 'WH2', 'WH3', 'WH4', 'WH5']
            for wh in warehouses:
                if wh.lower() in query:
                    result_df = result_df[result_df['warehouse'] == wh]
                    break
        
        if 'delay' in query:
            result_df = result_df[result_df['delay_minutes'] > 0]
        
        if 'traffic' in query:
            result_df = result_df[result_df['delay_reason'] == 'Traffic']
        elif 'weather' in query:
            result_df = result_df[result_df['delay_reason'] == 'Weather']
        elif 'customs' in query:
            result_df = result_df[result_df['delay_reason'] == 'Customs Delay']
        elif 'driver' in query:
            result_df = result_df[result_df['delay_reason'] == 'Driver Issue']
        elif 'vehicle' in query:
            result_df = result_df[result_df['delay_reason'] == 'Vehicle Breakdown']
        elif 'overload' in query:
            result_df = result_df[result_df['delay_reason'] == 'Warehouse Overload']
        
        if len(result_df) == 0:
            return f"No shipments found matching: '{query}'"
        
        result = f"Found {len(result_df)} shipments matching '{query}':\n\n"
        
        # Show top 10 results
        for idx, row in result_df.head(10).iterrows():
            result += f"ID {row['id']}: {row['route']} from {row['warehouse']} | "
            result += f"Delivered in {row['delivery_time']:.1f} days | "
            if row['delay_minutes'] > 0:
                result += f"Delayed {row['delay_minutes']}min ({row['delay_reason']}) | "
            result += f"{row['date'].strftime('%Y-%m-%d')}\n"
        
        if len(result_df) > 10:
            result += f"\n... and {len(result_df) - 10} more shipments"
        
        return result
