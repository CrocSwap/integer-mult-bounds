"""Authenticate the artifact and independently certify its signed invoice price."""
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
from runpy import run_path


ROOT = Path(__file__).resolve().parent
INCUMBENT = "aa83ede3e5833d43606d711068619db0dc28cbcd858dd11e8e89da6d09883916"
CANDIDATE = "dcd797e45b6d4b74411a8a73a9b6e8247bb2ea8744924332b0dd43db3e219f02"
CALLER = "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc"


def authenticate():
    seen = set()
    for line in (ROOT / "SHA256SUMS").read_text().splitlines():
        digest, name = line.split("  ", 1)
        path = Path(name)
        assert not path.is_absolute() and ".." not in path.parts and path not in seen
        seen.add(path)
        source = ROOT / path
        assert source.resolve() == source and sha256(source.read_bytes()).hexdigest() == digest, name
    actual = {p.relative_to(ROOT) for p in ROOT.rglob("*") if p.is_file() and "__pycache__" not in p.parts}
    assert actual == seen | {Path("SHA256SUMS")}


def read(name):
    return json.loads((ROOT / "receipts" / name).read_bytes())


def paid_check(old, new):
    delta = {k: new.get(k, 0) - old.get(k, 0) for k in new.keys() | old.keys()}
    assert {k: n for k, n in delta.items() if n} == {"1":-34, "2":34, "3":-17, "4":-17, "5":17}
    assert (sum(old.values()), sum(new.values())) == (110349, 110332)


def price_vector(invoice):
    paid, target = invoice["P"], invoice["T"]
    return {int(r): target.get(r, 0) - paid.get(r, 0) for r in target.keys() | paid.keys()}


def main():
    assert __debug__
    authenticate()
    native, signed, final, incumbent = [read(n) for n in ("NATIVE.json","SIGNED.json","FINAL.json","7642-FINAL.json")]
    assert native["status"] == "PASS_CONTACT134_329_COMPLETE_NATIVE"
    assert signed["status"] == "PASS_CONTACT134_329_COMPLETE_SIGNED_APPLICATION"
    assert final["status"] == "PASS_CONTACT134_329_FINAL_APPLICATION"
    assert incumbent["candidate_canonical_sha256"] == INCUMBENT
    assert native["word_canonical_sha256"] == final["candidate_canonical_sha256"] == CANDIDATE
    assert final["caller_sha256"] == signed["caller_sha256"] == incumbent["caller_sha256"] == CALLER
    assert signed["source_head"] == "d7f82810689ed2cd649ec9aaaf3b1485b585c82e"
    assert signed["component_head"] == "e814828ee5b869c9468282d57ba28c364b07d130"
    controls = ("missing_contact_paid_return","wrong_contact_chart","missing_contact_add")
    assert all(native["controls"][c] for c in controls)

    price, recount = signed["price"], read("RECOUNT.json")
    old, new = price["before"], price["after"]
    assert price["new_native"] == CANDIDATE and price["old_native"] == INCUMBENT
    assert old["P"] == recount["old_paid"] and new["P"] == recount["new_paid"]
    assert old["T"] == new["T"] == recount["new_targets"] and sum(new["T"].values()) == 22461
    assert old["S"] == new["S"] == 1424 and not new["empty_root_credits"]
    paid_check(old["P"], new["P"])
    bad = new["P"].copy()
    bad["5"] -= 1
    try:
        paid_check(old["P"], bad)
    except AssertionError:
        pass
    else:
        raise AssertionError("Missing rank-five paid position control accepted")

    cost = run_path(str(ROOT / "checks/pricing.py"))["cost"]
    claim = Q(final["framework_claim"])
    previous = Q(incumbent["framework_claim"])
    assert Q(signed["claim"]) == claim
    assert final["comparator_crossing"] == incumbent["raw_crossing"]
    assert claim > Q(incumbent["raw_crossing"][1]) > previous
    assert cost(price_vector(old), claim)[1] < 0 < cost(price_vector(new), claim)[0]
    assert final["ordinary_bound"] == recount["ordinary_projected"] == 782668204
    assert final["precision_c"] == 2430 and final["signed_physical_map_count"] >= 3000
    print("PASS exact contact price separation and evidence bindings")


if __name__ == "__main__":
    main()
