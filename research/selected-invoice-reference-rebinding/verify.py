#!/usr/bin/env python3
"""Source-bound experiment and replay for the PR1094 invoice subgraph.

No supplier execution, network, generated-source edits, or third-party modules.
Adam Gall, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from collections import Counter
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tarfile
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import compare_invoice as engine

SOURCE = "research/community-frontier1094-audit/"
ARCHIVE = SOURCE + "selected-replay.tar.gz"
BEFORE = "research/selected-final-stage-portability/compare_payloads.py"
CLAIM = "https://github.com/CrocSwap/integer-mult-bounds/discussions/2049#discussioncomment-18931179"


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def dump(value, **kwargs):
    return (json.dumps(value, ensure_ascii=True, allow_nan=False, **kwargs) + "\n").encode("ascii")


def check_sources(root=ROOT):
    manifest = json.loads((HERE / "SOURCES.json").read_bytes())
    for row in manifest["files"]:
        if row["usage"] == "input":
            require(engine.sha256((root / row["path"]).read_bytes()) == row["sha256"],
                    "immutable source hash mismatch: " + row["path"])


def load_corpus(root=ROOT):
    check_sources(root)
    prefix = "candidate/strict/"
    with tarfile.open(root / ARCHIVE) as archive:
        corpus = {}
        for member in archive.getmembers():
            if not member.isfile() or not member.name.startswith(prefix):
                continue
            name = member.name[len(prefix):]
            require(name not in corpus, "duplicate archive member: " + name)
            corpus[name] = archive.extractfile(member).read()
        receipt = archive.extractfile("RESULT.json").read()
    require(receipt == (root / SOURCE / "RESULT.json").read_bytes(), "archive receipt differs")
    require(corpus["ASSEMBLY.json"] == (root / SOURCE / "ASSEMBLY.json").read_bytes(),
            "archive assembly differs from committed selected certificate")
    require(engine.sha256(corpus["ASSEMBLY.json"]) == json.loads(receipt)["assembly_sha256"],
            "receipt assembly binding differs")
    require(len(corpus) == 105, "reviewed strict-output inventory differs")
    return corpus


def walk(value, path=()):
    yield path, value
    if type(value) is dict:
        for key in sorted(value):
            yield from walk(value[key], path + (key,))
    elif type(value) is list:
        for index, item in enumerate(value):
            yield from walk(item, path + (index,))


def typed(value):
    """Independent structural oracle: no serializer and no digest projection."""
    if type(value) is dict:
        return ("object", tuple((key, typed(value[key])) for key in sorted(value)))
    if type(value) is list:
        return ("array", tuple(typed(item) for item in value))
    return (type(value).__name__, value)


def oracle(files):
    """Preserve the two edge ROLES as tuples, independently of content hashes."""
    values = {name: json.loads(files[name]) for name in engine.FILES}
    digest = hashlib.sha256(files[engine.INVOICE]).hexdigest()
    for name in engine.CONSUMERS:
        require(values[name]["input_sha256"]["fresh_invoice"] == digest,
                "oracle raw edge mismatch")
        values[name]["input_sha256"]["fresh_invoice"] = ("edge", engine.INVOICE)
    return tuple((name, typed(values[name])) for name in engine.FILES)


def alter(value, path, replacement=None, omit=False):
    """Copy only containers on the edited path; never change the reference tree."""
    if not path:
        require(not omit, "cannot omit root")
        return replacement
    key, *rest = path
    changed = value.copy()
    if rest:
        changed[key] = alter(value[key], rest, replacement, omit)
    elif omit:
        del changed[key]
    else:
        changed[key] = replacement
    return changed


def replacement(value):
    if type(value) is bool:
        return not value
    if type(value) is int:
        return value + 1
    if type(value) is str:
        return value + "#semantic-change"
    if type(value) is dict:
        return {"semantic-change": None}
    if type(value) is list:
        return ["semantic-change"]
    if value is None:
        return "semantic-change"
    raise RuntimeError("unexpected fixture value type")


def rebound(files, invoice_bytes):
    candidate = dict(files)
    candidate[engine.INVOICE] = invoice_bytes
    digest = engine.sha256(invoice_bytes)
    for name in engine.CONSUMERS:
        value = json.loads(candidate[name])
        value["input_sha256"]["fresh_invoice"] = digest
        candidate[name] = dump(value, indent=2)
    return candidate


def reverse_objects(value):
    if type(value) is dict:
        return {key: reverse_objects(item) for key, item in reversed(tuple(value.items()))}
    if type(value) is list:
        return [reverse_objects(item) for item in value]
    return value


def source_census(corpus):
    invoice_digest = engine.sha256(corpus[engine.INVOICE])
    occurrences, byte_occurrences = [], []
    json_files = gzip_files = 0
    for name, raw in sorted(corpus.items()):
        if name.endswith(".gz"):
            raw = gzip.decompress(raw)
            gzip_files += 1
        count = raw.count(invoice_digest.encode("ascii"))
        if count:
            byte_occurrences.append({"file": name, "count": count})
        if name.removesuffix(".gz").endswith(".json"):
            json_files += 1
            for path, value in walk(json.loads(raw)):
                if value == invoice_digest:
                    occurrences.append({"file": name, "path": list(path)})
    expected = [{"file": name, "path": list(engine.REFERENCE_PATH)} for name in engine.CONSUMERS]
    require(occurrences == expected, "invoice has an unaccounted direct JSON consumer")
    require(byte_occurrences == [{"file": name, "count": 1} for name in engine.CONSUMERS],
            "invoice digest occurs outside the two declared references")
    return {"strict_files": len(corpus), "json_payloads": json_files,
            "gzip_payloads": gzip_files, "direct_references": occurrences,
            "raw_digest_occurrences": byte_occurrences}


def before_classification(reference, candidate):
    spec = importlib.util.spec_from_file_location("pinned_before_comparator", ROOT / BEFORE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    with tempfile.TemporaryDirectory(prefix="invoice-before-") as tmp:
        directory = Path(tmp)
        result = {}
        for name in engine.FILES:
            a, b = directory / "ref" / name, directory / "run" / name
            a.parent.mkdir(parents=True, exist_ok=True)
            b.parent.mkdir(parents=True, exist_ok=True)
            a.write_bytes(reference[name])
            b.write_bytes(candidate[name])
            result[name] = module.classify(a, b, (), ())
    require(result[engine.INVOICE]["cls"] == "json-format", "before invoice fixture differs")
    for name in engine.CONSUMERS:
        require(result[name]["verdict"] == "proof-relevant-candidate", "before did not flag reference")
        require(result[name]["differing"] == 1, "before differs beyond the single fresh_invoice edge")
    return result


def audit():
    corpus = load_corpus()
    source = {name: corpus[name] for name in engine.FILES}
    trees = {name: json.loads(source[name]) for name in engine.FILES}
    reference = engine.normalized(source)
    reference_oracle = oracle(source)
    summary = {"schema_version": 1, "status": "PASS_SELECTED_INVOICE_REFERENCE_REBINDING",
               "scope": engine.SCOPE, "source_census": source_census(corpus),
               "artifacts": {}, "positive_controls": [], "field_mutations": {},
               "edge_and_parser_controls": []}
    for name in engine.FILES:
        counts = Counter(type(value).__name__ for _, value in walk(trees[name]))
        # Oracle comparison retains full trees; only the authenticated edge values
        # use a content hash in the primary representation, versus a role token here.
        projected = json.loads(reference[name])
        original = json.loads(source[name])
        if name in engine.CONSUMERS:
            projected["input_sha256"]["fresh_invoice"] = ("edge", engine.INVOICE)
            original["input_sha256"]["fresh_invoice"] = ("edge", engine.INVOICE)
        require(typed(projected) == typed(original), "normalization dropped or changed a field")
        summary["artifacts"][name] = {
            "raw_sha256": engine.sha256(source[name]),
            "canonical_sha256": engine.sha256(reference[name]),
            "bytes": len(source[name]), "nodes": sum(counts.values()),
            "types": dict(sorted(counts.items())),
        }

    def accepted(label, candidate):
        require(engine.normalized(candidate) == reference, "positive rejected: " + label)
        require(oracle(candidate) == reference_oracle, "positive oracle differs: " + label)
        summary["positive_controls"].append({"name": label,
            "raw_sha256": {name: engine.sha256(candidate[name]) for name in engine.FILES}})

    accepted("identical-valid-subgraph", source)
    portable = rebound(source, dump(trees[engine.INVOICE], sort_keys=True, separators=(",", ":")))
    require(portable[engine.INVOICE] != source[engine.INVOICE], "positive must change invoice bytes")
    accepted("sorted-compact-invoice-both-edges-rebound", portable)
    accepted("reverse-every-invoice-object-both-edges-rebound",
             rebound(source, dump(reverse_objects(trees[engine.INVOICE]), indent=1)))
    # Replace a JSON string escape, not a value. The invoice has many letter P's.
    escaped = source[engine.INVOICE].replace(b"PASS_", b"\\u0050ASS_", 1)
    require(escaped != source[engine.INVOICE], "escape positive did not change source")
    accepted("equivalent-string-escape-both-edges-rebound", rebound(source, escaped))
    for name in engine.CONSUMERS:
        candidate = dict(source)
        candidate[name] = dump(reverse_objects(trees[name]), separators=(",", ":"))
        accepted("receipt-format-only:" + name, candidate)
    candidate = rebound(source, dump(reverse_objects(trees[engine.INVOICE]), separators=(",", ":")))
    for name in engine.CONSUMERS:
        candidate[name] = dump(reverse_objects(json.loads(candidate[name])), sort_keys=True)
    accepted("all-three-reformatted-with-authenticated-links", candidate)
    summary["before_comparison"] = before_classification(source, portable)

    transcript = hashlib.sha256()
    total = 0
    for name in engine.FILES:
        counts = Counter()
        for path, value in walk(trees[name]):
            if not path:
                continue
            for operation in ("omit", "replace"):
                mutated = alter(trees[name], path, replacement(value), omit=operation == "omit")
                candidate = dict(source)
                candidate[name] = dump(mutated)
                if name == engine.INVOICE:
                    candidate = rebound(candidate, candidate[name])
                try:
                    normalized = engine.normalized(candidate)
                except engine.InvalidGraph:
                    verdict = "invalid-raw-edge"
                else:
                    require(normalized != reference, f"semantic mutation accepted: {name} {path} {operation}")
                    require(oracle(candidate) != reference_oracle, "independent oracle missed mutation")
                    verdict = "different-complete-payload"
                transcript.update(dump([name, list(path), operation, verdict,
                                        engine.sha256(candidate[name])], separators=(",", ":")))
                counts[verdict] += 1
                total += 1
        summary["field_mutations"][name] = dict(sorted(counts.items()))
    summary["field_mutation_total"] = total
    summary["field_mutation_transcript_sha256"] = transcript.hexdigest()
    summary["synchronized_invoice_mutations"] = 2 * (summary["artifacts"][engine.INVOICE]["nodes"] - 1)

    def rejected(label, candidate, left=source):
        try:
            report = engine.compare(left, candidate)
        except engine.InvalidGraph:
            verdict = "invalid-graph"
        else:
            require(not report["equivalent"], "control accepted: " + label)
            verdict = "different-complete-payload"
        summary["edge_and_parser_controls"].append({"name": label, "verdict": verdict})

    stale = dict(source)
    stale[engine.INVOICE] = portable[engine.INVOICE]
    rejected("reformatted-invoice-both-edges-stale", stale)
    rejected("identical-stale-graphs-no-byte-shortcut", stale, stale)
    for name in engine.CONSUMERS:
        partial = dict(portable)
        partial[name] = source[name]
        rejected("only-other-edge-rebound:" + name, partial)
        wrong = dict(source)
        value = json.loads(wrong[name])
        value["input_sha256"]["fresh_invoice"] = value["input_sha256"]["owner_audit"]
        wrong[name] = dump(value)
        rejected("misbound-to-owner-audit:" + name, wrong)
    for name in engine.FILES:
        duplicate = dict(source)
        duplicate[name] = b'{"status":"forged",' + duplicate[name].lstrip()[1:]
        if name == engine.INVOICE:
            duplicate = rebound(duplicate, duplicate[name])
        rejected("duplicate-key:" + name, duplicate)
        for token in (b"NaN", b"Infinity", b"-Infinity", b"1.0", b"1e0"):
            malformed = dict(source)
            malformed[name] = b'{"unexpected-number":' + token + b',' + source[name].lstrip()[1:]
            if name == engine.INVOICE:
                malformed = rebound(malformed, malformed[name])
            rejected("unsupported-number:" + name + ":" + token.decode(), malformed)
        missing = dict(source)
        del missing[name]
        rejected("missing-file:" + name, missing)
        unexpected = dict(source)
        value = json.loads(source[name])
        value["unexpected-proof-field"] = True
        unexpected[name] = dump(value)
        if name == engine.INVOICE:
            unexpected = rebound(unexpected, unexpected[name])
        rejected("unfamiliar-field-retained:" + name, unexpected)
    # Type-distinct equal Python values are especially plausible canonicalization bugs.
    for name in engine.FILES:
        for path, value in walk(trees[name]):
            if type(value) is bool:
                candidate = dict(source)
                candidate[name] = dump(alter(trees[name], path, int(value)))
                if name == engine.INVOICE:
                    candidate = rebound(candidate, candidate[name])
                rejected("boolean-to-integer:" + name + ":" + repr(path), candidate)
    summary["negative_controls"] = total + len(summary["edge_and_parser_controls"])
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--write-result", action="store_true",
                        help="initial experiment only: exclusively create RESULT.json")
    args = parser.parse_args()
    result = audit()
    path = HERE / "RESULT.json"
    if args.write_result:
        with path.open("xb") as stream:
            stream.write(dump(result, indent=2, sort_keys=True))
    else:
        recorded = engine.parse(path.read_bytes())
        require(engine.canonical(result) == engine.canonical(recorded), "complete result receipt differs")
    print("PASS_SELECTED_INVOICE_REFERENCE_REBINDING"
          f" files={result['source_census']['strict_files']} nodes={sum(a['nodes'] for a in result['artifacts'].values())}"
          f" edges=2 positives={len(result['positive_controls'])} field_mutations={result['field_mutation_total']}"
          f" synchronized_invoice_mutations={result['synchronized_invoice_mutations']}"
          f" negatives={result['negative_controls']} no_new_kappa")


if __name__ == "__main__":
    main()
