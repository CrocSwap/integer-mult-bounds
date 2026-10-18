# SPDX-License-Identifier: Apache-2.0
"""Bind the stored invoice to actual six-skip native and stock receipts."""

from fractions import Fraction

from word_check import need


def provider(value, native, declared, replay):
    need(value["paid_profile"] == declared["actual_paid_profile"], "invoice local profile")
    need(value["widths"] == declared["widths"], "invoice ordered widths")
    files = native["complete_native_files"]
    need(len(value["artifacts"]) == 11, "complete provider artifacts")
    for name, digest in value["artifacts"].items():
        need(files.get("local/" + name) == digest, "invoice native artifact: " + name)
    need(replay["canonical_word_sha256"] == files["local/CANONICAL-WORD.json.gz"] and
         replay["local_programs_sha256"] == files["local/LOCAL-PROGRAMS.json.gz"],
         "native replay source artifacts")
    bits = []
    for direction in ("forward", "backward"):
        local = replay["local"][direction]
        need(replay["paid_profiles"][direction] == declared["actual_paid_profile"],
             "native replay profile")
        upper = local["prefix_bits_upper"]
        need(type(upper) is int and 0 <= upper <= 128, "native local prefix reserve")
        need(0 < Fraction(local["prefix_l1_upper"]) <= 2 ** upper, "native prefix magnitude")
        need(value["local"][direction]["prefix_bits"] == upper,
             "invoice authenticated local prefix")
        need(local["all_exact_columns"] == 632 and local["private_work_erased"] is True
             and local["zero_buffers_returned_to_zero"] == 91, "native dirty returns")
        bits.append(upper)
    return max(bits)


def validate(invoice, native, declarations, replays, stock):
    need(invoice["status"] == "PASS_INDEPENDENT_MIXED_ASYNC_SCALAR_PREFIX_AND_FINITE_INVOICE",
         "accepted finite invoice status")
    checks = {"local_primitive_bound", "logical", "router", "literal", "mass",
              "precision", "tape", "row", "halving"}
    need(set(invoice["strict_checks"]) == checks and
         all(value is True for value in invoice["strict_checks"].values()), "all invoice checks")
    need(set(invoice["providers"]) == {"gauge44", "extra"}, "invoice providers")
    prefix = max(provider(invoice["providers"][pid], native["providers"][tag],
                          declarations[pid], replays[tag])
                 for pid, tag in (("gauge44", "base"), ("extra", "extra")))
    need(invoice["provider_counts"] == {"gauge44": 2500, "extra": 4160}, "dispatch counts")
    need(len(invoice["selected_calls"]) == invoice["complete_invocation_sweeps"] ==
         invoice["bridge_sweeps"] == 6660, "complete T740 invocation bill")
    paid = {int(r): 6660 * n for r, n in declarations["gauge44"]["actual_paid_profile"].items()}
    need({int(r): n for r, n in invoice["selected_local_paid_profile"].items()} == paid,
         "invoice selected local children")
    need((invoice["physical"], invoice["live"], invoice["private_zero_buffers"])
         == (stock["physical"], stock["live"], 91), "invoice physical bill")
    bn = invoice["blocknorm"]
    expected = {"replicas": 740, "physical_families": stock["physical"],
                "live_families": stock["live"], "max_active_depth": 18,
                "input_l2_bits": 37, "stock_l2_bits": stock["stock_l2_bits"],
                "physical_stock_bits": stock["group_order_times_physical_bit_length"],
                "local_actual_prefix_bits": prefix, "local_reserve_bits": 128,
                "required_reserve_bits": stock["reserve"], "retained_payload_bits": 2048,
                "partial_cover_bits": 1}
    need(all(bn[k] == value for k, value in expected.items()), "invoice blocknorm formula")
    global_bits = prefix + 37 + 18 + stock["stock_l2_bits"] + 1 + 4
    need(invoice["global_prefix_bits"] == bn["actual_prefix_bits"] == global_bits <= 2048,
         "invoice exact global prefix formula")
    need(invoice["charged_prefix_bits"] == 2048, "invoice charged payload")
    return {"local_prefix_bits": prefix, "global_prefix_bits": global_bits,
            "physical": stock["physical"]}
