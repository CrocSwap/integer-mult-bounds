"""Bind a temporary #7481 native validator to the literal two-rung composition."""
from pathlib import Path
from hashlib import sha256
import json
from sys import argv

root = Path(argv[1]).resolve()
source = Path(argv[2]).resolve()
frozen = root / "frozen-composition"
receipt = json.loads((frozen / "COMPOSITION.json").read_text())
expected = "2acc6bfd2807239fafdb3f9e09ff8ad34703df958496590ab657ef0b9ac93aef"
prior = "64fca675b91298868e12f09423b47e0c2327cba7095e35c8919c1953b4ed68b8"
assert receipt["canonical_sha256"] == expected
raw = source.read_bytes()
assert sha256(raw).hexdigest() == "96257fbcebd3a1ac7f742868bd40d6a15dc4804bda2802ecf5d89bbd88e3a5d4"
before = raw.decode()
patches = (
    (f"EXPECTED='{prior}'", f"EXPECTED='{expected}'"),
    ("affected={(3,721),(721,724),(721,904),(3,724),(724,904)}",
     """affected={(3,721),(721,724),(721,904),(3,724),(724,904)}
    before = read(ROOT/'frozen-composition/7481-WORD.json.gz')
    need(sha256(canonical(before)).hexdigest()=='64fca675b91298868e12f09423b47e0c2327cba7095e35c8919c1953b4ed68b8','Exact #7481 control')
    pairs = lambda w: {(e[2],e[3]) for e in w['program'] if e[0]=='MOVE'}
    new_pairs = pairs(word)-pairs(before)
    need(len(new_pairs)==2,'Both new chart pairs')
    affected |= new_pairs"""),
    ("need(new==dict(old,program=emitted),'Literal complete emitted splice and unchanged boundary')",
     """incumbent=read(ROOT/'frozen-composition/7481-WORD.json.gz')
        need(incumbent==dict(old,program=emitted),'Rebuild exact #7481 from its predecessor')
        need(new==read(ROOT/'frozen-composition/COMPOSED-WORD.json.gz'),'Literal composed word')
        need({k:v for k,v in new.items() if k!='program'}=={k:v for k,v in incumbent.items() if k!='program'},'Unchanged boundary metadata')"""),
    ("=={1:1,3:-1,4:-1,6:1}", "=={1:-1,3:-1,4:-1,5:-1,6:1,7:1}"),
    ("len(old['program'])+3", "len(old['program'])+19"),
    ("('doubled_824_compensation',['ADD',824,54,'-1',721])):",
     """('doubled_824_compensation',['ADD',824,54,'-1',721]),
            ('doubled_1438_restoration',['ADD',1438,1439,'1',127])):"""),
    ("'PASS_CHANGED_485_1455_PRODUCER_COMPLETE_NATIVE'", "'PASS_COMPOSED_7481_7542_COMPLETE_NATIVE'"),
)
adapted = before
for old,new in patches:
    assert adapted.count(old) == 1, old
    adapted = adapted.replace(old,new)
compile(adapted, str(source), "exec")
out = root/"producer54/validation_native/run.py"
out.write_text(adapted)
(root/"receipts/NATIVE-ADAPTER.json").write_text(json.dumps(dict(
    source_sha256=sha256(before.encode()).hexdigest(),
    adapted_sha256=sha256(adapted.encode()).hexdigest(),
    replacements=[{"source":a,"adapted":b,"count":1} for a,b in patches]),indent=2)+"\n")
