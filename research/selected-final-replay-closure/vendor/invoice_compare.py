#!/usr/bin/env python3
"""Compare only PR1094's three-node invoice subgraph, never admit a supplier.

Authenticate each side's two literal raw invoice references before replacing
those two fields by a complete canonical invoice digest. Every other field is
retained. The accepted JSON domain is the reviewed integer/string/Boolean/null
schema: decimal/exponent numbers, duplicate keys and nonfinite values fail.

Adam Gall, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
import hashlib
import json
from pathlib import Path

INVOICE = "global/audit/PREFIX-AND-INVOICE.json"
CONSUMERS = ("ADMISSION-CONTROLS.json", "ASSEMBLY.json")
FILES = (INVOICE, *CONSUMERS)
REFERENCE_PATH = ("input_sha256", "fresh_invoice")
SCOPE = "PR1094 three-node invoice subgraph only; not mathematical admission"


class InvalidGraph(ValueError):
    """Malformed JSON, incomplete subgraph, or an unauthenticated raw edge."""


def sha256(raw):
    return hashlib.sha256(raw).hexdigest()


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise InvalidGraph("duplicate JSON key: " + repr(key))
        result[key] = value
    return result


def _unsupported_number(value):
    raise InvalidGraph("outside reviewed integer JSON domain: " + value)


def parse(raw):
    """Parse without binary64 rounding or Python Boolean/integer conflation."""
    try:
        return json.loads(raw, object_pairs_hook=_unique_object,
                          parse_float=_unsupported_number,
                          parse_constant=_unsupported_number)
    except (ValueError, UnicodeError) as exc:
        raise InvalidGraph(str(exc)) from exc


def canonical(value):
    """An injective encoding of parsed trees up to object order/string escapes."""
    return json.dumps(value, sort_keys=True, ensure_ascii=True,
                      separators=(",", ":"), allow_nan=False).encode("ascii")


def normalized(files):
    """Return complete canonical bytes, after authenticating BOTH raw edges.

    Callers must establish trust in their reference separately. Byte-identical
    inputs do not bypass parsing or edge checks. No path, time, generic digest,
    or unknown field is masked. Only the named three files are in this API.
    """
    if set(files) != set(FILES):
        raise InvalidGraph("expected exactly the three declared subgraph files")
    values = {name: parse(files[name]) for name in FILES}
    if any(type(value) is not dict for value in values.values()):
        raise InvalidGraph("each subgraph artifact must be a JSON object")
    raw_digest = sha256(files[INVOICE])
    for name in CONSUMERS:
        inputs = values[name].get("input_sha256")
        if type(inputs) is not dict:
            raise InvalidGraph(name + ": missing input_sha256 object")
        digest = inputs.get("fresh_invoice")
        if type(digest) is not str or digest != raw_digest:
            raise InvalidGraph(name + ": stale or misbound fresh_invoice")
    invoice = canonical(values[INVOICE])
    content_digest = sha256(invoice)
    result = {INVOICE: invoice}
    for name in CONSUMERS:
        values[name]["input_sha256"]["fresh_invoice"] = content_digest
        result[name] = canonical(values[name])
    return result


def compare(reference, candidate):
    """A fresh parse and edge check on each side, then complete byte equality."""
    left, right = normalized(reference), normalized(candidate)
    different = [name for name in FILES if left[name] != right[name]]
    return {
        "scope": SCOPE,
        "equivalent": not different,
        "different_files": different,
        "authenticated_edges_per_side": len(CONSUMERS),
        "reference_invoice_raw_sha256": sha256(reference[INVOICE]),
        "candidate_invoice_raw_sha256": sha256(candidate[INVOICE]),
        "reference_canonical_sha256": {name: sha256(left[name]) for name in FILES},
        "candidate_canonical_sha256": {name: sha256(right[name]) for name in FILES},
    }


def read_graph(directory):
    """Read the three documented paths; other directory files are OUT OF SCOPE."""
    return {name: (directory / name).read_bytes() for name in FILES}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("reference", type=Path, help="trusted strict-output directory")
    parser.add_argument("candidate", type=Path, help="candidate strict-output directory")
    args = parser.parse_args(argv)
    try:
        report = compare(read_graph(args.reference), read_graph(args.candidate))
    except (OSError, InvalidGraph) as exc:
        print(json.dumps({"scope": SCOPE, "valid_graph": False, "error": str(exc)}))
        return 2
    print(json.dumps(report, sort_keys=True, indent=2))
    return 0 if report["equivalent"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
