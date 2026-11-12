"""Reconcile the retained odd rails and all 32 port/phase cases from source."""
from argparse import ArgumentParser
from fractions import Fraction
from hashlib import sha256
from json import dumps,loads
from math import comb
from pathlib import Path
from signal import SIGALRM,alarm,signal

ROOT=Path(__file__).resolve().parent
PINS={
    "7113-SHA256.json":"064e11ecfedce9937ea1782e5baee37e89b3c9eebabed5b4a9ba84f412bbe078",
    "7334-ADMITTED.json":"c95300e9bca27e44a25c82d794f88cbf70757c142806b0e4c590ea29feb81a13",
    "PLAN.md":"5673bc5c34a77cfa919010c40bc1666f1293fc2be7079869fd287968e933deaf",
    "QUOTE.json":"89106529258a20b7e16d0e89a48eec6daf578ed6c3d5565b8a953676a9aaad53",
    "CONTRACT-READBACK.json":"2ae99cc148441ffe655b2b33f9e87b8f0939f55436a4b81ff18654efa295f72e",
    "PR7344-CONTRACT.json":"e77f3e124605a059cbf803e8a64cfb99e528091c7b99cbe4ea9dc82b56c75967",
}
SOURCE_FILES=("check_odd_physical_binding.py","upstream_application.py","emit_odd_type_b.py",
              "emit_odd_type_ab.py","signed_model.py","independent.py","lower.py",
              "odd_unit_dyadic_tapes.py","ODD-LOCALIZED-GROUPING.json","mirrored.py")
HEAD="aaeec8c0acf01e99a5f331ef363a698d9c084ace"
CALLER="07a76c5e2738882c0cb322278e56f6cae3c9885d"
CALLER_BYTES="255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc"
PORTS=[15,17,27,34,35,42,47,55]
CASES,SECONDS=32,30


def unique(items):
    obj=dict(items)
    if len(obj)!=len(items):
        raise ValueError("duplicate JSON key")
    return obj


def check(root,name,digest):
    data=(root/"inputs"/name).read_bytes()
    if sha256(data).hexdigest()!=digest:
        raise ValueError("changed dependency inputs/"+name)
    return data


def inputs(root):
    raw={n:check(root,n,d) for n,d in PINS.items()}
    manifest=loads(raw["7113-SHA256.json"],object_pairs_hook=unique)
    source_pins={name:manifest["replay/supplier7112/short-caller/"+name] for name in SOURCE_FILES}
    source_pins["CALLER.json"]=manifest["expected/ODD-TYPE-AB-CALLER.json"]
    assert source_pins["CALLER.json"]==CALLER_BYTES
    raw.update({n:check(root,n,d) for n,d in source_pins.items()})
    return raw,PINS|source_pins


def phase_cases(ports,axes):
    phases=("1","i","-1","-i")
    results=[]
    for port in ports:
        for a in range(4):
            opposite=(a+2)%4
            pos=a
            signed=(-a)%4
            shift=2*a%4
            assert (signed+shift)%4==pos and shift==2*opposite%4
            assert (-opposite)%4==(signed+2)%4
            results.append(dict(port=port,q=phases[a],positive_coefficient=phases[pos],
                signed_coefficient=phases[signed],translation_coefficient=phases[shift],
                fixed_erased_normalized_rank=0,opposite_pair_required_rank=2,
                return_owners=[["main",port,r] for r in axes]))
    assert len(results)==CASES
    return results


