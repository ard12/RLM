#!/usr/bin/env python3

import argparse
import json
import subprocess
import textwrap


START_MARKER = "__RLM_PDF_OUTPUT_START__"
END_MARKER = "__RLM_PDF_OUTPUT_END__"
HELPER_OK_MARKER = "__PDF_HELPER_OK__"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extract text from a PDF on macOS using PDFKit via osascript."
    )
    parser.add_argument("pdf_path", help="Path to the PDF file")
    parser.add_argument(
        "--search",
        action="append",
        default=[],
        help="Search term to narrow output to matching pages",
    )
    parser.add_argument(
        "--window",
        type=int,
        default=1,
        help="Number of neighboring pages to include around each match",
    )
    parser.add_argument(
        "--quote-search",
        action="append",
        default=[],
        help="Search term to return matching paragraph/quote snippets instead of full pages",
    )
    return parser.parse_args()


def build_jxa(pdf_path: str, search_terms: list[str], window: int) -> str:
    return textwrap.dedent(
        """
        ObjC.import("Foundation")
        ObjC.import("PDFKit")

        const path = PDF_PATH
        const terms = SEARCH_TERMS
        const windowSize = WINDOW_SIZE
        const url = $.NSURL.fileURLWithPath(path)
        const doc = $.PDFDocument.alloc.initWithURL(url)

        if (!doc) {
          throw new Error("failed to open pdf")
        }

        const pages = []
        for (let i = 0; i < doc.pageCount; i++) {
          const page = doc.pageAtIndex(i)
          const text = ObjC.unwrap(page.string) || ""
          pages.push({ page: i + 1, text })
        }

        let selected = pages
        if (terms.length > 0) {
          const keep = new Set()
          for (let i = 0; i < pages.length; i++) {
            const lower = pages[i].text.toLowerCase()
            const matched = terms.some((term) => lower.includes(term.toLowerCase()))
            if (matched) {
              for (let j = Math.max(0, i - windowSize); j <= Math.min(pages.length - 1, i + windowSize); j++) {
                keep.add(j)
              }
            }
          }
          selected = Array.from(keep).sort((a, b) => a - b).map((index) => pages[index])
        }

        const payload = JSON.stringify(selected)
        console.log(START_MARKER)
        console.log(payload)
        console.log(END_MARKER)
        """
    ).replace("PDF_PATH", json.dumps(pdf_path)).replace(
        "SEARCH_TERMS", json.dumps(search_terms)
    ).replace("WINDOW_SIZE", str(window)).replace(
        "START_MARKER", json.dumps(START_MARKER)
    ).replace("END_MARKER", json.dumps(END_MARKER))


def extract_pages(pdf_path: str, search_terms: list[str], window: int) -> list[dict]:
    jxa = build_jxa(pdf_path, search_terms, window)
    result = subprocess.run(
        ["osascript", "-l", "JavaScript"],
        input=jxa,
        text=True,
        capture_output=True,
        check=True,
    )

    raw_output = "\n".join(part for part in [result.stdout, result.stderr] if part)
    start = raw_output.find(START_MARKER)
    end = raw_output.find(END_MARKER)
    if start == -1 or end == -1 or end <= start:
        raise RuntimeError("Could not parse PDF extraction output")

    payload_block = raw_output[start + len(START_MARKER) : end]
    json_start = payload_block.find("[{")
    json_end = payload_block.rfind("]")
    if json_start == -1 or json_end == -1 or json_end < json_start:
        raise RuntimeError("Could not locate JSON payload in PDF extraction output")

    payload = payload_block[json_start : json_end + 1]
    return json.loads(payload)


def format_pages(pages: list[dict]) -> str:
    chunks = []
    for page in pages:
        chunks.append(f"=== PAGE {page['page']} ===\n{page['text']}")
    return "\n\n".join(chunks)


def format_quote_matches(pages: list[dict], quote_terms: list[str]) -> str:
    matches = []
    normalized_terms = [term.lower() for term in quote_terms]

    for page in pages:
        paragraphs = page["text"].split("\n\n")
        for paragraph in paragraphs:
            compact = " ".join(line.strip() for line in paragraph.splitlines() if line.strip())
            if not compact:
                continue

            lower = compact.lower()
            if any(term in lower for term in normalized_terms):
                matches.append(f"=== QUOTE MATCH PAGE {page['page']} ===\n{compact}")

    if not matches:
        return ""

    return "\n\n".join(matches)


def main() -> None:
    args = parse_args()
    pages = extract_pages(args.pdf_path, args.search, args.window)
    print(HELPER_OK_MARKER)
    if args.quote_search:
        print(format_quote_matches(pages, args.quote_search))
    else:
        print(format_pages(pages))


if __name__ == "__main__":
    main()
