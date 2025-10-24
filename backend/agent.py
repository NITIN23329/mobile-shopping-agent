"""
Mobile Shopping Agent - Built with Google ADK (Agent Development Kit)
Main agent definition for the shopping assistant
"""
import os
from google.adk.models.lite_llm import LiteLlm
from google.adk.agents import LlmAgent
import google.generativeai as genai
from dotenv import load_dotenv

try:
    from .tools import (
        search_phones_by_filters,
        get_phone_details,
        list_all_phones,
        compare_phones,
        explain_phone_feature,
    )
    from .agent_instructions import (
        get_shopping_agent_instruction,
        get_recommendation_agent_instruction,
        get_comparison_agent_instruction,
        get_root_agent_instruction,
    )
except ImportError:
    from tools import (
        search_phones_by_filters,
        get_phone_details,
        list_all_phones,
        compare_phones,
        explain_phone_feature,
    )
    from agent_instructions import (
        get_shopping_agent_instruction,
        get_recommendation_agent_instruction,
        get_comparison_agent_instruction,
        get_root_agent_instruction,
    )

load_dotenv()

# Initialize Gemini
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY environment variable is not set")


genai.configure(api_key=GOOGLE_API_KEY)

# Set environment variable for LiteLlm to use Google AI Studio
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY
os.environ["LITELLM_LOG"] = "DEBUG"

# Initialize Gemini model using LiteLlm with Google AI Studio
# Explicitly set custom provider so LiteLLM routes to Gemini API directly
model = LiteLlm(
    model="gemini-2.5-flash",
    custom_llm_provider="gemini",
    api_key=GOOGLE_API_KEY,
)

# Define the Shopping Agent
shopping_agent = LlmAgent(
    name="shopping_agent",
    model=model,
    description="Mobile phone shopping assistant that helps users find, compare, and understand phones",
    instruction=get_shopping_agent_instruction(),
    tools=[
        search_phones_by_filters,
        get_phone_details,
        list_all_phones,
        explain_phone_feature,
    ],
)

# Define the Recommendation Agent (specialized for recommendations)
recommendation_agent = LlmAgent(
    name="recommendation_agent",
    model=model,
    description="Provides personalized phone recommendations based on user budget and preferences",
    instruction=get_recommendation_agent_instruction(),
    tools=[
        search_phones_by_filters,
        get_phone_details,
        list_all_phones,
    ],
)

# Define the Comparison Agent (specialized for comparisons)
comparison_agent = LlmAgent(
    name="comparison_agent",
    model=model,
    description="Compares two or more phones side-by-side with trade-offs and recommendations",
    instruction=get_comparison_agent_instruction(),
    tools=[
        get_phone_details,
        compare_phones,
        explain_phone_feature,
    ],
)

# Root Agent - Entry point that routes queries to appropriate sub-agents
root_agent = LlmAgent(
    name="mobile_shopping_agent",
    model=model,
    description="Root mobile phone shopping agent that routes queries to specialized sub-agents",
    instruction=get_root_agent_instruction(),
    sub_agents=[shopping_agent, recommendation_agent, comparison_agent],
)

# Main agent for external use
agent = root_agent

# For backwards compatibility
main_agent = root_agent
