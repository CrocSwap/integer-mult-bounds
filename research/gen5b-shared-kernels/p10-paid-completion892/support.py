"""Portable, hash-checked data and authored-code contract. Upstream is inert."""
from pathlib import Path
from functools import lru_cache
import gzip, hashlib, json, os
HERE = Path(__file__).resolve().parent
INPUTS = Path(os.environ.get('P10P_INPUTS', str(HERE/'local-inputs'))).resolve()
OUTPUT = Path(os.environ.get('P10P_OUTPUT', str(HERE/'output'))).resolve()
BASE_CODE = HERE.parent/'p10-updated1047'
BASE_OUTPUT = OUTPUT/'baseline'
INPUT_MANIFEST = BASE_CODE/'inputs.json'
HEAD = '1b37957d1520c80b6ea796bf418e52be5109c2d4'
WORD_SHA = '25a0edc8c5f399fcf536b28c4e3575aa52177bb78b6078a631acb748954f0739'
ADM, BANK, FRAME, LOWER, AUDIT = [OUTPUT/x for x in ['admission','bank','frame','lowering','audit']]
WORD = ADM/'word_weighted892.json'
for p in [ADM, BANK, FRAME, LOWER, AUDIT]: p.mkdir(parents=True, exist_ok=True)
def require_assertions():
    if not __debug__: raise RuntimeError('Assertions must be enabled; run without -O.')
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def out(*parts):
    p = OUTPUT.joinpath(*parts); p.parent.mkdir(parents=True, exist_ok=True); return p
def verify_dependencies():
    require_assertions()
    pins = json.loads((HERE/'dependencies.json').read_text())
    for name, digest in pins.items():
        p = HERE.parent/name
        assert sha(p) == digest, 'Published authored dependency changed: '+name
    return pins
@lru_cache(None)
def pins():
    require_assertions(); verify_dependencies()
    result = json.loads(INPUT_MANIFEST.read_text()); assert result['head'] == HEAD
    assert len({r['path'] for r in result['files']}) == len(result['files'])
    for row in result['files']:
        for key in ('path', 'local'):
            assert not Path(row[key]).is_absolute() and '..' not in Path(row[key]).parts
        assert not row['local'].endswith('.py'), 'Upstream programs must remain inert text.'
        assert row['url'] == f"https://raw.githubusercontent.com/{result['repository']}/{HEAD}/{result['package']}{row['path']}"
    return result
def check_bytes(raw, row):
    require_assertions()
    assert len(raw) == row['bytes'] and hashlib.sha256(raw).hexdigest() == row['sha256'], row['path']
    assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest() == row['git_blob'], row['path']
@lru_cache(None)
def read_bytes(name):
    row = next(r for r in pins()['files'] if r['path'] == name)
    raw = (INPUTS/row['local']).read_bytes(); check_bytes(raw, row); return raw
def verify_inputs():
    require_assertions()
    for row in pins()['files']: read_bytes(row['path'])
def materialize_word():
    word = json.loads(gzip.decompress(read_bytes('bitword/selected/bit/word_p10.json.gz')))
    delta = json.loads((HERE/'witnesses/weighted892-delta.json').read_text())
    assert delta['source_head'] == HEAD and delta['candidate_word_sha256'] == WORD_SHA
    pairs = set(map(tuple, word['pairs'])); remove = set(map(tuple, delta['remove'])); add = set(map(tuple, delta['add']))
    assert remove <= pairs and not pairs & add and len(remove) == 71 and len(add) == 73
    word['pairs'] = [list(x) for x in sorted((pairs-remove)|add)]; word['reads'].update(delta['reads_add'])
    assert len(word['pairs']) == len({a for a,b in word['pairs']}) == len({b for a,b in word['pairs']}) == 892
    raw = json.dumps(word, sort_keys=True, separators=(',',':')).encode()+b'\n'
    assert hashlib.sha256(raw).hexdigest() == WORD_SHA; WORD.write_bytes(raw); return WORD
