from pathlib import Path

from graph import build_assessment_graph


def run_assessment(
    source_1: str | Path,
    source_2: str | Path,
):
    """
    Run the complete assessment pipeline.

    Returns the final LangGraph state.
    """

    source_1 = Path(source_1)
    source_2 = Path(source_2)

    if not source_1.exists():
        raise FileNotFoundError(
            f"Source 1 not found: {source_1}"
        )

    if not source_2.exists():
        raise FileNotFoundError(
            f"Source 2 not found: {source_2}"
        )

    graph = build_assessment_graph()

    result = graph.invoke(
        {
            "source_documents": [
                str(source_1),
                str(source_2),
            ]
        }
    )

    return result