"""Optional reconstruction from CTblLib's release and the seven original MOC PDFs.

Usage: python rebuild.py path/to/ctbllib-1.3.11.tar.gz directory/of/PDFs
The PDF files must retain their published names. PyMuPDF is needed only here.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import tarfile

from verify import EXPECTED, MINUS, PLUS, ROOT, SP, require, verify


ARCHIVE = "f201e9da571c681a7bbfb1e4683bdb2c80a23b005099ed0453521f59cb443434"
ORDINARY_FILES = {
    "ctosymp1.tbl": "461519e33cb31b2bc46f554b09f283f0afb7125fd805840d79bfc614fce75b6f",
    "ctoorth3.tbl": "736b8f34211dd8a20c51312015fa72c1bb0a4931db19b317ea436ac0e9644626",
}
PDFS = {
    (SP, 5): "1c886ad45671812c7c1cd3b9b7032c7a8057ca091673488c76ffac8c865ff5f0",
    (SP, 7): "cdb7f8814c8a3fed2416ac994fa246d32b9dc875c0d61b0ad4439b3400b72708",
    (SP, 11): "44a7cd8da9136d08f2988dc72e370db129cbace6c27dc7adfac222c858f973b3",
    (SP, 17): "1da32315cddc39cea3ef162462e23dc48b29fde9651b48772a658989b5f5b03e",
    (SP, 31): "935757534974ac96c14b2a96c36e1f8b1772d8cdeab2fe3671a24a76ab617204",
    (PLUS, 3): "f0fde410061164fea325b9f7cf4893edb6197d0713eb675eeb7bbe0f6be4ce67",
    (MINUS, 3): "6d2e24c110cfdc780f8f1d700e0407f3a38ba6999c809375c6025d8b35b07d37",
}


def take_list(text):
    start, depth = text.index("["), 0
    for i in range(start, len(text)):
        depth += (text[i] == "[") - (text[i] == "]")
        if depth == 0:
            return text[start:i+1], text[i+1:]
    raise ValueError("Unterminated CTblLib list")


def ordinary_triples(source, group):
    rest = source.split(f'MOT("{group}",', 1)[1]
    for _ in range(3):  # header, centralizer sizes, power maps
        _, rest = take_list(rest)
    table, _ = take_list(rest)
    rest = "".join(table[1:-1].split())
    rows = []
    cols = [0, 2, 5] if group == SP else [0, 1, 3]
    while rest:
        record, rest = take_list(rest)
        rest = rest.removeprefix(",")
        ref = re.fullmatch(r"\[(GALOIS|TENSOR),\[(\d+),(\d+)\]\]", record)
        if ref:
            kind, a, b = ref.groups()
            row = rows[int(a)-1]
            if kind == "TENSOR":
                row = [x*y for x, y in zip(row, rows[int(b)-1], strict=True)]
            # Galois acts trivially on rational values at order one or two.
        else:
            entries = record[1:-1].split(",")
            row = [int(entries[j]) for j in cols]
        rows.append(row)
    return rows


def read_decomposition(path, digest, nord, nmod):
    import pymupdf

    require(hashlib.sha256(path.read_bytes()).hexdigest() == digest, f"Wrong source: {path.name}")
    rows = [{} for _ in range(nord)]

    def insert(i, j, value):
        require(1 <= i <= nord and 1 <= j <= nmod, "Decomposition index outside table")
        require(j not in rows[i-1], "Duplicate matrix entry")
        rows[i-1][j] = value

    with pymupdf.open(path) as document:
        for page in document:
            lines = page.get_text().splitlines()
            for i, line in enumerate(lines):
                single = re.search(r"= χ(\d+), ϕ(\d+)$", line)
                if single:
                    insert(int(single[1]), int(single[2]), 1)
                if not re.fullmatch(r"\(?Block\s*\d+:\)?", line):
                    continue
                pos = i+1
                cols = []
                while pos < len(lines) and re.fullmatch(r"ϕ\d+", lines[pos]):
                    cols.append(int(lines[pos][1:]))
                    pos += 1
                require(cols, "Missing block header")
                while pos < len(lines):
                    row = re.fullmatch(r"\d+\s*= χ(\d+)", lines[pos])
                    if not row:
                        break
                    pos += 1
                    for col, cell in zip(cols, lines[pos:pos+len(cols)], strict=True):
                        insert(int(row[1]), col, 0 if cell == "." else int(cell))
                    pos += len(cols)
    return [[[j, a] for j, a in sorted(row.items()) if a] for row in rows]


def rebuild(archive, directory):
    require(hashlib.sha256(archive.read_bytes()).hexdigest() == ARCHIVE, "Wrong release archive")
    sources = {}
    with tarfile.open(archive) as tar:
        for name, digest in ORDINARY_FILES.items():
            with tar.extractfile("ctbllib-1.3.11/data/"+name) as f:
                raw = f.read()
            require(hashlib.sha256(raw).hexdigest() == digest, "Wrong ordinary table")
            sources[name] = raw.decode("latin-1")
    result = {}
    for group, primes in EXPECTED.items():
        rows = ordinary_triples(sources["ctosymp1.tbl" if group == SP else "ctoorth3.tbl"], group)
        reductions = {}
        for p, count in primes.items():
            path = directory / f"{group}mod{p}.pdf"
            reductions[str(p)] = read_decomposition(path, PDFS[group, p], len(rows), count)
        result[group] = {"ordinary": rows, "reduction": reductions}
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path)
    parser.add_argument("pdf_directory", type=Path)
    parser.add_argument("--output", type=Path, help="Write reconstructed data to a new file")
    args = parser.parse_args()
    result = rebuild(args.archive, args.pdf_directory)
    verify(result)
    if args.output:
        with args.output.open("x", encoding="utf-8") as f:
            f.write(json.dumps(result, separators=(",", ":")).replace("]],[[", "]],\n[[")+"\n")
    else:
        require(result == json.loads((ROOT/"CHARACTERS.json").read_text()), "Retained data changed")
    print("PASS original numerical sources: two ordinary table files and seven decomposition matrices")
