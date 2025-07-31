from typing import Dict, Any, List
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from dashboard_insights_agentic_system.static_pipeline.reasoning.heuristics_engine import all_heuristics
llm = None  # Placeholder for the LLM instance, should be initialized elsewhere
def apply_heuristics(extracted_data: List[Dict[str, Any]], user_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Applies heuristics using both dashboard-extracted data and user-provided company data.

    Args:
        extracted_data (List[Dict]): Extracted dashboard data.
        user_data (Dict): User-provided company info (e.g., stage, tier, size).

    Returns:
        Dict[str, Any]: Heuristic findings.
    """
    if not user_data:
        print("Please provide some company information for tailored analysis.")
        user_stage = input("Enter the company's funding stage (e.g., Seed, Series A, Series B): ")
        user_size = input("Enter the number of employees: ")
        user_industry = input("Enter the industry (e.g., SaaS, Retail, Healthcare): ")

        user_data = {
            "stage": user_stage,
            "employees": int(user_size),
            "industry": user_industry
        }
    merged_data = {}

    # Merge extracted dashboard data
    for item in extracted_data:
        merged_data.update(item)

    # Add (or overwrite) with user-provided company data
    merged_data.update(user_data)

    # Run heuristics on the combined data
    results = all_heuristics(merged_data)
    return results

def format_for_llm(extracted_data: List[Dict[str, Any]], heuristics: Dict[str, Any]) -> str:
    """Format extracted data and heuristics into a readable prompt."""
    return (
        "Here is the dashboard data and heuristic analysis:\n\n"
        f"Dashboard Data: {extracted_data}\n\n"
        f"Heuristic Findings: {heuristics}\n\n"
        "Please provide actionable business recommendations tailored to this company's stage and performance."
    )

def generate_insights(prompt: str) -> str:
    """Generate business insights using the LLM."""
    llm_prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content="You are an optimized business solutions strategist."),
        HumanMessage(content=prompt)
    ])
    response = llm.invoke(llm_prompt.format())
    return response.content if response else "No insights generated."

def reasoning_pipeline(extracted_data: List[Dict[str, Any]]) -> str:
    """Full reasoning pipeline."""
    heuristics = apply_heuristics(extracted_data)
    prompt = format_for_llm(extracted_data, heuristics)
    insights = generate_insights(prompt)
    return insights