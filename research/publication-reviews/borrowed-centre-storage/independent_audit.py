"""Check package sources and the corrected section and donor identities.

This audit imports no package or producer code. It uses exact rational
arithmetic. OpenAI Codex assisted this review.
"""

from collections import defaultdict
from fractions import Fraction as F
from hashlib import sha256
from io import BytesIO
from pathlib import Path
import argparse
import difflib
import gzip
import json
import shutil
import subprocess
import tarfile


def need(value, message):
    if not value:
        raise ValueError(message)


def digest(raw):
    return sha256(raw).hexdigest()


def blob(repo, commit, path):
    return subprocess.check_output(["git", "-C", str(repo), "show", commit + ":" + path])


def multiply(left, right):
    output = []
    for row in left:
        result = defaultdict(F)
        for index, coefficient in row.items():
            for column, value in right[index].items():
                result[column] += coefficient * value
        output.append({column: value for column, value in result.items() if value})
    return output


def identity(n):
    return [{i: F(1)} for i in range(n)]


def parse(rows):
    return [{int(k): F(v) for k, v in row.items()} for row in rows]


def apply(columns, value):
    result = 0
    while value:
        bit = value & -value
        result ^= columns[bit.bit_length() - 1]
        value ^= bit
    return result


def main(args):
    package = args.package.resolve()
    need(shutil.disk_usage(package).free >= 3 * 1024**3, "At least 3 GiB free")
    hashes = json.loads((package / "PACKAGE-HASHES.json").read_bytes())
    actual_files = {str(p.relative_to(package)) for p in package.rglob("*") if p.is_file()}
    need(actual_files == set(hashes) | {"PACKAGE-HASHES.json"}, "Exact package file set")
    for name, expected in hashes.items():
        need(digest((package / name).read_bytes()) == expected, "Exact package bytes: " + name)
    adaptations = json.loads((package / "ADAPTATIONS.json").read_bytes())
    changes = []
    for name, entry in adaptations.items():
        original = (package / entry["frozen_source"]).read_text()
        revised = (package / "checks" / name).read_text()
        need(digest(original.encode()) == entry["source_sha256"], "Exact adapter source")
        need(digest(revised.encode()) == entry["adapted_sha256"], "Exact adapted checker")
        changes += list(difflib.unified_diff(original.splitlines(keepends=True), revised.splitlines(keepends=True),
                                            fromfile=entry["frozen_source"], tofile="checks/" + name))
    diff = "".join(changes)
    need(diff == (package / "ADAPTATIONS.patch").read_text(), "Complete adapter diff")

    pins = json.loads((package / "SOURCE-PINS.json").read_bytes())["files"]
    archives = defaultdict(list)
    for name, entry in pins.items():
        if "archive_sha256" in entry:
            archives[(entry["git_commit"], entry["git_path"], entry["archive_sha256"])].append((name, entry))
    source_checks = []
    for (commit, path, expected), members in archives.items():
        raw = blob(args.repo, commit, path)
        need(digest(raw) == expected, "Exact source archive")
        with tarfile.open(fileobj=BytesIO(raw), mode="r:gz") as source:
            for name, entry in members:
                found = [item for item in source.getmembers() if item.name == entry["origin"]]
                need(len(found) == 1 and found[0].isfile(), "Unique source member")
                value = source.extractfile(found[0]).read()
                need(value == (package / name).read_bytes(), "Exact packaged archive member")
                source_checks.append({"path": name, "commit": commit, "archive": path, "sha256": digest(value)})
    plan = "sources/alias-upstream/PLAN.json"
    entry = pins[plan]
    need(blob(args.repo, entry["git_commit"], entry["git_path"]) == (package / plan).read_bytes(), "Exact original plan")
    for path in (package / "notices").rglob("*"):
        if path.is_file():
            relative = str(path.relative_to(package / "notices"))
            need(blob(args.repo, "bce54fb3f895cbe5cd4c0eb477c3afeed100190f", relative) == path.read_bytes(), "Exact contributor or license bytes")

    lanes = package / "sources/work/centre-encoding-campaign-20261014/lanes"
    certificate_path = lanes / "paired-package-review/upstream-followthrough-20261015/base/research/joint-query/certificate.json.gz"
    certificate_raw = certificate_path.read_bytes()
    need(blob(args.repo, "a6e6ad3936f67b8f63b5b68c5e75d540610a65e7", "research/joint-query/certificate.json.gz") == certificate_raw,
         "Exact published joint-query certificate")
    certificate = json.loads(gzip.decompress(certificate_raw))
    mask_path = lanes / "portable-source-codes/dirty-record-hosting-20261015/masked-query/masked-sum/MASKED-QUERY-PROGRAM.json.gz"
    mask = json.loads(gzip.decompress(mask_path.read_bytes()))
    r = parse(certificate["R_rows"])
    need(r == parse(mask["R"]), "Same source R")
    a, u = set(mask["selected_A"]), set(mask["kept_ports"])
    la = [{p: value for p, value in row.items() if p in a} for row in r]
    ru = [{p: value for p, value in row.items() if p in u} for row in r]
    pa = [{k: row[p] / 4 for k, row in enumerate(r) if p in row} if p in a else {} for p in range(112)]
    c, ci = parse(mask["target_code"]), parse(mask["inverse_target_code"])
    need(multiply(c, ci) == multiply(ci, c) == identity(112), "Both target inverse orders")
    need(multiply(la, c) == ru and multiply(la, pa) == identity(8), "Section hypotheses")
    unprojected = multiply(ci, pa)
    projected = [row if p in u else {} for p, row in enumerate(unprojected)]
    outside = [p for p, row in enumerate(unprojected) if p not in u and row]
    need(outside, "The unprojected actual section is not supported on U")
    need(multiply(ru, projected) == identity(8), "The corrected section is a right inverse")
    need(all(not row for p, row in enumerate(projected) if p not in u), "The corrected section is supported on U")

    # The three input symbols are the arbitrary query, donor, and target.
    q, donor, target = [F(1), F(0), F(0)], [F(0), F(1), F(0)], [F(0), F(0), F(1)]
    def swap(left, right):
        left = [x + y for x, y in zip(left, right)]
        right = [y - x for x, y in zip(left, right)]
        left = [x + y for x, y in zip(left, right)]
        return left, [-y for y in right]
    parked, stored = swap(q, donor)
    changed_target = [t - x for t, x in zip(target, stored)]
    need(swap(parked, stored) == (q, donor), "Both arbitrary values return")
    need(changed_target == [F(-1), F(0), F(1)], "The bridge reads the query and no donor baseline")
    wrong_target = [t - x for t, x in zip(target, parked)]
    need(wrong_target != changed_target and wrong_target[1] == -1, "The old bridge read leaks the donor baseline")

    routes = []
    for p in range(112):
        event = next(e for e in certificate["programs"]["F_2"] if e[0] == "cover_map" and e[1] == ["L", p])
        record = certificate["map_registry"][event[2]]
        g, shift = record["owner_right_matrix_columns"], record["payload_translation_at_identity_owner"]
        need(all(apply(g, value) == 1 << i for i, value in enumerate(g)), "Exact linear involution")
        need(apply(g, shift) == shift, "Exact affine involution for route-word cancellation")
        routes.append(event[2])
    report = {"status": "PASS_INDEPENDENT_STORAGE_PUBLICATION_AUDIT",
              "imports": "Python standard library only; no package or producer code",
              "package_files_checked": len(actual_files), "package_hashes_sha256": digest((package / "PACKAGE-HASHES.json").read_bytes()),
              "adapter_diffs_checked": len(adaptations), "adapter_diff_matches": True,
              "source_archive_members_checked": source_checks,
              "plan_and_five_notices_match_git": True, "joint_query_certificate_matches_published_git": True,
              "section_check": {"size": [112, 8], "unprojected_non_U_rows": outside, "projected_right_inverse": True, "projected_support_U": True},
              "arbitrary_donor_swap_and_bridge": True, "wrong_bridge_baseline_control": True,
              "stage2_affine_involutions_checked": len(routes),
              "limits": "These checks support the reviewed proofs. They do not admit the changed masked global caller or prove a complete supplier."}
    args.out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(report["status"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package", required=True, type=Path)
    parser.add_argument("--repo", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    main(parser.parse_args())
