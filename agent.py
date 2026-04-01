import os
import logging
import google.cloud.logging
from dotenv import load_dotenv

from google.adk import Agent
from google.adk.agents import SequentialAgent
from google.adk.tools.tool_context import ToolContext

# --- Setup Logging and Environment ---

cloud_logging_client = google.cloud.logging.Client()
cloud_logging_client.setup_logging()

load_dotenv()

model_name = os.getenv("MODEL")

# --- Custom Tools ---

def add_prompt_to_state(
    tool_context: ToolContext, prompt: str
) -> dict[str, str]:
    """Stores the user's raw prompt into state."""
    tool_context.state["RAW_PROMPT"] = prompt
    logging.info(f"[State updated] RAW_PROMPT: {prompt}")
    return {"status": "success"}


# --- Agent Definitions ---

# 1. Prompt Analyzer Agent
prompt_analyzer = Agent(
    name="prompt_analyzer",
    model=model_name,
    description="Analyzes the user's raw prompt and identifies intent, gaps, and improvements needed.",
    instruction="""
    You are an expert in prompt engineering.

    Analyze the RAW_PROMPT and do the following:
    - Identify the user's intent.
    - Detect missing details or ambiguity.
    - Identify the type of task (e.g., coding, writing, research, etc.).
    - Suggest what additional context would improve the prompt.

    Produce a structured analysis.

    RAW_PROMPT:
    { RAW_PROMPT }
    """,
    output_key="analysis_data"
)

# 2. Prompt Refiner Agent
prompt_refiner = Agent(
    name="prompt_refiner",
    model=model_name,
    description="Refines the user prompt into a clear, structured, and high-quality version.",
    instruction="""
    You are a senior AI prompt engineer.

    Using the ANALYSIS_DATA and RAW_PROMPT:
    - Rewrite the prompt to be clear, specific, and unambiguous.
    - Add missing details where necessary (assume reasonable defaults if needed).
    - Structure the prompt for best AI performance.
    - Keep it concise but powerful.

    Output:
    1. Refined Prompt
    2. Optional: Variations (2-3 alternative improved prompts)

    RAW_PROMPT:
    { RAW_PROMPT }

    ANALYSIS_DATA:
    { analysis_data }
    """,
    output_key="refined_prompt"
)

# 3. Output Formatter Agent
response_formatter = Agent(
    name="response_formatter",
    model=model_name,
    description="Formats the refined prompt into a clean final output.",
    instruction="""
    Present the final result clearly:

    - Show the REFINED PROMPT as the main output.
    - Then list 2-3 alternative variations.
    - Keep formatting clean and readable.

    REFINED_PROMPT:
    { refined_prompt }
    """
)

# --- Workflow Setup ---

prompt_refiner_workflow = SequentialAgent(
    name="prompt_refiner_workflow",
    description="Workflow that analyzes and improves user prompts.",
    sub_agents=[
        prompt_analyzer,
        prompt_refiner,
        response_formatter,
    ]
)

# Root Agent
root_agent = Agent(
    name="prompt_refiner_greeter",
    model=model_name,
    description="Entry point for the Smart Prompt Refiner system.",
    instruction="""
    - Welcome the user to the Smart Prompt Refiner System.
    - Ask the user to provide a raw or unclear prompt.
    - When the user provides input, store it using 'add_prompt_to_state'.
    - Then transfer control to 'prompt_refiner_workflow'.
    """,
    tools=[add_prompt_to_state],
    sub_agents=[prompt_refiner_workflow]
)
