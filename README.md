# AI Product Launch Team

A hierarchical multi-agent simulation of a corporate product launch workflow, built with **LangGraph** and **Pydantic**. A CEO/Supervisor layer orchestrates a team of specialized agents covering marketing, finance, pricing, and research, with a live dashboard visualizing the agent hierarchy and task flow in real time.

## Overview

This project models how a company's leadership and functional teams collaborate to plan and execute a product launch. Instead of a single monolithic agent, tasks are delegated across a hierarchy of specialized agents:

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

A live dashboard (`dashboard.py` / `index.html`) renders this hierarchy and shows each agent's status as the workflow runs.

## Stack

- **Python** (LangGraph + Pydantic for the multi-agent supervisor system)
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
├── config/           # Configuration for models, routing, and agent settings
├── docs/             # Project documentation
├── graphs/           # LangGraph graph definitions (state machine / workflow)
├── state/            # Shared state schema passed between agents
├── tests/            # Test suite
├── tools/            # Tools/functions available to agents
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
4. Each agent processes its task via a shared **Model** configuration and returns results/state updates through the LangGraph state graph.
5. The supervisor aggregates results, resolves dependencies, and determines the next step — looping until the launch plan is complete.
6. The dashboard subscribes to state updates and renders live progress across the hierarchy.

## Author

**Hailemichael Tesfaye Mekuria**
[LinkedIn](https://www.linkedin.com/in/hailemichael-tesfaye-2b7114401/) · [GitHub](https://github.com/hailemichaeltesfsye-hue)
