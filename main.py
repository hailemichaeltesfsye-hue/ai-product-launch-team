import logging
from config.logging_config import setup_logging
from graphs.launch_graph import launch_graph
from state.state import LaunchGraphState

setup_logging()
logger = logging.getLogger(__name__)


def main():
    logger.info("Starting AI Product Launch Team initialization test...")

    # Mock initial graph state
    initial_state: LaunchGraphState = {
        "product_idea": "An offline-first encrypted notes application.",
        "product_brief": None,
        "tech_specs": None,
        "marketing_plan": None,
        "final_package": None,
        "errors": [],
    }

    logger.info("Invoking LangGraph orchestrator...")
    result = launch_graph.invoke(initial_state)

    logger.info("Graph processing completed successfully.")
    print("Final state outcome:", result)


if __name__ == "__main__":
    main()
