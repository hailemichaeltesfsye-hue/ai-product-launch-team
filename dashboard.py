"""Live Streamlit dashboard for the AI Product Launch Team."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Iterator

import streamlit as st

from graphs.ceo_graph import ceo_graph
from state.state import HierarchicalState


st.set_page_config(page_title="Launch Team Control Room", page_icon="✦", layout="wide")

NODE_META = {
    "decompose": ("CEO", "Directing the launch brief", "#ef8354"),
    "marketing": ("Marketing Manager", "Delegating the market lane", "#2a9d8f"),
    "finance": ("Finance Manager", "Delegating the money lane", "#3a86ff"),
    "aggregate": ("CEO", "Synthesizing the executive report", "#ef8354"),
}


def initial_state(request: str) -> HierarchicalState:
    return {
        "user_request": request,
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


def serialise(value: Any) -> Any:
    if hasattr(value, "model_dump"):
        return value.model_dump()
    if isinstance(value, dict):
        return {key: serialise(item) for key, item in value.items()}
    if isinstance(value, list):
        return [serialise(item) for item in value]
    return value


def stream_run(request: str) -> Iterator[tuple[str, dict[str, Any]]]:
    """Yield graph updates, including nested manager nodes when supported."""
    stream = ceo_graph.stream(initial_state(request), stream_mode="updates", subgraphs=True)
    for event in stream:
        if isinstance(event, tuple) and len(event) == 2:
            namespace, update = event
            yield ".".join(namespace) if namespace else "CEO", update
        else:
            yield "CEO", event


def node_name(path: str, update: dict[str, Any]) -> str:
    return next(iter(update), path.split(".")[-1])


def render_update(path: str, update: dict[str, Any], activity: Any, graph_state: dict[str, Any]) -> None:
    name = node_name(path, update)
    label, description, color = NODE_META.get(name, (name.replace("_", " ").title(), "Working", "#6c757d"))
    payload = update.get(name, update)
    if isinstance(payload, dict):
        graph_state.update(serialise(payload))
    timestamp = datetime.now().strftime("%H:%M:%S")
    activity_log = graph_state.setdefault("_activity_log", [])
    activity_log.append(
        f'<div class="activity-row"><span class="activity-dot" style="background:{color}"></span>'
        f'<div><strong>{label}</strong><span class="activity-time">{timestamp}</span>'
        f'<div class="activity-copy">{description} <em>· {name}</em></div></div></div>'
    )
    activity.markdown("".join(activity_log), unsafe_allow_html=True)


def render_list(items: list[str]) -> None:
    for item in items:
        st.markdown(f"- {item}")


def render_reports(state: dict[str, Any]) -> None:
    final = state.get("final_response")
    marketing = state.get("marketing_report")
    finance = state.get("finance_report")
    research = state.get("research_output")
    content = state.get("content_output")
    cost = state.get("cost_output")
    pricing = state.get("pricing_output")

    st.markdown('<div class="section-kicker">DELIVERABLES</div>', unsafe_allow_html=True)
    if not final:
        st.markdown("## The room is ready")
        st.write("Submit a launch brief to watch the CEO delegate work and receive the executive readout here.")
        return

    st.markdown(f"## {final.get('executive_summary', 'Executive report')}")
    st.info(final.get("strategic_analysis", ""))
    report_tabs = st.tabs(["Executive", "Marketing", "Finance", "Specialists"])
    with report_tabs[0]:
        st.markdown("### Recommended next moves")
        render_list(final.get("action_items", []))
    with report_tabs[1]:
        if marketing:
            st.markdown("### Marketing manager synthesis")
            st.write(marketing.get("summary", ""))
            st.markdown("**Positioning**")
            st.write(marketing.get("market_positioning", ""))
            st.markdown("**Channels**")
            render_list(marketing.get("recommended_channels", []))
    with report_tabs[2]:
        if finance:
            st.markdown("### Finance manager synthesis")
            st.write(finance.get("summary", ""))
            st.markdown("**Cost outlook**")
            st.write(finance.get("cost_overview", ""))
            st.markdown("**Pricing outlook**")
            st.write(finance.get("pricing_overview", ""))
    with report_tabs[3]:
        left, right = st.columns(2)
        with left:
            if research:
                st.markdown("### Research")
                st.write(research.get("summary", ""))
                st.markdown("**Opportunities**")
                render_list(research.get("opportunities", []))
            if content:
                st.markdown("### Content")
                st.write(content.get("headline", ""))
                st.write(content.get("core_messaging", ""))
        with right:
            if cost:
                st.markdown("### Cost")
                st.metric("Setup estimate", cost.get("estimated_setup_cost", "Not available"))
                st.write(cost.get("break_even_timeline", ""))
            if pricing:
                st.markdown("### Pricing")
                st.write(pricing.get("pricing_model", ""))
                render_list(pricing.get("pricing_tiers", []))


st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Manrope:wght@400;600;700;800&display=swap');
    :root { --ink:#17212b; --muted:#68737d; --paper:#f7f4ee; --line:#dedbd2; --coral:#ef8354; }
    .stApp { background:var(--paper); color:var(--ink); font-family:'Manrope',sans-serif; }
    [data-testid="stSidebar"] { background:#17212b; }
    [data-testid="stSidebar"] * { color:#f7f4ee !important; }
    h1,h2,h3 { font-family:'Manrope',sans-serif; letter-spacing:0; }
    h1 { font-size:clamp(2rem,4vw,4rem); line-height:1; font-weight:800; }
    .section-kicker { color:var(--coral); font:500 0.72rem 'DM Mono',monospace; letter-spacing:0.08em; margin:1.5rem 0 0.5rem; }
    .activity-row { display:flex; gap:0.8rem; align-items:flex-start; padding:0.75rem 0; border-bottom:1px solid var(--line); }
    .activity-dot { width:9px; height:9px; border-radius:50%; display:block; margin-top:0.35rem; flex:none; }
    .activity-time { color:var(--muted); font:0.7rem 'DM Mono',monospace; margin-left:0.7rem; }
    .activity-copy { color:var(--muted); font-size:0.78rem; margin-top:0.2rem; }
    .activity-copy em { font-family:'DM Mono',monospace; font-style:normal; color:var(--coral); }
    div[data-testid="stMetric"] { background:#fffdf9; border:1px solid var(--line); padding:0.7rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown("# ✦ Launch Team")
    st.caption("A live control room for strategic collaboration")
    st.markdown("### Launch brief")
    request = st.text_area(
        "What should the team launch?",
        value="Launch an AI-powered smart productivity and time-management assistant for engineering teams.",
        height=130,
        label_visibility="collapsed",
    )
    run_clicked = st.button("Run the launch team", type="primary", use_container_width=True)
    st.markdown("---")
    st.caption("ARCHITECTURE")
    st.markdown("CEO → Marketing + Finance → Specialists")

st.markdown('<div class="section-kicker">AI PRODUCT LAUNCH TEAM / LIVE CONTROL ROOM</div>', unsafe_allow_html=True)
st.title("Make the launch legible.")
st.write("Watch strategy move from brief to delegation to decision-ready output.")

overview, activity_panel = st.columns([1.55, 1], gap="large")
with overview:
    st.markdown('<div class="section-kicker">COLLABORATION MAP</div>', unsafe_allow_html=True)
    st.graphviz_chart(
        """digraph { graph [bgcolor="transparent", rankdir=TB, nodesep=.45, ranksep=.65];
        node [shape=box, style="rounded,filled", fontname="Manrope", color="#dedbd2", fontcolor="#17212b", margin=".18,.12"];
        CEO [label="CEO", fillcolor="#ef8354"]; Marketing [label="Marketing Manager", fillcolor="#bce5dc"];
        Finance [label="Finance Manager", fillcolor="#c9dcff"]; Research [label="Research", fillcolor="#fffdf9"];
        Content [label="Content", fillcolor="#fffdf9"]; Cost [label="Cost", fillcolor="#fffdf9"]; Pricing [label="Pricing", fillcolor="#fffdf9"];
        CEO -> {Marketing Finance}; Marketing -> {Research Content}; Finance -> {Cost Pricing}; }""",
        use_container_width=True,
    )
with activity_panel:
    st.markdown('<div class="section-kicker">LIVE ACTIVITY</div>', unsafe_allow_html=True)
    activity = st.empty()
    if run_clicked:
        activity.markdown("Connecting to the launch team…")
        current_state: dict[str, Any] = {}
        try:
            for path, update in stream_run(request):
                render_update(path, update, activity, current_state)
            st.session_state["launch_state"] = current_state
            st.success("The executive report is ready.")
        except Exception as exc:
            st.error(f"Run failed: {exc}")

st.markdown("---")
render_reports(st.session_state.get("launch_state", {}))