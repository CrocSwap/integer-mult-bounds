"""Source-bound complete-price admission adapter; Python standard library only.

The trusted policy is a reviewer-maintained capability: never derive it from a
candidate. It pins independent receipt bytes, source dependencies, and the exact
model domain. The oracle checks compatibility and consumes those receipts; it
is not a new physical proof, interval engine, or authority to select a result.
No file I/O, network, mutable global registry, binary floats, or hidden zero costs.
"""
from fractions import Fraction
from hashlib import sha256
import json
import re

VERSION = "source-bound-price-oracle/v1"
PLANES = ("paid_productive", "ordinary", "ownership_stock", "precision_tape",
          "compiler_reserves", "bit_outer")
ASSUMPTIONS = ("native_all_columns", "owned_erasure", "compiler", "precision_tape",
               "analytic_recovery")
LABELS = ("MODEL_ONLY", "WITNESS_READY", "PHYSICAL_CHECKED", "COMPLETE_BILL_READY",
          "FUNDED_CONDITIONAL", "PUBLIC_REVIEWABLE", "SELECTED")
COST_STATES = ("proved", "constructively_upper_bounded", "optimistically_relaxed", "unknown")
# These are coverage obligations, not claims that all cost items are numerically
# comparable or that scalar costs may be inserted into the recursive moment.
COVERAGE = {
    "physical": ("literal_all_columns", "arbitrary_owned_entries", "frames_phases_spectators",
                 "chronology_restoration", "independent_productive_credit"),
    "census": ("complete_paid_targets", "event_reconciliation", "alias_exclusions",
               "ordinary_charge_inventory"),
    "closure": ("disjoint_live_banks", "expanded_W_P_O_R_G_N", "precision_error_growth",
                "fixed_tape_eventual_threshold", "source_lemma_applicability"),
    "arithmetic": ("recursive_moment", "reserve_completion_rounding", "shifted_exit_capacity",
                   "uniform_compiler_height", "adjacent_grid", "strong_bit_admission",
                   "outer_predicate_inventory"),
    "publication": ("exact_head_export", "registered_normal_optimized", "public_review_url"),
}
HEX64 = re.compile(r"[0-9a-f]{64}\Z")
HEX40 = re.compile(r"[0-9a-f]{40}\Z")

class ContractError(ValueError):
    """An incompatible/untrusted input, not a mathematical counterexample."""


def digest(raw):
    return sha256(raw).hexdigest()


def encode(obj):
    """Canonical output encoding. Input SHA always binds original literal bytes."""
    return (json.dumps(obj, sort_keys=True, indent=2, allow_nan=False) + "\n").encode()


def _no_float(value):
    if isinstance(value, float):
        raise ContractError("BINARY_FLOAT_FORBIDDEN")
    if isinstance(value, dict):
        for item in value.values():
            _no_float(item)
    elif isinstance(value, list):
        for item in value:
            _no_float(item)


