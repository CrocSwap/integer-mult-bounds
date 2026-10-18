#!/usr/bin/env python3
"""Offline PR211 source-retention proof and saved-certificate reconciliation.

steph4n (@steph4n-gh), with substantial Google Gemini assistance. Apache-2.0.
This checks Git object identity and recorded accounting, not physical execution.
"""
import argparse
import base64
from collections import Counter
from fractions import Fraction as Q
import gzip
import hashlib
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = "0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2"
MERGE_BASE = "3b6b66891c0ac888521cf591fe306c6286601d4f"
PR205 = "95c58706ad231d532bd7038308946a0344d08186"
PR211 = "c63e50a5dde96fe1459d6b29e55e47f42f104347"
PR210 = "b0c058ba979c748bb3a8604bfb6502e9fac9b84d"
PR217 = "b739fc226a54a4a507989aa1bef092d491287451"
ARCHIVE = "bd1b279e5e5449f81ca262c1647961e81dd69e50"

PACKED_DIR = "research/packed-diagonal-bit"
PACKED_WORKFLOW = ".github/workflows/packed-diagonal-bit.yml"
PACKED_TREE = "409a4737d6ca0aa6c59f40b732c5d4608e705246"
PACKED_WORKFLOW_BLOB = "b00ddc44b8f866f57a62a82dd7ba6b43894301b6"

CASCADE_DIR = "research/cascade-frames-bit"
CASCADE_WORKFLOW = ".github/workflows/cascade-frames-bit.yml"
CASCADE_TREE = "1708e493cbb1931e4fd11eca058b72193dfec3ac"
CASCADE_WORKFLOW_BLOB = "aed05819ec6a716b8de02d243b447031ef1309a1"

FRAMES_BLOB = "8433d7724cbed83401fa42beee8653c62657ec0d"
FRAMES_SHA256 = "56b2ed0f6b867e8cafdc32ac70419cfda36d02838844572098b3fc77f8026e58"
FRAMES_B64_BLOB = "6b3b66eaa484a50f1f45ab9f7515a1b4ff26897f"
NOTICE_BLOB = "9edc2572378be7a7819f229de985eeaffa1173b6"
BANKS_BLOB = "6505ebd37e3414016168511cca7c2f69216cc9f1"
CONTROLS_BLOB = "51235415282f631caa4402e80b72f84915ff977d"

PR210_FRAMES_PATH = "research/coordinated-crossover-pr200/search/pr211-frames.json"
PR210_NOTICE_PATH = "research/coordinated-crossover-pr200/search/PR211-NOTICE"
PR217_FRAMES_B64_PATH = "research/butterfly-coordinated-bit-211/opframe-bases.json.gz.b64"
PR217_NOTICE_PATH = "research/butterfly-coordinated-bit-211/UPSTREAM_NOTICE_PR211.md"

INPUTS = (
    "research/community-reconciliation-next100-audit/ARCHIVE.json",
    "research/community-reconciliation-next100-audit/REVIEW.json",
    "research/community-round9-audit/pr211-changed.log.txt",
    "research/community-round9-audit/review-ledger.json",
)

