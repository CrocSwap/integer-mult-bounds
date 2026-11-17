"""Freeze a fresh isolated candidate application over the authenticated #7605 source."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import shutil


HERE = Path(__file__).resolve().parent
PACKAGE = Path("research/p104-timed-helper757")
BASE_APPLICATION = "b46e39f81116aaa2feb3283d0e53bf95608313240b16e96f174b43fa7b4ab69e"
PUBLIC_CLAIM = "0.0036506661663"


def replace_exact(text, before, after):
    if text.count(before) != 1:
        raise ValueError(f"Expected unique source text {before!r}")
    return text.replace(before, after)


def replace_function(text, begin, next_begin, replacement):
    start = text.index(f"def {begin}(")
    end = text.index(f"def {next_begin}(", start + 1)
    return text[:start] + replacement + text[end:]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-checkout", type=Path, required=True)
    parser.add_argument("--overlay", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--peer-edits", type=Path, required=True)
    parser.add_argument("--invoice-receipt", type=Path, required=True)
    args = parser.parse_args()
    src = args.source_checkout / PACKAGE
    source_text = (src / "application.py").read_bytes()
    assert sha256(source_text).hexdigest() == BASE_APPLICATION
    if args.overlay.exists():
        raise ValueError("Overlay must be new")
    shutil.copytree(src, args.overlay)
    data = args.overlay / "data"
    for name in ("word.json.gz", "NATIVE.json", "SIGNED.json", "FINAL.json"):
        prefix = "WORD.json.gz" if name == "word.json.gz" else name
        shutil.copyfile(data / name, data / f"7605-{prefix}")
    for name in ("NATIVE.json", "SIGNED.json", "FINAL.json"):
        (data / name).unlink()
    shutil.copyfile(args.candidate, data / "word.json.gz")
    shutil.copyfile(args.peer_edits, data / "edits7610.json")
    independent = json.loads(args.invoice_receipt.read_bytes())
    bill = json.loads((src / "data/invoice-new.json").read_bytes())
    bill["paid"] = independent["new_full_paid"]
    assert bill["targets"] == independent["productive_targets"]
    (data / "invoice-new.json").write_text(json.dumps(bill, indent=2) + "\n")

    text = source_text.decode()
    text = replace_function(text, "authenticate", "adapt", (HERE / "authenticate.inc").read_text())
    text = replace_function(text, "signed_adapter", "prepare", (HERE / "signed_adapter.inc").read_text())
    edits = [
        ("NATIVE_MARKER = 'PASS_HELPER757_COMPLETE_NATIVE'",
         f"PUBLIC_CLAIM = '{PUBLIC_CLAIM}'\nNATIVE_MARKER = 'PASS_MAIN46_COMPLETE_NATIVE'"),
        ("SIGNED_MARKER = 'PASS_HELPER757_COMPLETE_SIGNED_APPLICATION'",
         "SIGNED_MARKER = 'PASS_MAIN46_COMPLETE_SIGNED_APPLICATION'"),
        ("        '7604-INVOICE.json': PEER / 'invoice-new.json',",
         """        '7604-INVOICE.json': PEER / 'invoice-new.json',
        '7605-WORD.json.gz': HERE / 'data/7605-WORD.json.gz',
        '7605-NATIVE.json': HERE / 'data/7605-NATIVE.json',
        '7605-SIGNED.json': HERE / 'data/7605-SIGNED.json',
        '7610-EDITS.json': HERE / 'data/edits7610.json',"""),
        ("old = read(RETAINED / 'expected/FINAL.json')", "old = read(HERE / 'data/7605-FINAL.json')"),
        ("""    assert native['controls']['wrong_helper757_source'] and native['controls']['missing_helper757_paid_move']""",
         """    required_controls = (
        'wrong_helper757_source', 'missing_helper757_paid_move', 'missing_main46_paid_move',
        'wrong_main46_move_source', 'missing_main46_coframe_correction',
    )
    assert all(native['controls'][name] for name in required_controls)
    assert native['charts']['main46_composed_columns'] == native['charts']['main46_composed_adjoint_columns'] == 512"""),
        ("((3, 603), 2)):", "((3, 603), 2), ((914, 245), 1), ((245, 127), 1), ((914, 127), 2)):"),
        ("sum(invoice['P'].values()) == 110366", "sum(invoice['P'].values()) == 110349"),
        ("Q(price['public_claim_gate']['claim']) == Q('0.0036504442446')",
         "Q(price['public_claim_gate']['claim']) == Q(PUBLIC_CLAIM)"),
        ("Q(price['public_claim_gate']['tested']) == Q('0.00365044424467')",
         "Q(price['public_claim_gate']['tested']) == Q(PUBLIC_CLAIM) + Q(7,10**14)"),
        ("assert ordinary < 10**9", "assert ordinary == 782685204 < 10**9"),
        ("status='PASS_HELPER757_FINAL_APPLICATION', claim='0.0036504442446'",
         "status='PASS_MAIN46_FINAL_APPLICATION', claim=PUBLIC_CLAIM"),
        ("paid_calls=110366", "paid_calls=110349"),
        ("ordinary_change_over_7546=", "ordinary_change_over_7605="),
        ("tape_change_over_7546=", "tape_change_over_7605="),
        ("                public_context_bound_bits=public_context_bits, public_H=public_h,",
         "                public_context_bound_bits=public_context_bits, public_H=public_h,\n"
         "                comparator_claim=old['framework_claim'], comparator_crossing=old['raw_crossing'],"),
    ]
    for before, after in edits:
        text = replace_exact(text, before, after)
    compile(text, str(args.overlay / "application.py"), "exec")
    (args.overlay / "application.py").write_text(text)


if __name__ == "__main__":
    main()
