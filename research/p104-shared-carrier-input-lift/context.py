"""Explicit path adapter for unchanged, locally retained predecessor engines."""
from pathlib import Path
import native

ROOT=Path(__file__).resolve().parent
need=native.need
MAP={
 'research/higher-moment-strictification/verify.py':'intervals.py',
 'research/kappa-rebuild/architecture/mixed_target_probe.py':'second_intervals.py',
 'research/pr4359-p7-padding/dependencies/compiler-refill/endpoint.py':'endpoint.py',
 'research/pr4359-p7-padding/native_inventory.py':'native_inventory.py',
 'research/kappa-0023-productive-jobs/dependencies/kappa-next-regime/direct-decoder/sources/DATA-PHASES.json':'DATA-PHASES.json',
 'research/query-thinned-controllers/RESULT.json':'BIT-RESULT.json',
}
def resolve(path):
    return ROOT/'retained/runtime'/MAP[path.relative_to(ROOT).as_posix()]
def load(path,name):return native.load(resolve(path),name)
def read(path):return native.read(resolve(path))
