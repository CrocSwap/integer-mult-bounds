# usage: cmp.py facts   (stdin: verA.py / qB.py output) -> prints FACTS_OK n if every fact status equals the pinned one.
# usage: cmp.py chk2    (stdin: sixheavy/chk2.py output) -> CHK2_OK if killed/open rows equal the pinned lists.
import sys,re
t=sys.stdin.read(); print(t)
if sys.argv[1]=='facts':
    NONE={'E7:7,7','E7:6,6,4,4,1','E7:6,6,4,4,1,1','E7:6,6,4,4,2','E7:6,6,5,3,1','E7:6,6,5,4','D7:6,6,6,5,4','D7:6,6,6,4,4,1,1','D7:6,6,6,4,4,2','D7:6,6,6,4,4,3'}
    COVER={'E7:7,7,1','E7:6,6,5,5','E7:6,6,4,4,4','E7:6,6,4,4,3,1','D7:7,7,6,6'}
    got={m.group(1):m.group(2) for m in re.finditer(r'^(\S+) (NONE|COVER)',t,re.M)}
    bad=[f for f in got if (f in NONE and got[f]!='NONE') or (f in COVER and got[f]!='COVER') or f not in NONE|COVER]
    assert not bad,bad; assert len(got)>=1; print('FACTS_OK',len(got),'facts:',' '.join(sorted(got)))
else:
    op=sorted(int(m.group(1)) for m in re.finditer(r'^(\d+) open',t,re.M)); kl=sorted(int(m.group(1)) for m in re.finditer(r'^(\d+) KILLED',t,re.M))
    assert op==[303,315,400,401,402,409,411,417,424,425] and kl==[169,312,316,332,333,418,420,426,427,430,435,464],(op,kl)
    print('CHK2_OK killed',kl,'open',op)
