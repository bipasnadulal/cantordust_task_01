import json
from pathlib import Path


def _serialize(value):
    """
    Convert Pydantic models / nested objects into JSON-compatible data.
    """

    if hasattr(value, "model_dump"):
        return value.model_dump()

    if isinstance(value, dict):
        return {
            key: _serialize(item)
            for key, item in value.items()
        }

    if isinstance(value, list):
        return [_serialize(item) for item in value]

    return value


def save_json(result: dict, output_path: str | Path):
    """
    Save the complete assessment result as JSON.
    """

    output_path = Path(output_path)
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    data = _serialize(result)

    with output_path.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            data,
            file,
            indent=2,
            ensure_ascii=False,
        )


def build_report(result: dict) -> str:
    """
    Build a human-readable assessment report.
    """

    assessment = result["assessment"]

    if hasattr(assessment, "model_dump"):
        assessment = assessment.model_dump()

    product_model = result.get(
        "product_model",
        "Unknown",
    )

    lines = [
        "=" * 60,
        "INVERTER DATASHEET ASSESSMENT",
        "=" * 60,
        "",
        f"Target Model: {product_model}",
        "",
    ]

    summary = assessment.get(
    "summary",
    "",
)

    lines.extend(
    [
        "-" * 60,
        "SUMMARY",
        "-" * 60,
        "",
        summary,
    ]
)

    coverage = assessment.get("checklist_coverage", [])
    lines.extend([
        "",
        "-" * 60,
        "CHECKLIST COVERAGE",
        "-" * 60,
        "",
    ])
    for item in coverage:
        category = item.get("category", "unknown")
        count = item.get("field_count", 0)
        note = item.get("note", "")
        status = "ADDRESSED" if item.get("present") else "GAP / FOLLOW-UP"
        lines.append(f"{category}: {status} ({count} evidence field(s))")
        if note:
            lines.append(f"  Note: {note}")

    overall_status = assessment.get(
        "overall_status"
    )

    if overall_status:
        lines.extend(
            [
                "",
                f"Overall Status: {overall_status}",
            ]
        )

    review_items = assessment.get(
        "review_items",
        [],
    )

    lines.extend(
        [
            "",
            "-" * 60,
            "REVIEW ITEMS",
            "-" * 60,
            "",
        ]
    )

    if not review_items:
        lines.append(
            "No review items."
        )

    for index, item in enumerate(
        review_items,
        start=1,
    ):
        lines.append(
            f"[{index}]"
        )

        if isinstance(item, dict):
            for key, value in item.items():
                lines.append(
                    f"{key}: {value}"
                )
        else:
            lines.append(str(item))

        lines.append("")

    lines.append("=" * 60)

    return "\n".join(lines)


def save_report(
    result: dict,
    output_path: str | Path,
):
    """
    Save a human-readable assessment report.
    """

    output_path = Path(output_path)
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    report = build_report(result)

    output_path.write_text(
        report,
        encoding="utf-8",
    )