from output import build_report, save_json, save_report


def test_build_report(tmp_path):

    result = {
        "product_model": "SUN-5K-G06P3-EU-AM2",
        "assessment": {
            "overall_status": "AGREES",
            "summary": (
                "Fields compared: 5\n"
                "Agreements: 5\n"
                "Conflicts: 0"
            ),
            "review_items": [],
        },
    }

    report = build_report(result)

    assert "SUN-5K-G06P3-EU-AM2" in report
    assert "AGREES" in report
    assert "No review items." in report

    json_path = tmp_path / "assessment.json"
    report_path = tmp_path / "assessment.txt"

    save_json(result, json_path)
    save_report(result, report_path)

    assert json_path.exists()
    assert report_path.exists()