"""
agent_setup.py
ReAct-style LangChain agent scaffold for dashboard interaction,
with explicit reasoning and action steps.
"""

from typing import List, Dict, Any
from urllib import response
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.tools import BaseTool
from langchain.chat_models import ChatOpenAI  # Or your chosen LLM
from .tools import dashboard_tools
from langchain.prompts import ChatPromptTemplate
from utils.data_cleaning import DataCleaner

class DashboardAgentFactory:
    """
    Factory for creating and running a dashboard-interacting agent
    that reasons over initial dashboard data and acts via tools.
    """

    def __init__(self, llm_model: str = "gpt-4", temperature: float = 0.0):
        self.llm_model = llm_model
        self.temperature = temperature
        self.llm = None
        self.agent = None
        self.tools = []

    def init_llm(self):
        """
        Initialize the LLM for the agent.
        """
        # TODO: Initialize your chat LLM here
        # Example:
        # self.llm = ChatOpenAI(model=self.llm_model, temperature=self.temperature)
        self.llm = ChatOpenAI(model=self.llm_model, temperature=self.temperature)
        return self.llm

    def init_tools(self) -> List[BaseTool]:
        """
        Initialize dashboard interaction tools for agent actions.
        """
        # TODO: Import your tools from dashboard_tools.py
        # Wrap them as LangChain Tool objects with names and descriptions
        self.tools = dashboard_tools
        return self.tools
    
    def create_agent(self):
        """
    Create the agent with tools and LLM, ready for reasoning + action.
    """
        if not self.llm:
            self.init_llm()
        self.tools = self.init_tools()
        prompt = ChatPromptTemplate.from_messages([
        ("system",
         "You are an expert BI analyst. Given the dashboard data and a business question, "
         "autonomously explore, filter, and analyze the dashboard using your tools. "
         "For each step, explain what you did, why you did it, and what you found. "
         "Reference specific data points, highlights, or visuals. "
         "Provide a concise summary that answers the user's question, and suggest next steps if relevant."
        ),
        ("human", "Business Question: {user_query}\n\nDashboard Data:\n{dashboard_data}")
    ])
        self.agent = create_react_agent(
        llm=self.llm,
        tools=self.tools,
        prompt=prompt,
        verbose=True
    )
        return self.agent

    def reason_over_dashboard(self, raw_dashboard_data: Dict[str, Any]) -> str:
        """
        Reasoning step: analyze initial dashboard data structure.

        Args:
            raw_dashboard_data: The original output from DataCleaner or similar.

        Returns:
            Summary string of the dashboard’s data, KPIs, layout, etc.
        """
        # TODO: Implement your logic to parse raw_dashboard_data
        # and produce a concise textual summary or gist.
        # This could be used to inform subsequent tool usage.
        dashboard_data = DataCleaner.clean_unified_dashboard_data(raw_dashboard_data)
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert BI analyst. Understand and analyze the following cleaned dashboard data:"),
            ("human", "{dashboard_data}")
        ])
        formatted_prompt = prompt.format_messages(dashboard_data=str(dashboard_data))
        summary = self.llm(formatted_prompt)
        return summary.content if hasattr(summary, "content") else summary

    def act_on_dashboard(self, user_query: str, dashboard_state_summary: str) -> str:
        """
    Action step: run the user query via the agent using the
    dashboard tools, informed by the reasoning summary.

    Args:
        user_query: The user's natural language query.
        dashboard_state_summary: The reasoning output about the dashboard.

    Returns:
        Agent's response after interacting with the dashboard.
    """
        if self.agent is None:
            self.create_agent()
        actions = AgentExecutor(agent=self.agent, tools=self.tools, verbose=True)
    # Combine the user query and dashboard summary for the agent's context
        agent_input = {
        "user_query": user_query,
        "dashboard_data": dashboard_state_summary
    }
        response = actions.invoke(agent_input)
    # Extract the content if the response is an object with 'content'
        if hasattr(response, "content"):
            return response.content
        elif isinstance(response, dict) and "output" in response:
            return response["output"]
        return str(response)

    def run(self, user_query: str, raw_dashboard_data: Dict[str, Any]) -> str:
        """
        Full pipeline:
        1. Reason about the dashboard data.
        2. Act on the dashboard to fulfill the user's query.

        Args:
            user_query: User's natural language question or goal.
            raw_dashboard_data: Original dashboard data from DataCleaner.

        Returns:
            Final agent response.
        """
        dashboard_summary = self.reason_over_dashboard(raw_dashboard_data)
        return self.act_on_dashboard(user_query, dashboard_summary)

        