from pathlib import Path

from pdf_extractor import extract_pdf


INPUT_DIR = Path("data/input")


def main():
    pdf_files = list(INPUT_DIR.glob("*.pdf"))

    if not pdf_files:
        print("No PDF files found in data/input/")
        return

    for pdf_path in pdf_files:

        print("\n" + "=" * 80)
        print(f"FILE: {pdf_path.name}")
        print("=" * 80)

        result = extract_pdf(pdf_path)

        print(f"Total pages: {result['page_count']}")

        for page in result["pages"]:

            print("\n" + "-" * 80)
            print(f"PAGE {page['page_number']}")
            print("-" * 80)

            print("\n--- TEXT PREVIEW ---")

            text = page["text"]

            print(text[:1500])

            print("\n--- TABLES ---")

            if not page["tables"]:
                print("No tables detected.")
                continue

            for table_index, table in enumerate(
                page["tables"],
                start=1,
            ):

                print(f"\nTABLE {table_index}")

                for row in table:
                    print(row)


if __name__ == "__main__":
    main()