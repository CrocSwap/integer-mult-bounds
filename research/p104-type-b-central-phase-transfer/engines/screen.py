"""Price and test one Type B signed central-axis transfer on the admitted comparator."""

import argparse
from bisect import bisect_left, bisect_right
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
import json
from math import isqrt
from pathlib import Path
import runpy
from time import monotonic

H7277 = "ed090b57ed88f8859e5ff4643645099e6ba856ea"
H7314 = "9d0119eb12fbd9fa534b48cd37b68e7099757b91"
CALLER_HEAD = "07a76c5e2738882c0cb322278e56f6cae3c9885d"
CALLER = "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc"
PINS = {
    "7113/CALLER.json": CALLER,
    "7113/check_odd_physical_binding.py": "5c80c3b0415a7f91d216395248dd6f13297eed637732098e1ca8fb0548951b98",
    "r52/screen.py": "cdf54b266ac31fd0efe544badbb9840598d4c63c4d3cd363f60ae9a74cc4b256",
    "7298/pricing.py": "f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182",
    "r44/RESULT.json": "8d17c43c46d0a3a98f2c3c5849f13ac49a86244ffb87ef1b62e7bf4688cd525b",
    "r53/PRICE.json": "86f779c3eeb43563793e6ccb2227257ef732b2ca12fbbde2f9099988f903a484",
    "7277/WORD.json.gz": "2c523ce6fdd6092d758fedc3602a0bcedb692b9766f1e41f903351ba4dee1756",
    "7277/EARLY-RESULT.json": "691025fe95c7938a6da211244d4d5b6187d88a9de1acff0862eeb7f0ce7deaa7",
    "7277/PRICE.json": "8df5a1b86b5c2429f1581dcf4216d51e45f4297fa94fabc7f9847b128d7568e2",
    "7314/WORD.json.gz": "c404b9b61220e6cf740d85276df2828bbb4a9d68a4d44b5e283f8d96f78c0fd9",
    "7314/EARLY-RESULT.json": "b5043855411432b24336ecc443cba9ebfae6392e2045ddd01c87cfe2c51f5f08",
    "7314/SOURCES.json": "ac7b4473035af648d6073e78b6c39675e706e8194b346bb55ed62a0adc81d593",
    "7314/VERIFY.json": "ede7dd2dd3733b9a73f72af9dd7edfe819b49b859c5c76e227ec82cb9c220513",
    "7314/PRICE-ONLY.json": "b757665a3a50324b2ae6649cc89f5b8d9a752c7af996f1ee894a0de47ade94e1",
}
STAGES = {"early","native","caller","frontier"}
ASSUMPTIONS = {"native_all_columns","owned_erasure","compiler","precision_tape","analytic_recovery"}


def checked(path,pin):
    raw = path.read_bytes()
    if sha256(raw).hexdigest() != pin:
        raise ValueError(f"Changed SHA-256 for {path.name}")
    return raw


def duplicate_guard(pairs):
    value = dict(pairs)
    assert len(value) == len(pairs), "Duplicate key"
    return value


def load_json(raw):
    return json.loads(raw,object_pairs_hook=duplicate_guard)


def admission(path,pin):
    if path is None or pin is None:
        raise ValueError("The pending author invoice needs an independently verified admission receipt")
    doc = load_json(checked(path,pin))
    assert (doc["head"],doc["caller_sha256"],doc["status"]) == (
        H7314,CALLER,"independently_reproduced_comparable")
    hosted = doc["hosted"]
    history = doc["source_history"]
    assert hosted["head"] == H7314 and hosted["status"] in ("queued","passed")
    assert (history["validation"],history["stock_wrapper"]) in (
        ("full_history","passed"),("exact_anchored_pins","refused_shallow"),
        ("exact_anchored_pins","skipped_shallow"))
    assert set(doc["assumptions"]) == ASSUMPTIONS
    assert set(doc["stages"]) == STAGES
    root = path.resolve().parent
    seen = set()
    for item in doc["stages"].values():
        relative = Path(item["path"])
        local = (root/relative).resolve()
        assert not relative.is_absolute() and ".." not in relative.parts and local.is_relative_to(root)
        assert local not in seen and item["exit"] == 0
        seen.add(local)
        checked(local,item["sha256"])
    evidence = history["evidence"]
    relative = Path(evidence["path"])
    local = (root/relative).resolve()
    assert not relative.is_absolute() and ".." not in relative.parts and local.is_relative_to(root)
    checked(local,evidence["sha256"])
    return {"head":H7314,"sha256":pin,"hosted":hosted,"source_history":history,"stages":doc["stages"]}


