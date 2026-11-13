#!/usr/bin/env python3
"""Read-only, source-only replay for the public one-relation price screen."""
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import sys

PACKAGE = Path(__file__).resolve().parent
VERIFIER = PACKAGE / "verifier"
EXPECTED_WORD = "acee323696b18914bd863d55341f92112b48d3d1dc1443c276efb6c396fcc0a9"
EXPECTED_PAYLOAD = "64fca675b91298868e12f09423b47e0c2327cba7095e35c8919c1953b4ed68b8"
EXPECTED_CALLER = "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc"
EXPECTED_INVOICE = "86f71ccbc923db5d7a6753aa971c3a9c8a572680534498ed17be072cfa2aae6b"
EXPECTED_RECORDS = "4db450ed8d88b2617f88b80609af56d4b255682a07420970973e6a8646d97844"
EXPECTED_SAMPLE_CHECK = "08bc3bbdee447461f62b4781130321270a32deac19cd2e3d9671a919987decc2"
EXPECTED_EVENTS = [40710, 43183, 39929, 46241, 41697, 44603, 33204, 33779,
                   37903, 37906, 32222, 32615, 38170, 38401, 28367, 28388]


def need(condition, message):
    if not condition:
        raise ValueError(message)


def canonical_hash(value):
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return sha256(payload).hexdigest()


def load_module(name, path):
    spec = importlib.util.spec_from_file_location("p104_public_price_" + name, path)
    need(spec is not None and spec.loader is not None, "load module " + name)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def checked_hash(raw, expected, label):
    need(sha256(raw).hexdigest() == expected, label)


def rejects_wrong_hash(raw, expected, label):
    try:
        checked_hash(raw, expected, label)
    except ValueError:
        return True
    return False


