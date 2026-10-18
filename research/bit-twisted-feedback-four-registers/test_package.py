"""Actual subprocess receipt-corruption controls; Apache-2.0."""
import copy
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent


def main():
    original = json.loads((HERE / 'RESULT.json').read_text(encoding='utf-8'))
    variants = []
    wrong = copy.deepcopy(original)
    wrong['cases'][-1]['maximum_example']['restricted'] -= 1
    variants.append(('understated_minimum',wrong))
    wrong = copy.deepcopy(original)
    wrong['cases'][-1]['maximum_example']['twist'] = [1,2,4]
    variants.append(('wrong_helper_exit',wrong))
    wrong = copy.deepcopy(original)
    wrong['cases'][-1]['full_group_states'] -= 1
    variants.append(('incomplete_group',wrong))
    wrong = copy.deepcopy(original)
    wrong['cases'].pop()
    variants.append(('missing_shape',wrong))
    wrong = copy.deepcopy(original)
    wrong['cases'][-1]['maximum_example']['restricted_word'].pop()
    variants.append(('missing_gate',wrong))
    with tempfile.TemporaryDirectory(prefix='twisted-feedback-') as temp:
        work = Path(temp)
        for file in ['verify.py','independent.py']:
            shutil.copyfile(HERE / file, work / file)
        for name,receipt in [('positive_relocation',original)] + variants:
            (work / 'RESULT.json').write_text(json.dumps(receipt),encoding='utf-8')
            for engine in ['verify.py','independent.py']:
                proc = subprocess.run([sys.executable,'-I','-O','-B',str(work / engine)],
                                      capture_output=True,text=True,timeout=30)
                expected = name == 'positive_relocation'
                if (proc.returncode == 0) != expected:
                    raise ValueError(name + '/' + engine + ': ' + proc.stdout + proc.stderr)
    print('PASS_TWISTED_FEEDBACK_PACKAGE positive_relocation=2 rejected_corruptions=10')


if __name__ == '__main__':
    main()
