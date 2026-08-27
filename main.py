import argparse
import logging
from config.logging_config import setup_logging
from graphs.ceo_graph import ceo_graph
from graphs.supervisor_graph import supervisor_graph
from state.state import HierarchicalState, SupervisorGraphState

setup_logging()
logger = logging.getLogger("main")


# ---------------------------------------------------------------------------
# Flat mode (Supervisor -> Research/Content/Financial)
# ---------------------------------------------------------------------------


def run_flat(user_request: str) -> SupervisorGraphState:
    """Runs the flat LangGraph supervisor workflow for a given user request."""
    logger.info("Initializing Flat Supervisor Workflow...")
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


def print_flat_report(result: SupervisorGraphState) -> None:
    """Pretty prints the full execution result for the flat architecture."""
    print("\n" + "=" * 80)
    print(" 🚀 SUPERVISOR MULTI-AGENT EXECUTION REPORT (Flat)")
    print("=" * 80)

    print(f"\n📌 USER REQUEST:\n   {result.get('user_request')}\n")

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

    errors = result.get("errors")
    if errors:
        print("⚠️  Encountered Warnings/Errors during execution:")
        for err in errors:
            print(f"  - {err}")
        print()
    print("=" * 80)


# ---------------------------------------------------------------------------
# Hierarchical mode (CEO -> Marketing/Finance Managers -> Specialists)
# ---------------------------------------------------------------------------


def run_hierarchical(user_request: str) -> HierarchicalState:
    """Runs the hierarchical CEO -> Manager -> Specialist LangGraph workflow."""
    logger.info("Initializing Hierarchical CEO Multi-Agent Workflow...")
    logger.info("User Request: %s", user_request)

    initial_state: HierarchicalState = {
        "user_request": user_request,
        "current_agent": "CEO",
        "handoff_history": [],
        "marketing_directive": None,
        "finance_directive": None,
        "marketing_decomposition": None,
        "finance_decomposition": None,
        "research_output": None,
        "content_output": None,
        "marketing_report": None,
        "cost_output": None,
        "pricing_output": None,
        "finance_report": None,
        "final_response": None,
        "errors": [],
    }

    result: HierarchicalState = ceo_graph.invoke(initial_state)
    return result


def print_hierarchical_report(result: HierarchicalState) -> None:
    """Pretty prints the full execution result for the hierarchical architecture."""
    print("\n" + "=" * 80)
    print(" 🏢 CEO HIERARCHICAL MULTI-AGENT EXECUTION REPORT")
    print("=" * 80)

    print(f"\n📌 USER REQUEST:\n   {result.get('user_request')}\n")

    marketing_directive = result.get("marketing_directive")
    finance_directive = result.get("finance_directive")
    if marketing_directive or finance_directive:
        print("-" * 80)
        print("📋 1. CEO DIRECTIVES")
        print("-" * 80)
        if marketing_directive:
            print(f"Marketing Directive:\n  {marketing_directive}\n")
        if finance_directive:
            print(f"Finance Directive:\n  {finance_directive}\n")

    research = result.get("research_output")
    if research:
        print("-" * 80)
        print("🔍 2a. RESEARCH AGENT DELIVERABLE (Marketing Manager team)")
        print("-" * 80)
        print(f"Summary: {research.summary}\n")
        print(f"Market Trends: {', '.join(research.market_trends)}")
        print(f"Competitors:   {', '.join(research.competitors)}")
        print(f"Opportunities: {', '.join(research.opportunities)}\n")

    content = result.get("content_output")
    if content:
        print("-" * 80)
        print("✍️  2b. CONTENT AGENT DELIVERABLE (Marketing Manager team)")
        print("-" * 80)
        print(f"Headline:       {content.headline}")
        print(f"Core Messaging: {content.core_messaging}")
        print(f"Channels:       {', '.join(content.target_channels)}")
        print(f"CTA:            {content.call_to_action}\n")

    marketing_report = result.get("marketing_report")
    if marketing_report:
        print("-" * 80)
        print("📣 2c. MARKETING MANAGER REPORT (synthesized)")
        print("-" * 80)
        print(f"Summary: {marketing_report.summary}\n")
        print(f"Positioning: {marketing_report.market_positioning}\n")
        print(f"Recommended Channels: {', '.join(marketing_report.recommended_channels)}\n")

    cost = result.get("cost_output")
    if cost:
        print("-" * 80)
        print("💵 3a. COST AGENT DELIVERABLE (Finance Manager team)")
        print("-" * 80)
        print(f"Setup Cost:          {cost.estimated_setup_cost}")
        print(f"Recurring Costs:     {', '.join(cost.recurring_costs)}")
        print(f"Break-even Timeline: {cost.break_even_timeline}\n")

    pricing = result.get("pricing_output")
    if pricing:
        print("-" * 80)
        print("💲 3b. PRICING AGENT DELIVERABLE (Finance Manager team)")
        print("-" * 80)
        print(f"Pricing Model: {pricing.pricing_model}")
        print(f"Pricing Tiers: {', '.join(pricing.pricing_tiers)}")
        print(f"Revenue Streams: {', '.join(pricing.revenue_streams)}\n")

    finance_report = result.get("finance_report")
    if finance_report:
        print("-" * 80)
        print("💰 3c. FINANCE MANAGER REPORT (synthesized)")
        print("-" * 80)
        print(f"Summary: {finance_report.summary}\n")
        print(f"Cost Overview:    {finance_report.cost_overview}")
        print(f"Pricing Overview: {finance_report.pricing_overview}\n")

    final = result.get("final_response")
    if final:
        print("=" * 80)
        print("🎯 4. CEO FINAL EXECUTIVE REPORT")
        print("=" * 80)
        print(f"Executive Summary:\n{final.executive_summary}\n")
        print(f"Strategic Analysis:\n{final.strategic_analysis}\n")
        print(f"Marketing Highlights:\n{final.marketing_highlights}\n")
        print(f"Finance Highlights:\n{final.finance_highlights}\n")
        print("Action Items:")
        for idx, item in enumerate(final.action_items, start=1):
            print(f"  {idx}. {item}")
        print()

    errors = result.get("errors")
    if errors:
        print("⚠️  Encountered Warnings/Errors during execution:")
        for err in errors:
            print(f"  - {err}")
        print()
    print("=" * 80)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(
        description="Run the AI Product Launch Team multi-agent system (LangGraph + Pydantic AI)"
    )
    parser.add_argument(
        "--request",
        type=str,
        default="Launch an AI-powered smart productivity & time-management assistant for engineering teams.",
        help="The objective or product launch request for the multi-agent system",
    )
    parser.add_argument(
        "--architecture",
        type=str,
        choices=["hierarchical", "flat"],
        default="hierarchical",
        help="Which architecture to run: 'hierarchical' (CEO -> Managers -> Specialists, default) "
        "or 'flat' (Supervisor -> Research/Content/Financial)",
    )
    args = parser.parse_args()

    if args.architecture == "hierarchical":
        result = run_hierarchical(args.request)
        print_hierarchical_report(result)
    else:
        result = run_flat(args.request)
        print_flat_report(result)


if __name__ == "__main__":
    main()