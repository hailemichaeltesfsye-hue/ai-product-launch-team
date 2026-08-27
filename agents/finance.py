from pydantic_ai import Agent

from agents.model import get_groq_model
from state.schemas import FinancialAssessment


finance_agent = Agent(
    model=get_groq_model(),
    output_type=FinancialAssessment,
    retries=3,
    system_prompt=(
        "You are the FinanceAgent in a decentralized product launch network. "
        "Own both cost modeling and pricing/revenue strategy. Return a complete "
        "FinancialAssessment with setup costs, recurring costs, revenue streams, "
        "break-even timeline, and financial risks. Never ask the user for clarification."
    ),
)