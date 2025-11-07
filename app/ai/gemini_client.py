"""
Gemini AI client for document analysis and assistance
"""

import google.generativeai as genai
from typing import List, Dict, Any, Optional
from app.core.config import get_settings


class GeminiClient:
    """Client for interacting with Google Gemini API"""
    
    def __init__(self, api_key: Optional[str] = None):
        settings = get_settings()
        self.api_key = api_key or settings.google_api_key
        self.model_name = settings.gemini_model
        self.temperature = settings.temperature
        self.max_tokens = settings.max_tokens
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        
        # Initialize model
        self.model = genai.GenerativeModel(
            model_name=self.model_name,
            generation_config={
                "temperature": self.temperature,
                "max_output_tokens": self.max_tokens,
            }
        )
    
    def analyze_checklist_results(self, validation_result: Dict[str, Any]) -> str:
        """Analyze checklist validation results and provide insights"""
        
        prompt = f"""
You are an expert accounting assistant analyzing month-end close checklist results.

VALIDATION RESULTS:
{self._format_validation_results(validation_result)}

Please provide:
1. A brief summary of the completion status
2. Key findings and concerns
3. Priority items that need immediate attention
4. Overall assessment and recommendations

Keep your response concise and actionable.
"""
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error generating analysis: {str(e)}"
    
    def generate_completion_guidance(self, checklist_item: Dict[str, Any]) -> str:
        """Generate step-by-step guidance for completing a checklist item"""
        
        prompt = f"""
You are an expert accounting assistant helping someone complete their month-end close checklist.

CHECKLIST ITEM: {checklist_item.get('name')}
DESCRIPTION: {checklist_item.get('description')}
STATUS: {checklist_item.get('status')}
ISSUES: {', '.join(checklist_item.get('issues', []))}

Provide:
1. Clear step-by-step instructions to complete this item
2. What data or information is needed
3. Common mistakes to avoid
4. Expected format and structure

Be specific and practical.
"""
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error generating guidance: {str(e)}"
    
    def ask_followup_questions(self, checklist_item: Dict[str, Any]) -> List[str]:
        """Generate follow-up questions to gather data for missing item"""
        
        prompt = f"""
You are an accounting assistant helping gather information to complete: {checklist_item.get('name')}.

This checklist item requires: {checklist_item.get('description')}

Current issues: {', '.join(checklist_item.get('issues', []))}

Generate 3-5 specific questions to ask the user to gather the necessary data to create this document.
Questions should be clear, practical, and help collect actual numbers and details.

Format your response as a numbered list of questions.
"""
        
        try:
            response = self.model.generate_content(prompt)
            # Parse questions from response
            questions = self._parse_questions(response.text)
            return questions
        except Exception as e:
            return [f"Error generating questions: {str(e)}"]
    
    def analyze_user_data(self, user_input: str, context: str) -> Dict[str, Any]:
        """Analyze user-provided data and extract structured information"""
        
        prompt = f"""
You are an accounting data analyst. A user has provided the following information:

USER INPUT: {user_input}

CONTEXT: {context}

Extract and structure the key information from this input. Identify:
1. Numeric values and amounts
2. Dates and periods
3. Account names or categories
4. Any other relevant accounting data

Provide a clear summary of what data was provided and what might still be needed.
Format your response as structured data where possible.
"""
        
        try:
            response = self.model.generate_content(prompt)
            return {
                "success": True,
                "analysis": response.text,
                "extracted_data": self._extract_structured_data(response.text)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def generate_document_structure(
        self, 
        checklist_item: Dict[str, Any], 
        user_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate structure for a document based on checklist item and user data"""
        
        prompt = f"""
You are creating a template for: {checklist_item.get('name')}

PURPOSE: {checklist_item.get('description')}

USER PROVIDED DATA:
{self._format_user_data(user_data)}

Design a structured template (Excel-like format) with:
1. Column headers needed
2. Sample row structure
3. Formulas or calculations required
4. Any sections or tabs needed

Provide the structure in a clear, implementable format.
"""
        
        try:
            response = self.model.generate_content(prompt)
            return {
                "success": True,
                "structure": response.text,
                "columns": self._extract_columns(response.text)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def chat(self, message: str, context: Optional[str] = None) -> str:
        """General chat interface for user questions"""
        
        system_context = """
You are an expert accounting assistant specializing in month-end close processes.
You help users complete their checklist items, answer accounting questions, and provide
practical guidance. Be concise, clear, and actionable in your responses.
"""
        
        full_prompt = system_context
        if context:
            full_prompt += f"\n\nCONTEXT:\n{context}"
        full_prompt += f"\n\nUSER: {message}\n\nASSISTANT:"
        
        try:
            response = self.model.generate_content(full_prompt)
            return response.text
        except Exception as e:
            return f"I apologize, but I encountered an error: {str(e)}"
    
    def _format_validation_results(self, validation_result: Dict[str, Any]) -> str:
        """Format validation results for AI processing"""
        summary = validation_result.get("summary", {})
        results = validation_result.get("checklist_results", [])
        
        output = f"""
Total Items: {summary.get('total_items', 0)}
Complete: {summary.get('complete', 0)}
Incomplete: {summary.get('incomplete', 0)}
Missing: {summary.get('missing', 0)}
Completion Rate: {summary.get('completion_rate', 0)}%

ITEM DETAILS:
"""
        for item in results:
            output += f"\n- {item['name']}: {item['status']}"
            if item.get('issues'):
                output += f"\n  Issues: {', '.join(item['issues'][:2])}"
        
        return output
    
    def _format_user_data(self, user_data: Dict[str, Any]) -> str:
        """Format user data for AI processing"""
        output = ""
        for key, value in user_data.items():
            output += f"{key}: {value}\n"
        return output
    
    def _parse_questions(self, text: str) -> List[str]:
        """Parse questions from AI response"""
        lines = text.strip().split('\n')
        questions = []
        
        for line in lines:
            line = line.strip()
            # Look for numbered questions
            if line and (line[0].isdigit() or line.startswith('-') or line.startswith('•')):
                # Remove numbering
                question = line.lstrip('0123456789.-•) ').strip()
                if question:
                    questions.append(question)
        
        return questions if questions else [text]
    
    def _extract_structured_data(self, text: str) -> Dict[str, Any]:
        """Attempt to extract structured data from AI response"""
        # Basic implementation - could be enhanced
        return {"raw_analysis": text}
    
    def _extract_columns(self, text: str) -> List[str]:
        """Extract column names from AI response"""
        # Basic implementation - could be enhanced
        columns = []
        lines = text.split('\n')
        for line in lines:
            if 'column' in line.lower() or '|' in line:
                # Try to extract column names
                parts = [p.strip() for p in line.split('|') if p.strip()]
                columns.extend(parts)
        return columns[:10]  # Limit to 10 columns
