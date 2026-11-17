"""Adapt the frozen #7642 replay to its one literal contact splice."""
import argparse
from gzip import decompress
from hashlib import sha256
import json
from pathlib import Path
from shutil import copyfile, copytree

BASE = "aa83ede3e5833d43606d711068619db0dc28cbcd858dd11e8e89da6d09883916"
NEW = "dcd797e45b6d4b74411a8a73a9b6e8247bb2ea8744924332b0dd43db3e219f02"
PLAN = "512dbbc3c5133b07400b720f55753e976aca48020e91b2d0086345802de1bc14"
OLD_HEAD = "d7f82810689ed2cd649ec9aaaf3b1485b585c82e"
PEER_HEAD = "e814828ee5b869c9468282d57ba28c364b07d130"
PUBLIC = "0.00365098237428"


def replace(text, old, new):
    if text.count(old) != 1:
        raise ValueError(f"Cannot match source text exactly once: {old!r}")
    return text.replace(old, new)


def many(text, edits):
    for old, new in edits:
        text = replace(text, old, new)
    return text


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("overlay-7642", "output", "candidate", "contact", "invoice"):
        parser.add_argument(f"--{name}", type=Path, required=True)
    args = parser.parse_args()
    assert __debug__
    src = args.overlay_7642
    dst = args.output
    assert sha256(decompress((src/"data/word.json.gz").read_bytes())).hexdigest() == BASE
    assert sha256(decompress(args.candidate.read_bytes())).hexdigest() == NEW
    assert sha256(args.contact.read_bytes()).hexdigest() == PLAN
    bill = json.loads(args.invoice.read_bytes())
    assert sum(bill["paid"].values()) == 110332 and sum(bill["targets"].values()) == 22461
    copytree(src, dst)
    data = dst / "data"
    for name in ("word.json.gz", "NATIVE.json", "SIGNED.json", "FINAL.json", "invoice-new.json"):
        alias = "WORD.json.gz" if name == "word.json.gz" else name
        copyfile(data/name, data/f"7642-{alias}")
    for name in ("NATIVE.json", "SIGNED.json", "FINAL.json"):
        (data/name).unlink()
    copyfile(args.candidate, data/"word.json.gz")
    copyfile(args.contact, data/"contact.json")
    copyfile(args.invoice, data/"invoice-new.json")

    target = dst/"application.py"
    text = target.read_text()
    auth_start = text.index("    word = read(HERE / 'data/word.json.gz')")
    auth_stop = text.index("    return word", auth_start)
    text = text[:auth_start] + f"""    incumbent = read(HERE / 'data/7642-WORD.json.gz')
    assert incumbent == {{**old, 'program': program}}
    assert digest(canonical(incumbent)) == '{BASE}'
    plans = HERE / 'data/contact.json'
    assert digest(plans.read_bytes()) == '{PLAN}'
    plan = read(plans)
    assert plan['incumbent_word_sha256'] == '{BASE}'
    edits = {{int(k): v for k, v in plan['proposed_events'].items()}}
    assert all(incumbent['program'][int(k)] == v for k, v in plan['old_events'].items())
    word = read(HERE / 'data/word.json.gz')
    projected = [edits.get(i, event) for i, event in enumerate(incumbent['program'])]
    assert word == {{**incumbent, 'program': [e for e in projected if e is not None]}}
    assert digest(canonical(word)) == '{NEW}'
    bill = read(HERE / 'data/7642-invoice-new.json')
    for r, n in plan['paid_delta'].items():
        bill['paid'][r] += n
    assert read(HERE / 'data/invoice-new.json') == bill
""" + text[auth_stop:]

    head = text.index("def signed_adapter(")
    tail = text.index("def prepare(", head)
    signed = many(text[head:tail], [
        ("FROZEN/'7605-WORD.json.gz'", "FROZEN/'7642-WORD.json.gz'"),
        ("FROZEN/'7605-NATIVE.json'", "FROZEN/'7642-NATIVE.json'"),
        ("FROZEN/'7605-SIGNED.json'", "FROZEN/'7642-SIGNED.json'"),
        ("Pinned literal main46 word", "Pinned literal 134/329 contact word"),
        ("=='e20f3f9240ac3f5fa4bbd7ab9b5550d660886901bb209f335409c329ac45d9cd'", f"=='{BASE}'"),
        ("Q('0.003650444244716')", "Q('0.003650666180757')"),
        ('"{1:-34,2:17}"', '"{1:-34,2:34,3:-17,4:-17,5:17}"'),
        ('"==110349"', '"==110332"'),
        ("Whole reconstructed #7605 invoice", "Whole reconstructed #7642 invoice"),
        ("Strictly higher than #7605 raw crossing", "Strictly higher than #7642 raw crossing"),
        ("Exact #7605 invoice rejects the new signed claim", "Exact #7642 invoice rejects the new signed claim"),
        ("source_head='e1d2756eecf03e146338239fee81772a99ba8d4c'", f"source_head='{OLD_HEAD}'"),
        ("component_head='93fded4340bb08bc1f99d6f18e47a198456a41df'", f"component_head='{PEER_HEAD}'"),
    ])
    text = text[:head] + signed + text[tail:]
    text = many(text, [
        ("PUBLIC_CLAIM = '0.0036506661663'", f"PUBLIC_CLAIM = '{PUBLIC}'"),
        ("NATIVE_MARKER = 'PASS_MAIN46_COMPLETE_NATIVE'", "NATIVE_MARKER = 'PASS_CONTACT134_329_COMPLETE_NATIVE'"),
        ("SIGNED_MARKER = 'PASS_MAIN46_COMPLETE_SIGNED_APPLICATION'", "SIGNED_MARKER = 'PASS_CONTACT134_329_COMPLETE_SIGNED_APPLICATION'"),
        ("        '7610-EDITS.json': HERE / 'data/edits7610.json',",
         """        '7610-EDITS.json': HERE / 'data/edits7610.json',
        '7642-WORD.json.gz': HERE / 'data/7642-WORD.json.gz',
        '7642-NATIVE.json': HERE / 'data/7642-NATIVE.json',
        '7642-SIGNED.json': HERE / 'data/7642-SIGNED.json',
        '7612-CONTACT.json': HERE / 'data/contact.json',"""),
        ("    old = read(HERE / 'data/7605-FINAL.json')", "    old = read(HERE / 'data/7642-FINAL.json')"),
        ("sum(invoice['P'].values()) == 110349", "sum(invoice['P'].values()) == 110332"),
        ("assert ordinary == 782685204 < 10**9", "assert ordinary == 782668204 < 10**9"),
        ("status='PASS_MAIN46_FINAL_APPLICATION'", "status='PASS_CONTACT134_329_FINAL_APPLICATION'"),
        ("paid_calls=110349", "paid_calls=110332"),
        ("ordinary_change_over_7605=", "ordinary_change_over_7642="),
        ("tape_change_over_7605=", "tape_change_over_7642="),
    ])
    compile(text, str(target), "exec")
    target.write_text(text)


if __name__ == "__main__":
    main()
