"""Fixed fork-round evaluator; lower total copied rank is better."""
import argparse
import json
from pathlib import Path
from exact import Instance

parser = argparse.ArgumentParser()
parser.add_argument("candidate", type=Path)
args = parser.parse_args()
candidate = json.loads(args.candidate.read_text())
print(json.dumps(Instance(candidate["instance"]).evaluate(candidate["terms"]), sort_keys=True))
