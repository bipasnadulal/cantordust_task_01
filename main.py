import argparse
from pathlib import Path

from runner import run_assessment
from output import save_json, save_report


def main():
    parser = argparse.ArgumentParser(
        description="Inverter Datasheet Assessment"
    )

    parser.add_argument(
        "source_1",
        help="Path to source 1 PDF",
    )

    parser.add_argument(
        "source_2",
        help="Path to source 2 PDF",
    )

    parser.add_argument(
        "--output-dir",
        default="output",
        help="Directory for generated results",
    )

    args = parser.parse_args()

    result = run_assessment(
        args.source_1,
        args.source_2,
    )

    output_dir = Path(args.output_dir)
    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    json_path = (
        output_dir / "assessment.json"
    )

    report_path = (
        output_dir / "assessment.txt"
    )

    draft_path = (
        output_dir / "draft.md"
    )

    save_json(
        result,
        json_path,
    )

    save_report(
        result,
        report_path,
    )

    draft_path.write_text(
        result.get("draft", ""),
        encoding="utf-8",
    )

    print()
    print("=" * 60)
    print("ASSESSMENT COMPLETE")
    print("=" * 60)
    print()
    print(f"JSON report:   {json_path}")
    print(f"Text report:   {report_path}")
    print(f"Client draft:  {draft_path}")
    print()


if __name__ == "__main__":
    main()