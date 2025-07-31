"""
Heuristics for analyzing company limitations and providing insights.
"""
from typing import Dict, Any, List

def sales_trend_heuristic(data: Dict[str, Any]) -> Dict[str, Any]:
    """Check if sales increased over time."""
    sales = data.get("sales_history", [])
    if len(sales) >= 2:
        trend = "increasing" if sales[-1] > sales[0] else "stable_or_decreasing"
        return {"sales_trend": trend}
    return {"sales_trend": "insufficient_data"}


def profit_margin_heuristic(data: Dict[str, Any]) -> Dict[str, Any]:
    """Check if profit margin is above threshold."""
    margin = data.get("profit_margin")
    if margin is None:
        return {"profit_margin_status": "unknown"}
    return {"profit_margin_status": "healthy" if margin >= 0.1 else "low"}


def customer_satisfaction_heuristic(data: Dict[str, Any]) -> Dict[str, Any]:
    """Check if customer satisfaction score is acceptable."""
    score = data.get("csat_score")
    if score is None:
        return {"csat_status": "unknown"}
    return {"csat_status": "good" if score >= 7 else "poor"}


def expense_growth_heuristic(data: Dict[str, Any]) -> Dict[str, Any]:
    """Check if expenses are growing faster than revenue."""
    revenue_growth = data.get("revenue_growth")
    expense_growth = data.get("expense_growth")
    if revenue_growth is None or expense_growth is None:
        return {"expense_trend": "unknown"}
    if expense_growth > revenue_growth:
        return {"expense_trend": "concerning"}
    return {"expense_trend": "manageable"}


def churn_rate_heuristic(data: Dict[str, Any]) -> Dict[str, Any]:
    """Check if churn rate exceeds threshold."""
    churn = data.get("churn_rate")
    if churn is None:
        return {"churn_status": "unknown"}
    return {"churn_status": "high" if churn > 0.05 else "acceptable"}

def all_heuristics(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Applies all heuristics to the provided data.

    Args:
        data (Dict[str, Any]): Dashboard data containing relevant metrics.

    Returns:
        Dict[str, Any]: Combined heuristic findings.
    """
    return {
        **sales_trend_heuristic(data),
        **profit_margin_heuristic(data),
        **customer_satisfaction_heuristic(data),
        **expense_growth_heuristic(data),
        **churn_rate_heuristic(data)
    }