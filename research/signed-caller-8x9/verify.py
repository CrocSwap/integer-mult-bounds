from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
import json,shutil,subprocess,sys
root=Path(__file__).resolve().parent
assert __debug__
for name,expected in json.loads((root/"SHA256.json").read_text()).items():
    assert sha256((root/name).read_bytes()).hexdigest()==expected,name
commands=("emit_odd_type_b.py","emit_odd_type_ab.py","check_odd_caller_exact_grid.py",
          "check_odd_physical_binding.py","check_odd_precision.py","check_odd_partial_admission.py",
          "check_odd_fixed_tape_counts.py","assemble_odd_application.py")
with TemporaryDirectory(prefix="signed-caller-8x9-") as tmp:
    replay=Path(tmp)/"replay"
    shutil.copytree(root/"replay",replay)
    folder=replay/"supplier7112/short-caller"
    for script in commands:
        print("Running",script,flush=True)
        subprocess.run([sys.executable,"-B",script],cwd=folder,check=True)
    for src in sorted((root/"expected").glob("*.json")):
        actual=folder/src.name
        if src.name=="ODD-TYPE-AB-CALLER.json":
            assert actual.read_bytes()==src.read_bytes(),src.name
        else:
            assert json.loads(actual.read_bytes())==json.loads(src.read_bytes()),src.name
print("PASS_SIGNED_CALLER_8X9 363797977/100000000000")
