"""
UI Manager for Streamlit interface components.
Handles all UI rendering and interactions.
"""

import streamlit as st
from datetime import datetime
from typing import List, Dict, Any, Optional


class UIManager:
    """Manages the Streamlit UI components and layout."""
    
    @staticmethod
    def setup_page_config(page_title: str, page_icon: str, layout: str):
        """
        Configure the Streamlit page.
        
        Args:
            page_title: Page title
            page_icon: Page icon
            layout: Layout style ('wide' or 'centered')
        """
        st.set_page_config(
            page_title=page_title,
            page_icon=page_icon,
            layout=layout,
            initial_sidebar_state="expanded"
        )
    
    @staticmethod
    def apply_custom_css():
        """Apply custom CSS styling."""
        st.markdown("""
        <style>
            .main-header {
                font-size: 2.5rem;
                color: #1f77b4;
                text-align: center;
                margin-bottom: 1rem;
            }
            .stAlert {
                margin-top: 1rem;
            }
        </style>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_header(title: str):
        """
        Render main header.
        
        Args:
            title: Header title
        """
        st.markdown(f'<h1 class="main-header">{title}</h1>', unsafe_allow_html=True)
    
    @staticmethod
    def render_welcome_message():
        """Render welcome message for new users."""
        st.info("""
        👋 **Welcome to the Logistics AI Agent!**
        
        I can help you analyze shipment data, identify delays, optimize routes, and provide recommendations.
        
        **Try asking me:**
        - "What's the summary of our shipments?"
        - "Show me the delay analysis"
        - "Which route performs best?"
        - "What are your recommendations?"
        - "Find shipments with traffic delays"
        """)
    
    @staticmethod
    def render_chat_history(messages: List[Dict[str, str]]):
        """
        Render chat message history.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
        """
        for message in messages:
            with st.chat_message(message["role"]):
                # Check if message has tool results (COMMENTED OUT)
                # if message["role"] == "assistant" and "tool_results" in message and message["tool_results"]:
                #     # Display tool results in expander
                #     with st.expander("🔧 Tool Execution Results", expanded=False):
                #         st.markdown(message["tool_results"])
                #     # Display the actual response (remove the HTML details tag if present)
                #     content = message["content"]
                #     if "<details>" in content:
                #         # Extract content before details tag
                #         content = content.split("<details>")[0].strip()
                #     st.markdown(content)
                # else:
                #     st.markdown(message["content"])
                
                # Simplified: just display content without tool results
                st.markdown(message["content"])
    
    @staticmethod
    def render_sidebar(
        dataset_summary: str,
        messages: List[Dict[str, str]],
        tool_calls: List[Dict[str, Any]],
        model_name: str,
        temperature: float,
        max_tokens: int
    ):
        """
        Render sidebar with controls and information.
        
        Args:
            dataset_summary: Summary of the dataset
            messages: Chat message history
            tool_calls: List of tool execution logs
            model_name: Name of the Gemini model being used
            temperature: LLM temperature setting
            max_tokens: Max tokens setting
        """
        with st.sidebar:
            st.title("⚙️ Agent Settings")
            
            # Display settings
            st.info(f"""
            **Provider:** Gemini  
            **Model:** {model_name}  
            **Temperature:** {temperature}  
            **Max Tokens:** {max_tokens}
            """)
            
            st.divider()
            
            # Actions
            st.subheader("🎛️ Actions")
            
            if st.button("🗑️ Clear Conversation", use_container_width=True):
                st.session_state.messages = []
                st.session_state.tool_calls = []
                st.rerun()
            
            if st.button("📊 Show Dataset Info", use_container_width=True):
                with st.spinner("Loading dataset info..."):
                    st.info(dataset_summary)
            
            # Export conversation
            if messages:
                st.divider()
                conversation_text = "\n\n".join([
                    f"{msg['role'].upper()}: {msg['content']}"
                    for msg in messages
                ])
                st.download_button(
                    label="💾 Export Chat",
                    data=conversation_text,
                    file_name=f"chat_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain",
                    use_container_width=True
                )
            
            st.divider()
            
            # Statistics
            st.subheader("📊 Chat Statistics")
            st.metric("Total Messages", len(messages))
            st.metric("Tool Calls", len(tool_calls))
            
            st.divider()
            
            # Available tools
            with st.expander("🔧 Available Tools"):
                st.markdown("""
                - **get_dataset_summary**: Overview of shipments
                - **analyze_delays**: Delay patterns & causes
                - **analyze_route_performance**: Route analysis
                - **analyze_warehouse_performance**: Warehouse analysis
                - **get_recommendations**: AI recommendations
                - **search_shipments**: Search specific shipments
                """)
    
    @staticmethod
    def render_footer():
        """Render footer information."""
        st.divider()
        # st.caption("🤖 Powered by Groq LLM | 📊 Analyzing 500 shipments across 5 routes and 5 warehouses")
    
    @staticmethod
    def show_tool_results(tool_results: str):
        """
        Display tool execution results in an expander.
        
        Args:
            tool_results: Tool execution results text
        """
        with st.expander("🔍 View Tool Results", expanded=False):
            st.markdown(tool_results)
    
    @staticmethod
    def show_error(error_message: str):
        """
        Display an error message.
        
        Args:
            error_message: Error message to display
        """
        st.error(f"❌ {error_message}")
    
    @staticmethod
    def show_spinner(message: str):
        """
        Show a spinner with a message.
        
        Args:
            message: Message to display with spinner
            
        Returns:
            Spinner context manager
        """
        return st.spinner(message)
    
    @staticmethod
    def show_status(message: str):
        """
        Show a status message.
        
        Args:
            message: Status message
            
        Returns:
            Status context manager
        """
        return st.status(message)