def inputs(args):
    chosen = {key:pin for key,pin in PINS.items()
              if key.split("/",1)[0] not in ("7277","7314") or key.startswith(args.comparator+"/")}
    values = {key:checked(args.inputs/key,pin) for key,pin in chosen.items()}
    if args.comparator == "7277":
        assert args.admission is None and args.admission_sha is None
        admitted = {"head":H7277,"status":"sealed_independently_reproduced_comparable"}
    else:
        admitted = admission(args.admission,args.admission_sha)
    return chosen,values,admitted


def invoice(comparator,values):
    early = load_json(values[f"{comparator}/EARLY-RESULT.json"])["invoice"]
    paid = Counter({int(k):v for k,v in early["P"].items()})
    targets = Counter({int(k):v for k,v in early["T"].items()})
    assert early["empty_root_credits"] == 0 and early["S"] == 1424
    assert sum(paid.values()) == 110536 and sum(targets.values()) == 22461
    if comparator == "7277":
        frozen = load_json(values["7277/PRICE.json"])
        assert frozen["head"] == H7277 and frozen["caller_head"] == CALLER_HEAD and frozen["copies"] == 17
        assert {int(r):v for r,v in frozen["original_paid"].items()} == paid
        assert {int(r):v for r,v in frozen["original_productive"].items()} == targets
        crossing = Q(frozen["crossing_upper"])
    else:
        frozen = load_json(values["7314/PRICE-ONLY.json"])
        assert frozen["head"] == H7314 and frozen["predecessor_head"] == H7277
        assert {int(r):v for r,v in frozen["paid"].items()} == paid
        assert {int(r):v for r,v in frozen["productive"].items()} == targets
        crossing = Q(frozen["new_crossing"][1])
    net = targets.copy()
    net.subtract(paid)
    assert sum(r*v for r,v in net.items()) == 1424
    return paid,targets,net,crossing


def stock(caller,odd_receipt,even_receipt):
    odd,even = {},{}
    block = caller["types"]["B"]
    assert (block["offset"],block["roles"],len(block["ports"]),caller["stages"]) == (36,36,8,17)
    for clock,event in enumerate(caller["events"]):
        if event[:2] not in (["B","IDLE_ODD"],["B","IDLE_ONE"]):
            continue
        role,mask = event[2:4]
        assert 36 <= role < 72 and mask and len(set(mask)) == len(mask)
        assert all(1 <= j <= 17 for j in mask)
        if event[1] == "IDLE_ODD":
            assert len(mask) == 1 and event[4:] == [-1]
            odd[clock] = (role-36,mask)
        elif len(mask) > 1:
            even[clock] = (role-36,mask)
    assert len(odd) == 4 and len(even) == 26
    assert {str(i):{"role":r+36,"stage":mask[0],"q_power":-1} for i,(r,mask) in odd.items()} == odd_receipt["odd_idles"]
    assert [[i,r,sorted(mask)] for i,(r,mask) in even.items()] == [
        row for row in even_receipt["job_masks"] if len(row[2]) > 1]
    assert Counter(len(mask) for _,mask in even.values()) == {2:4,3:4,4:4,5:4,6:4,7:4,8:2}
    return odd,even


def rank_delta(m):
    assert m >= 2
    return {9:8,8*m:8,8:-8,8*m+1:-8}


