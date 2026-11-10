"""Run the full independent history/rank check and physical-domain proof check."""
from pathlib import Path
import json
import runpy

HERE = Path(__file__).resolve().parent
history = runpy.run_path(str(HERE / 'check_review.py'))
domain = runpy.run_path(str(HERE / 'physical_domain.py'))
actual = {
    'domain': domain['check_domain'](history['w'], history['r']['audit'], history['times'][0]),
    'controls': domain['domain_controls'](),
}
if actual != json.loads((HERE / 'DOMAIN-RESULT.json').read_bytes()):
    raise ValueError('Exact independent physical-domain receipt')
print(json.dumps(actual, sort_keys=True))
print('PASS_INDEPENDENT_FULL_HUB_AND_DOMAIN')
