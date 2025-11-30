# Hermes - AI Logistics Agent - Restructured

A clean, class-based architecture for the Logistics AI Agent using Streamlit and Gemini LLM.

## 📁 Project Structure

```
.
├── app.py                      # Legacy app (original)
├── app_new.py                  # New refactored app (recommended)
├── tools.py                    # Legacy tools file
├── requirements.txt            # Python dependencies
├── shipments_filled.csv        # Dataset
├── src/                        # Source code (new structure)
│   ├── __init__.py
│   ├── config/                 # Configuration
│   │   ├── __init__.py
│   │   └── settings.py         # App config, LLM config, prompts
│   ├── services/               # Business logic
│   │   ├── __init__.py
│   │   ├── data_analyzer.py    # Data analysis service
│   │   ├── llm_service.py      # LLM provider abstractions
│   │   └── agent_service.py    # Agent coordination service
│   ├── utils/                  # Utilities
│   │   ├── __init__.py
│   │   └── ui_manager.py       # Streamlit UI components
│   └── models/                 # Data models (future use)
│       └── __init__.py
└── README.md                   # This file
```

## 🏗️ Architecture Overview

### **Separation of Concerns**

The codebase is organized into distinct layers:

1. **Configuration Layer** (`src/config/`)
   - `settings.py`: All configuration classes (LLM, App, System Prompts)
   - Centralizes all settings and prompts

2. **Service Layer** (`src/services/`)
   - `data_analyzer.py`: **DataAnalyzer** class - handles all data analysis operations
   - `llm_service.py`: **GeminiService** class for Gemini LLM integration
     - `LLMServiceFactory`: Factory for creating Gemini service
   - `agent_service.py`: 
     - **ToolExecutor**: Manages tool registration and execution
     - **AgentService**: Coordinates LLM and tool interactions

3. **Utils Layer** (`src/utils/`)
   - `ui_manager.py`: **UIManager** class - all Streamlit UI components
   - Handles rendering, layout, and user interactions

4. **Models Layer** (`src/models/`)
   - Reserved for future data models and DTOs

## 🎯 Key Classes

### DataAnalyzer
```python
class DataAnalyzer:
    """Handles all shipment data analysis operations."""
    
    def __init__(self, data_file: str)
    def get_dataset_summary() -> str
    def analyze_delays() -> str
    def analyze_route_performance(route: Optional[str]) -> str
    def analyze_warehouse_performance(warehouse: Optional[str]) -> str
    def get_recommendations() -> str
    def analyze_by_time_period(...) -> str
    def search_shipments(query: str) -> str
```

### GeminiService
```python
class GeminiService:
    """Gemini LLM service implementation."""
    
    def generate_response(messages: List[Dict]) -> str
    def is_available() -> bool
```

### AgentService
```python
class AgentService:
    """Coordinates LLM interactions and tool execution."""
    
    def __init__(self, llm_service, data_analyzer, system_prompt)
    def process_message(user_message, conversation_history) 
        -> Tuple[str, Optional[str], List[Dict]]
```

### UIManager
```python
class UIManager:
    """Manages Streamlit UI components (all static methods)."""
    
    @staticmethod
    def setup_page_config(...)
    @staticmethod
    def render_header(title: str)
    @staticmethod
    def render_sidebar(...) -> Tuple[str, str]
    @staticmethod
    def render_chat_history(messages: List)
    # ... and more
```

## 🚀 Usage

### Running the App

```bash
streamlit run app.py
```

### Environment Setup

1. Create a `.env` file:
```env
GEMINI_API_KEY=your_gemini_api_key_here
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## 📦 Dependencies

- `streamlit==1.29.0` - Web UI framework
- `google-generativeai==0.3.2` - Gemini API
- `pandas==2.1.4` - Data analysis
- `python-dotenv==1.0.0` - Environment variables

## 🎨 Design Patterns Used

1. **Factory Pattern**: `LLMServiceFactory` for creating LLM service instances
2. **Strategy Pattern**: Different LLM providers implement same interface
3. **Facade Pattern**: `AgentService` provides simple interface to complex subsystems
4. **Singleton Pattern**: Streamlit session state for maintaining application state
5. **Separation of Concerns**: Clear boundaries between config, services, and UI

## 🔧 Extending the Application

### Adding a New Analysis Tool

1. Add method to `DataAnalyzer` class in `data_analyzer.py`
2. Register tool in `ToolExecutor._register_tools()` in `agent_service.py`
3. Tool automatically becomes available to the agent

### Customizing UI

All UI components are in `UIManager` class - modify static methods to change appearance or behavior.

## 🆚 Differences from Legacy Code

| Aspect | Legacy (`app.py`, `tools.py`) | New Structure (`src/`) |
|--------|-------------------------------|------------------------|
| **Organization** | 2 large monolithic files | Modular directory structure |
| **Code Reuse** | Functions scattered | Organized in classes |
| **Testing** | Difficult to unit test | Easy to mock and test |
| **Maintainability** | Hard to navigate | Clear separation of concerns |
| **Extensibility** | Requires editing core files | Add new classes/methods |
| **Configuration** | Hardcoded in main file | Centralized in `config/` |




