# SPDX-License-Identifier: Apache-2.0
"""Prepare #7611's already-published joint main-46 repair on #7644.

Credits: DreamingOfClouds #7611, SYLforge #7616 W1, ToikY #7644,
Ali Romman #7605 and all retained NOTICE authors. Source pins below.
This builds a word only; it is not a replay, price, or supplier proof.
"""
import gzip, hashlib, json
from pathlib import Path
D=Path(__file__).resolve().parent
SOURCE=D/'source7644/data/word.json.gz'
PEER=D/'source7644/data/peer7611.json'
assert hashlib.sha256(gzip.decompress(SOURCE.read_bytes())).hexdigest()=='86bc8a1d1276c5b8d80a19704f90279e85b24b9490a02b9afa67c1a5b119c114'
assert hashlib.sha256(PEER.read_bytes()).hexdigest()=='64f096802f328cac7e51c655c2c5a1aa6c011dd33ea278c53a05caaa598594df'
w=json.loads(gzip.decompress(SOURCE.read_bytes())); p=w['program']; peer=json.loads(PEER.read_bytes()); edits=dict(peer['insert_before'])
entrance=[e for e in edits[0] if e[1] not in (185,196)]
assert len(entrance)==24
expected={43543:['MOVE',46,513,914,False],43544:['ADD',145,46,'1',914],45387:['MOVE',46,914,245,False],45388:['ADD',1456,46,'1',245],45390:['ADD',588,46,'-1',245],47973:['MOVE',46,245,127,False]}
assert all(p[i]==e for i,e in expected.items())
assert p[45391]==['MOVE',818,914,245,False]
assert p[45392]==['ADD',818,1456,'1',245]
assert edits[43525]==[['ADD',145,818,'-1',914]]
assert edits[45372]==[['ADD',588,818,'1',245],['ADD',1456,818,'-1',245]]
assert edits[47953]==[['MOVE',46,513,127,False]]
inserts={43543:edits[43525],45392:edits[45372],47973:edits[47953]}
out=list(entrance)
for i,e in enumerate(p):
 out.extend(inserts.get(i,[]))
 if i not in expected:out.append(e)
w['program']=out
raw=json.dumps(w,sort_keys=True,separators=(',',':')).encode()
(D/'candidate.json.gz').write_bytes(gzip.compress(raw,compresslevel=9,mtime=0))
print(json.dumps({'canonical_sha256':hashlib.sha256(raw).hexdigest(),'events':len(out),'entrance_ops':len(entrance),'removed':len(expected),'added_local':sum(map(len,inserts.values()))},indent=2))
