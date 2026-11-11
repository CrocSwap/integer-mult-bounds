"""Reconcile frozen chart-207 occupancy and paired support keys."""
from collections import Counter
from gzip import decompress
from hashlib import sha256
import json
from pathlib import Path
import sys

HEAD="aaeec8c0acf01e99a5f331ef363a698d9c084ace"
FRAME=207
PINS={
    "72/lead/OCCUPANCY.json":"4c349e06b22bfebb431fab1c9ae04f0e798f398acc6fdd99591b49b1c95ef6ca",
    "72/independent/RESULT.json":"587739d21541e7ffe01af9cb7e51abaa757ee69b580befe8bb768a81b614aa08",
    "72/independent/COMPARE.json":"0217f80d0aafdc9fa8f281bf725ff68ba2952b68b19e6ab5b3fee802000ed97c",
    "72/support/RESULT.json":"d90ce338aab69c0c074f72e2e91e2eaa04fd347ea6cded83237d0996af327f98",
    "72/lead/PAIRED.json":"5529a4338efed76989d113100eed30a46bc15c572ab55a58020e8eab423f9143",
    "72/inputs/7334-WORD.json.gz":"4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a",
    "72/price/PRICE.json":"b3c36d5a1d199a1e74f979d660fac295c55659a9d4edb70eaef541095670323b",
    "73/support/RESULT.json":"8ef9be1998d67edf665fc9be07b96e00157f17e86f22f87038ec3b84aa3334ba",
    "73/support/SELECTION.json":"d68ce20cabfd2262aec3925d6b055dcc9ffa08d125e694401760c1ffab5d899a",
    "73/lead/PAIRED.json":"9b06f7b2e17e6d46fa811e05ab7e0fcc45ff5ecd98cacecb8617b662142a6ddc",
}


def unpack(path, expected):
    data=path.read_bytes()
    if sha256(data).hexdigest()!=expected:
        raise ValueError(f"changed receipt or source: {path.name}")
    def unique(items):
        result=dict(items)
        if len(result)!=len(items):
            raise ValueError("duplicate JSON key")
        return result
    return json.loads(decompress(data) if path.suffix==".gz" else data, object_pairs_hook=unique)


def touched(event):
    return event[2:4] if event[0]=="MOVE" else event[-1:]


def bank(row):
    return (row["public_bank"],row["owned_bank"],row["pivots"])


