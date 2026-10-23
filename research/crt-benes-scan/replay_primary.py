"""Review helper: run the primary verifier against an explicit source checkout."""
import argparse
import importlib.util
from pathlib import Path
import sys

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("package")
parser.add_argument("source_checkout")
args = parser.parse_args()
package = Path(args.package).resolve()
spec = importlib.util.spec_from_file_location("_independent_review_primary", package / "verify.py")
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)
module.ROOT = Path(args.source_checkout).resolve()
sys.argv = [str(package / "verify.py")]
module.main()
