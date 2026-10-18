#!/usr/bin/env python3
"""Classify the three assembly digests omitted by the #626 Linux reconciliation.

The reconciliation already refuses to call those differences gzip metadata.
This check says what each digest measures, using the producers at the pinned
sprint base. It does not rerun the supplier. Python 3.10+.
"""

from hashlib import sha256
import gzip
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
PREDECESSOR = ROOT / "research/selected626-linux-reconciliation"
BASE = "66849e1475c930fd7732b1a0067ffee7e1e95f60"
BLOBS = {
    "research/complex-k492-owner-repair/code/invoice_allcold.py":
        "b244cd59940659465c07b013ebe3225077496f45",
    "research/complex-k492-owner-repair/code/assemble.py":
        "d1674e657ff046f9d55c917723002f270e05c42a",
    "research/complex-k492-owner-repair/code/audit_allcold.py":
        "e29d90e89af9d7535c96de6ebf7c4d03616f7c48",
}
SNIPPETS = {
    "research/complex-k492-owner-repair/code/invoice_allcold.py": (
        "def filehash(path): return hashlib.sha256(path.read_bytes()).hexdigest()",
        "return hashlib.sha256(gzip.decompress(data) if path.suffix=='.gz' else data).hexdigest()",
        "assert replay['canonical_word_sha256']==filehash(cp)==registry['canonical_word_sha256']",
        "template_hash=contenthash(template_path)",
        "owner_audit_sha256=filehash(audit/'OWNERS-AND-PROFILE.json')",
        "(out/'PREFIX-AND-INVOICE.json').write_text(json.dumps(receipt,indent=2)+'\\n')",
    ),
    "research/complex-k492-owner-repair/code/assemble.py": (
        "sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()",
        "input_hashes={'owner_audit':owner_sha,'fresh_invoice':invoice_sha,'inputs/PR543-EXPECTED.json':sha(bit_path)}",
        "template_sha256=owner['template_sha256']",
        "owner_path=C/'audit/OWNERS-AND-PROFILE.json';invoice_path=C/'audit/PREFIX-AND-INVOICE.json'",
        "r=assemble(owner,invoice,sha(owner_path),sha(invoice_path))",
    ),
    "research/complex-k492-owner-repair/code/audit_allcold.py": (
        "raw=gzip.decompress((OUT/'GLOBAL-TEMPLATE.json.gz').read_bytes());assert hashlib.sha256(raw).hexdigest()==summary['template_sha256']",
        "source_artifacts=summary['source_artifacts']",
        "(REPORT.parent/'OWNERS-AND-PROFILE.json').write_text(json.dumps(owners,indent=2)+'\\n')",
    ),
}


def need(condition, message):
    if not condition:
        raise ValueError(message)


def git_show(spec):
    return subprocess.check_output(["git", "-C", str(ROOT), "show", spec])


def git_rev_parse(spec):
    return subprocess.check_output(
        ["git", "-C", str(ROOT), "rev-parse", spec], text=True).strip()


def filehash(data):
    return sha256(data).hexdigest()


def contenthash(data, gzip_wrapped):
    payload = gzip.decompress(data) if gzip_wrapped else data
    return sha256(payload).hexdigest()


def check_producers():
    sources = {}
    for path, blob in BLOBS.items():
        need(git_rev_parse(BASE + ":" + path) == blob, "producer blob changed: " + path)
        text = git_show(BASE + ":" + path).decode()
        for snippet in SNIPPETS[path]:
            need(snippet in text, "producer no longer defines: " + snippet)
        sources[path] = text
    return sources


