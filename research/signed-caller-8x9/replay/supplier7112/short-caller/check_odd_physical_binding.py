"""Check physical phase-polynomial substitution and exact paid occurrence binding."""
from pathlib import Path
from hashlib import sha256
from collections import Counter
import gzip
import json

root=Path(__file__).resolve().parent
source=root/"upstream_application.py"
phase=root/"DATA-PHASES.json"
assert sha256(source.read_bytes()).hexdigest()=="d98987db98553dc55bfc80e3ca47abfcd51c57af6f8cda61101391d8eae94184"
assert sha256(phase.read_bytes()).hexdigest()=="c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa"
cpath=root/"ODD-TYPE-AB-CALLER.json"
caller=json.loads(cpath.read_bytes())
rec=json.loads((root/"ODD-TYPE-AB-REPLAY.json").read_text())
assert sha256(cpath.read_bytes()).hexdigest()==rec["caller_sha256"]
word=json.loads(gzip.decompress((root.parent/"WORD.json.gz").read_bytes()))
sha=sha256(json.dumps(word,sort_keys=True,separators=(",",":")).encode()).hexdigest()
assert sha==rec["source_word_sha256"]
r=json.loads((root.parent/"RESULT.json").read_text())
stages=caller["stages"]
ambient=9+8*stages
helper_count=sum(r["native"]["helpers"].values())
main_count=sum(d["roles"]*len(d["ports"]) for d in caller["types"].values())
a=source.read_text()
a=a[:a.index("def inverse(matrix):")]
def patch(old,new,count=1):
    global a
    assert a.count(old)==count,(old,a.count(old))
    a=a.replace(old,new)
patch("range(153)","range(expected_ambient)",2)
patch("caller['ambient_rank'] == 153 and caller['stages'] == 18","caller['ambient_rank'] == expected_ambient and caller['stages'] == expected_stages")
patch("list(range(1,19))","list(range(1,expected_stages+1))",2)
patch("len(helpers) == 1080","len(helpers) == expected_helpers")
patch("len(owners) == 3952","len(owners) == expected_mains")
patch("all(0 <= r < 38 for r in plane_a)","all(r in type_owners(caller, 'A') for r in plane_a)")
patch("all(38 <= r < 76 for r in plane_b[:2])","all(r in type_owners(caller, 'B') for r in plane_b[:2])")
patch("word['public']+51","word['public']+word['owned_fields']")
patch("op in ('QUERY','IDLE_ONE')","op in ('QUERY','IDLE_ONE','IDLE_ODD')")
patch("all(1 <= s <= 18 for s in selected)","all(1 <= s <= expected_stages for s in selected)")
patch("rank = 8*len(selected); idle_uses += len(kind['ports'])","""rank = 8*len(selected); idle_uses += len(kind['ports'])
                    if op == 'IDLE_ODD':
                        need(len(selected)==1 and a[1:]==[-1], 'one complete signed child')
                        rank += 1
                        stage=selected[0]
                        for pi in kind['ports']:
                            q=word['ports'][pi]
                            axes=[q]+[1 << (9+8*(stage-1)+j) for j in range(8)]
                            need(all(dot(x,y)==(i==j) for i,x in enumerate(axes) for j,y in enumerate(axes)),
                                 'signed rank-nine axes are independent and orthonormal')
                            pos=terms((x,1) for x in axes)
                            signed=sub(pos,terms([(q,2)]))
                            need(translation(sub(pos,signed))==q,'exact negative central phase correction')""")
patch("len(selection)==18","len(selection)==expected_stages")
patch("ambient=153, native_calls=18, native_public=1480, fresh_helpers=19440",
      "ambient=expected_ambient, native_calls=expected_stages, native_public=word['public'], fresh_helpers=expected_helpers*expected_stages")
patch("reserved_native_banks=18*51","reserved_native_banks=expected_stages*word['owned_fields']")
def type_owners(C,t):
    x=C["types"][t]
    return range(x["offset"],x["offset"]+x["roles"])
env=dict(globals(),__file__=str(source),expected_ambient=ambient,expected_stages=stages,
         expected_helpers=helper_count,expected_mains=main_count)
exec(compile(a,str(source),"exec"),env)
invoice={"P":rec["paid"],"T":rec["target"]}
f=env["complex_application"]
phases=json.loads(phase.read_bytes())
result=f(word,caller,{"invoice":invoice},phases)
bad=next(i for i,e in enumerate(caller["events"]) if e[0]=="J")
caller["events"][bad][2][0]=caller["events"][bad][2][1]
try:
    f(word,caller,{"invoice":invoice},phases)
except ValueError as e:
    assert str(e)=="A owners"
else:
    raise AssertionError("alias control")
record={"native_sha256":sha,"caller_sha256":rec["caller_sha256"],
        "source_reviewer_sha256":sha256(source.read_bytes()).hexdigest(),
        "patched_application_sha256":sha256(a.encode()).hexdigest(),
        "occurrence_and_geometry":result,"aliased_main_rejected":True,
        "scope":"Current caller port and ownership substitution, full phase-polynomial native contact identities on disjoint stage axes, whole signed idle/output geometry, and ordered paid positions. Retains the standard nested chart and local operator premises and requires separate full native replay and complete fixed-tape tariff application."}
with (root/"ODD-PHYSICAL-BINDING.json").open("x") as out:json.dump(record,out,indent=2)
print("PASS exact physical binding",result["paid_positions"],result["native_contact_boundaries"],result["productive_fields"],flush=True)
