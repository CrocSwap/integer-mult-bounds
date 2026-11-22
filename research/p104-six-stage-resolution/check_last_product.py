"""Replay the candidate configuration on feasible signed and full-product controls."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from upstream import install
install()
from calibration import LAST_TICK
from check_product import physical_product
import json
print(json.dumps(physical_product(LAST_TICK)), flush=True)
print('PASS_LAST_TICK_FEASIBLE_PHYSICAL_PRODUCT', flush=True)
