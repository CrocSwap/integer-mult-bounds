"""External binding replay; Lean kernel compilation is a separate command."""
import copy
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('cex19_kernel', HERE / 'kernel.py')
K = importlib.util.module_from_spec(spec)
spec.loader.exec_module(K)


def rejects(function, message):
    try:
        function()
    except (ValueError, KeyError, IndexError):
        return
    raise ValueError('accepted negative control: ' + message)


def main():
    result, clauses, proof, actions = K.evidence()
    K.require(result == json.loads((HERE / 'RESULT.json').read_text()), 'complete result receipt')
    bad = copy.deepcopy(actions)
    bad[0][2].pop()
    rejects(lambda: K.check_trace(clauses, proof, bad), 'missing conflict')
    bad = copy.deepcopy(actions)
    bad[0][2][0] = bad[0][0]
    rejects(lambda: K.check_trace(clauses, proof, bad), 'future antecedent')
    bad = copy.deepcopy(actions)
    bad[0][1][0] *= -1
    rejects(lambda: K.check_trace(clauses, proof, bad), 'changed consequence')
    rejects(lambda: K.check_trace(clauses, proof[:-1], actions[:-1]), 'missing final contradiction')
    print('PASS_CEX19_PROPOSITIONAL_BINDING core_clauses=2675 derived=602 antecedents=25711 controls=4')
    print('Lean kernel compilation is separate: check_lean.py --lean PATH_TO_LEAN')


if __name__ == '__main__':
    main()