def admission_artifact(name):
    return ADM/name[7:] if name.startswith('output/') else HERE/'admission'/name
ADMISSION_OUTPUTS = ['kernel-path-receipts.json','rebound-kernel-entries.json','rebound-later-selections.json','reorder-controls-result.json','reorder-transport-result.json','scalar-recurrence-result.json','source-target-geometry-result.json','target-chronology-result.json','transport-result.json','virtual-physical-map.json']
def finalize_admission(test_count):
    assert test_count == 17
    result = json.loads((HERE/'witnesses/admission-summary.json').read_text())
    result['source_input_manifest_sha256'] = sha(INPUT_MANIFEST)
    result['regression_tests_passed'] = test_count
    result['all_regenerated_outputs_bound'] = True
    result['artifact_hashes'] = {'output/'+n:sha(ADM/n) for n in ADMISSION_OUTPUTS}
    (ADM/'ADMISSION-RESULT.json').write_text(json.dumps(result, indent=2)+'\n')
    files = [{'path':'output/'+n, 'bytes':(ADM/n).stat().st_size, 'sha256':sha(ADM/n)} for n in ADMISSION_OUTPUTS]
    files += [{'path':p.name, 'bytes':p.stat().st_size, 'sha256':sha(p)} for p in sorted((HERE/'admission').glob('*.py'))]
    (ADM/'MANIFEST.json').write_text(json.dumps({'head':HEAD,'word_sha256':WORD_SHA,'files':files},indent=2)+'\n')
    verify_admission()
def verify_admission():
    require_assertions(); result = json.loads((ADM/'ADMISSION-RESULT.json').read_text())
    assert result['head'] == HEAD and result['candidate_sha256'] == WORD_SHA
    assert result['candidate_pairs'] == 892 and result['all_installed_kernels'] == 1047
    assert result['regression_tests_passed'] == 17 and result['all_regenerated_outputs_bound']
    for name, digest in result['artifact_hashes'].items(): assert sha(admission_artifact(name)) == digest, name
    manifest = json.loads((ADM/'MANIFEST.json').read_text())
    for row in manifest['files']:
        p = admission_artifact(row['path']); assert p.stat().st_size == row['bytes'] and sha(p) == row['sha256'], row['path']
    scalar = json.loads((ADM/'scalar-recurrence-result.json').read_text())
    assert scalar['checker_sha256'] == sha(HERE/'admission/check_scalar_recurrence.py')
    assert scalar['forward']['max_row_l1'] == 132143 and scalar['inverse']['max_row_l1'] == 1307556
    return result

def portable(value):
    """Normalize only declared root names before hashing generated receipts."""
    if isinstance(value, dict): return {portable(k):portable(v) for k,v in value.items()}
    if isinstance(value, list): return [portable(v) for v in value]
    if isinstance(value, str):
        for path,label in [(OUTPUT, '$OUTPUT'), (INPUTS, '$INPUTS'), (HERE, '$PACKAGE'), (HERE.parent, '$AUTHORED')]: value=value.replace(str(path),label)
    return value

def validate_correction(value):
    """Bind the regenerated correction to its current producer and exact inputs."""
    require_assertions(); verify_admission()
    assert value['status'] == 'PASS_CORRECTED_ALL960_FINAL_DESCENDED_SOURCE_CHAINS'
    assert value['head'] == HEAD and value['candidate_sha256'] == WORD_SHA
    assert value['checker_sha256'] == sha(HERE/'frame/check_descended_sources.py')
    assert value['previous_admission_manifest_sha256'] == sha(ADM/'MANIFEST.json')
    assert value['previous_supplementary_receipt_sha256'] == sha(ADM/'source-target-geometry-result.json')
    assert value['input_manifest_sha256'] == sha(INPUT_MANIFEST)
    assert value['source_columns'] == 960 and value['retimed_setups'] == 480
    return value

def verify_correction():
    return validate_correction(json.loads((FRAME/'SOURCE-GEOMETRY-CORRECTION.json').read_text()))
