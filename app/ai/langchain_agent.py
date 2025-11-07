"""
LangChain agent for intelligent checklist assistance
"""

from typing import Dict, Any, List, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools import Tool
from langchain.memory import ConversationBufferMemory
from langchain import hub
from app.core.config import get_settings
from app.validation.checklist_validator import ChecklistValidator


class ChecklistAgent:
    """LangChain agent for month-end checklist assistance"""
    
    def __init__(self):
        settings = get_settings()
        
        # Initialize Gemini LLM
        self.llm = ChatGoogleGenerativeAI(
            model=settings.gemini_model,
            google_api_key=settings.google_api_key,
            temperature=settings.temperature,
            max_output_tokens=settings.max_tokens
        )
        
        # Initialize validator
        self.validator = ChecklistValidator()
        
        # Initialize memory
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        # Setup tools
        self.tools = self._create_tools()
        
        # Create agent
        try:
            # Try to get ReAct prompt from hub
            prompt = hub.pull("hwchase17/react-chat")
        except:
            # Fallback to creating our own prompt
            from langchain.prompts import PromptTemplate
            template = """You are an expert accounting assistant helping with month-end close processes.

You have access to the following tools:
{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Chat History: {chat_history}

Question: {input}
Thought: {agent_scratchpad}"""
            
            prompt = PromptTemplate(
                template=template,
                input_variables=["input", "chat_history", "agent_scratchpad", "tools", "tool_names"]
            )
        
        # Create agent executor
        agent = create_react_agent(self.llm, self.tools, prompt)
        self.agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            memory=self.memory,
            verbose=True,
            max_iterations=5,
            handle_parsing_errors=True
        )
    
    def _create_tools(self) -> List[Tool]:
        """Create tools for the agent"""
        
        tools = [
            Tool(
                name="GetChecklistStatus",
                func=self._get_checklist_status,
                description="Get the current status of the month-end checklist. Use this to see which items are complete, incomplete, or missing."
            ),
            Tool(
                name="GetItemDetails",
                func=self._get_item_details,
                description="Get detailed information about a specific checklist item. Input should be the checklist item ID (e.g., 'bank_reconciliation', 'ar_aging')."
            ),
            Tool(
                name="GetCompletionGuidance",
                func=self._get_completion_guidance,
                description="Get step-by-step guidance on how to complete a specific checklist item. Input should be the checklist item ID."
            ),
            Tool(
                name="AnalyzeData",
                func=self._analyze_data,
                description="Analyze user-provided data for accounting purposes. Input should be the data to analyze."
            )
        ]
        
        return tools
    
    def _get_checklist_status(self, query: str = "") -> str:
        """Tool: Get overall checklist status"""
        # This would use the current session's validation results
        # For now, return a template response
        return """Current checklist status:
- Total items: 10
- Complete: 0
- Incomplete: 0
- Missing: 10

Please upload your month-end files to get an accurate status."""
    
    def _get_item_details(self, item_id: str) -> str:
        """Tool: Get details about a checklist item"""
        from app.validation.checklist_config import get_checklist_by_id
        
        item = get_checklist_by_id(item_id.strip())
        if not item:
            return f"Checklist item '{item_id}' not found."
        
        return f"""
{item.name}
Description: {item.description}
Required files should contain: {', '.join(item.required_files[:3])}
Expected content: {', '.join(item.required_content[:5])}
Priority: {item.priority} (1=High, 2=Medium, 3=Low)
"""
    
    def _get_completion_guidance(self, item_id: str) -> str:
        """Tool: Get guidance for completing an item"""
        from app.validation.checklist_config import get_checklist_by_id
        
        item = get_checklist_by_id(item_id.strip())
        if not item:
            return f"Checklist item '{item_id}' not found."
        
        # Provide guidance based on item type
        guidance = {
            "bank_reconciliation": """
To complete the Bank Reconciliation:
1. Obtain your bank statement for the month
2. Prepare a reconciliation schedule showing:
   - Opening balance per bank statement
   - Add: Deposits in transit
   - Less: Outstanding checks
   - Closing balance per books
3. Ensure the reconciled balance matches your cash book
4. Save as Excel file with 'bank_reconciliation' or 'recon' in the filename
""",
            "ar_aging": """
To complete the AR Aging Report:
1. Extract customer balances from your accounting system
2. Create columns: Customer Name, Invoice #, Invoice Date, Amount, Current, 30 days, 60 days, 90+ days
3. Age each invoice based on days outstanding
4. Calculate totals for each aging bucket
5. Save as Excel file with 'ar_aging' or 'receivables' in the filename
""",
            "ap_aging": """
To complete the AP Aging Report:
1. Extract vendor balances from your accounting system
2. Create columns: Vendor Name, Invoice #, Invoice Date, Amount, Current, 30 days, 60 days, 90+ days
3. Age each invoice based on days outstanding
4. Calculate totals for each aging bucket
5. Save as Excel file with 'ap_aging' or 'payables' in the filename
"""
        }
        
        return guidance.get(item_id, f"Please complete {item.name} by creating a file containing {', '.join(item.required_content[:3])}")
    
    def _analyze_data(self, data: str) -> str:
        """Tool: Analyze user-provided data"""
        return f"Analyzing the provided data: {data[:200]}... I can help you structure this information for your month-end close documents."
    
    def process_query(self, query: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Process a user query using the agent"""
        try:
            # Add context if provided
            full_query = query
            if context:
                full_query = f"Context: {context}\n\nQuestion: {query}"
            
            # Run agent
            result = self.agent_executor.invoke({"input": full_query})
            return result.get("output", "I'm not sure how to help with that.")
        
        except Exception as e:
            return f"I encountered an error: {str(e)}. Let me try to help you directly with your month-end close."
    
    def reset_memory(self):
        """Reset conversation memory"""
        self.memory.clear()