def reconcile(p):
    f,r,c=(p[k] for k in ("72/lead/OCCUPANCY.json","72/independent/RESULT.json","72/independent/COMPARE.json"))
    a,b=(p[k] for k in ("72/support/RESULT.json","73/support/RESULT.json"))
    selection=p["73/support/SELECTION.json"]
    price=p["72/price/PRICE.json"]
    assert f["head"]==r["comparator_head"]==a["head"]==b["head"]==price["head"]==HEAD
    assert f["price_sha256"]==r["price_sha256"]==a["price_sha256"]==PINS["72/price/PRICE.json"]
    assert not price["paid_delta"] and price["productive_delta"]=={"1":17,"8":17,"9":-17}
    assert f["new_interval"]==[44588,44628] and f["new"]["complete"] and f["old"]["complete"]
    assert c["matched_raw_new_cuts"]==41 and c["matched_old_overlap_cuts"]==47
    first=f["representative_keys"]
    remaining=f["unvisited_keys"]
    rev_remaining=r["unvisited_keys"]
    assert first==r["representative_keys"] and len(first)==128
    assert remaining==rev_remaining[:18]==selection["representative_keys"]==a["unresolved"]
    assert len(remaining)==18 and len(rev_remaining)==23
    aliases=rev_remaining[18:]
    assert len(aliases)==5 and aliases==c["equivalent_extra_pairs"]
    tape=p["72/inputs/7334-WORD.json.gz"]["program"]
    snapshots=f["new"]["rows"]
    assert len(snapshots)==41 and [row["cut"] for row in snapshots]==list(range(44588,44629))
    assert all(bank(row)==bank(r["new_snapshots"][str(row["cut"])]) for row in snapshots)
    banks={}
    raw=[]
    repr_cut=None
    for row in snapshots:
        cut=row["cut"]
        if cut==44588 or FRAME in touched(tape[cut-1]):
            repr_cut=cut
            banks[repr_cut]=row
        assert row["representative"]==(repr_cut==cut)
        assert bank(row)==bank(banks[repr_cut])
        assert all(FRAME not in touched(event) for event in tape[repr_cut:cut])
        for pivot in row["pivots"]:
            raw.append(dict(key=[cut,FRAME,pivot],representative=[repr_cut,FRAME,pivot]))
    assert len(raw)==166
    keys=first+remaining
    assert len({tuple(k) for k in keys})==146
    assert sorted({tuple(x["representative"]) for x in raw})==sorted(map(tuple,keys))
    alias_lookup={tuple(x["key"]):x["representative"] for x in raw}
    assert [alias_lookup[tuple(k)] for k in aliases]==[[44626,FRAME,p] for p in (205,532,969,1250,1453)]
    assert tape[44626:44628]==[["ADD",1467,319,"1",127],["ADD",319,1467,"-1",127]]
    assert all(r not in set(banks[44626]["public_bank"]+banks[44626]["owned_bank"]) for r in (319,1467))
    assert a["status"]=="CAPPED" and a["selected"]==a["cap"]==128 and not a["support_only"]
    assert b["status"]=="EXHAUSTED" and b["selected"]==b["case_cap"]==18 and not b["unresolved"] and not b["support_only"]
    assert b["same_bank_reused"]==2 and b["fresh_replayed"]==16
    solved=[]
    for round_no,data,subset in ((72,a,first),(73,b,remaining)):
        independent=p[f"{round_no}/lead/PAIRED.json"]
        assert not independent["unvisited"] and independent["cases"]==len(subset)
        by_cut={row["cut"]:row["status"].replace(" ","_") for row in independent["rows"]}
        assert [row["key"] for row in data["decisions"]]==subset
        for item in data["decisions"]:
            key=item["key"]
            cut,chart,pivot=key
            assert item["public_bank"]==banks[cut]["public_bank"] and pivot in banks[cut]["pivots"]
            assert item["status"]==by_cut[cut] and item["status"] in (
                "no_nonzero_pure_prefix","no_nonzero_pure_suffix","no_unit_pairing")
            assert chart==FRAME
            route="new exact bank check"
            if key in selection["same_bank_keys"]:
                route="exact same cut and bank certificate from initial 128"
            solved.append(dict(key=key,round=round_no,bank_cut=cut,disposition=item["status"],route=route))
    status={tuple(row["key"]):row["disposition"] for row in solved}
    for row in raw:
        row["disposition"]=status[tuple(row["representative"])]
    return dict(head=HEAD,price_sha256=PINS["72/price/PRICE.json"],pins=PINS,
        cut_convention="cut k immediately precedes literal event k",
        budgets=dict(initial_cap=128,initial_resolved=128,initial_capped=True,
                     continuation_cap=18,continuation_resolved=18,continuation_same_bank_reuse=2,
                     continuation_fresh_keys=16,seconds_per_support_runner=35,extra_alias_cases_run=0),
        first_128=first,forward_pending_at_cap=remaining,reverse_pending_at_cap=rev_remaining,
        reverse_post_block_aliases=[dict(key=k,representative=alias_lookup[tuple(k)]) for k in aliases],
        post_block_bank=dict(representative=44626,alias_cut=44628,
            public_bank=banks[44626]["public_bank"],owned_bank=banks[44626]["owned_bank"],
            pivots=banks[44626]["pivots"],events=[[i,tape[i]] for i in (44626,44627)]),
        banks=list(banks.values()),raw_keys=raw,canonical_dispositions=solved,
        summary=dict(raw_keys=len(raw),canonical_keys=len(solved),reverse_keys=151,
                     unresolved=0,advanced=0,exclusions=dict(Counter(row["disposition"] for row in solved))))


def main():
    roots=dict(zip(("72","73"),map(Path,sys.argv[1:]),strict=True))
    inputs={key:unpack(roots[key[:2]]/key[3:],digest) for key,digest in PINS.items()}
    print(json.dumps(reconcile(inputs),indent=2,sort_keys=True))


if __name__=="__main__":
    main()
