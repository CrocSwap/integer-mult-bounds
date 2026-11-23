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

def controls(directory):
    import gzip
    plan = json.loads((ROOT/directory/'PLAN.json').read_text())
    roles = json.loads(gzip.decompress((ROOT/directory/'OWNERS.json.gz').read_bytes()))
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
    literal_binding = run([sys.executable, '-B', str(ROOT/'generate_table.py'), '--check']).stdout
    (build/'literal-binding.json').write_text(literal_binding)
    hosting_binding = run([sys.executable, '-B', str(ROOT/'generate_separation.py'), '--check']).stdout
    (build/'hosting-binding.json').write_text(hosting_binding)
    controller_binding = run([sys.executable, '-B', str(ROOT/'generate_schedule.py'), '--check']).stdout
    (build/'controller-binding.json').write_text(controller_binding)
    started = time.monotonic()
    names = []
    source_hashes = {}
    modules = [('OwnerTransport', 'OwnerTransport'), ('WidthMatching', 'OwnerTransport.WidthMatching'),
               ('PR527Templates', 'OwnerTransport.PR527'), ('PR531Templates', 'OwnerTransport.PR531'),
               ('OwnerTable', 'OwnerTransport.OwnerTable'),
               ('OwnerTableControls', 'OwnerTransport.OwnerTableControls'),
               ('PR531TableData', 'OwnerTransport.PR531Table'),
               ('PR531TableCertificate', 'OwnerTransport.PR531Table'),
               ('OwnerSeparation', 'OwnerTransport.OwnerSeparation'),
               ('PR531DataWindows', 'OwnerTransport.PR531DataWindows'),
               ('PR531InvocationOwners', 'OwnerTransport.PR531InvocationOwners'),
               ('BorrowSchedule', 'OwnerTransport.BorrowSchedule'),
               ('BorrowScheduleControls', 'OwnerTransport.BorrowScheduleControls'),
               ('PR531Controller', 'OwnerTransport.PR531Controller'),
               ('PR531ScheduledOwners', 'OwnerTransport.PR531ScheduledOwners')]
    for module, namespace in modules:
        p = ROOT/(module+'.lean')
        source = p.read_text()
        # This package contains no nested comments. Exclude documentation from the token scan.
        code = re.sub(r'/\-.*?\-/', '', source, flags=re.S)
        require(not re.search(r'\b(sorry|admit|axiom|native_decide|unsafe)\b', code), 'Forbidden proof escape')
        names += [namespace+'.'+n for n in re.findall(r'^theorem\s+(\w+)', code, flags=re.M)]
        source_hashes[p.name] = hashlib.sha256(p.read_bytes()).hexdigest()
        print('Checking '+module, flush=True)
        r = run([lean, '-s', '65536', '-o', str(build/(module+'.olean')), str(p)], env)
        require(not (r.stdout+r.stderr).strip(), 'Unexpected compiler diagnostics: '+r.stdout+r.stderr)
        (build/(module+'.log')).write_text(r.stdout+r.stderr)
    probe = build/'Axioms.lean'
    probe.write_text('import WidthMatching\nimport PR527Templates\nimport PR531Templates\nimport OwnerTableControls\nimport PR531TableCertificate\nimport PR531InvocationOwners\nimport BorrowScheduleControls\nimport PR531ScheduledOwners\n'+'\n'.join('#print axioms '+n for n in names)+'\n')
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
    regression = build/'MatchingControls.lean'
    regression.write_text("""import WidthMatching
open OwnerTransport.WidthMatching
-- Processing a small demand first can consume the only owner for a larger one.
example : allocate id [1, 2] [2, 1] = none := by decide
example : allocate id (descending [1, 2]) [2, 1] = some ([2, 1], []) := by
  simp [descending, List.mergeSort, allocate, select]
-- Owners of identical widths retain their separate physical identities.
example : allocate (fun a : Nat × Nat => a.2) [3, 3] [(10, 3), (11, 3)] =
    some ([(10, 3), (11, 3)], []) := by decide
example : allocate id (descending [0, 2]) [0, 2] = some ([2, 0], []) := by
  simp [descending, List.mergeSort, allocate, select]
example : allocate id [] [4] = some ([], [4]) := by decide
example : allocate id [5] [4] = none := by decide
""")
    result = run([lean, str(regression)], env)
    require(not (result.stdout+result.stderr).strip(), 'Unexpected regression diagnostics')
    (build/'matching-controls.log').write_text(result.stdout+result.stderr)
    receipt = {'status':'PASS' ,'lean':version,'seconds':time.monotonic()-started,
       'fresh_project_modules':len(modules),'theorems_audited':len(names),'theorems':names,
       'source_binding':json.loads(binding),'literal_binding':json.loads(literal_binding),'hosting_binding':json.loads(hosting_binding),'controller_binding':json.loads(controller_binding),'source_sha256':source_hashes,
       'external_negative_controls':{label:controls(directory) for label,directory in [('PR527','source'),('PR531','source531')]},'matching_regression_examples':6,'owner_table_control_theorems':10,'controller_control_theorems':7,'lean_false_capacity_rejected':True,
       'kernel_object_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in build.glob('*.olean')},
       'verification_phases':[{'phase':'Fresh full package compilation and axiom audit','modules':len(modules)}],
       'boundary':'Lean checks compaction, complete sorted-dominance matching, stateful admissible-policy correctness, both source template tables, and a sound full-row owner-table checker with rejection controls. Lean also certifies the complete selected literal row witness, every inverse group and family index link, declared-window separation from active data, injective ownership for all 728 registers in each invocation, and the finite controller trace with exact borrowing windows, untouched interiors and same-lane separation. Python performs source-byte parsing/projection into Lean literals, associates the source data-bank formula and helper routes, and checks the PR527 source-to-template association. Neither the source Python allocator nor the physical implementation of the controller/events, charts, all-size compiler, numerical/analytic dependencies or full multiplication theorem is proved.'}
    (build/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt,indent=2))

if __name__ == '__main__':
    main()
