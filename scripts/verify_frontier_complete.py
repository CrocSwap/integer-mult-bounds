#!/usr/bin/env python3
"""Run the immutable historical replay with enforced versioned coverage."""
import argparse
from pathlib import Path
import subprocess
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from verify_replay_coverage import check_ancestor, check_selected, require
import json

ROOT = Path(__file__).resolve().parents[1]


def publish(work, replay, frontier, ancestor=None):
    """Publish a public success record only after real evidence passes."""
    if frontier == '799':
        result = check_selected(replay, ancestor)
    else:
        parent = check_ancestor(replay / 'bit', replay / 'complex')
        result = dict(status='PASS_COMPLETE_PR741_REPLAY_COVERAGE', binding=parent)
    temporary = work / 'RESULT.json.tmp'
    temporary.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    temporary.replace(work / 'RESULT.json')
    (work / 'COVERAGE.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--frontier', choices=['741', '799'], required=True)
    p.add_argument('--work', type=Path, required=True)
    p.add_argument('--ancestor', type=Path)
    a = p.parse_args()
    require(not sys.flags.optimize, 'Cold replay workers require enabled assertions')
    require(a.frontier == '799' or a.ancestor is None, 'Ancestor flag is only for PR799')
    work = a.work.resolve()
    require(not work.exists() and not work.is_relative_to(ROOT),
            'Use a fresh output directory outside the repository')
    # Reject incomplete reuse before paying for any new native/global work.
    if a.ancestor is not None:
        check_ancestor(a.ancestor / 'bit', a.ancestor / 'complex')
    work.mkdir(parents=True)
    replay = work / 'replay'
    command = [sys.executable, '-B', str(ROOT / ('scripts/verify_frontier' + a.frontier + '.py')),
               '--work', str(replay)]
    if a.ancestor is not None:
        command += ['--ancestor', str(a.ancestor)]
    subprocess.run(command, check=True)
    result = publish(work, replay, a.frontier, a.ancestor.resolve() if a.ancestor else None)
    print(result['status'], flush=True)


if __name__ == '__main__':
    main()