def check_container_is_not_payload():
    payload = b'{"frames":[1,2,3],"paid":{"1":4}}\n'
    first = gzip.compress(payload, compresslevel=9, mtime=0)
    second = gzip.compress(payload, compresslevel=1, mtime=5)
    need(first != second, "fixture failed to build two containers")
    need(contenthash(first, True) == contenthash(second, True) == sha256(payload).hexdigest(),
         "decompressed payload hash changed with the container")
    need(filehash(first) != filehash(second), "container file hash ignored a real container change")
    changed = payload.replace(b"[1,2,3]", b"[1,2,4]")
    recompressed = gzip.compress(changed, compresslevel=9, mtime=0)
    need(contenthash(recompressed, True) != contenthash(first, True),
         "payload hash missed a template change")
    return {"same_payload_containers_differ": True,
            "payload_hash": contenthash(first, True),
            "container_hashes_differ": True}


def owner_text(artifact_hash):
    owner = {
        "status": "PASS_INDEPENDENT_ASYNC_OWNERS_AND_PROFILE",
        "template_sha256": "ab" * 32,
        "paid_profile": {"1": 4},
        "source_artifacts": {"providers/p/CANONICAL-WORD.json.gz": artifact_hash},
    }
    return (json.dumps(owner, indent=2) + "\n").encode()


def projected_assembly(owner_text_bytes):
    """Fields the #626 assembly keeps after the three omitted digests are removed."""
    owner = json.loads(owner_text_bytes)
    return {"complex_profile": owner["paid_profile"]}


def check_omitted_file_can_hide_container_change(container):
    payload = b'{"frames":[1,2,3],"paid":{"1":4}}\n'
    other = gzip.compress(payload, compresslevel=1, mtime=5)
    left = owner_text(filehash(container))
    right = owner_text(filehash(other))
    need(filehash(left) != filehash(right), "owner file hash missed a nested container change")
    need(projected_assembly(left) == projected_assembly(right),
         "reduced assembly changed when only a container hash changed")
    # A real profile change is still visible without the omitted file hash.
    mutated = json.loads(left)
    mutated["paid_profile"] = {"1": 5}
    mutated_text = (json.dumps(mutated, indent=2) + "\n").encode()
    need(projected_assembly(mutated_text) != projected_assembly(left),
         "reduced assembly missed a profile change")


def classify_recorded_differences():
    expected = json.loads((PREDECESSOR / "EXPECTED.json").read_text())
    rows = expected["assembly_digest_differences"]
    need([row["path"] for row in rows] == [
        ["template_sha256"],
        ["input_sha256", "owner_audit"],
        ["input_sha256", "fresh_invoice"],
    ], "recorded difference paths changed")
    classes = {
        ("template_sha256",): "decompressed-payload",
        ("input_sha256", "owner_audit"): "indented-json-file",
        ("input_sha256", "fresh_invoice"): "indented-json-file",
    }
    classified = []
    for row in rows:
        path = tuple(row["path"])
        need(row["linux"] != row["committed"], "recorded digests unexpectedly agree: " + str(path))
        need(len(row["linux"]) == len(row["committed"]) == 64, "digest length")
        classified.append({"path": list(path), "measures": classes[path],
                           "linux": row["linux"], "committed": row["committed"]})
    predecessor = (PREDECESSOR / "verify.py").read_text()
    need("DIFFERING_PATHS = [('template_sha256',), ('input_sha256', 'owner_audit'),\n"
         "                   ('input_sha256', 'fresh_invoice')]" in predecessor,
         "reconciliation no longer omits these three paths")
    need("require(left == right, 'Mathematical assembly fields differ')" in predecessor,
         "reconciliation equality check moved")
    return classified


def main():
    check_producers()
    containers = check_container_is_not_payload()
    sample = gzip.compress(b'{"frames":[1,2,3],"paid":{"1":4}}\n', compresslevel=9, mtime=0)
    check_omitted_file_can_hide_container_change(sample)
    classified = classify_recorded_differences()
    need([row["measures"] for row in classified] == [
        "decompressed-payload", "indented-json-file", "indented-json-file"],
         "classification changed")
    need(containers["same_payload_containers_differ"], "container fixture lost")
    print("PASS_PR626_OMITTED_DIGEST_AUDIT "
          "template=decompressed-payload owner_audit=indented-json-file "
          "fresh_invoice=indented-json-file differences=3")


if __name__ == "__main__":
    main()
