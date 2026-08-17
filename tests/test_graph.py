from graph import build_assessment_graph


def test_graph_builds():

    graph = build_assessment_graph()

    assert graph is not None

def test_graph_structure():

    graph = build_assessment_graph()

    print(graph.get_graph().draw_ascii())