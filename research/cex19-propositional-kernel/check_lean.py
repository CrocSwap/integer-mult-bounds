"""Compile the complete explicit proof and reject altered small proof controls."""
import argparse
import importlib.util
from pathlib import Path
import re
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('cex19_kernel', HERE / 'kernel.py')
K = importlib.util.module_from_spec(spec)
spec.loader.exec_module(K)


def compile_file(lean, path, timeout):
    result = subprocess.run([str(lean), '-j1', str(path)], cwd=path.parent,
                            capture_output=True, text=True, encoding='utf-8', timeout=timeout)
    return result.returncode, result.stdout + result.stderr


def audit(output, root):
    matches = re.findall(r"'" + re.escape(root) + r"' depends on axioms:\s*\[([^]]*)\]", output)
    K.require(len(matches) == 1, 'missing or duplicate axiom report')
    names = {x.strip() for x in matches[0].split(',') if x.strip()}
    K.require(names <= {'propext', 'Classical.choice', 'Quot.sound'}, 'nonstandard axiom')
    K.require('sorry' not in output.lower() and not re.search(r'\berror(?:\([^\n]*\))?:', output.lower()), 'Lean diagnostics')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--lean', required=True, type=Path)
    args = parser.parse_args()
    lean = args.lean.resolve()
    version = subprocess.check_output([str(lean), '--version'], text=True)
    K.require('version 4.34.1' in version, 'use pinned Lean4.34.1')
    _, clauses, _, actions = K.evidence()
    raw = (HERE / 'Certificate.lean').read_text(encoding='utf-8')
    K.require(not re.search(r'\b(sorry|admit|axiom|native_decide|ofReduceBool)\b', raw), 'forbidden proof shortcut')
    code, output = compile_file(lean, HERE / 'Certificate.lean', 600)
    K.require(code == 0, 'full kernel compilation failed: ' + output[-3000:])
    audit(output, 'Cex19Core.core_unsat')
    small = K.render(clauses, actions, first_only=True)
    changed_clause = re.sub(r'(  c\d+ : ).*', r'\1True', small, count=1)
    referenced = next(name for name in re.findall(r'  have (a\d+) : ', small)
                      if len(re.findall(r'\b' + name + r'\b', small)) > 1)
    changed_step = small.replace('  have ' + referenced + ' : ', '  have broken_assumption : ', 1)
    with tempfile.TemporaryDirectory(prefix='cex19-lean-') as folder:
        directory = Path(folder)
        positive = directory / 'Positive.lean'
        positive.write_text(small, encoding='utf-8')
        code, output = compile_file(lean, positive, 120)
        K.require(code == 0, 'positive small proof failed: ' + output[-1000:])
        audit(output, 'Cex19Core.s9965')
        for name, text in [('ChangedClause', changed_clause), ('LostDerivation', changed_step)]:
            path = directory / (name + '.lean')
            path.write_text(text, encoding='utf-8')
            code, output = compile_file(lean, path, 120)
            K.require(code != 0 and re.search(r'\berror(?:\([^\n]*\))?:', output),
                      'invalid proof accepted: ' + name + '\n' + output[-1000:])
    try:
        audit("'Cex19Core.core_unsat' depends on axioms: [propext, invented_assumption]", 'Cex19Core.core_unsat')
    except ValueError:
        pass
    else:
        raise ValueError('axiom audit accepted an invented assumption')
    print('PASS_CEX19_KERNEL core_unsat standard_axioms_only positive_projection=1 rejected_mutants=2 axiom_control=1')


if __name__ == '__main__':
    main()
