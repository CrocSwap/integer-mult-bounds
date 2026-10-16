#!/usr/bin/env python3
"""Compile the pinned proof and actual examples; never accept a stored log.

Prepared by ywz65 with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

from verify import LEAN_SHA256, lean_source, require

ROOTS = ['XorLift.basis_complete', 'XorLift.run_linear',
         'XorLift.basis_to_stream', 'XorLift.continuation_substitution',
         'XorLift.example_stream']
EXAMPLE = '''
namespace XorLift
def sampleA : List (Gate 3) := [⟨0, 1⟩, ⟨0, 2⟩]
def sampleB : List (Gate 3) := [⟨1, 2⟩, ⟨0, 1⟩, ⟨1, 2⟩]
theorem example_columns : ∀ j i, run sampleA (basis j) i = run sampleB (basis j) i := by
  decide
theorem example_stream (x : Streams 3 α) : streamRun sampleA x = streamRun sampleB x :=
  basis_to_stream sampleA sampleB (fun j => funext (example_columns j)) x
#print axioms example_stream
end XorLift
'''


def audit(output):
    pattern = re.compile(r"^'([^']+)' (?:does not depend on any axioms|depends on axioms:\s*\[([^]]*)\])", re.M)
    found = {}
    for match in pattern.finditer(output):
        name, axioms = match.groups()
        require(name not in found, 'duplicate axiom report')
        found[name] = [a.strip() for a in axioms.split(',')] if axioms else []
    require(set(found) == set(ROOTS), 'missing or unexpected live axiom reports')
    require(all(set(names) <= {'propext', 'Quot.sound', 'Classical.choice'} for names in found.values()),
            'nonstandard axiom in live kernel result')
    return found


def check(lean):
    require(lean is not None, 'Lean compiler required; pass --lean or put lean on PATH')
    version = subprocess.run([lean, '--version'], capture_output=True, text=True, encoding='utf-8', check=True).stdout.strip()
    source = lean_source()
    controls = {
        'positive': EXAMPLE,
        'missing_restoration': EXAMPLE.replace('[⟨1, 2⟩, ⟨0, 1⟩, ⟨1, 2⟩]', '[⟨1, 2⟩, ⟨0, 1⟩]'),
        'missing_helper_read': EXAMPLE.replace('[⟨0, 1⟩, ⟨0, 2⟩]', '[⟨0, 1⟩]'),
    }
    rows, axioms = [], None
    with tempfile.TemporaryDirectory() as directory:
        for name, suffix in controls.items():
            path = Path(directory) / (name + '.lean')
            path.write_text(source + suffix, encoding='utf-8', newline='\n')
            run = subprocess.run([lean, str(path)], capture_output=True, text=True,
                                 encoding='utf-8', timeout=120)
            output = run.stdout + run.stderr
            if name == 'positive':
                require(run.returncode == 0, 'positive kernel compilation failed: ' + output)
                axioms = audit(output)
            else:
                require(run.returncode != 0 and 'decide' in output and 'false' in output,
                        'negative basis proposition was not rejected by decide: ' + output)
            rows.append({'case': name, 'exit_code': run.returncode, 'output': output})
    return {'status': 'PASS_LIVE_XOR_PREFIX_STREAM_KERNEL', 'lean_version': version,
            'lean_source_sha256': LEAN_SHA256, 'axioms': axioms, 'runs': rows,
            'scope': 'Live compilation of generic theorem and three-wire examples; 661-wire source translation remains external.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lean', default=shutil.which('lean'))
    args = parser.parse_args()
    print(json.dumps(check(args.lean), indent=2))
