"""Extract the SOTA train_gpt.py LZMA self-extracting wrapper into readable source.

The submitted SOTA train_gpt.py is a ~16KB self-extracting wrapper of the form:

    import lzma as L, base64 as B
    exec(L.decompress(B.b85decode("<big blob>"),
                      format=L.FORMAT_RAW,
                      filters=[{"id": L.FILTER_LZMA2}]))

This script mirrors that decode/decompress step but writes the raw Python source
to train_gpt_extracted.py on disk instead of executing it, so the full source can
be read and understood.

Usage:
    python tools/extract_sota.py

Inputs:
    train_gpt.py (repo root; must be the self-extracting wrapper)

Outputs:
    train_gpt_extracted.py (repo root; raw Python source of the SOTA)
"""
import base64
import lzma
import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
SRC = REPO_ROOT / "train_gpt.py"
DST = REPO_ROOT / "train_gpt_extracted.py"


def main() -> int:
    if not SRC.exists():
        print(f"ERROR: {SRC} does not exist", file=sys.stderr)
        return 1

    text = SRC.read_text(encoding="utf-8")
    match = re.search(r'b85decode\("([^"]+)"\)', text)
    if not match:
        print(
            "ERROR: could not find base85 blob in train_gpt.py.\n"
            "       Is this really the LZMA self-extracting wrapper?",
            file=sys.stderr,
        )
        return 2

    blob_b85 = match.group(1).encode("ascii")
    compressed = base64.b85decode(blob_b85)
    raw = lzma.decompress(
        compressed,
        format=lzma.FORMAT_RAW,
        filters=[{"id": lzma.FILTER_LZMA2}],
    )
    DST.write_bytes(raw)

    source = raw.decode("utf-8")
    line_count = source.count("\n") + (0 if source.endswith("\n") else 1)
    print(f"Extracted {len(raw):,} bytes to {DST.relative_to(REPO_ROOT)}")
    print(f"Line count: {line_count:,}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
