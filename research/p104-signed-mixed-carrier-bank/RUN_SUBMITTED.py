#!/usr/bin/env python3
"""Standard-library acceptance for the committed subset of the finite laboratory."""
import subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parent
for name in ('verify.py','optimize_bank.py','root_line_gate.py','zero_restore.py','rank2_gate.py'):
    subprocess.run([sys.executable,'-I','-B',str(root/name)],check=True)
print('PASS_P104_SCHEMATIC_SUBMISSION zero_restored=YES no_kappa no_native_supplier')
