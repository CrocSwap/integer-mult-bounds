"""Write the relaxed copy of PR #370's independent checker that this package uses for mutable-source words.
usage: relax.py OUT_DIR   ->  OUT_DIR/checkword_mut.py

The relaxed copy is generated from the pinned, byte-identical checkword.py next to this file, so its difference from
PR #370's checker is exactly what is written here: ONE assertion is removed, the one that forbids gates whose
destination is a source register x ("x registers are never destinations").  Instead such gates are counted.  Every
other check is unchanged; in particular (3) still requires every source register to end holding exactly its own
column x_s over F2 (all 2v+R columns), so a source that is used as a carrier must be restored.  This is PR #425's
mutable-basis interface (Zhihao Chen) on the bit side.
Prepared by eumemic with substantial Anthropic Claude assistance; Apache-2.0."""
import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, "checkword.py")).read()   # byte-identity with PR #370 is checked by code/provenance.py
EDITS = [
    ("def run(gates,tag):\n",
     "xdest=[0]   # relaxed copy: count of gates whose destination is a source register\ndef run(gates,tag):\n"),
    ("        assert all(x>=v for x in [d]), ('x register written',tag,k)   # x registers are never destinations\n",
     "        xdest[0]+=d<v   # RELAXED (PR #425 mutable-basis interface): x may be a destination; restoration is checked in (3)\n"),
    ("print('legality + exact F2 on all %d columns: PASS (gates D/A/B/C = %d/%d/%d/%d)'%(nreg,len(c['D']),len(c['A']),len(c['B']),len(c['C'])))\n",
     "print('legality + exact F2 on all %d columns: PASS (gates D/A/B/C = %d/%d/%d/%d)'%(nreg,len(c['D']),len(c['A']),len(c['B']),len(c['C'])))\n"
     "print('relaxed check: %d gates have a source register as destination; all %d sources restored exactly'%(xdest[0],v))\n"),
]
for old, new in EDITS:
    assert src.count(old) == 1, ("pinned checker text not found exactly once", old)
    src = src.replace(old, new)
os.makedirs(sys.argv[1], exist_ok=True)
out = os.path.join(sys.argv[1], "checkword_mut.py")
open(out, "w").write(src)
print("   relaxed checker written: PR #370's checkword.py with exactly one assertion (x never a destination) replaced by a"
      " counter; sha256", hashlib.sha256(src.encode()).hexdigest()[:16] + "...")
