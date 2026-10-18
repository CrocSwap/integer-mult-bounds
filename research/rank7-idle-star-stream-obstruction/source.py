"""Authenticate and project the literal PR3148 fill; execute no vendor code."""

import gzip
import hashlib
import io
import json
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parent.parent
MAIN = "research/rank7-joint-endframes/allocation/"
PHASES = "research/adaptive-kernel-demotion/inputs/DATA-PHASES.json"
FILL_SHA = "8f4d6965ba573ff2b71fd7bf6b552643e086739d90bd73c55889502077638e00"
BASE_ROWS = 9 * 74 * 408
TOTAL_ROWS = 10 * BASE_ROWS
MAX_RAW = 32_000_000


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_bytes(path):
    require(path.is_file() and not path.is_symlink(), "missing or linked input")
    require(path.stat().st_size <= MAX_RAW, "oversized input")
    return path.read_bytes()


def decode(raw):
    if raw[:2] == b"\x1f\x8b":
        with gzip.GzipFile(fileobj=io.BytesIO(raw)) as stream:
            raw = stream.read(MAX_RAW + 1)
    require(len(raw) <= MAX_RAW, "oversized decoded input")
    return json.loads(raw)


def authenticate(package=PACKAGE, root=ROOT):
    sources = decode(read_bytes(package / "SOURCES.json"))
    for row in sources["files"]:
        if row["usage"] == "input":
            raw = read_bytes(root / row["path"])
            require(hashlib.sha256(raw).hexdigest() == row["sha256"], "live source pin")
    require(len(sources["retained_files"]) == 6, "retained source inventory")
    for row in sources["retained_files"]:
        raw = read_bytes(package / row["local_path"])
        blob = b"blob " + str(len(raw)).encode() + b"\0" + raw
        require(hashlib.sha256(raw).hexdigest() == row["sha256"], "retained source pin")
        require(
            hashlib.sha1(blob, usedforsecurity=False).hexdigest() == row["git_blob"],
            "retained Git blob",
        )


def lifted_row(base, index):
    copy, original = divmod(index, BASE_ROWS)
    time, helper, owner, child, port, offset = base[original]
    return [10 * time + copy, helper, owner + 74 * copy, child, port, offset]


def journal_edits(base, journal):
    require(len(base) == BASE_ROWS, "base role count")
    require(journal["copies"] == 10 and len(journal["edits"]) == 145, "journal size")
    edits = {}
    for index, before, after in journal["edits"]:
        require(type(index) is int and 0 <= index < TOTAL_ROWS, "journal index")
        require(index not in edits, "duplicate journal edit")
        require(before == lifted_row(base, index), "journal preimage")
        require(len(after) == 6 and all(type(x) is int for x in after), "journal row")
        require(after[:2] == before[:2], "changed call/helper identity")
        edits[index] = after
    return edits


def project_fill(base, edits):
    header = {
        "columns": ["time", "helper", "owner_replica", "child", "port", "offset"],
        "dispatch_overrides": [],
    }
    prefix = (
        json.dumps(header, sort_keys=True, separators=(",", ":"))[:-1] + ',"rows":['
    )
    digest = hashlib.sha256(prefix.encode())
    projection = []
    for index in range(TOTAL_ROWS):
        row = edits[index] if index in edits else lifted_row(base, index)
        encoded = ("," if index else "") + json.dumps(row, separators=(",", ":"))
        digest.update(encoded.encode())
        if row[2] == row[4] == 0:
            projection.append(row)
    digest.update(b"]}\n")
    require(digest.hexdigest() == FILL_SHA, "complete PR3148 fill payload")
    require(len(projection) == 30, "projected hosted role count")
    return projection


def load_context():
    authenticate()
    vendor = PACKAGE / "vendor"
    base_raw = read_bytes(vendor / "BASE-FILL.json.gz")
    journal = decode(read_bytes(vendor / "EXCHANGE.json"))
    require(
        hashlib.sha256(base_raw).hexdigest() == journal["base_fill_sha256"],
        "journal base source",
    )
    base = decode(base_raw)["rows"]
    rows = project_fill(base, journal_edits(base, journal))
    order = decode(read_bytes(ROOT / (MAIN + "ORDER.json")))
    require(len(order) == 666, "base chronology count")
    lifted = [[s, r + 74 * copy] for s, r in order for copy in range(10)]
    dispatch_rows = decode(read_bytes(ROOT / (MAIN + "DISPATCH.json")))
    dispatch = {(s, r): tag for s, r, tag in dispatch_rows}
    require(len(dispatch) == 666, "base dispatch count")
    providers = decode(read_bytes(vendor / "PROVIDERS.json"))
    return dict(
        rows=rows,
        order=lifted,
        dispatch=dispatch,
        providers=providers,
        recipe=decode(read_bytes(ROOT / PHASES))["recipes"][0],
        template=decode(read_bytes(ROOT / (MAIN + "vendor/TEMPLATE.json.gz"))),
        plan=decode(read_bytes(ROOT / (MAIN + "vendor/PLAN.json.gz"))),
        moves=[
            m
            for m in decode(read_bytes(vendor / "STAR-MOVES.json.gz"))["moves"]
            if m[:2] == [0, 0]
        ],
    )
