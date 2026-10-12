#!/usr/bin/env python3
"""Fresh Lean compilation, complete local theorem axiom audit, source binding,
and deliberately invalid controls. Uses Lean 4.21.0 core only, no Mathlib.
"""
from pathlib import Path
import argparse, copy, hashlib, json, os, re, shutil, subprocess, sys, time
from generate import extract, require

ROOT = Path(__file__).resolve().parent

def run(cmd, env=None, ok=True):
    r = subprocess.run(cmd, cwd=ROOT, env=env, text=True, capture_output=True)
    if ok and r.returncode:
        raise RuntimeError(r.stdout + r.stderr)
    return r

def controls():
    import gzip
    plan = json.loads((ROOT/'source/PLAN.json').read_text())
    roles = json.loads(gzip.decompress((ROOT/'source/OWNERS.json.gz').read_bytes()))
    result = {}
    for name in ['overlap', 'wrong_width', 'duplicate_family', 'wrong_time', 'capacity_overflow', 'missing_helper']:
        p, rs = copy.deepcopy(plan), copy.deepcopy(roles)
        if name == 'overlap':
            rs[0]['offset'] += 1
        elif name == 'wrong_width':
            rs[0]['width'] += 1
        elif name == 'duplicate_family':
            other = next(r for r in rs[1:] if r['time'] == rs[0]['time'])
            other['family'] = rs[0]['family']
        elif name == 'wrong_time':
            rs[0]['time'] = len(p['order'])
        elif name == 'capacity_overflow':
            p['windows'][f"{rs[0]['owner_replica']},{rs[0]['child']}"][0] = rs[0]['width'] - 1
        else:
            rs.pop()
        try:
            extract(p, rs)
        except ValueError as e:
            result[name] = str(e)
        else:
            raise RuntimeError(f'Invalid control accepted: {name}')
    return result

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--lean', default='lean')
    parser.add_argument('--build-dir', type=Path, required=True, help='New empty directory; retained objects are not reused')
    args = parser.parse_args()
    lean = shutil.which(args.lean)
    require(lean is not None, 'Lean executable not found')
    version = run([lean, '--version']).stdout.strip()
    require('version 4.21.0,' in version, 'Expected pinned Lean 4.21.0')
    build = args.build_dir.resolve()
    require(not build.exists(), 'Build directory must not already exist')
    build.mkdir(parents=True)
    env = dict(os.environ, LEAN_PATH=str(build), PYTHONDONTWRITEBYTECODE='1')
    binding = run([sys.executable, '-B', str(ROOT/'generate.py'), '--check']).stdout
    (build/'source-binding.json').write_text(binding)
    started = time.monotonic()
    names = []
    source_hashes = {}
    for module, namespace in [('OwnerTransport', 'OwnerTransport'), ('PR527Templates', 'OwnerTransport.PR527')]:
        p = ROOT/(module+'.lean')
        source = p.read_text()
        # This package contains no nested comments. Exclude documentation from the token scan.
        code = re.sub(r'/\-.*?\-/', '', source, flags=re.S)
        require(not re.search(r'\b(sorry|admit|axiom|native_decide|unsafe)\b', code), 'Forbidden proof escape')
        names += [namespace+'.'+n for n in re.findall(r'^theorem\s+(\w+)', code, flags=re.M)]
        source_hashes[p.name] = hashlib.sha256(p.read_bytes()).hexdigest()
        r = run([lean, '-o', str(build/(module+'.olean')), str(p)], env)
        require(not (r.stdout+r.stderr).strip(), 'Unexpected compiler diagnostics: '+r.stdout+r.stderr)
        (build/(module+'.log')).write_text(r.stdout+r.stderr)
    probe = build/'Axioms.lean'
    probe.write_text('import PR527Templates\n'+'\n'.join('#print axioms '+n for n in names)+'\n')
    audit = run([lean, str(probe)], env).stdout
    (build/'axioms.log').write_text(audit)
    reports = re.findall(r"'([^']+)' (?:depends on axioms: \[([^\]]*)\]|does not depend on any axioms)", audit, re.S)
    require(len(reports) == len(names) and {n for n,_ in reports} == set(names), 'Incomplete axiom audit')
    for name, axioms in reports:
        used = {a.strip() for a in axioms.split(',') if a.strip()}
        require(used <= {'propext','Classical.choice','Quot.sound'}, f'Unapproved axiom for {name}: {used}')
    negative = build/'InvalidCapacity.lean'
    negative.write_text('import OwnerTransport\nexample : OwnerTransport.offset (fun _ => 2) 2 ≤ 3 := by decide\n')
    rejected = run([lean, str(negative)], env, ok=False)
    require(rejected.returncode != 0 and 'false' in rejected.stdout, 'False capacity was not rejected as false')
    (build/'rejected-capacity.log').write_text(rejected.stdout+rejected.stderr)
    receipt = {'status':'PASS','lean':version,'seconds':time.monotonic()-started,
       'fresh_project_modules':2,'theorems_audited':len(names),'theorems':names,
       'source_binding':json.loads(binding),'source_sha256':source_hashes,
       'external_negative_controls':controls(),'lean_false_capacity_rejected':True,
       'boundary':'Lean checks generic arithmetic and 29 templates; Python checks JSON parsing and the association of all source roles with templates. No physical machine, all-size compiler or kappa theorem is proved.'}
    (build/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt,indent=2))

if __name__ == '__main__':
    main()
