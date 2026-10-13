"""Audit PR232, normalizing only the corpus root's machine-local path.
No construction obligations are discharged by this arithmetic replay.
"""
import json
import sys
from pathlib import Path

root = Path(sys.argv[1]).resolve()
package = root / "research/complex-bank-run3"
sys.path.insert(0, str(package))
import verify
import run3

saved = json.loads((package / "certificate.json").read_text())
original = run3.build

def audited_build():
    record = original()
    assert record["supplier_density"]["corpus"]["root"] == str(root)
    record["supplier_density"]["corpus"]["root"] = saved["supplier_density"]["corpus"]["root"]
    assert json.loads(json.dumps(record, default=str)) == saved, "another certificate difference"
    print("AUDIT: all certificate fields exact except validated machine-local corpus root")
    return record

run3.build = audited_build
sys.argv = [str(package / "verify.py")]
verify.main()