def main():
    assert __debug__
    cli=ArgumentParser(description=__doc__)
    cli.add_argument("--root",type=Path,default=ROOT)
    args=cli.parse_args()
    def stop(*_):
        raise TimeoutError("30-second exact source cap")
    signal(SIGALRM,stop)
    alarm(SECONDS)
    try:
        raw,pins=inputs(args.root)
        exact=loads(raw["7334-ADMITTED.json"],object_pairs_hook=unique)
        readback=loads(raw["CONTRACT-READBACK.json"],object_pairs_hook=unique)
        quote=loads(raw["QUOTE.json"],object_pairs_hook=unique)
        assert (exact["head"],exact["caller"])==(HEAD,CALLER)
        assert readback["caller"]==CALLER and readback["caller_sha256"]==CALLER_BYTES
        assert readback["binding_sha256"]==pins["check_odd_physical_binding.py"]
        assert readback["events"]==[["B","IDLE_ODD",68,[8],-1],["B","IDLE_ODD",70,[9],-1]]

        # Authenticate the retained caller bytes, but parse only its header.
        header,separator,_=raw["CALLER.json"].partition(b',"events":')
        assert separator
        c=loads(header+b"}",object_pairs_hook=unique)
        b=c["types"]["B"]
        assert (c["stages"],b["offset"],b["roles"],b["ports"])==(17,36,36,PORTS)
        axes=[e[2] for e in readback["events"]]
        assert [r-b["offset"] for r in axes]==[32,34]
        for e in readback["events"]:
            d=b["diagonal"][e[2]-b["offset"]]
            assert d[:2]==[-1,0] and [i for i,x in enumerate(d[2:],1) if x]==e[3]

        groups=loads(raw["ODD-LOCALIZED-GROUPING.json"],object_pairs_hook=unique)
        chosen=min((g for g in groups["results"] if "idles" in g),
                   key=lambda g:g["idle_basis_ops"]+g["host_basis_ops"])
        assert len(chosen["idles"])==60
        assert all(0<=r<32 for _,v,w in chosen["idles"] for z in (v,w) for r,_ in z)
        tokens={
            "emit_odd_type_b.py":('phase=(half,half,half+1,half+1)','s,t=0,1',
                "events.append(['B','IDLE_ODD',N+i,[j],-1])",
                "events.extend(['B','LAMBDA',r,-1] for r in range(N))",
                "[0,1,'-1','1/2']"),
            "emit_odd_type_ab.py":('out[2]+=offset','[s+offset,t+offset,al,be]'),
            "odd_unit_dyadic_tapes.py":("a,b=8,9","n=2+2*(a-1+b-1)","N=n,masks=masks"),
            "check_odd_physical_binding.py":("signed=sub(pos,terms([(q,2)]))","translation(sub(pos,signed))==q"),
            "upstream_application.py":("('main', pi, pair[0])","('helper', ci, r)","('owned', ci, r-word['public'])"),
            "signed_model.py":("q=e[4] if op=='IDLE_ODD' else 0",),
            "independent.py":("q=2);rows[r]=out",),
        }
        for file,proof in tokens.items():
            assert all(s.encode() in raw[file] for s in proof),file
        results=phase_cases(PORTS,axes)
        classes=[sum(comb(8,k) for k in range(9) if k%4==r) for r in range(4)]
        need=Fraction(2*(min(classes[0],classes[2])+min(classes[1],classes[3])),256)
        assert classes==quote["phase"]==[72,64,56,64] and str(need)==quote["need"]=="15/16"
        assert [r["rank"] for r in quote["rows"]]==[16,18]
        assert all(Fraction(r["necessary_volume"])>Fraction(r["affordable_upper"])
                   and Fraction(r["complete_upper"])<0 for r in quote["rows"])
        result=dict(head=HEAD,caller=CALLER,pins={"inputs/"+n:d for n,d in pins.items()},
            caps={"comparisons":CASES,"seconds":SECONDS},comparisons=results,
            clocks=[1339,2970],masks=[[8],[9]],unchanged_rail_support=[32,33,34,35],
            core_support=[0,31],host_pairs=[0,1],grouped_even_sites=60,
            residues=classes,minimum_paired_displacement=str(need),
            q_sensitive_retained_path_to_selected_returns=False,
            canonical_volume_obstruction=[dict(rank=r["rank"],necessary_volume=r["necessary_volume"],
                affordable_upper=r["affordable_upper"],complete_upper=r["complete_upper"]) for r in quote["rows"]],
            scope="Fixed source, return and incidence bindings, with no caller event or native word decoded.")
    finally:
        alarm(0)
    print(dumps(result,indent=2,sort_keys=True))


if __name__=="__main__":
    main()
