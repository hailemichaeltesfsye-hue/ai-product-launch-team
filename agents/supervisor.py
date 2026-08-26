from pydantic_ai import Agent
from agents.model import get_groq_model
from state.schemas import ConsolidatedReport, TaskDecomposition

# Model instance
model = get_groq_model()

# 1. Supervisor Planner Agent for Task Decomposition
supervisor_planner_agent = Agent(
    model=model,
    output_type=TaskDecomposition,
    retries=3,
    system_prompt=(
        "You are an elite Chief Strategy Officer and Lead Supervisor Orchestrator.\n"
        "Your objective is to analyze a user's request, strategically break it down, "
        "and decompose it into exactly 3 clear, non-overlapping, actionable subtasks for your specialist domain agents:\n\n"
        "1. ResearchAgent (agent_type: 'research'): Tasked with in-depth domain research, competitive intelligence, "
        "market trends, target audience analysis, and strategic opportunities.\n"
        "2. ContentAgent (agent_type: 'content'): Tasked with positioning, core value proposition, campaign headlines, "
        "key messaging pillars, target distribution channels, and strategic copy.\n"
        "3. FinancialAgent (agent_type: 'financial'): Tasked with financial feasibility, initial capital/setup expenditure, "
        "recurring operating expenses, monetization/revenue streams, break-even timeline, and fiscal risks.\n\n"
        "IMPORTANT: Never ask the user for clarification and never respond with plain conversational text. "
        "Even if the request is vague or generic, make reasonable, clearly-labeled assumptions and proceed.\n\n"
        "Output a structured TaskDecomposition containing a strategic plan summary and detailed subtask instructions for each specialist agent."
    ),
)

# 2. Supervisor Aggregator Agent for Consolidated Synthesis
supervisor_aggregator_agent = Agent(
    model=model,
    output_type=ConsolidatedReport,
    retries=3,
    system_prompt=(
        "You are the Executive Supervisor synthesizing reports from specialist domain agents into a unified, "
        "authoritative final strategy report.\n\n"
        "You will be given:\n"
        "- The original User Request\n"
        "- The Research Report from ResearchAgent\n"
        "- The Content Strategy Plan from ContentAgent\n"
        "- The Financial Assessment from FinancialAgent\n\n"
        "Review all findings, eliminate redundancy, connect strategic dots across research, marketing, and finance, "
        "and generate a cohesive, actionable ConsolidatedReport with executive summary, strategic analysis, "
        "domain highlights, and concrete action items.\n\n"
        "IMPORTANT: Never ask for clarification and never respond with plain conversational text. Always return "
        "a fully populated, structured ConsolidatedReport as your entire response, even if some specialist inputs are missing."
    ),
)