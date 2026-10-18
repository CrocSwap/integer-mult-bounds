"""Repository locations used by the toolkit.

The checkout is the repository root two levels above this package; set IMB_ROOT to use another checkout.
Every path below is an unchanged upstream source that the toolkit imports or runs, never a generated file."""
import os
from pathlib import Path

PKG = Path(__file__).resolve().parent
ROOT = Path(os.environ.get("IMB_ROOT", PKG.parents[1])).resolve()
AUDIT_LOCAL = ROOT / "research/gauge44-frames-x/independent/audit_local.py"      # #645 independent local audit
MULTICOLD = ROOT / "research/complex-k492-owner-repair/vendor/multicold"          # moment / outer engines, run_portable
PR589_EXPECTED = ROOT / "research/gauge44-frames-x/inputs/PR589-EXPECTED.json"    # PR589 bit supplier endpoint
PR635_CODE = ROOT / "research/complex-sw4-frame8/vendor/pr635/research/complex-571-cold14-st2/code"   # native local chain
SLOT_RECIPE = ROOT / "research/gauge44-slots/construction/slots/RECIPE-SLOTS-k8.json"                # #1018 seven slots
