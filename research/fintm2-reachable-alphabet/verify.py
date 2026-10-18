"""Source binding and finite controls; --kernel adds a fresh isolated Lean build."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

P = Path(__file__).resolve().parent
sys.path.insert(0, str(P))
from check_model import run_checks, need

NAMES = ('all_prefixes_allowed', 'input_prefixes_allowed', 'work_le_depth', 'work_le_programBound')


def clean(text):
    # Source definitions contain no nested comments; reject unexpected residue.
    text = re.sub(r'/\-.*?\-/', '', text, flags=re.S)
    text = re.sub(r'--[^\n]*', '', text)
    return ' '.join(text.split())


def block(text, start):
    hit = re.search(r'^' + re.escape(start) + r'.*?(?=\n\n)', text, re.M | re.S)
    need(hit is not None, 'missing definition: ' + start)
    return hit[0]


def bind_sources():
    sources = json.loads((P/'SOURCES.json').read_text(encoding='utf-8'))
    for item in sources['snapshots']:
        need(hashlib.sha256((P/item['path']).read_bytes()).hexdigest() == item['sha256'],
             'source hash: ' + item['path'])
    src = (P/'source/StackTuringMachine.lean').read_text(encoding='utf-8')
    fn = (P/'source/Function.lean').read_text(encoding='utf-8')
    dest = (P/'Extracted.lean').read_text(encoding='utf-8')
    for name in ('stepAux', 'step'):
        need(clean(block(src, 'def '+name+' ')) == clean(block(dest, 'def '+name+' ')),
             'changed exact step semantics: ' + name)
    # The source uses section parameters and recursive shorthand. Expand only
    # these binders to a standalone Type-valued declaration; constructors stay.
    original = block(src, 'inductive Stmt')
    lines = original.splitlines()[1:]
    expected = 'inductive Stmt (Γ : K → Type) (Λ σ : Type)\n' + '\n'.join(
        re.sub(r'\bStmt\b', 'Stmt Γ Λ σ', line) for line in lines)
    need(clean(expected) == clean(block(dest, 'inductive Stmt')), 'constructor extraction')
    cfg = block(src, 'structure Cfg').replace('structure Cfg where',
                                            'structure Cfg (Γ : K → Type) (Λ σ : Type) where')
    need(clean(cfg) == clean(block(dest, 'structure Cfg')), 'configuration extraction')
    update_src = block(fn, 'def update').split(':=',1)[1]
    update_dst = block(dest, 'def update').split(':=',1)[1]
    need(clean(update_src) == clean(update_dst), 'dependent update semantics')
    definitions = clean(block((P/'source/Computable.lean').read_text(encoding='utf-8'), 'structure FinTM2'))
    for premise in ('[kFin : Fintype K]', '[ΛFin : Fintype Λ]', '[σFin : Fintype σ]',
                    '[Γk₀Fin : Fintype (Γ k₀)]'):
        need(premise in definitions, 'actual FinTM2 premise: ' + premise)
    need('∀ k, Fintype (Γ k)' not in definitions, 'source boundary changed')
    if (P/'KERNEL.json').is_file():
        retained = json.loads((P/'KERNEL.json').read_text(encoding='utf-8'))
        for name in ('Extracted.lean','Closure.lean'):
            need(hashlib.sha256((P/name).read_bytes()).hexdigest() == retained['sources'][name],
                 'retained kernel receipt names different proof bytes: '+name)
    return {'definitions': ['Stmt','Cfg','update','stepAux','step'],
            'snapshots': len(sources['snapshots']), 'full_mathlib_import': False}


def reports(text):
    need(not re.search(r'\b(error|warning):|sorryAx|\badmitted\b', text), 'Lean diagnostics')
    found = re.findall(r"'Model\.([^']+)' depends on axioms: \[([^\]]*)\]", text)
    need(len(found) == len(NAMES), 'incomplete or duplicate axiom reports')
    need({x[0] for x in found} == set(NAMES), 'theorem inventory')
    result = {}
    for name, raw in found:
        axioms = sorted(x.strip() for x in raw.split(',') if x.strip())
        need(set(axioms) <= {'propext', 'Quot.sound', 'Classical.choice'}, 'unexpected axiom')
        result[name] = axioms
    return result


def report_controls():
    valid = '\n'.join("'Model.%s' depends on axioms: [propext]" % n for n in NAMES)
    reports(valid)
    variants = [valid.split('\n',1)[1], valid+'\n'+valid.splitlines()[0],
                valid.replace('all_prefixes_allowed','unknown_theorem'),
                valid.replace('propext','customAxiom',1), valid+'\nerror: broken',
                valid.replace('propext','sorryAx',1), valid+'\nwarning: skipped']
    for bad in variants:
        try:
            reports(bad)
        except ValueError:
            continue
        raise ValueError('report mutation accepted')
    return len(variants)


def kernel(lean):
    version = subprocess.run([lean,'--version'],capture_output=True,text=True,check=True).stdout
    need('version 4.34.1,' in version and '5045d0056413266e57c625dcd7c365b10e377c52' in version,
         'use pinned Lean4.34.1 release compiler')
    for name in ('Extracted.lean','Closure.lean'):
        body = (P/name).read_text(encoding='utf-8')
        need(not re.search(r'\b(sorry|admit|axiom|unsafe|native_decide)\b', clean(body)),
             'unapproved proof command: '+name)
    with tempfile.TemporaryDirectory(prefix='fintm2-kernel-') as tmp:
        tmp = Path(tmp)
        for name in ('Extracted.lean','Closure.lean'):
            shutil.copyfile(P/name, tmp/name)
        env = os.environ.copy()
        env['LEAN_PATH'] = str(tmp)
        logs = []
        for name in ('Extracted','Closure'):
            result = subprocess.run([lean,'-o',str(tmp/(name+'.olean')),str(tmp/(name+'.lean'))],
                                    cwd=tmp,env=env,capture_output=True,text=True,timeout=120)
            need(result.returncode == 0, 'Lean failed: '+result.stdout+result.stderr)
            logs.append(result.stdout+result.stderr)
        ax = reports('\n'.join(logs))
    return {'status':'PASS_FRESH_ISOLATED_KERNEL_NOT_FULL_MATHLIB', 'lean':'4.34.1',
            'compiler_commit':'5045d0056413266e57c625dcd7c365b10e377c52', 'axioms':ax,
            'sources':{name:hashlib.sha256((P/name).read_bytes()).hexdigest()
                       for name in ('Extracted.lean','Closure.lean')}}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--kernel', action='store_true')
    ap.add_argument('--lean', default=os.environ.get('LEAN'))
    ap.add_argument('--write-kernel-receipt', action='store_true')
    args = ap.parse_args()
    binding = bind_sources()
    finite = run_checks()
    need(finite == json.loads((P/'RESULT.json').read_text(encoding='utf-8')), 'finite receipt differs')
    output = {'status':'PASS_SOURCE_BINDING_AND_FINITE_CONTROLS_NOT_KERNEL',
              'binding':binding,'finite':finite,'report_rejections':report_controls()}
    if args.kernel:
        lean = args.lean or shutil.which('lean')
        need(lean is not None, 'Lean4.34.1 required; provide --lean or LEAN')
        actual = kernel(lean)
        if args.write_kernel_receipt:
            need(not (P/'KERNEL.json').exists(), 'refusing to overwrite kernel receipt')
            (P/'KERNEL.json').write_text(json.dumps(actual,indent=2)+'\n')
        else:
            need(actual == json.loads((P/'KERNEL.json').read_text(encoding='utf-8')), 'kernel receipt differs')
        output['kernel'] = actual
        output['status'] = 'PASS_BOUND_ISOLATED_KERNEL_AND_CONTROLS'
    else:
        need(not args.write_kernel_receipt, 'receipt requires fresh kernel execution')
    print(json.dumps(output,sort_keys=True))


if __name__ == '__main__':
    main()
