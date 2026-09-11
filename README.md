# AI Product Launch Team

An autonomous multi-agent simulation of a corporate product launch workflow, built with **LangGraph** and **Pydantic**. The project implements two agent-coordination architectures side by side — a **peer-to-peer (P2P)** agent network and a **hierarchical supervisor** system — plus a live dashboard that visualizes the agent hierarchy and task flow in real time.

## Overview

The system models how a company's leadership and functional teams collaborate to plan and execute a product launch. Two coordination styles are implemented:

- **Peer-to-peer (P2P)** — agents hand off tasks directly to one another via `graphs/p2p_graph.py` and `state/p2p_state.py`
- **Hierarchical / Supervisor** — a top-down structure where a supervisor routes work down through manager agents to specialists, visualized live on the dashboard

### Agents (`agents/`)

- **Supervisor** (`supervisor.py`) — receives the high-level goal, breaks it into subtasks, and routes them to the right specialist agent
- **CEO** (`ceo.py`) — top-level decision-making and final sign-off on strategy
- **Marketing Manager** (`marketing_manager.py`) — coordinates marketing strategy and delegates to the content agent
- **Content** (`content.py`) — produces launch messaging and content
- **Finance Manager** (`finance_manager.py`) — coordinates financial planning and delegates to finance/cost/pricing agents
- **Finance** (`finance.py`) / **Financial** (`financial.py`) — financial planning and analysis
- **Cost** (`cost.py`) — cost estimation and budget analysis
- **Pricing** (`pricing.py`) — pricing strategy for the launch
- **Research** (`research.py`) — market/competitive research to inform decisions
- **Model** (`model.py`) — shared LLM/model configuration used across agents

A live dashboard (`dashboard.py` / `index.html`) renders the hierarchy and shows each agent's status as the workflow runs. An architecture diagram is available at `docs/architecture.svg`.

## Stack

- **Python** (LangGraph + Pydantic for agent orchestration and structured state)
- **HTML/CSS** — live dashboard front end
- **uv** — Python package and environment management (`pyproject.toml`, `uv.lock`)

## Project Structure

```
ai-product-launch-team/
├── agents/
│   ├── supervisor.py         # Orchestrates and routes tasks to specialist agents
│   ├── ceo.py                 # Top-level decision-making agent
│   ├── marketing_manager.py   # Marketing team lead
│   ├── content.py             # Content/messaging agent
│   ├── finance_manager.py     # Finance team lead
│   ├── finance.py             # Finance agent
│   ├── financial.py           # Financial analysis agent
│   ├── cost.py                # Cost estimation agent
│   ├── pricing.py             # Pricing strategy agent
│   ├── research.py            # Market research agent
│   └── model.py               # Shared LLM/model config
├── config/
│   ├── settings.py            # App/environment settings
│   └── logging_config.py      # Logging setup
├── docs/
│   └── architecture.svg       # System architecture diagram
├── graphs/
│   ├── supervisor_graph.py    # Top-level supervisor LangGraph
│   ├── ceo_graph.py           # CEO decision subgraph
│   ├── marketing_subgraph.py  # Marketing team subgraph
│   ├── finance_subgraph.py    # Finance team subgraph
│   └── p2p_graph.py           # Peer-to-peer agent network graph
├── state/
│   ├── state.py                # Core shared state schema
│   ├── schemas.py              # Pydantic models for agent I/O
│   ├── handoffs.py             # Agent-to-agent handoff logic
│   └── p2p_state.py            # State schema for the P2P graph
├── tools/
│   └── research.py             # Research tool used by agents
├── tests/
│   ├── test_agents.py
│   ├── test_graph.py
│   ├── test_schemas.py
│   ├── test_tools.py
│   ├── test_hierarchical_agents.py
│   ├── test_hierarchical_graph.py
│   └── test_hierarchical_schemas.py
├── app.py            # Application entry point
├── main.py           # Core orchestration logic
├── dashboard.py      # Live dashboard backend
├── index.html        # Dashboard front end
├── style.css         # Dashboard styling
├── AGENTS.md         # Agent roles and responsibilities
├── .env.example      # Example environment variables
├── pyproject.toml    # Project metadata and dependencies (uv)
└── uv.lock           # Locked dependency versions
```

## Getting Started

### Prerequisites

- Python (version pinned in `.python-version`)
- [uv](https://github.com/astral-sh/uv) installed
- API keys for your chosen LLM provider

### Installation

```bash
git clone https://github.com/hailemichaeltesfsye-hue/ai-product-launch-team.git
cd ai-product-launch-team
uv sync
```

### Environment Variables

Copy the example file and fill in your keys:

```bash
cp .env.example .env
```

### Running

Run the core multi-agent workflow:

```bash
uv run main.py
```

Launch the live hierarchical dashboard:

```bash
uv run dashboard.py
```

Then open `index.html` (or the URL printed in the console) to watch the agent hierarchy work through a launch scenario in real time.

### Tests

```bash
uv run pytest
```

## How It Works

1. A launch goal is submitted to the **Supervisor** agent.
2. The supervisor decomposes the goal and routes subtasks to the **CEO**, **Marketing Manager**, or **Finance Manager**, depending on the type of decision needed.
3. Manager agents delegate further: Marketing Manager to **Content**; Finance Manager to **Finance**, **Financial**, **Cost**, and **Pricing**. The **Research** agent can be called on to inform any of these decisions.
4. Handoffs between agents are tracked via `state/handoffs.py`, with shared state validated against Pydantic schemas in `state/schemas.py`.
5. Each agent processes its task via a shared **Model** configuration and returns results/state updates through the LangGraph state graph.
6. The supervisor aggregates results, resolves dependencies, and determines the next step — looping until the launch plan is complete.
7. The dashboard subscribes to state updates and renders live progress across the hierarchy.

## Author

**Hailemichael Tesfaye Mekuria**
[LinkedIn](https://www.linkedin.com/in/hailemichael-tesfaye-2b7114401/) · [GitHub](https://github.com/hailemichaeltesfsye-hue)
