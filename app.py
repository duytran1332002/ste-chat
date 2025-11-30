"""
Hermes - AI Logistics Agent with Memory
Uses Gemini LLM and Streamlit UI to analyze shipment data and answer questions.
Refactored with clean class-based architecture.
"""

import streamlit as st
from datetime import datetime

from src.config.settings import LLMConfig, AppConfig, SystemPromptConfig
from src.services.llm_service import LLMServiceFactory
from src.services.data_analyzer import DataAnalyzer
from src.services.agent_service import AgentService
from src.utils.ui_manager import UIManager


def initialize_session_state(system_prompt: str):
    """Initialize Streamlit session state variables."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "tool_calls" not in st.session_state:
        st.session_state.tool_calls = []
    
    if "system_prompt" not in st.session_state:
        st.session_state.system_prompt = system_prompt


def main():
    """Main application entry point."""
    
    # Initialize configurations
    llm_config = LLMConfig()
    app_config = AppConfig()
    
    # Setup page
    UIManager.setup_page_config(
        page_title=app_config.page_title,
        page_icon=app_config.page_icon,
        layout=app_config.layout
    )
    UIManager.apply_custom_css()
    
    # Initialize data analyzer
    data_analyzer = DataAnalyzer(app_config.data_file)
    
    # Check if Gemini API key is available
    if not llm_config.gemini_api_key:
        st.error("⚠️ GEMINI_API_KEY not configured! Please set it in your .env file.")
        st.stop()
    
    # Initialize session state
    if "agent" not in st.session_state:
        # Create agent with Gemini
        provider = "Gemini"
        model = app_config.gemini_model
        api_key = llm_config.gemini_api_key
        
        llm_service = LLMServiceFactory.create_service(
            provider=provider,
            api_key=api_key,
            model_name=model,
            temperature=llm_config.temperature,
            max_tokens=llm_config.max_tokens
        )
        
        # Create tool executor to get tools description
        from src.services.agent_service import ToolExecutor
        tool_executor = ToolExecutor(data_analyzer)
        tools_desc = tool_executor.get_tools_description()
        current_date = datetime.now().strftime("%B %d, %Y")
        system_prompt = SystemPromptConfig.get_agent_prompt(tools_desc, current_date)
        
        st.session_state.agent = AgentService(llm_service, data_analyzer, system_prompt)
        initialize_session_state(system_prompt)
    
    # Render sidebar
    UIManager.render_sidebar(
        dataset_summary=data_analyzer.get_dataset_summary(),
        messages=st.session_state.messages,
        tool_calls=st.session_state.tool_calls,
        model_name=app_config.gemini_model,
        temperature=llm_config.temperature,
        max_tokens=llm_config.max_tokens
    )
    
    # Main content
    UIManager.render_header(app_config.page_title)
    
    # Welcome message for new users
    if not st.session_state.messages:
        UIManager.render_welcome_message()
    
    # Display chat history
    UIManager.render_chat_history(st.session_state.messages)
    
    # Chat input
    if prompt := st.chat_input("Ask me about shipments, delays, routes, or warehouses..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate assistant response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            # tool_results_container = st.container()
            
            try:
                # Process message through agent
                with UIManager.show_spinner("🤔 Thinking..."):
                    response, tool_results, execution_logs = st.session_state.agent.process_message(
                        user_message=prompt,
                        conversation_history=st.session_state.messages[:-1]  # Exclude the just-added user message
                    )
                
                # Update tool calls history
                st.session_state.tool_calls.extend(execution_logs)
                
                # Display tool results if available (COMMENTED OUT)
                # if tool_results:
                #     with tool_results_container:
                #         with st.expander("🔧 Tool Execution Results", expanded=False):
                #             st.markdown(tool_results)
                
                # Display final response
                message_placeholder.markdown(response)
                
            except Exception as e:
                error_msg = f"Error: {str(e)}"
                message_placeholder.error(error_msg)
                response = error_msg
        
        # Add assistant response to history (tool results commented out)
        # full_response = response
        # if tool_results:
        #     full_response = f"{response}\n\n<details><summary>🔧 Tool Results</summary>\n\n{tool_results}\n\n</details>"
        # st.session_state.messages.append({"role": "assistant", "content": full_response, "tool_results": tool_results})
        st.session_state.messages.append({"role": "assistant", "content": response})
    
    # Footer
    UIManager.render_footer()


if __name__ == "__main__":
    main()
