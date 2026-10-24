#!/usr/bin/env python3
"""Run the inherited rational-projector BIT audit, not only its XOR subroutine."""
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path.cwd()/'research/kappa-rebuild/bit'))
sys.path.insert(0, str(Path.cwd()/'research/kappa-0023-productive-jobs/dependencies/kappa-next-regime/bit-compression/carrier-reuse/reference'))
import mixed_productive_bit as bit
word, streams, receipt = bit.audit_local(bit.HERE/'sources/pr589-regenerated/WORD.json.gz')
Path(__file__).with_name('source-control-result.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt))