def run():
    word_raw = (PACKAGE / "inputs/WORD.json.gz").read_bytes()
    caller_raw = (PACKAGE / "inputs/CALLER.json").read_bytes()
    invoice_raw = (PACKAGE / "inputs/CURRENT-PRICE.json").read_bytes()
    checked_hash(word_raw, EXPECTED_WORD, "exact #7481 WORD bytes")
    checked_hash(caller_raw, EXPECTED_CALLER, "exact signed caller bytes")
    checked_hash(invoice_raw, EXPECTED_INVOICE, "exact complete invoice bytes")
    altered = word_raw[:-1] + bytes((word_raw[-1] ^ 1,))
    need(rejects_wrong_hash(altered, EXPECTED_WORD, "mutated WORD bytes"),
         "executed source-byte mutation control")

    scan = load_module("scan", VERIFIER / "scan.py")
    paired = load_module("paired", VERIFIER / "paired_prices.py")
    samples = load_module("crosscheck", VERIFIER / "crosscheck_samples.py")
    profiles = load_module("profile_sign", VERIFIER / "profile_sign_check.py")
    prices = load_module("prices", VERIFIER / "integer_prices.py")

    main_doc = scan.run()
    paired_doc = paired.run()
    sample_check = samples.check(main_doc, paired_doc)
    sign_check = profiles.check(paired_doc, prices)

    need(main_doc["source_sha256"] == paired_doc["source_sha256"] == EXPECTED_WORD,
         "main and paired methods use the pinned word")
    need(main_doc["source_payload_sha256"] == paired_doc["source_payload_sha256"] == EXPECTED_PAYLOAD,
         "canonical source payload agrees")
    need(main_doc["caller_sha256"] == paired_doc["caller_sha256"] == EXPECTED_CALLER,
         "both methods use the exact caller")
    need(main_doc["invoice_sha256"] == paired_doc["invoice_sha256"] == EXPECTED_INVOICE,
         "both methods use the exact complete invoice")
    need(main_doc["move_count"] == paired_doc["move_count"] == 6279,
         "complete MOVE census")
    need(main_doc["frame_count"] == 1096 and main_doc["all_move_frame_pairs_nested"],
         "frame count and nested MOVE geometry")
    need(main_doc["helper_only_move_count"] == paired_doc["helper_only_move_count_separate"] == 468,
         "468 helper-only targets separated")
    need(main_doc["screen_classes_all_moves"] == {"main_hit": 1080, "main_miss": 4731},
         "independent main-projection screen counts")
    need(main_doc["screen_classes_by_owner"] == {
        "main_hit|owned": 14, "main_hit|public": 1066,
        "main_miss|owned": 33, "main_miss|public": 4698},
         "owned/public main-projection classification")
    need(main_doc["public_nonzero_main_history_hit_rank_counts"] == {
        1:611,2:128,3:177,4:27,5:111,6:4,7:6,8:2},
         "all public main-history-hit rank counts")
    need(main_doc["selected_events"] == EXPECTED_EVENTS and main_doc["selected_count"] == 16,
         "same deterministic 16 full-L witness sample")
    need(main_doc["selected_full_history_misses"] == 16 and
         main_doc["selected_full_history_hits"] == 0,
         "all selected full-L witnesses are strict full-history misses")
    need(len(sample_check["sampled_events"]) == 16 and
         sample_check["status"] == "PASS" and
         canonical_hash(sample_check) == EXPECTED_SAMPLE_CHECK,
         "all 16 direct full-L witnesses and deterministic receipt hash")

    records_digest = canonical_hash(paired_doc["records"])
    need(records_digest == EXPECTED_RECORDS,
         "canonical SHA256 of complete all-1,066 record census")
    mutated = [dict(row) for row in paired_doc["records"]]
    mutated[0]["minimum_enabling_relation_rank"] += 1
    need(canonical_hash(mutated) != EXPECTED_RECORDS,
         "executed census-content mutation control")
    need(paired_doc["public_main_history_hit_count"] == 1066 and
         paired_doc["public_full_history_miss_count"] == 1066 and
         paired_doc["public_full_history_hit_count"] == 0,
         "all 1,066 public candidates are full-history misses")
    need(paired_doc["saving_class_counts"] == {
        "negative":253,"positive":376,"zero_or_interval_overlap":437},
         "exact all-1,066 price class counts")
    need(sign_check["counts"] == {"equal":437,"negative":253,"positive":376},
         "rank-difference sign theorem and exact cancellation census")
    need(paired_doc["native_calls"] == 17,
         "actual complete signed caller has 17 native calls")
    need(paired_doc["best_single_relation_saving"]["event"] == 40710 and
         paired_doc["best_single_relation_saving"]["target_rank"] == 8 and
         paired_doc["best_single_relation_saving"]["minimum_helper_target_rank"] == 1,
         "best gross per-target price is the rank-8 to rank-1 profile")
    need(paired_doc["best_single_relation_saving"]["exact_interval"] == [
        "6937034079270974725608699/1000000000000000000000000",
        "69370340792709747256087/10000000000000000000000"],
         "certified exact f(8)-f(1) interval")
    need(paired_doc["best_single_relation_saving"]["beats_required_per_call"],
         "best optimistic single-target rank-price interval exceeds per-call threshold")
    need(paired_doc["required_net_native_saving_per_call_0038"] == [
        "2369677355374996009685597/680000000000000000000000",
        "29620966942187450121094791/8500000000000000000000000"],
         "exact interval for the full 17-call per-call threshold")
    need(paired_doc["baseline_full_signed_moment_0038"]["exact"] == [
        "-29620966942187450121094791/500000000000000000000000",
        "-2369677355374996009685597/40000000000000000000000"],
         "complete signed moment at kappa 0.0038")

    best_sample = next(row for row in main_doc["candidate_relations"] if row["event"] == 40710)
    need(best_sample["minimum_enabling_relation"] == {
        "1459":"-1", "705":"-1", "885":"1"},
         "event 40710 exact helper-only relation")
    need(best_sample["target"] == {"885":"1", "943":"1"} and
         best_sample["destination"] == 189 and best_sample["source"] == 3,
         "event 40710 exact source/destination and target")

    receipt = {
        "status": "PASS_P104_PUBLIC_CACHE_PRICE_SCREEN",
        "source": {"word_sha256": EXPECTED_WORD, "payload_sha256": EXPECTED_PAYLOAD,
                    "caller_sha256": EXPECTED_CALLER, "invoice_sha256": EXPECTED_INVOICE},
        "source_only_read_only": True,
        "method_results": {"main_projection": "PASS", "paired_exact_Q_prices": "PASS",
                            "direct_full_L_samples": "PASS"},
        "main_screen": {
            "moves": 6279, "helper_only_separate":468,
            "main_hits":1080,"main_misses":4731,
            "public_main_hits":1066,"public_main_misses":4698,
            "owned_main_hits":14,"owned_main_misses":33,
            "public_hit_rank_counts":main_doc["public_nonzero_main_history_hit_rank_counts"],
            "sample_events":EXPECTED_EVENTS,
            "sample_full_L_receipt_sha256":canonical_hash(sample_check),
            "sample_crosscheck":sample_check["sampled_events"],
        },
        "all_1066_census": {
            "record_count":1066,"full_history_misses":1066,
            "canonical_record_sha256":records_digest,
            "sign_counts":sign_check["counts"],
            "sign_law":sign_check["sign_law"],
        },
        "best_optimistic_single_target": {
            "event":40710,"owner":885,"move":"3->189","target_rank":8,
            "relation":{"1459":"-1","705":"-1","885":"1"},
            "minimum_original_helper_target_rank":1,
            "gross_saving_interval":paired_doc["best_single_relation_saving"]["exact_interval"],
            "exceeds_per_call_threshold_before_implementation_costs":True,
        },
        "complete_17_call_price_gate": {
            "baseline_moment_0038":paired_doc["baseline_full_signed_moment_0038"]["exact"],
            "calls":17,
            "required_saving_per_call_0038":paired_doc["required_net_native_saving_per_call_0038"],
        },
        "executed_controls": {
            "mutated_source_bytes_rejected":True,
            "mutated_census_content_changes_hash":True,
            "equal_rank_dict_collision_rejected":sign_check["negative_control"]["rejected"],
        },
        "limitations": "Optimistic per-target rank-price screen only. It does not show that all candidate prices can be funded simultaneously, that the relation can be physically prepared or used, or that the public MOVE can be deleted/reframed. It does not claim source admission, a full supplier, a kappa gain, or a multiplication theorem. Separate A54 preparation analysis requires an additional initial-access premise and is not part of this result.",
    }
    print(json.dumps(receipt, sort_keys=True, indent=2))
    return receipt


if __name__ == "__main__":
    run()