def make_price(args,transport,tariff):
    pins,values,admitted = inputs(args)
    caller = load_json(values["7113/CALLER.json"])
    assert b"len(selected)==1 and a[1:]==[-1]" in values["7113/check_odd_physical_binding.py"]
    odd,even = stock(caller,load_json(values["r44/RESULT.json"]),load_json(values["r53/PRICE.json"]))
    paid,targets,net,kappa = invoice(args.comparator,values)
    cost,power = tariff["cost"],tariff["power_bounds"]
    old = cost(net,kappa)
    assert old[1] < 0
    quotes = {}
    for m in range(2,9):
        d = rank_delta(m)
        result = net.copy()
        result.update(d)
        saving,margin = cost(d,kappa),cost(result,kappa)
        assert saving[0] > Q(1,100) and margin[0] > 0
        broad = power(8*m+1,kappa)
        ninth,old_broad,eighth = (power(r,kappa) for r in (9,8*m,8))
        volume = ((ninth[0]+old_broad[0]-eighth[1])/broad[1],
                  (ninth[1]+old_broad[1]-eighth[0])/broad[0])
        quotes[m] = {"old_ranks":[9,8*m],"new_ranks":[8,8*m+1],"paid_old_minus_new":d,
                     "saving_interval":list(map(str,saving)),"complete_margin_interval":list(map(str,margin)),
                     "promoted_volume_break_even_before_other_costs":list(map(str,volume))}
    assert all(Q(quotes[m]["saving_interval"][1]) < Q(quotes[m+1]["saving_interval"][0]) for m in range(2,8))
    chosen = sorted(even,key=lambda i:(-len(even[i][1]),i))[:len(odd)]
    assert [len(even[i][1]) for i in chosen] == [8,8,7,7]
    upper = sum(Q(quotes[len(even[i][1])]["saving_interval"][1]) for i in chosen)
    keys = [[a,b,len(even[b][1])] for a in odd for b in even]
    assert len(keys) == 104 and len({(a,b) for a,b,m in keys}) == 104
    price = {
        "comparator":args.comparator,"comparator_admission":admitted,"caller_head":CALLER_HEAD,
        "source_pins":pins,"complete_paid":paid,"complete_targets":targets,"copies":17,
        "type_b_ports":8,"crossing_upper":str(kappa),"old_complete_margin_interval":list(map(str,old)),
        "odd_jobs":odd,"even_jobs":even,"pair_keys":keys,"price_by_mask_length":quotes,
        "whole_compatible_optimistic_upper":str(upper),"upper_broad_job_choices":chosen,
        "extra_costs_granted_free_only_for_upper":True,"paid_multistage_odd_binding":"unproved",
        "followup":{"body_one_hard_seconds":25,"nonunit_body_vectors":transport["BODIES"],
                    "nonunit_hard_seconds":25,"structural_max_cases":3,"structural_hard_seconds":45,
                    "one_candidate_uniform_binding_seconds":90},
    }
    return price,caller,odd,even


def support_rows(transport,caller,odd,even,keys,bodies,deadline):
    prime = transport["MOD"]
    compiled = [transport["compile_gates"](caller,prime-1,v) for v in bodies]
    rows = []
    for a,b,m in keys:
        if monotonic() >= deadline:
            break
        left,right = sorted((a,b))
        source,target = (odd[a][0],even[b][0]) if a < b else (even[b][0],odd[a][0])
        witness = None
        for phase,(clocks,gates) in enumerate(compiled):
            window = gates[bisect_right(clocks,left):bisect_left(clocks,right)]
            col,_ = transport["transport"](window,source,False,prime)
            row,_ = transport["transport"](window,target,True,prime)
            col_out,row_out = transport["outside"](col,target),transport["outside"](row,source)
            if col_out or row_out:
                witness = {"body_vector":phase,"q":-1,"outside_write":col_out,"outside_read":row_out}
                break
        rows.append({"key":[a,b,m],"earlier_role":source,"later_role":target,"witness":witness})
    return rows


