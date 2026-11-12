"""Verify only the explicitly frozen R89 exact suffix-drop selection."""
from argparse import ArgumentParser
from collections import Counter
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from runpy import run_path
from signal import SIGALRM, alarm, signal
from time import monotonic

ROOT=Path(__file__).resolve().parent
PINS={
    "keys":"a131ec5bf96baac89f0f6623cf7d9dff06601b36ea720474311ee7ecb394f6e2",
    "price":"b4bf8e00a8289f03b1da731fb3ab563a771d88d875e0da73acf70954df2f2c56",
    "word":"4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a",
    "suffix":"560a22da8219d5ca3d5ec9cb8fa25bdd32f068ca28242cdd4383351dbed82f67",
    "reused/exact_six.py":"5bffcbbbdc5b0622e29fbc778540cc240b41e7d252e3e5c68d708d48808fcb5a",
    "reused/rolling_exterior.py":"ffc6dfa01554974f2b913b65c39230d3a7f7b6c06da1c940617b7938afe2b9c7",
}
HEAD="aaeec8c0acf01e99a5f331ef363a698d9c084ace"


def pinned(path,pin):
    raw=path.read_bytes()
    if sha256(raw).hexdigest()!=pin:
        raise ValueError(f"Changed input {path.name}")
    return raw


def read(path,pin,unique):
    return loads(pinned(path,pin),object_pairs_hook=unique)


def normalize_selection(rows):
    return [tuple(r["key"] if isinstance(r,dict) else r) for r in rows]


def selected_banks(frozen,suffix,selection):
    assert frozen["head"]==suffix["head"]==HEAD and suffix["prime"]==65537
    assert suffix["pins"]["keys"]==PINS["keys"] and suffix["pins"]["word"]==PINS["word"]
    assert not suffix["unvisited"] and not suffix["control_discrepancies"]
    banks={tuple(r["key"]):r for r in frozen["keys"]}
    modular={tuple(r["key"]):r for r in suffix["tested"] if r["status"]=="modular_suffix_rank_drop"}
    assert len(banks)==2128 and len(modular)==1465
    rows=selection["selected"]
    keys=normalize_selection(rows)
    assert 0<len(keys)<=6 and len(keys)==len(set(keys))
    selected=[]
    for key,advertised in zip(keys,rows,strict=True):
        saved=banks[key]
        mod=modular[key]
        assert all(saved[k]==mod[k] for k in ("key","public","owned","pivots"))
        if isinstance(advertised,dict):
            assert all(advertised.get(k,saved[k])==saved[k] for k in ("key","public","owned","pivots"))
        selected.append(saved|{"suffix_modular_rank":mod["suffix_exterior_rank"]})
    return selected


def main():
    parser=ArgumentParser(description=__doc__)
    for k in ("keys","price","word","suffix","selection"):
        parser.add_argument("--"+k,type=Path)
    parser.add_argument("--selection-sha")
    parser.add_argument("--controls-only",action="store_true")
    args=parser.parse_args()
    if not __debug__:
        raise RuntimeError("Run with assertions")
    for rel in ("reused/exact_six.py","reused/rolling_exterior.py"):
        pinned(ROOT/rel,PINS[rel])
    engine=run_path(str(ROOT/"reused/exact_six.py"))
    if args.controls_only:
        assert normalize_selection([[1,2],{"key":[3,4]}])==[(1,2),(3,4)]
        print(dumps(engine["checks"]()+["selection_key_parsing"]))
        return
    if not all(getattr(args,k) for k in ("keys","price","word","suffix","selection","selection_sha")):
        parser.error("Require the five pinned paths and an explicit selection SHA-256")
    if len(args.selection_sha)!=64 or any(v not in "0123456789abcdef" for v in args.selection_sha):
        parser.error("Selection SHA-256 must be a complete lowercase hex digest")

    def stop(*_):
        raise TimeoutError("hard 35-second exact cap")

    checks,selected,results=[],[],[]
    timeout=None
    signal(SIGALRM,stop)
    alarm(35)
    deadline=monotonic()+33
    try:
        checks=engine["checks"]()
        unique=engine["unique"]
        price=read(args.price,PINS["price"],unique)
        frozen=read(args.keys,PINS["keys"],unique)
        suffix=read(args.suffix,PINS["suffix"],unique)
        selection=read(args.selection,args.selection_sha,unique)
        assert price["head"]==HEAD and price["word_sha256"]==PINS["word"]
        selected=selected_banks(frozen,suffix,selection)
        word=engine["checked"](args.word,"word")
        cohort=set(price["endpoint_cohort"])
        n=word["public"]
        mains=set(word["live"])|{r+112 for r in word["live"]}|set(word["hosted"]["X2"])|set(word["hosted"]["Y2"])
        assert cohort=={r for r,az in enumerate(zip(word["initial"],word["final"],strict=True))
                       if az==(3,127) and r not in mains|engine["PROTECTED"]}
        both=engine["trace"](word,selected,deadline)
        for bank,(P,S) in zip(selected,both,strict=True):
            engine["stop_at"](deadline)
            pre_rank,prefix=engine["pure"](P,cohort)
            suf_rank,suffix_basis=engine["pure"](S,cohort)
            assert pre_rank>=bank["exterior_rank"] and suf_rank>=bank["suffix_modular_rank"]
            answer=engine["pair"](prefix,suffix_basis,deadline)
            if answer:
                assert engine["compose"](answer["a"],P)==answer["c"]
                assert engine["compose"](answer["b"],S)==answer["d"]
                assert answer["c"].keys()<=cohort and answer["d"].keys()<=cohort
                assert engine["dot"](answer["a"],answer["b"])==engine["dot"](answer["c"],answer["d"])==1
            counts=(sum(bool(x) for _,x in prefix),sum(bool(x) for _,x in suffix_basis))
            status="exact_unit_pair" if answer else (
                "no_nonzero_pure_prefix" if not counts[0] else "no_nonzero_pure_suffix" if not counts[1] else "no_exact_unit_pair")
            entry=dict(key=bank["key"],public=bank["public"],owned=bank["owned"],pivots=bank["pivots"],
                prefix_rank=pre_rank,suffix_rank=suf_rank,prefix_nullity=len(prefix),suffix_nullity=len(suffix_basis),
                nonzero_prefix_basis_images=counts[0],nonzero_suffix_basis_images=counts[1],
                prefix_rank_mod_65521=bank["exterior_rank"],suffix_rank_mod_65537=bank["suffix_modular_rank"],
                status=status)
            if answer:
                for name in ("a","b"):
                    answer[name]={bank["public"][j]:v for j,v in answer[name].items()}
                entry["physical_coefficient_preflight"]=engine["physical_screen"](answer,bank["pivots"])
                entry["witness"]={k:{j:str(v) for j,v in row.items()} for k,row in answer.items()}
            results.append(entry)
    except TimeoutError as exc:
        timeout=str(exc)
    finally:
        alarm(0)
    print(dumps(dict(head=HEAD,input_sha256=PINS|{"selection":args.selection_sha},
        case_cap=6,runner_cap_seconds=35,controls=checks,results=results,
        modular_drops_outside_exact_scope=1465-len(selected),
        unresolved=[r["key"] for r in selected[len(results):]],timeout=timeout,
        counts=dict(Counter(r["status"] for r in results))),indent=2,sort_keys=True))
    if timeout:
        raise SystemExit(2)


if __name__=="__main__":
    main()
