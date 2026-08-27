import logging
from datetime import datetime, timezone
from typing import Any, Dict, Iterable

from state.schemas import AgentHandoff

logger = logging.getLogger("agent_handoffs")


def record_handoff(from_agent: str, to_agent: str, reason: str) -> Dict[str, Any]:
    """Build a reducer-ready state update and emit a searchable audit log."""
    handoff = AgentHandoff(
        from_agent=from_agent,
        to_agent=to_agent,
        reason=reason,
        timestamp=datetime.now(timezone.utc),
    )
    logger.info(
        "Agent handoff: %s -> %s | reason=%s | timestamp=%s",
        handoff.from_agent,
        handoff.to_agent,
        handoff.reason,
        handoff.timestamp.isoformat(),
        extra={"handoff": handoff.model_dump(mode="json")},
    )
    return {"current_agent": to_agent, "handoff_history": [handoff]}


def record_handoffs(*handoffs: tuple[str, str, str]) -> Dict[str, Any]:
    """Record several same-step delegations without overwriting the reducer list."""
    records = [record_handoff(*handoff)["handoff_history"][0] for handoff in handoffs]
    return {
        "current_agent": records[-1].to_agent,
        "handoff_history": records,
    }