from google.adk.agents import LlmAgent
from techai_agent.prompt import *
from techai_agent.tools import *

Model = "gemini-2.0-flash"
root_agent = LlmAgent(
    name="tech_agent",
    model=Model,
    description="Agent that helps users shop a curated selection of Electronics, Fashion, Home essentials, and Sports gear, complete with customer ratings and deals. ", 
    instruction=ROOT_AGENT_PROMPT,
    tools= [fetch_products,]
)