import sys
from pathlib import Path

import ocrmypdf
from PyPDF2 import PdfReader


def print_stderr(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


if __name__ == "__main__":

    input = Path("test2.pdf")
    output = "output" / input

    if output.exists():
        print_stderr(f"'{output}' has already been processed")
    else:
        ocrmypdf.ocr(input, output, skip_text=True)

    pdf = PdfReader(output)

    for page in pdf.pages:
        print(page.extract_text())