BOUNDARY_CHILD_OFFSETS = {1: 5280, 2: 6160, 20: 2640, 22: 2640, 60: 2200}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def no_duplicate_keys(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate JSON key: " + key)
        result[key] = value
    return result


def loads(raw):
    return json.loads(raw, object_pairs_hook=no_duplicate_keys)


def git_id(kind, raw):
    return hashlib.sha1(kind.encode() + b" " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


class Proof:
    def __init__(self, document):
        require(document["schema_version"] == 1, "unsupported proof schema")
        self.objects = document["objects"]
        self.used = set()

    def raw(self, oid, kind):
        require(re.fullmatch(r"[0-9a-f]{40}", oid) is not None, "invalid Git id")
        require(oid in self.objects, "missing Git object: " + oid)
        obj = self.objects[oid]
        require(obj["type"] == kind, "Git object type mismatch")
        raw = base64.b64decode(obj["base64"], validate=True)
        require(git_id(kind, raw) == oid, "Git object digest mismatch: " + oid)
        self.used.add(oid)
        return raw

    def commit(self, oid):
        header = self.raw(oid, "commit").split(b"\n\n", 1)[0].decode("utf-8").splitlines()
        trees = [line[5:] for line in header if line.startswith("tree ")]
        require(len(trees) == 1, "commit needs one tree")
        return trees[0], [line[7:] for line in header if line.startswith("parent ")]

    def tree(self, oid):
        raw, offset, entries = self.raw(oid, "tree"), 0, {}
        while offset < len(raw):
            space = raw.find(b" ", offset)
            zero = raw.find(b"\0", space + 1)
            require(space > offset and zero > space + 1 and zero + 21 <= len(raw),
                    "malformed Git tree")
            mode = raw[offset:space].decode("ascii")
            name = raw[space + 1:zero].decode("utf-8")
            require(mode in ("40000", "100644", "100755", "120000"), "unsupported tree mode")
            require(name not in (".", "..") and "/" not in name and name not in entries,
                    "invalid or duplicate tree path")
            entries[name] = (mode, raw[zero + 1:zero + 21].hex())
            offset = zero + 21
        return entries

    def resolve(self, commit, path, expected_mode=None):
        parts = path.split("/")
        require(all(p and p not in (".", "..") for p in parts), "invalid requested path")
        oid, _ = self.commit(commit)
        mode = "40000"
        for part in parts:
            require(mode == "40000", "path traverses a non-directory")
            entries = self.tree(oid)
            require(part in entries, "missing path component: " + part)
            mode, oid = entries[part]
        if expected_mode is not None:
            require(mode == expected_mode, "path mode mismatch: " + path)
        return mode, oid

    def inventory(self, tree, prefix=""):
        result = {}
        for name, (mode, oid) in self.tree(tree).items():
            path = prefix + name
            if mode == "40000":
                result.update(self.inventory(oid, path + "/"))
            else:
                result[path] = {"mode": mode, "blob": oid}
        return result

    def difference(self, before, after, prefix=""):
        """Walk every changed subtree; equal Git trees are skipped exactly."""
        if before == after:
            return {}
        left, right = self.tree(before), self.tree(after)
        changed = {}
        for name in sorted(set(left) | set(right)):
            a, b = left.get(name), right.get(name)
            path = prefix + name
            if a == b:
                continue
            if a is None and b[0] == "40000":
                changed.update({p: {"before": None, "after": row}
                                for p, row in self.inventory(b[1], path + "/").items()})
            elif a is not None and b is not None and a[0] == b[0] == "40000":
                changed.update(self.difference(a[1], b[1], path + "/"))
            else:
                changed[path] = {
                    "before": None if a is None else {"mode": a[0], "blob": a[1]},
                    "after": None if b is None else {"mode": b[0], "blob": b[1]},
                }
        return changed


def int_histogram(mapping, max_rank):
    out = {}
    for k, count in mapping.items():
        require(isinstance(k, str) and k.isdigit(), "non-integer histogram rank key")
        rank = int(k)
        require(type(count) is int and 0 < rank <= max_rank and count > 0, "invalid histogram entry")
        require(rank not in out, "duplicate histogram rank")
        out[rank] = count
    require(bool(out), "empty histogram")
    return out


def nonzero(counter):
    return {str(k): v for k, v in sorted(counter.items()) if v}


def parse_round9_log(raw_text):
    lines = raw_text.splitlines()
    require(len(lines) > 6, "truncated Round-9 replay log")
    require(lines[0] == "bound 39780 bits 24 columns 20634", "Round-9 log header bound mismatch")
    require(lines[2] == "conditional kappa = 683847872495777/1000000000000000000",
            "Round-9 log header kappa mismatch")
    require(lines[4] == "conditional kappa = 683847872495777/1000000000000000000",
            "Round-9 log second kappa mismatch")
    return loads("\n".join(lines[5:]))


def check_frame_bases(bases, source_meta):
    require(isinstance(bases, list) and len(bases) == 6191, "frame-base count mismatch")
    require(source_meta["bit_commit"] == "a1175449f34d39ff933d9d8ab23ced1f32b290ec", "wrong bit parent commit")
    require(source_meta["complex_commit"] == "187e1010ac8b259af8e9b5166f68b64bc27b4b47",
            "wrong complex parent commit")
    require(source_meta["frames_sha256"] == FRAMES_SHA256, "SOURCE.json frames_sha256 mismatch")
    seen_ops = set()
    dim_counts = Counter()
    total_rows = 0
    for entry in bases:
        require(isinstance(entry, list) and len(entry) == 2, "malformed frame-base entry")
        op_idx, rows = entry
        require(type(op_idx) is int and 0 <= op_idx < 40266, "invalid operation index in frame bases")
        require(op_idx not in seen_ops, "duplicate operation index in frame bases")
        seen_ops.add(op_idx)
        require(isinstance(rows, list) and 3 <= len(rows) <= 21, "invalid replacement frame dimension")
        for row in rows:
            require(isinstance(row, list) and len(row) == 24 and all(type(x) is int for x in row),
                    "invalid replacement frame row")
            require(any(x != 0 for x in row), "zero row in replacement frame basis")
        dim_counts[len(rows)] += 1
        total_rows += len(rows)
    return {
        "changed_frames": len(bases),
        "min_dim": min(dim_counts),
        "max_dim": max(dim_counts),
        "total_basis_rows": total_rows,
        "dimension_histogram": {str(k): v for k, v in sorted(dim_counts.items())},
    }


def check_accounting(c205, c211, r9_log, bases, source_meta):
    """Reconcile PR205 and PR211 certificates, Round-9 replay log and 6,191 frame bases."""
    frame_summary = check_frame_bases(bases, source_meta)
    require(r9_log["status"] == "PASS_FRESH_CHANGED_BIT_AND_BANKS" and r9_log["pr"] == 211,
            "Round-9 replay log status/PR mismatch")
    require(r9_log["kappa"] == "683847872495777/1000000000000000000", "Round-9 replay log kappa mismatch")
    fresh = r9_log["fresh"]
    require(set(fresh) == {"admitted", "physical", "arithmetic", "independent", "bank_controls"},
            "Round-9 replay log section set mismatch")
    for section in ("admitted", "physical", "arithmetic", "independent", "bank_controls"):
        require(fresh[section] == c211[section], "Round-9 replay log differs from PR211 certificate: " + section)
    require(c211["pinned_bit_files"] == c205["pinned_bit_files"] == 2242, "pinned_bit_files mismatch")

    admitted = c211["admitted"]
    require(admitted["changed_frames"] == frame_summary["changed_frames"] == 6191, "admitted changed_frames mismatch")
    require(admitted["used_frames"] == 24611 and admitted["integer_residual_bound"] == 39780,
            "admitted frame/residual metadata mismatch")

    over = admitted["overridden_profile"]
    prof = admitted["profile"]
    require((over["h"], over["m"], over["v"]) == (prof["h"], prof["m"], prof["v"]) == (24, 72, 1760),
            "wrong bit profile geometry")
    require(prof["terminal_sinks"] == 34, "terminal sink count mismatch")
    require(over["W_per_vertex"] - prof["W_per_vertex"] == 34 and prof["W_per_vertex"] == 20634,
            "terminal sink W_per_vertex reduction mismatch")
    require(over["R"] - prof["R"] == 34 and prof["R"] == 17114, "terminal sink R reduction mismatch")

    for label, row in (("overridden_profile", over), ("profile", prof)):
        ch = int_histogram(row["child_histogram"], row["m"])
        pi = int_histogram(row["physical_internal_histogram"], row["h"])
        pt = int_histogram(row["physical_target_histogram"], row["h"])
        sr = int_histogram(row["selected_rank_histogram"], row["h"])
        require(sr == {20: 2200} and row["selected_roles"] == 2200, "selected gauge role mismatch: " + label)
        reconstructed = Counter(BOUNDARY_CHILD_OFFSETS)
        for r, n in pi.items():
            reconstructed[r] += 3 * n
        for r, n in pt.items():
            reconstructed[r] += 3 * n
        require(dict(sorted(reconstructed.items())) == dict(sorted(ch.items())),
                "physical internal/target decomposition mismatch: " + label)
        mass = sum(r * n for r, n in ch.items())
        require(mass == row["rank_per_vertex"] == row["m"] * row["W_per_vertex"] - row["deficit_per_vertex"],
                "unpacked rank mass mismatch: " + label)
        require(row["deficit_per_vertex"] == 1936, "unpacked deficit mismatch: " + label)

    term_delta = Counter(int_histogram(prof["child_histogram"], 72))
    term_delta.subtract(int_histogram(over["child_histogram"], 72))
    require(nonzero(term_delta) == admitted["terminal_child_delta"] == {"3": -102, "21": -102},
            "terminal sink child-histogram delta mismatch")
    require(over["rank_per_vertex"] - prof["rank_per_vertex"] == 3 * 102 + 21 * 102 == 2448,
            "terminal sink rank reduction mismatch")

    u205_row = c205["arithmetic"]["unpacked_profile"]
    u211_row = c211["arithmetic"]["unpacked_profile"]
    for key in ("m", "W", "N", "L", "total_rank", "maxchild"):
        require(type(u205_row[key]) is int and u205_row[key] == u211_row[key],
                "changed unpacked common parameter: " + key)
    require((u211_row["m"], u211_row["W"], u211_row["N"], u211_row["total_rank"], u211_row["maxchild"])
            == (72, 20634, 1936, 1483712, 60), "unpacked profile parameter mismatch")
    u205 = int_histogram(u205_row["child_multiplicities"], 72)
    u211 = int_histogram(u211_row["child_multiplicities"], 72)
    require(u211 == int_histogram(prof["child_histogram"], 72), "admitted profile differs from arithmetic unpacked")
    for hist in (u205, u211):
        require(sum(r * n for r, n in hist.items()) == u211_row["total_rank"], "unpacked histogram mass mismatch")

    du = Counter(u211)
    du.subtract(u205)
    du_nonzero = {r: v for r, v in sorted(du.items()) if v}
    require(bool(du_nonzero) and all(1 <= r <= 19 and v % 3 == 0 for r, v in du_nonzero.items()),
            "unpacked delta must be supported on internal ranks 1..19 in multiples of 3")
    require(sum(r * v for r, v in du_nonzero.items()) == 0, "unpacked delta does not conserve rank mass")
    require(sum(du_nonzero.values()) == 531, "unpacked child-count delta mismatch")

    p205_row, p211_row = c205["physical"], c211["physical"]
    shared_phys_keys = (
        "W", "m", "copies", "banks", "physical_roles", "interior_splices", "terminal_sinks",
        "gauge_roles", "distinct_gauges", "incidences", "rank_mass", "deficit", "maxchild",
        "chart_sha256", "incidence_sha256", "word_sha256", "max_chart_factors",
        "max_num", "max_den", "conservative_selector_calls", "patterns", "color_stats",
    )
    for key in shared_phys_keys:
        require(p205_row[key] == p211_row[key], "changed bank physical parameter: " + key)
    require((p211_row["m"], p211_row["W"], p211_row["copies"], p211_row["banks"], p211_row["rank_mass"],
             p211_row["deficit"], p211_row["maxchild"]) == (72, 56402, 3, 45842, 4055136, 5808, 22),
            "bank physical summary mismatch")

    for label, u_hist, p_row in (("PR205", u205, p205_row), ("PR211", u211, p211_row)):
        p_hist = int_histogram(p_row["child_histogram"], 72)
        expected_packed = {r: 3 * n for r, n in u_hist.items() if r != 60}
        require(u_hist.get(60) == 2200 and p_hist == expected_packed,
                "3-copy bank histogram projection mismatch: " + label)
        require(sum(r * n for r, n in p_hist.items()) == p_row["rank_mass"] == 72 * p_row["W"] - p_row["deficit"],
                "banked rank mass mismatch: " + label)

    dp = Counter(int_histogram(p211_row["child_histogram"], 72))
    dp.subtract(int_histogram(p205_row["child_histogram"], 72))
    require({r: v for r, v in sorted(dp.items()) if v} == {r: 3 * v for r, v in du_nonzero.items()},
            "banked histogram delta is not 3x the unpacked delta")
    require(sum(dp.values()) == 1593 and sum(r * v for r, v in dp.items()) == 0,
            "banked child-count or rank-mass delta mismatch")

    ar = c211["arithmetic"]
    coarse = Q(ar["bit_after"]["saving"])
    chain = [Q(x) for x in ar["ordinary_chain"]]
    require(len(chain) == 4 and chain[0] == Q(admitted["coarse"]["ordinary_saving"]),
            "ordinary leaf chain start mismatch")
    for j in range(1, 4):
        step = (1 - coarse) * coarse + coarse * chain[j - 1]
        require(chain[j] == step and chain[j - 1] < chain[j] < coarse < 1 - chain[j],
                "ordinary leaf recurrence mismatch")
    require(Q(ar["selector_toll_gap"]) == 1 - chain[-1] - coarse and Q(ar["selector_toll_gap"]) > 0,
            "selector toll gap mismatch")

    b = Q(ar["complex"]["saving"])
    eta = beta = Q(1, 10 ** 24)
    weak = Q(1, 10 ** 30)
    grid = Q(1, 10 ** 18)
    for key, saving in (("before_packing", chain[0]), ("after_packing", chain[-1])):
        a = min(saving, (1 - beta) * b - weak)
        require(a == saving < b, "bit supplier is not the binding side: " + key)
        q = a * (1 - 2 * eta)
        ceiling = (1 - eta) * q / (1 + q)
        kappa = Q(ar[key]["kappa"])
        require(kappa < ceiling <= kappa + grid, "assembly grid ceiling mismatch: " + key)

    kappa_after = Q(ar["after_packing"]["kappa"])
    kappa_before = Q(ar["before_packing"]["kappa"])
    kappa_207 = Q(ar["comparison_pr207_kappa"])
    kappa_205 = Q(ar["comparison_pr205_kappa"])
    require(kappa_after == Q(683847872495777, 10 ** 18), "PR211 conditional kappa mismatch")
    require(kappa_205 == Q(c205["arithmetic"]["after_packing"]["kappa"]) == Q(683061299399923, 10 ** 18),
            "PR205 comparison kappa mismatch")
    require(kappa_after > kappa_207 > kappa_205 > kappa_before, "kappa ordering mismatch")
    require(Q(ar["kappa_gain_from_packing"]) == kappa_after - kappa_before, "kappa_gain_from_packing mismatch")
    require(Q(ar["relative_gain_over_pr207"]) == kappa_after / kappa_207 - 1, "relative_gain_over_pr207 mismatch")

    return {
        "frame_bases": frame_summary,
        "terminal_sinks": 34,
        "terminal_child_delta": nonzero(term_delta),
        "unpacked_histogram_delta": nonzero(du),
        "unpacked_child_count_delta": sum(du_nonzero.values()),
        "unpacked_rank_mass_delta": 0,
        "banked_child_count_delta": sum(dp.values()),
        "banked_rank_mass_delta": 0,
        "unpacked_rank_per_vertex": u211_row["total_rank"],
        "banked_rank_mass": p211_row["rank_mass"],
        "banked_width_W": p211_row["W"],
        "banked_deficit": p211_row["deficit"],
        "pr205_conditional_kappa": str(kappa_205),
        "pr211_conditional_kappa": str(kappa_after),
        "round9_certificate_sections_verified": 5,
    }


def external_inputs():
    pins = loads((HERE / "SOURCES.json").read_bytes())
    require(pins["base_commit"] == BASE, "wrong research base")
    rows = {row["path"]: row for row in pins["files"] if row["usage"] == "input"}
    require(set(rows) == set(INPUTS), "external input coverage changed")
    loaded = {}
    for path in INPUTS:
        raw = (ROOT / path).read_bytes()
        require(hashlib.sha256(raw).hexdigest() == rows[path]["sha256"], "external source drift: " + path)
        require(git_id("blob", raw) == rows[path]["git_blob"], "external blob drift: " + path)
        loaded[path] = raw
    archive = loads(loaded["research/community-reconciliation-next100-audit/ARCHIVE.json"])
    reviews = loads(loaded["research/community-reconciliation-next100-audit/REVIEW.json"])
    r9_log = parse_round9_log(loaded["research/community-round9-audit/pr211-changed.log.txt"].decode("utf-8"))
    r9_ledger = loads(loaded["research/community-round9-audit/review-ledger.json"])
    contributors = (ROOT / "CONTRIBUTORS.md").read_text(encoding="utf-8") if (ROOT / "CONTRIBUTORS.md").is_file() else None
    return archive, reviews, r9_ledger, r9_log, contributors


def verify(document, archive, reviews, r9_ledger, r9_log, contributors=None):
    proof = Proof(document)
    mb_tree, _ = proof.commit(MERGE_BASE)
    pr205_tree, pr205_parents = proof.commit(PR205)
    pr211_tree, pr211_parents = proof.commit(PR211)
    require(pr205_parents == [MERGE_BASE], "PR205 comparison parent changed")
    require(pr211_parents == [PR205], "PR211 direct parent changed")

    _, packed_205 = proof.resolve(PR205, PACKED_DIR, "40000")
    _, packed_211 = proof.resolve(PR211, PACKED_DIR, "40000")
    require(packed_205 == packed_211 == PACKED_TREE, "inherited PR205 package tree differs in PR211")
    _, wf_205 = proof.resolve(PR205, PACKED_WORKFLOW, "100644")
    _, wf_211 = proof.resolve(PR211, PACKED_WORKFLOW, "100644")
    require(wf_205 == wf_211 == PACKED_WORKFLOW_BLOB, "inherited PR205 workflow blob differs in PR211")

    inherited_files = {PACKED_WORKFLOW: {"mode": "100644", "blob": wf_205}}
    for path, row in proof.inventory(packed_205).items():
        inherited_files[PACKED_DIR + "/" + path] = row
    require(len(inherited_files) == 12 and inherited_files == document["inherited_files"],
            "incomplete or changed inherited PR205 inventory")

    diff_inherited = proof.difference(mb_tree, pr205_tree)
    expected_inherited = {path: {"before": None, "after": row} for path, row in inherited_files.items()}
    require(diff_inherited == expected_inherited, "PR205 commit diff differs from the 12 inherited files")

    _, cascade_211 = proof.resolve(PR211, CASCADE_DIR, "40000")
    require(cascade_211 == CASCADE_TREE, "PR211 cascade-frames-bit tree mismatch")
    _, cwf_211 = proof.resolve(PR211, CASCADE_WORKFLOW, "100644")
    require(cwf_211 == CASCADE_WORKFLOW_BLOB, "PR211 cascade workflow blob mismatch")

    direct_files = {CASCADE_WORKFLOW: {"mode": "100644", "blob": cwf_211}}
    for path, row in proof.inventory(cascade_211).items():
        direct_files[CASCADE_DIR + "/" + path] = row
    require(len(direct_files) == 13 and direct_files == document["direct_files"],
            "incomplete or changed direct PR211 inventory")

    diff_direct = proof.difference(pr205_tree, pr211_tree)
    expected_direct = {path: {"before": None, "after": row} for path, row in direct_files.items()}
    require(diff_direct == expected_direct, "PR211 direct commit diff differs from the 13 cascade-frames-bit files")

    diff_full = proof.difference(mb_tree, pr211_tree)
    expected_full = {}
    expected_full.update(expected_inherited)
    expected_full.update(expected_direct)
    require(len(diff_full) == 25 and diff_full == expected_full,
            "PR211 merge-base diff differs from the 25 combined files")

    archive_tree, archive_parents = proof.commit(ARCHIVE)
    require(archive["commit"] == ARCHIVE and archive["tree"] == archive_tree
            and archive["parents"] == archive_parents, "archive receipt does not match its Git commit")
    for parent in (PR205, PR210, PR217):
        require(parent in archive_parents, "retaining parent absent from next100 archive: " + parent)

    expected_reviews = {
        "205": (PR205, "rohanarun"),
        "210": (PR210, "eumemic"),
        "217": (PR217, "hcg890"),
    }
    for pr_num, (head, login) in expected_reviews.items():
        require(reviews[pr_num]["head"] == head, f"next100 review #{pr_num} refers to a different head")
        require(reviews[pr_num]["contributor"]["login"] == login,
                f"next100 review #{pr_num} contributor mismatch")

    r9_prs = r9_ledger["prs"]
    r9_rows = [row for row in (r9_prs.values() if isinstance(r9_prs, dict) else r9_prs) if row.get("number") == 211]
    require(len(r9_rows) == 1, "missing PR211 entry in Round-9 review ledger")
    r9_211 = r9_rows[0]
    require(r9_211["head"] == PR211 and r9_211["author"] == "rohanarun",
            "Round-9 ledger PR211 head or author mismatch")
    require(r9_211["disposition"] == "complete-changed-work-replay-passed",
            "Round-9 ledger PR211 disposition mismatch")
    require(sorted(r9_211["source_files"]) == sorted(diff_full),
            "Round-9 ledger PR211 source_files mismatch")

    _, frames_211 = proof.resolve(PR211, CASCADE_DIR + "/opframe-bases.json", "100644")
    _, frames_210 = proof.resolve(PR210, PR210_FRAMES_PATH, "100644")
    require(frames_211 == frames_210 == FRAMES_BLOB, "PR210 does not retain the exact PR211 opframe-bases blob")

    _, frames_b64_217 = proof.resolve(PR217, PR217_FRAMES_B64_PATH, "100644")
    require(frames_b64_217 == FRAMES_B64_BLOB, "PR217 opframe-bases.json.gz.b64 blob mismatch")
    frames_b64_raw = proof.raw(frames_b64_217, "blob")
    frames_raw = gzip.decompress(base64.b64decode(frames_b64_raw.rstrip(b"\n"), validate=True))
    require(git_id("blob", frames_raw) == FRAMES_BLOB,
            "PR217 decompressed opframe-bases does not match PR211 Git blob")
    require(hashlib.sha256(frames_raw).hexdigest() == FRAMES_SHA256,
            "PR217 decompressed opframe-bases SHA256 mismatch")

    _, notice_211 = proof.resolve(PR211, CASCADE_DIR + "/NOTICE", "100644")
    _, notice_205 = proof.resolve(PR205, PACKED_DIR + "/NOTICE", "100644")
    _, notice_210 = proof.resolve(PR210, PR210_NOTICE_PATH, "100644")
    _, notice_217 = proof.resolve(PR217, PR217_NOTICE_PATH, "100644")
    require(notice_211 == notice_205 == notice_210 == notice_217 == NOTICE_BLOB,
            "NOTICE blob mismatch across PR211/PR205/PR210/PR217")
    require(proof.raw(notice_211, "blob") == (HERE / "UPSTREAM-NOTICE").read_bytes(),
            "original notice was not retained exactly in UPSTREAM-NOTICE")

    _, banks_211 = proof.resolve(PR211, CASCADE_DIR + "/banks.py", "100644")
    _, banks_205 = proof.resolve(PR205, PACKED_DIR + "/banks.py", "100644")
    require(banks_211 == banks_205 == BANKS_BLOB, "banks.py blob mismatch between PR211 and PR205")

    _, controls_211 = proof.resolve(PR211, CASCADE_DIR + "/controls.py", "100644")
    _, controls_205 = proof.resolve(PR205, PACKED_DIR + "/controls.py", "100644")
    require(controls_211 == controls_205 == CONTROLS_BLOB, "controls.py blob mismatch between PR211 and PR205")

    direct_payloads = {}
    for path, row in direct_files.items():
        if path == CASCADE_DIR + "/opframe-bases.json":
            direct_payloads[path] = frames_raw
        else:
            direct_payloads[path] = proof.raw(row["blob"], "blob")

    _, c205_oid = proof.resolve(PR205, PACKED_DIR + "/certificate.json", "100644")
    c205 = loads(proof.raw(c205_oid, "blob"))
    c211 = loads(direct_payloads[CASCADE_DIR + "/certificate.json"])
    source_meta = loads(direct_payloads[CASCADE_DIR + "/SOURCE.json"])
    bases = loads(frames_raw)

    accounting = check_accounting(c205, c211, r9_log, bases, source_meta)
    if contributors is not None:
        require("https://github.com/CrocSwap/integer-mult-bounds/pull/211" in contributors
                and "research/pr211-retention-receipt/README.md" in contributors,
                "CONTRIBUTORS.md missing PR211 attribution or receipt link")
    require(proof.used == set(proof.objects), "unused evidence objects")

    return {
        "status": "PASS_PR211_RETENTION_AND_CERTIFICATE_RECONCILIATION",
        "base_commit": BASE,
        "merge_base": MERGE_BASE,
        "parent_pr205_head": PR205,
        "original_pr211_head": PR211,
        "retaining_pr210_head": PR210,
        "retaining_pr217_head": PR217,
        "archive_commit": ARCHIVE,
        "inherited_package_tree": PACKED_TREE,
        "direct_package_tree": CASCADE_TREE,
        "frames_git_blob": FRAMES_BLOB,
        "frames_sha256": FRAMES_SHA256,
        "total_changed_paths": len(diff_full),
        "inherited_pr205_paths": len(inherited_files),
        "direct_pr211_paths": len(direct_files),
        "authenticated_git_objects": len(proof.used),
        "accounting": accounting,
        "fresh_physical_replay": False,
        "new_kappa_claim": False,
        "scope": "Complete PR211 25-path/13-direct-file source retention and saved-certificate reconciliation; no new construction acceptance.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--proof", type=Path, default=HERE / "SOURCE-PROOF.json")
    parser.add_argument("--write-result", type=Path,
                        help="write a newly recomputed receipt instead of comparing RESULT.json")
    args = parser.parse_args()
    result = verify(loads(args.proof.read_bytes()), *external_inputs())
    if args.write_result:
        args.write_result.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    else:
        require(result == loads((HERE / "RESULT.json").read_bytes()), "saved result differs from recomputation")
    acc = result["accounting"]
    print(f"{result['status']} paths={result['total_changed_paths']} direct={result['direct_pr211_paths']} "
          f"frames={acc['frame_bases']['changed_frames']} child_delta={acc['unpacked_child_count_delta']} "
          f"mass_delta={acc['unpacked_rank_mass_delta']}")


if __name__ == "__main__":
    main()
