"""Replay the finite proof premises in a temporary directory."""
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent

def require(condition, message):
    if not condition:
        raise ValueError(message)

for name, expected in json.loads((HERE / 'SOURCE-HASHES.json').read_text()).items():
    require(hashlib.sha256((HERE / name).read_bytes()).hexdigest() == expected,
            'Source hash mismatch: ' + name)

with tempfile.TemporaryDirectory(prefix='e8-small-redundancy-') as temp:
    work = Path(temp) / 'package'
    shutil.copytree(HERE, work, ignore=shutil.ignore_patterns('__pycache__'))
    def run(script, *args):
        completed = subprocess.run([sys.executable, '-E', '-B', str(work / script), *args],
                                   cwd=work, capture_output=True, text=True, timeout=300)
        require(completed.returncode == 0, script + '\n' + completed.stderr)
        print('PASS ' + script, flush=True)
        return completed.stdout
    for script in ['parabolic_check.py', 'e7_complements.py', 'eleven_facts.py',
                   'independent_structure.py', 'independent_eleven_facts.py',
                   'independent_coordinate_map.py']:
        run('binary/' + script)
    for name in ['parabolic-results.json', 'e7-complements.json', 'eleven-facts.json',
                 'independent-structure-result.json', 'independent-eleven-facts.json',
                 'independent-coordinate-map.json']:
        require(json.loads((work / 'binary' / name).read_text()) ==
                json.loads((HERE / 'binary' / name).read_text()),
                'Receipt mismatch: ' + name)
    certificate = str(work / 'inputs/complex-word.json.gz')
    actual = json.loads(run('coordinate/coordinate_totals_rigidity.py', certificate))
    expected = json.loads((HERE / 'coordinate/coordinate_totals_rigidity.json').read_text())
    require(actual == expected, 'Coordinate receipt mismatch')
    independent = json.loads(run('coordinate/rigidity_review_72vars.py', certificate))
    require(independent['variables'] == 72 and independent['field_prime'] == 107,
            'Independent coordinate model mismatch')
    require([x['rank_mod_107'] for x in independent['results']] == [71,72,72,72,72],
            'Independent coordinate ranks mismatch')
print('PASS_E8_SMALL_REDUNDANCY coordinate_rigidity=9 binary_terms<=11 pairing_floor=72 no_new_kappa')
