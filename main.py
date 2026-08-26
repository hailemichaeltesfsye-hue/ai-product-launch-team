import argparse
import logging
import sys
from config.logging_config import setup_logging
from graphs.supervisor_graph import supervisor_graph
from state.state import SupervisorGraphState

setup_logging()
logger = logging.getLogger("supervisor_main")


def run_supervisor(user_request: str) -> SupervisorGraphState:
    """Runs the LangGraph supervisor workflow for a given user request."""
    logger.info("Initializing Supervisor Workflow...")
    logger.info("User Request: %s", user_request)

    initial_state: SupervisorGraphState = {
        "user_request": user_request,
        "decomposition": None,
        "research_output": None,
        "content_output": None,
        "financial_output": None,
        "final_response": None,
        "errors": [],
    }

    result: SupervisorGraphState = supervisor_graph.invoke(initial_state)
    return result


def print_formatted_report(result: SupervisorGraphState) -> None:
    """Pretty prints the full execution result across all agent deliverables."""
    print("\n" + "=" * 80)
    print(" 🚀 SUPERVISOR MULTI-AGENT EXECUTION REPORT")
    print("=" * 80)

    # 1. User Request
    print(f"\n📌 USER REQUEST:\n   {result.get('user_request')}\n")

    # 2. Task Decomposition
    decomp = result.get("decomposition")
    if decomp:
        print("-" * 80)
        print("📋 1. SUPERVISOR TASK DECOMPOSITION")
        print("-" * 80)
        print(f"Plan Summary: {decomp.plan_summary}\n")
        print("Delegated Subtasks:")
        for idx, task in enumerate(decomp.subtasks, start=1):
            print(f"  [{idx}] Agent: {task.agent_type.upper()} | Title: {task.title}")
            print(f"      Instructions: {task.instructions}")
        print()

    # 3. Research Output
    research = result.get("research_output")
    if research:
        print("-" * 80)
        print("🔍 2. RESEARCH AGENT DELIVERABLE")
        print("-" * 80)
        print(f"Summary: {research.summary}\n")
        print(f"Market Trends: {', '.join(research.market_trends)}")
        print(f"Competitors:   {', '.join(research.competitors)}")
        print(f"Key Findings:  {', '.join(research.key_findings)}")
        print(f"Opportunities: {', '.join(research.opportunities)}\n")

    # 4. Content Output
    content = result.get("content_output")
    if content:
        print("-" * 80)
        print("✍️  3. CONTENT AGENT DELIVERABLE")
        print("-" * 80)
        print(f"Headline:       {content.headline}")
        print(f"Core Messaging: {content.core_messaging}")
        print(f"Channels:       {', '.join(content.target_channels)}")
        print(f"Content Pieces: {', '.join(content.content_pieces)}")
        print(f"CTA:            {content.call_to_action}\n")

    # 5. Financial Output
    financial = result.get("financial_output")
    if financial:
        print("-" * 80)
        print("💰 4. FINANCIAL AGENT DELIVERABLE")
        print("-" * 80)
        print(f"Setup Cost (Capex):   {financial.estimated_setup_cost}")
        print(f"Recurring Costs:      {', '.join(financial.recurring_costs)}")
        print(f"Revenue Streams:      {', '.join(financial.revenue_streams)}")
        print(f"Break-even Timeline:  {financial.break_even_timeline}")
        print(f"Financial Risks:      {', '.join(financial.financial_risks)}\n")

    # 6. Final Supervisor Consolidated Response
    final = result.get("final_response")
    if final:
        print("=" * 80)
        print("🎯 5. SUPERVISOR FINAL CONSOLIDATED REPORT")
        print("=" * 80)
        print(f"Executive Summary:\n{final.executive_summary}\n")
        print(f"Strategic Analysis:\n{final.strategic_analysis}\n")
        print(f"Research Highlights:\n{final.research_highlights}\n")
        print(f"Content Strategy Summary:\n{final.content_strategy_summary}\n")
        print(f"Financial Outlook:\n{final.financial_outlook}\n")
        print("Action Items:")
        for idx, item in enumerate(final.action_items, start=1):
            print(f"  {idx}. {item}")
        print()

    # Errors if any
    errors = result.get("errors")
    if errors:
        print("⚠️  Encountered Warnings/Errors during execution:")
        for err in errors:
            print(f"  - {err}")
        print()
    print("=" * 80)


def main():
    parser = argparse.ArgumentParser(
        description="Run Supervisor Multi-Agent System using LangGraph and Pydantic AI"
    )
    parser.add_argument(
        "--request",
        type=str,
        default="Launch an AI-powered smart productivity & time-management assistant for engineering teams.",
        help="The objective or product launch request for the supervisor multi-agent system",
    )
    args = parser.parse_args()

    result = run_supervisor(args.request)
    print_formatted_report(result)


if __name__ == "__main__":
    main()
