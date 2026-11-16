"""Bind the unchanged signed replay algorithm to the role902 literal word."""
from hashlib import sha256
import json
from pathlib import Path
from sys import argv

ROOT = Path(argv[1]).resolve()
SOURCE = Path(argv[2]).resolve()
OUTPUT = Path(argv[3]).resolve()
PINS = {
    "7544-NATIVE.json": "a4ecb5d836b7c2cd466e9ffb512229198795b87b9697a241dd373b3e4bfe8804",
    "7544-SIGNED.json": "0b072ea1a1cfcb74ec48a6b9485eaa03b61b74d9f456a6a75177020e30cdf4e3",
    "ROLE902-WORD.json.gz": "6e03624b173b90356e96f845d05fc93153846b863734dc8163ab6c44c602cd32",
}
PAIRS = (
    ("FROZEN=ROOT/'frozen-composition'", "FROZEN=ROOT/'frozen-role902'"),
    ("old_word=read(FROZEN/'7481-WORD.json.gz')", "old_word=read(ROOT/'frozen-composition/COMPOSED-WORD.json.gz')"),
    ("new_word==read(FROZEN/'COMPOSED-WORD.json.gz'),'Pinned literal composite word'",
     "new_word==read(FROZEN/'ROLE902-WORD.json.gz'),'Pinned literal role902 word'"),
    ("=='2acc6bfd2807239fafdb3f9e09ff8ad34703df958496590ab657ef0b9ac93aef'",
     "=='bdecd5cc1cb9f164dc695ce07a07d5d44e9961996fcdfa4d77b4092fecbda745'"),
    ("FROZEN/'7481-NATIVE.json'", "FROZEN/'7544-NATIVE.json'"),
    ("PASS_COMPOSED_7481_7542_COMPLETE_NATIVE", "PASS_ROLE902_COMPLETE_NATIVE"),
    ("=='64fca675b91298868e12f09423b47e0c2327cba7095e35c8919c1953b4ed68b8'",
     "=='2acc6bfd2807239fafdb3f9e09ff8ad34703df958496590ab657ef0b9ac93aef'"),
    ("FROZEN/'7481-SIGNED.json'", "FROZEN/'7544-SIGNED.json'"),
    ("Q('0.003647081039689')", "Q('0.003647969120276')"),
    ("{1:-34,5:-17,7:17}", "{2:-34,4:17}"),
    ("==110485", "==110468"),
    ("Whole reconstructed #7481 invoice", "Whole reconstructed #7544 invoice"),
    ("Strictly higher than #7481 raw crossing", "Strictly higher than #7544 raw crossing"),
    ("Exact #7481 invoice rejects the new signed claim", "Exact #7544 invoice rejects the new signed claim"),
    ("PASS_COMPOSED_7481_7542_COMPLETE_SIGNED_APPLICATION", "PASS_ROLE902_COMPLETE_SIGNED_APPLICATION"),
    ("source_head='89eaa9d8cae37c1540de98f2d29a3abaabb96a2b'", "source_head='d6be7d620c9c8337104daeb09fe01196eced5fe3'"),
)
for name, pin in PINS.items():
    assert sha256((ROOT / "frozen-role902" / name).read_bytes()).hexdigest() == pin, name
text = SOURCE.read_text()
digest = sha256(text.encode()).hexdigest()
assert digest == "f3a09f651e51b781c2b99244b215131615465423c1fdf044546ecf6a6645088d"
for old,new in PAIRS:
    assert text.count(old) == 1, old
    text = text.replace(old,new)
compile(text,str(OUTPUT),"exec")
with OUTPUT.open("x") as stream:
    stream.write(text)
print(json.dumps(dict(source_sha256=digest, adapted_sha256=sha256(text.encode()).hexdigest(),
                      source_pins=PINS, replacements=PAIRS),indent=2))
