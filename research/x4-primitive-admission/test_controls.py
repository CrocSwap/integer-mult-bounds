"""Adverse controls for the concrete emitted prefix and source boundary."""
from copy import deepcopy
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from lowering import read, require, sources, predecessor, check_prefix


def main(output):
    sources()
    module = predecessor()
    word, _, _ = module.load_inputs(HERE.parents[1])
    pairs = module.pairs(word)
    streams = read(output / 'lowering/PRIMITIVE-PROGRAMS.json.gz')
    rejected = []
    for orientation, stream in streams.items():
        backward = orientation == 'backward'
        check_prefix(stream, pairs, backward)
        mutations = []
        changed = deepcopy(stream); del changed[1]
        mutations.append(('missing_instruction', changed))
        changed = deepcopy(stream); changed[1][1][3] *= -1
        mutations.append(('wrong_sign', changed))
        changed = deepcopy(stream); changed[1][2] = 1
        mutations.append(('nonzero_frame', changed))
        changed = deepcopy(stream); changed[1][1][2] = ['W', 0]
        mutations.append(('scratch_source', changed))
        changed = deepcopy(stream); changed[1][1][3] = True
        mutations.append(('boolean_coefficient', changed))
        changed = deepcopy(stream); del changed[1:5]
        mutations.append(('missing_pair', changed))
        for name, changed in mutations:
            try:
                check_prefix(changed, pairs, backward)
            except (ValueError, IndexError, TypeError) as error:
                rejected.append(orientation + ':' + name)
            else:
                raise ValueError('Primitive corruption accepted: ' + name)
    # Source preflight rejects even whitespace-only changes in immutable inputs.
    path = HERE / 'vendor/pr883/PAIR-PROOF.md'
    original = path.read_bytes()
    try:
        path.write_bytes(original + b' ')
        try:
            sources()
        except ValueError:
            rejected.append('source_drift')
        else:
            raise ValueError('Source drift accepted')
    finally:
        path.write_bytes(original)
    original_invoice = read(output / 'invoice/PREFIX-AND-INVOICE.json')
    with tempfile.TemporaryDirectory(prefix='x4-invoice-controls-') as tmp:
        parent = Path(tmp)
        env = dict(os.environ, WITNESS_SPEC=str(output/'candidate-package/data/SPEC.json'),
                   PYTHONDONTWRITEBYTECODE='1')
        env.pop('PYTHONOPTIMIZE', None)
        mutations = []
        changed = deepcopy(original_invoice); changed['selected_real_component_primitives'] -= 1
        mutations.append(('undercharged_complete_invoice', changed))
        changed = deepcopy(original_invoice); changed['strict_checks']['precision'] = False
        mutations.append(('failed_precision_admission', changed))
        changed = deepcopy(original_invoice); del changed['providers']['gauge44']['primitive_lowering']
        mutations.append(('omitted_lowering_contract', changed))
        for name, changed in mutations:
            case = parent/name
            shutil.copytree(output/'assembly-input', case)
            (case/'audit/PREFIX-AND-INVOICE.json').write_bytes((json.dumps(changed)+'\n').encode())
            result = subprocess.run([sys.executable,'-B',str(output/'candidate-package/code/assemble.py'),
                                     str(HERE.parents[1]/'research/complex-k492-owner-repair/vendor/multicold'),
                                     str(case),str(case/'ASSEMBLY.json')], env=env, capture_output=True, text=True)
            require(result.returncode != 0 and 'AssertionError' in result.stderr,
                    'Assembly corruption accepted or wrong failure: '+name+' '+result.stderr[-500:])
            require(not (case/'ASSEMBLY.json').exists(), 'Failed admission published a result')
            rejected.append(name)
    require(len(rejected) == 16, 'Control coverage')
    print('PASS_X4_PRIMITIVE_ADMISSION_CONTROLS', json.dumps(rejected))


if __name__ == '__main__':
    main(Path(sys.argv[1]).resolve())
