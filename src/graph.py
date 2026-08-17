from langgraph.graph import StateGraph, START, END

from graph_state import AssessmentState

from graph_nodes import (
    extract_documents,
    identify_product,
    build_context,
    extract_source_1,
    extract_source_2,
    normalize_source_fields,
    canonicalize_source_fields,
    reconcile_sources,
    build_ground_truth,
    create_assessment,
    generate_draft,
)

#building actual langgraph

def build_assessment_graph():
    """
    Build the complete assessment LangGraph.
    """

    graph = StateGraph(AssessmentState)

    #nodes

    graph.add_node(
        "identify_product",
        identify_product,
    )

    graph.add_node(
        "build_context",
        build_context,
    )

    graph.add_node(
        "extract_source_1",
        extract_source_1,
    )

    graph.add_node(
        "extract_source_2",
        extract_source_2,
    )

    graph.add_node(
        "normalize_fields",
        normalize_source_fields,
    )

    graph.add_node(
        "canonicalize_fields",
        canonicalize_source_fields,
    )

    graph.add_node(
        "reconcile",
        reconcile_sources,
    )

    graph.add_node(
        "ground_truth",
        build_ground_truth,
    )

    graph.add_node(
        "assessment",
        create_assessment,
    )

    graph.add_node(
        "draft",
        generate_draft,
    )

    graph.add_node(
    "extract_documents",
    extract_documents,
)

    #edges
    graph.add_edge(
    START,
    "extract_documents",
)

    graph.add_edge(
    "extract_documents",
    "identify_product",
)

    graph.add_edge(
    "identify_product",
    "build_context",
)

    graph.add_edge(
        "build_context",
        "extract_source_1",
    )

    graph.add_edge(
        "build_context",
        "extract_source_2",
    )

    # Both extraction branches must finish
    # before normalization.

    graph.add_edge(
        "extract_source_1",
        "normalize_fields",
    )

    graph.add_edge(
        "extract_source_2",
        "normalize_fields",
    )

    graph.add_edge(
        "normalize_fields",
        "canonicalize_fields",
    )

    graph.add_edge(
        "canonicalize_fields",
        "reconcile",
    )

    graph.add_edge(
        "reconcile",
        "ground_truth",
    )

    graph.add_edge(
        "ground_truth",
        "assessment",
    )

    graph.add_edge(
        "assessment",
        "draft",
    )

    graph.add_edge(
        "draft",
        END,
    )

    return graph.compile()