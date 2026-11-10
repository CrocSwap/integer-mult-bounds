"""Run the separately authored finite forward-oracle negative controls."""
from pathlib import Path
import json
import sys
PACKAGE = Path(__file__).resolve().parent
sys.path.insert(0, str(PACKAGE))
import independent_forward
import oracle_checks

if __name__ == '__main__':
    result = oracle_checks.run(independent_forward)
    independent_forward.need(len(result['controls']) == 6, 'six independent decisive controls')
    print(json.dumps(dict(marker='PASS_INDEPENDENT_FORWARD_CONTROLS', **result), sort_keys=True))
