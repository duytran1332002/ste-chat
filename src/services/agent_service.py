"""
Agent Service for managing tool execution and LLM interactions.
Coordinates between the LLM and data analysis tools.
"""

import re
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime

from src.services.llm_service import GeminiService
from src.services.data_analyzer import DataAnalyzer


class ToolExecutor:
    """Handles execution of data analysis tools."""
    
    def __init__(self, data_analyzer: DataAnalyzer):
        """
        Initialize tool executor.
        
        Args:
            data_analyzer: DataAnalyzer instance for executing tools
        """
        self.data_analyzer = data_analyzer
        self.tools = self._register_tools()
    
    def _register_tools(self) -> Dict[str, Dict[str, Any]]:
        """Register available tools and their metadata."""
        return {
            "get_dataset_summary": {
                "function": self.data_analyzer.get_dataset_summary,
                "description": "Get an overview summary of the shipments dataset including total shipments, date range, routes, warehouses, and basic statistics.",
                "parameters": {}
            },
            "get_statistical_summary": {
                "function": self.data_analyzer.get_statistical_summary,
                "description": "Get detailed statistical analysis including mean, median, min, max, and standard deviation for delivery times and delays. Use this for statistical questions about median, mean, standard deviation, etc.",
                "parameters": {}
            },
            "analyze_delays": {
                "function": self.data_analyzer.analyze_delays,
                "description": "Analyze delays in shipments above. Shows delay reasons, affected routes, and warehouses.",
                "parameters": {}
            },
            "analyze_route_performance": {
                "function": self.data_analyzer.analyze_route_performance,
                "description": "Analyze performance of a specific route or compare all routes. Shows delivery times, delays, and warehouse usage.",
                "parameters": {
                    "route": "Specific route to analyze (e.g., 'Route A') or None for all routes"
                }
            },
            "analyze_warehouse_performance": {
                "function": self.data_analyzer.analyze_warehouse_performance,
                "description": "Analyze performance of a specific warehouse or compare all warehouses. Shows delivery times, delays, and route usage.",
                "parameters": {
                    "warehouse": "Specific warehouse to analyze (e.g., 'WH1') or None for all warehouses"
                }
            },
            "analyze_by_time_period": {
                "function": self.data_analyzer.analyze_by_time_period,
                "description": "Analyze shipments for a specific time period. Can filter by month (e.g., 'October', 'Oct'), year (e.g., 2024), or date range (start_date and end_date in YYYY-MM-DD format). Shows statistics, delays, and performance for that period.",
                "parameters": {
                    "month": "Month name (full or 3-letter abbreviation, e.g., 'October' or 'Oct')",
                    "year": "Year as integer (e.g., 2024)",
                    "start_date": "Start date in YYYY-MM-DD format",
                    "end_date": "End date in YYYY-MM-DD format"
                }
            },
            "get_recommendations": {
                "function": self.data_analyzer.get_recommendations,
                "description": "Generate actionable recommendations based on comprehensive data analysis. Identifies issues and suggests improvements.",
                "parameters": {}
            },
            "search_shipments": {
                "function": self.data_analyzer.search_shipments,
                "description": "Search for specific shipments based on natural language query (e.g., 'route A with delays', 'warehouse WH1 traffic issues').",
                "parameters": {
                    "query": "Natural language search query"
                }
            }
        }
    
    def get_tools_description(self) -> str:
        """Get formatted description of all available tools."""
        descriptions = []
        for tool_name, tool_info in self.tools.items():
            desc = f"- {tool_name}: {tool_info['description']}"
            if tool_info['parameters']:
                params = ", ".join([f"{k}: {v}" for k, v in tool_info['parameters'].items()])
                desc += f"\n  Parameters: {params}"
            descriptions.append(desc)
        return "\n\n".join(descriptions)
    
    def parse_tool_calls(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract tool calls from LLM response.
        
        Args:
            text: LLM response text
            
        Returns:
            List of tool call dictionaries with 'tool_name' and 'parameters'
        """
        tool_pattern = r'TOOL_CALL:\s*(\w+)\((.*?)\)'
        matches = re.findall(tool_pattern, text, re.DOTALL)
        
        tool_calls = []
        for tool_name, params_str in matches:
            # Parse parameters
            params = {}
            if params_str.strip():
                # Simple parameter parsing
                param_pattern = r'(\w+)=["\']?(.*?)["\']?(?:,|$)'
                param_matches = re.findall(param_pattern, params_str)
                for param_name, param_value in param_matches:
                    # Try to convert to appropriate type
                    param_value = param_value.strip().strip('"').strip("'")
                    if param_value.lower() == 'none':
                        params[param_name] = None
                    elif param_value.isdigit():
                        params[param_name] = int(param_value)
                    else:
                        params[param_name] = param_value
            
            tool_calls.append({
                "tool_name": tool_name,
                "parameters": params
            })
        
        return tool_calls
    
    def execute_tool(self, tool_name: str, **kwargs) -> str:
        """
        Execute a specific tool.
        
        Args:
            tool_name: Name of the tool to execute
            **kwargs: Tool parameters
            
        Returns:
            Result string
        """
        if tool_name not in self.tools:
            return f"Error: Tool '{tool_name}' not found. Available tools: {', '.join(self.tools.keys())}"
        
        try:
            tool_function = self.tools[tool_name]["function"]
            result = tool_function(**kwargs)
            
            # Handle tuple results (text only, ignore charts)
            if isinstance(result, tuple):
                return result[0]
            return result
        except Exception as e:
            return f"Error executing {tool_name}: {str(e)}"
    
    def execute_tool_calls(self, tool_calls: List[Dict[str, Any]]) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Execute multiple tool calls.
        
        Args:
            tool_calls: List of tool call dictionaries
            
        Returns:
            Tuple of (combined results string, execution logs)
        """
        results = []
        execution_logs = []
        
        for tool_call in tool_calls:
            tool_name = tool_call["tool_name"]
            params = tool_call["parameters"]
            
            # Log execution
            execution_logs.append({
                "tool": tool_name,
                "params": params,
                "timestamp": datetime.now().isoformat()
            })
            
            # Execute tool
            result = self.execute_tool(tool_name, **params)
            results.append(f"**Tool: {tool_name}**\n\n{result}")
        
        combined_results = "\n\n---\n\n".join(results)
        return combined_results, execution_logs


class AgentService:
    """
    Main agent service that coordinates LLM interactions and tool execution.
    """
    
    def __init__(self, llm_service: GeminiService, data_analyzer: DataAnalyzer, system_prompt: str):
        """
        Initialize agent service.
        
        Args:
            llm_service: Gemini LLM service for generating responses
            data_analyzer: Data analyzer for tool execution
            system_prompt: System prompt for the agent
        """
        self.llm_service = llm_service
        self.tool_executor = ToolExecutor(data_analyzer)
        self.system_prompt = system_prompt
    
    def process_message(self, user_message: str, conversation_history: List[Dict[str, str]]) -> Tuple[str, Optional[str], List[Dict[str, Any]]]:
        """
        Process a user message and generate a response.
        
        Args:
            user_message: User's input message
            conversation_history: Previous conversation messages
            
        Returns:
            Tuple of (response text, tool results if any, execution logs)
        """
        # Prepare messages for LLM
        messages = [{"role": "system", "content": self.system_prompt}]
        messages.extend(conversation_history)
        messages.append({"role": "user", "content": user_message})
        
        # First LLM call - determine if tools are needed
        initial_response = self.llm_service.generate_response(messages)
        
        # Check if tool calls are needed
        tool_calls = self.tool_executor.parse_tool_calls(initial_response)
        
        if not tool_calls:
            # No tools needed, return initial response
            return initial_response, None, []
        
        # Execute tools
        tool_results, execution_logs = self.tool_executor.execute_tool_calls(tool_calls)
        
        # Second LLM call with tool results
        messages.append({"role": "assistant", "content": initial_response})
        messages.append({
            "role": "user",
            "content": f"""Here are the tool results:

{tool_results}

Based on these tool results, answer the user's original question directly and concisely. Focus ONLY on what the user asked for. Extract the specific information they requested (e.g., if they asked for 'average delay', provide that number clearly). Do not repeat all the data - just answer their question."""
        })
        
        # Generate final response
        final_response = self.llm_service.generate_response(messages)
        
        return final_response, tool_results, execution_logs
    
    def get_tools_description(self) -> str:
        """Get description of available tools."""
        return self.tool_executor.get_tools_description()