def decode(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ContractError("DUPLICATE_JSON_KEY:" + key)
            result[key] = value
        return result
    obj = json.loads(raw, object_pairs_hook=pairs,
                     parse_constant=lambda x: (_ for _ in ()).throw(ContractError("NONFINITE_JSON")))
    _no_float(obj)
    return obj


def q(value):
    if isinstance(value, bool) or not isinstance(value, (str, int)):
        raise ContractError("EXACT_RATIONAL_REQUIRED")
    try:
        return Fraction(value)
    except (ValueError, ZeroDivisionError) as exc:
        raise ContractError("BAD_RATIONAL") from exc


def _require(condition, message):
    if not condition:
        raise ContractError(message)


def _artifact(key, artifacts):
    _require(isinstance(key, str) and HEX64.fullmatch(key), "BAD_ARTIFACT_SHA256")
    _require(key in artifacts, "MISSING_ARTIFACT:" + key)
    raw = artifacts[key]
    _require(isinstance(raw, bytes) and digest(raw) == key, "ARTIFACT_HASH_MISMATCH:" + key)
    return raw


def profile_hash(profile):
    return digest(encode(profile))


def _hist(hist):
    _require(isinstance(hist, dict) and hist, "EMPTY_HISTOGRAM")
    for rank, count in hist.items():
        _require(isinstance(rank, str) and rank.isdigit() and str(int(rank)) == rank and int(rank) > 0,
                 "INVALID_RANK")
        _require(type(count) is int and count >= 0, "INVALID_MULTIPLICITY")
    _require(any(hist.values()), "ZERO_HISTOGRAM")


def exact_rank_totals(profile):
    """Integer census summary, not a nonintegral-exponent moment evaluation."""
    for key in ("paid", "productive"):
        _hist(profile[key])
    return {key: {"jobs": sum(profile[key].values()),
                  "rank_mass": sum(int(r) * n for r, n in profile[key].items())}
            for key in ("paid", "productive")}


def _receipt(role, candidate_sha, c, artifacts, policy):
    ref = c.get("receipts", {}).get(role)
    if ref is None:
        return None
    _require(role in policy.get("receipt_sha256", {}), "UNTRUSTED_RECEIPT_ROLE:" + role)
    _require(ref == policy["receipt_sha256"][role], "UNTRUSTED_RECEIPT_SHA256:" + role)
    r = decode(_artifact(ref, artifacts))
    _require(r.get("schema") == "source-bound-price-receipt/v1", "RECEIPT_SCHEMA:" + role)
    _require(r.get("role") == role and r.get("independent") is True, "RECEIPT_ROLE:" + role)
    # Candidate receipt attachment would make a digest cycle. Receipts instead
    # bind immutable scientific_payload_sha256, which excludes receipt references.
    _require(r.get("scientific_payload_sha256") == candidate_sha, "STALE_RECEIPT_PAYLOAD:" + role)
    _require(r.get("scientific_head") == c["scientific_head"], "STALE_RECEIPT_HEAD:" + role)
    _require(r.get("profile_sha256") == profile_hash(c["profile"]), "STALE_RECEIPT_PROFILE:" + role)
    _require(r.get("source_dependencies") == c["source_dependencies"], "STALE_RECEIPT_DEPENDENCY:" + role)
    _require(set(r.get("coverage", ())) >= set(COVERAGE[role]), "INCOMPLETE_RECEIPT_COVERAGE:" + role)
    _require(r.get("open_obligations") == [], "OPEN_RECEIPT_OBLIGATIONS:" + role)
    _require(r.get("evidence_sha256"), "MISSING_RECEIPT_EVIDENCE:" + role)
    for evidence in r["evidence_sha256"]:
        _artifact(evidence, artifacts)
    if role == "physical" and policy.get("require_word_delta"):
        transfer = r.get("proof_transfer", {})
        _require(transfer.get("schema") == "explicit-word-delta-transfer/v1", "MISSING_WORD_DELTA_RECEIPT")
        _require(transfer.get("old_word_sha256") == policy.get("prior_word_sha256"), "STALE_TRANSFER_OLD_WORD")
        _require(transfer.get("new_word_sha256") == c.get("literal_witness_sha256"), "STALE_TRANSFER_NEW_WORD")
        _require(transfer.get("basis_physical_receipt_sha256") == policy.get("basis_physical_receipt_sha256"),
                 "UNTRUSTED_TRANSFER_BASIS")
        _require(transfer.get("word_delta_receipt_sha256") == policy.get("word_delta_receipt_sha256"),
                 "UNTRUSTED_WORD_DELTA")
        _require(transfer.get("invoice_sha256") == c["source_dependencies"].get("invoice"),
                 "TRANSFER_NOT_BOUND_TO_NEW_INVOICE")
        _require(transfer.get("changed_dependencies") and set(transfer["changed_dependencies"]) >=
                 set(policy.get("changed_dependencies", [])), "UNCOVERED_WORD_DELTA")
        for dep in (transfer["old_word_sha256"], transfer["new_word_sha256"],
                    transfer["basis_physical_receipt_sha256"], transfer["word_delta_receipt_sha256"],
                    transfer["invoice_sha256"]):
            _artifact(dep, artifacts)
    return r


def scientific_payload(c):
    return {key: value for key, value in c.items() if key not in ("receipts", "requested_label")}


def evaluate(candidate_bytes, artifacts, policy):
    """Pure compatibility/admission evaluation against separately trusted policy.

    Contract violations raise ContractError. Scientifically incomplete but valid
    candidates return explicit blocking obligations and the strongest justified
    label. Receipt role digests must be installed in policy by a reviewer after
    examining the underlying raw evidence; arbitrary authored PASS is ignored.
    """
    c = decode(candidate_bytes)
    _no_float(policy)
    _require(c.get("schema") == "source-bound-price-candidate/v1", "CANDIDATE_SCHEMA")
    cid = c.get("candidate_id")
    _require(cid == policy.get("candidate_id"), "CANDIDATE_ID_MISMATCH")
    payload_sha = digest(encode(scientific_payload(c)))
    _require(payload_sha == policy.get("scientific_payload_sha256"), "UNTRUSTED_SCIENTIFIC_PAYLOAD")
    _require(HEX40.fullmatch(c.get("scientific_head", "")) is not None, "BAD_SCIENTIFIC_HEAD")
    _require(c["scientific_head"] == policy.get("scientific_head"), "STALE_SCIENTIFIC_HEAD")
    _require(c.get("canonical_comparison_base") == policy.get("canonical_comparison_base"), "STALE_CANONICAL_BASE")
    _require(c.get("source_dependencies") == policy.get("source_dependencies"), "STALE_SOURCE_DEPENDENCIES")
    _require(c["source_dependencies"], "NO_SOURCE_DEPENDENCIES")
    for dep in c["source_dependencies"].values():
        _artifact(dep, artifacts)
    _require(c.get("attribution"), "MISSING_ATTRIBUTION")
    _require(tuple(c.get("assumptions", ())) == ASSUMPTIONS, "ALTERED_ASSUMPTIONS_REQUIRE_NEW_POLICY")
    model = c.get("model", {})
    _require(model.get("id") == policy.get("model_id"), "UNSUPPORTED_MODEL")
    _require(model.get("parameters") in policy.get("parameter_domain", []), "OUTSIDE_PROVED_DOMAIN")
    _require(model.get("theorem_evidence_sha256") in c["source_dependencies"].values(), "UNBOUND_MODEL_THEOREM")
    totals = exact_rank_totals(c["profile"])
    _require(c["profile"].get("paid_jobs") == totals["paid"]["jobs"], "PAID_CENSUS_MISMATCH")
    _require(c["profile"].get("productive_jobs") == totals["productive"]["jobs"], "PRODUCTIVE_CENSUS_MISMATCH")
    exclusions = c["profile"].get("excluded_productive_credit", {})
    _require(exclusions == {"aliases": 0, "copies": 0, "surrendered": 0}, "ILLEGAL_PRODUCTIVE_CREDIT")
    planes = c.get("planes", {})
    _require(set(planes) == set(PLANES), "SIX_PLANES_REQUIRED")
    blockers, plane_output = [], {}
    for plane in PLANES:
        entries = planes[plane]
        _require(isinstance(entries, list) and entries, "EMPTY_PLANE:" + plane)
        ids = [entry.get("id") for entry in entries]
        _require(len(set(ids)) == len(ids), "DUPLICATE_COST_ENTRY:" + plane)
        _require(set(ids) == set(policy["charge_inventory"][plane]), "MISSING_OR_EXTRA_CHARGE:" + plane)
        for entry in entries:
            state = entry.get("state")
            _require(state in COST_STATES, "INVALID_COST_STATE")
            _require(entry.get("unit") and entry.get("invalidation_conditions"), "UNTYPED_COST:" + entry["id"])
            _require(entry.get("dependency_hashes"), "UNBOUND_COST:" + entry["id"])
            for dep in entry["dependency_hashes"]:
                _artifact(dep, artifacts)
            if state == "unknown":
                _require(entry.get("value_or_symbol") is None, "UNKNOWN_COST_CANNOT_HAVE_NUMERIC_VALUE")
                blockers.append("UNKNOWN_COST:" + plane + ":" + entry["id"])
            else:
                _require(entry.get("value_or_symbol") is not None and entry.get("evidence_sha256"),
                         "MISSING_COST_VALUE_OR_EVIDENCE:" + entry["id"])
                for evidence in entry["evidence_sha256"]:
                    _artifact(evidence, artifacts)
                if state == "optimistically_relaxed":
                    blockers.append("OPTIMISTIC_COST:" + plane + ":" + entry["id"])
        plane_output[plane] = {"states": sorted(set(e["state"] for e in entries)),
                               "entries": entries}
    receipts = {role: _receipt(role, payload_sha, c, artifacts, policy) for role in COVERAGE}
    label = "MODEL_ONLY"
    if c.get("literal_witness_sha256"):
        _artifact(c["literal_witness_sha256"], artifacts)
        label = "WITNESS_READY"
    if receipts["physical"]:
        _require(label == "WITNESS_READY", "PHYSICAL_RECEIPT_WITHOUT_LITERAL_WITNESS")
        label = "PHYSICAL_CHECKED"
    complete = label == "PHYSICAL_CHECKED" and receipts["census"] and receipts["closure"] and not blockers
    if complete:
        label = "COMPLETE_BILL_READY"
    a = receipts["arithmetic"]
    funded = None
    if a:
        _require(a.get("invoice_receipt_sha256") == c.get("receipts", {}).get("census"), "ARITHMETIC_NOT_BOUND_TO_CENSUS")
        _require(a.get("closure_receipt_sha256") == c.get("receipts", {}).get("closure"), "ARITHMETIC_NOT_BOUND_TO_CLOSURE")
        _require(a.get("model") == model, "ARITHMETIC_MODEL_MISMATCH")
        _require(a.get("endpoint_funded") is True, "ENDPOINT_NOT_FUNDED")
        funded = q(a["funded_kappa"])
        tested = q(a["tested_saving"])
        lo, hi = map(q, a["raw_root_interval"])
        _require(0 < funded < tested < lo < hi < 1, "UNFUNDED_ENDPOINT_OR_ROOT")
        _require(q(a["root_sign_intervals"][0][0]) > 0 and q(a["root_sign_intervals"][1][1]) < 0,
                 "RAW_ROOT_SIGNS_NOT_STRICT")
        _require(a.get("compiler_domain") == model["parameters"], "UNSUPPORTED_COMPILER_TUPLE")
        inventory = policy.get("outer_predicate_ids", {})
        _require(set(a.get("strict_slacks", {})) == set(inventory.get("strict", [])) and bool(inventory.get("strict")),
                 "OUTER_STRICT_INVENTORY_MISMATCH")
        _require(set(a.get("functional_slacks", {})) == set(inventory.get("functional", [])) and bool(inventory.get("functional")),
                 "OUTER_FUNCTIONAL_INVENTORY_MISMATCH")
        for name, slack in a["strict_slacks"].items():
            _require(q(slack) > 0, "NONPOSITIVE_STRICT_SLACK:" + name)
        for name, slack in a["functional_slacks"].items():
            _require(q(slack) > 0, "NONPOSITIVE_FUNCTIONAL_SLACK:" + name)
        _require(a.get("checks") and all(type(v) is bool and v for v in a["checks"].values()), "FAILED_ARITHMETIC_CHECK")
        _require(set(a["checks"]) >= set(policy.get("arithmetic_check_ids", [])), "MISSING_ARITHMETIC_CHECK")
        _require(a.get("same_five_assumptions") is True, "EXTRA_FUNDING_ASSUMPTION")
        if complete:
            label = "FUNDED_CONDITIONAL"
        else:
            blockers.append("FUNDING_RECEIPT_PENDING_COMPLETE_PHYSICAL_BILL")
    if label == "FUNDED_CONDITIONAL" and receipts["publication"]:
        pub = receipts["publication"]
        _require(pub.get("review_head") == policy.get("public_review_head"), "STALE_PUBLIC_REVIEW_HEAD")
        _require(isinstance(pub.get("url"), str) and pub["url"].startswith("https://github.com/"), "INVALID_PUBLIC_REVIEW_URL")
        label = "PUBLIC_REVIEWABLE"
    # Selected status is an authenticated read-only import, never a requested
    # transition and never inferred from successful arithmetic/publication.
    if label == "PUBLIC_REVIEWABLE" and policy.get("selected_snapshot_sha256"):
        selected = decode(_artifact(policy["selected_snapshot_sha256"], artifacts))
        _require(selected.get("scientific_head") == c["scientific_head"] and
                 q(selected.get("kappa")) == funded, "SELECTED_SNAPSHOT_MISMATCH")
        label = "SELECTED"
    requested = c.get("requested_label", "MODEL_ONLY")
    _require(requested in LABELS, "INVALID_REQUESTED_LABEL")
    _require(LABELS.index(requested) <= LABELS.index(label), "UNSUPPORTED_PROMOTION:" + requested)
    for role in ("physical", "census", "closure", "arithmetic"):
        if not receipts[role]:
            blockers.append("MISSING_INDEPENDENT_RECEIPT:" + role)
    return {"schema": VERSION, "candidate_id": cid, "scientific_payload_sha256": payload_sha,
            "scientific_head": c["scientific_head"], "label": label,
            "funded_kappa": str(funded) if funded is not None and LABELS.index(label) >= LABELS.index("FUNDED_CONDITIONAL") else None,
            "arithmetic_claim_kappa": str(funded) if funded else None,
            "totals": totals, "planes": plane_output, "blocking_obligations": blockers,
            "optimization_scope": policy.get("optimization_scope"),
            "selected_is_read_only": True}


def source_moment_screen(profile, saving, backend, domain):
    """Use independent engine only on an explicitly source-certified domain.

    backend(histogram, exact exponent) -> (Fraction lower, Fraction upper).
    This necessary recursive screen never assigns an admission label.
    """
    c = q(saving)
    _require(domain.get("profile_sha256") == profile_hash(profile), "OUTSIDE_PROVED_PROFILE_DOMAIN")
    _require(domain.get("model_id"), "MISSING_SOURCE_MODEL_DOMAIN")
    _require(q(domain["saving_min"]) <= c <= q(domain["saving_max"]), "OUTSIDE_PROVED_DOMAIN")
    exact_rank_totals(profile)
    tlo, thi = backend(profile["productive"], 1-c)
    plo, phi = backend(profile["paid"], 1-c)
    _require(all(isinstance(v, Fraction) for v in (tlo, thi, plo, phi)) and tlo <= thi and plo <= phi,
             "BACKEND_REQUIRES_ORDERED_RATIONAL_INTERVALS")
    lower, upper = tlo-phi, thi-plo
    return {"schema": "necessary-recursive-screen/v1", "saving": str(c),
            "margin_interval": [str(lower), str(upper)],
            "decision": "REJECT_EXACT_PROFILE_TARGET" if upper <= 0 else
                        "POSITIVE_NECESSARY_SCREEN_ONLY" if lower > 0 else "UNRESOLVED_INTERVAL",
            "admission_label": "MODEL_ONLY", "unknown_ordinary_cost_is_zero": False}
