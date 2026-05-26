import argparse
from pathlib import Path

from diagram_rules import build_html_preview, build_mermaid_flowchart
from extract_pdf_text import extract_pdf_text


def safe_output_name(pdf_path: Path) -> str:
    name = pdf_path.stem
    keep = [char if char.isalnum() else "_" for char in name]
    return "".join(keep).strip("_").lower()


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a starter Mermaid flowchart from a client PDF.")
    parser.add_argument("--pdf", required=True, help="Path to the client PDF file")
    parser.add_argument("--max-pages", type=int, default=8, help="Number of PDF pages to read")
    parser.add_argument("--out", default="outputs", help="Output folder")
    args = parser.parse_args()

    pdf_path = Path(args.pdf)
    output_dir = Path(args.out)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Reading PDF: {pdf_path}")
    pdf_text = extract_pdf_text(pdf_path, max_pages=args.max_pages)

    if not pdf_text:
        print("No text was extracted. This PDF may be scanned images, so OCR will be needed later.")
        return

    mermaid_code = build_mermaid_flowchart(pdf_text, pdf_path.name)
    output_name = safe_output_name(pdf_path)

    text_file = output_dir / f"{output_name}.txt"
    mermaid_file = output_dir / f"{output_name}.mmd"
    html_file = output_dir / f"{output_name}.html"

    text_file.write_text(pdf_text, encoding="utf-8")
    mermaid_file.write_text(mermaid_code, encoding="utf-8")
    html_file.write_text(build_html_preview(pdf_path.stem, mermaid_code), encoding="utf-8")

    print(f"Saved extracted text: {text_file}")
    print(f"Saved Mermaid diagram: {mermaid_file}")
    print(f"Saved HTML preview: {html_file}")


if __name__ == "__main__":
    main()