def controls(transport,tariff):
    x = Q("0.003645669928698")
    assert sum(k*n for k,n in rank_delta(8).items()) == 0
    assert tariff["cost"](rank_delta(2),x)[0] > Q(1,100)
    assert tariff["cost"](rank_delta(8),x)[0] > tariff["cost"](rank_delta(2),x)[1]
    apply,outside = transport["transport"],transport["outside"]
    p = transport["MOD"]
    # SWAP carries both projector directions; a transverse ADD defeats one.
    swap = [(0,"SWAP",0,1,0)]
    assert outside(apply(swap,0,False,p,2)[0],1) is None
    assert outside(apply(swap,1,True,p,2)[0],0) is None
    assert outside(apply([(0,"ADD",1,0,1)],0,False,p,2)[0],0) == [1,1]
    def mul(a,b):
        return [[sum(a[i][k]*b[k][j] for k in (0,1)) for j in (0,1)] for i in (0,1)]
    phase_left = [[-1,0],[0,1]]
    phase_right = [[1,0],[0,-1]]
    middle = [[0,1],[1,0]]
    body_left = [[2,0],[0,1]]
    body_right = [[1,0],[0,3]]
    old = mul(body_right,mul(middle,mul(phase_left,body_left)))
    new = mul(phase_right,mul(body_right,mul(middle,body_left)))
    assert old == new
    assert mul(body_right,mul(phase_right,mul(middle,body_left))) == old
    return ["mass_neutral_positive_directed_price","full_phase_move_with_nonunit_bodies",
            "two_sided_swap_positive","outside_column_negative",*transport["controls"]()]


def main(args,start):
    for key in ("r52/screen.py","7298/pricing.py"):
        checked(args.inputs/key,PINS[key])
    transport = runpy.run_path(str(args.inputs/"r52/screen.py"))
    tariff = runpy.run_path(str(args.inputs/"7298/pricing.py"))
    checks = controls(transport,tariff)
    if args.controls_only:
        print(json.dumps({"controls":checks},indent=2,sort_keys=True))
        return
    args.out.mkdir(parents=True,exist_ok=True)
    pre,caller,odd,even = make_price(args,transport,tariff)
    save = transport["save"]
    if args.price_only:
        save(args.out,"PRICE.json",pre)
        return
    frozen = (args.out/"PRICE.json").read_bytes()
    assert load_json(frozen) == json.loads(json.dumps(pre)), "Price receipt differs from pinned inputs"
    pin = sha256(frozen).hexdigest()
    assert all(transport["MOD"]%d for d in range(2,isqrt(transport["MOD"])+1))
    keys,unvisited = pre["pair_keys"],[]
    if args.nonunit or args.structural:
        old = transport["previous"](args.out,"BODY1.json" if args.nonunit else "NONUNIT.json",pin)
        keys,unvisited = old["survivors"],old["unvisited"]
    if args.structural:
        rows = []
        for a,b,m in keys[:3]:
            if monotonic() >= start+42:
                break
            left,right = sorted((a,b))
            source,target = (odd[a][0],even[b][0]) if a < b else (even[b][0],odd[a][0])
            status,mixed,clock = transport["structural"](caller,left,right,source,target)
            rows.append({"key":[a,b,m],"status":status,"mixed":mixed,"stop_clock":clock})
        save(args.out,"STRUCTURAL.json",{
            "price_sha256":pin,"scope":len(keys),"visited":len(rows),"unvisited":[*unvisited,*keys[len(rows):]],
            "records":rows,"unresolved":[r["key"] for r in rows if r["status"] != "formal_projector_transport"],
            "support_survivors":[r["key"] for r in rows if r["status"] == "formal_projector_transport"],
            "paid_multistage_odd_binding":"unproved","controls":checks,
        })
        return
    bodies = transport["BODIES"] if args.nonunit else ((1,)*17,)
    rows = support_rows(transport,caller,odd,even,keys,bodies,start+22)
    survivors = [row["key"] for row in rows if not row["witness"]]
    save(args.out,"NONUNIT.json" if args.nonunit else "BODY1.json",{
        "price_sha256":pin,"scope":len(keys),"visited":len(rows),"exclusions":len(rows)-len(survivors),
        "survivors":survivors,"unvisited":[*unvisited,*keys[len(rows):]],"records":rows,
        "body_vectors":bodies,"prime":transport["MOD"],"controls":checks,
    })


if __name__ == "__main__":
    start = monotonic()
    if not __debug__:
        raise RuntimeError("Assertions required")
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--inputs",type=lambda x:Path(x).resolve(),required=True)
    p.add_argument("--out",type=Path,default=Path("run"))
    p.add_argument("--comparator",choices=("7277","7314"),default="7277")
    p.add_argument("--admission",type=Path)
    p.add_argument("--admission-sha")
    mode = p.add_mutually_exclusive_group(required=True)
    for flag in ("price-only","support","nonunit","structural","controls-only"):
        mode.add_argument("--"+flag,action="store_true")
    args = p.parse_args()
    main(args,start)
