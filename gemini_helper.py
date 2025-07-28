#!/usr/bin/env python3
"""
Google Gemini AI Helper for Plant Leaf Diagnosis

This module provides integration with Google's Gemini AI to generate
enhanced explanations for plant leaf diagnosis results.
"""

import os
import logging
from typing import Dict, Optional, Any

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

# Configure logging
logger = logging.getLogger(__name__)

class GeminiAIHelper:
    """Helper class for Google Gemini AI integration"""
    
    def __init__(self):
        """Initialize Gemini AI helper with API key from environment"""
        self.model = None
        self.api_key = None
        self._initialize_gemini()
    
    def _initialize_gemini(self):
        """Initialize Gemini AI with API key from environment variables"""
        try:
            # Load API key from environment variables
            # First try .env file using python-dotenv if available
            try:
                from dotenv import load_dotenv
                load_dotenv()
            except ImportError:
                # dotenv not available, continue with os.environ
                pass
            
            # Get API key from environment
            self.api_key = os.getenv('GEMINI_API_KEY') or os.environ.get('GEMINI_API_KEY')
            
            if not self.api_key:
                logger.warning("GEMINI_API_KEY not found in environment variables")
                return
            
            if not GEMINI_AVAILABLE:
                logger.warning("google-generativeai package not installed")
                return
            
            # Configure Gemini AI
            genai.configure(api_key=self.api_key)
            
            # Initialize the model
            self.model = genai.GenerativeModel('gemini-pro')
            logger.info("Gemini AI initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing Gemini AI: {str(e)}")
            self.model = None
    
    def is_available(self) -> bool:
        """Check if Gemini AI is available and properly configured"""
        return self.model is not None and self.api_key is not None
    
    def generate_explanation(self, diagnosis_result: Dict[str, Any]) -> Optional[str]:
        """
        Generate an enhanced explanation for leaf diagnosis using Gemini AI
        
        Args:
            diagnosis_result: Dictionary containing the original diagnosis results
            
        Returns:
            Enhanced explanation string or None if Gemini is not available
        """
        if not self.is_available():
            logger.warning("Gemini AI not available for explanation generation")
            return None
        
        try:
            # Extract key information from diagnosis
            prediction = diagnosis_result.get('prediction', 'unknown')
            confidence = diagnosis_result.get('confidence', 0)
            model_type = diagnosis_result.get('model_info', {}).get('type', 'Unknown')
            suggestions = diagnosis_result.get('suggestions', {})
            
            # Create a detailed prompt for Gemini
            prompt = self._create_explanation_prompt(
                prediction=prediction,
                confidence=confidence,
                model_type=model_type,
                suggestions=suggestions
            )
            
            # Generate response from Gemini
            response = self.model.generate_content(prompt)
            
            if response and response.text:
                logger.info("Successfully generated Gemini AI explanation")
                return response.text.strip()
            else:
                logger.warning("Gemini AI returned empty response")
                return None
                
        except Exception as e:
            logger.error(f"Error generating Gemini explanation: {str(e)}")
            return None
    
    def _create_explanation_prompt(self, prediction: str, confidence: float, 
                                 model_type: str, suggestions: Dict) -> str:
        """
        Create a detailed prompt for Gemini AI explanation
        
        Args:
            prediction: The diagnosis prediction (healthy/diseased)
            confidence: Confidence percentage
            model_type: Type of model used
            suggestions: Treatment/care suggestions
            
        Returns:
            Formatted prompt string
        """
        prompt = f"""
As an expert agricultural AI assistant, please provide a clear and educational explanation for a plant leaf diagnosis result.

Diagnosis Details:
- Prediction: {prediction}
- Confidence: {confidence:.1f}%
- Model Type: {model_type}

Current Suggestions:
{self._format_suggestions(suggestions)}

Please provide:
1. A simple explanation of what this diagnosis means in everyday terms
2. Why this condition might occur (possible causes)
3. What a farmer or gardener should understand about this result
4. Any additional insights or recommendations for plant care
5. When to seek further professional help if needed

Keep the explanation clear, practical, and accessible to non-experts. Focus on actionable advice and educational value. Limit response to 200-300 words.
"""
        return prompt.strip()
    
    def _format_suggestions(self, suggestions: Dict) -> str:
        """Format suggestions dictionary into readable text"""
        if not suggestions:
            return "No specific suggestions provided."
        
        formatted = []
        
        # Handle different suggestion types
        for key, value in suggestions.items():
            if isinstance(value, list):
                formatted.append(f"{key.replace('_', ' ').title()}: {', '.join(value[:3])}")
            elif isinstance(value, str):
                formatted.append(f"{key.replace('_', ' ').title()}: {value}")
        
        return "\n".join(formatted) if formatted else "No specific suggestions provided."
    
    def get_fallback_explanation(self, diagnosis_result: Dict[str, Any]) -> str:
        """
        Provide a fallback explanation when Gemini AI is not available
        
        Args:
            diagnosis_result: Dictionary containing the original diagnosis results
            
        Returns:
            Basic explanation string
        """
        prediction = diagnosis_result.get('prediction', 'unknown')
        confidence = diagnosis_result.get('confidence', 0)
        
        if prediction == 'healthy':
            return (f"The analysis shows your plant leaf appears healthy with {confidence:.1f}% confidence. "
                   "Continue your current care routine and monitor regularly for any changes.")
        elif prediction == 'diseased':
            return (f"The analysis indicates potential disease signs with {confidence:.1f}% confidence. "
                   "Consider the recommended treatment options and monitor closely. "
                   "If symptoms persist or worsen, consult with a local agricultural extension office.")
        else:
            return "The analysis could not determine a clear diagnosis. Please try again with a clearer image."


# Global instance for easy access
gemini_helper = GeminiAIHelper()


def get_enhanced_explanation(diagnosis_result: Dict[str, Any]) -> str:
    """
    Convenience function to get enhanced explanation
    
    Args:
        diagnosis_result: Dictionary containing the original diagnosis results
        
    Returns:
        Enhanced explanation string (either from Gemini AI or fallback)
    """
    # Try to get Gemini AI explanation first
    gemini_explanation = gemini_helper.generate_explanation(diagnosis_result)
    
    if gemini_explanation:
        return gemini_explanation
    
    # Fall back to basic explanation
    return gemini_helper.get_fallback_explanation(diagnosis_result)