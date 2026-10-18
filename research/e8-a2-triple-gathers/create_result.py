# Do not run as part of verification: just constructs the frozen receipt.
from verify import run
import json
from pathlib import Path
Path(__file__).with_name('RESULT.json').write_text(json.dumps(run(), indent=2, sort_keys=True)+'\n')
