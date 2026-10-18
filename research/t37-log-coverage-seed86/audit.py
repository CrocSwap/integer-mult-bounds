# SPDX-License-Identifier: Apache-2.0
"""Supplementary T37 stage/log coverage, not a supplier or execution proof.

Prepared for Sagar Thakrar with substantial OpenAI Codex assistance.
The fixed stage orders come from Jonathan Capalbo's PR942 and its U8 producer.
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path


TOP = (
    'ancestry-coverage', 'baseline799-binding', 'u8-native', 'prepare',
    'frozen-construction', 'independent-owners', 'build-parent', 'check-parent',
    'independent-price', 'discovery', 'strict', 'payload-controls', 'final-binding',
)
NATIVE = (
    'barch', 'barch-controls', 'layer-end-controls', 'native', 'ledgers',
    'local-replay', 'wrappers', 'phases',
)
COMMON = ('bind', 'emit', 'audit', 'invoice', 'assembly')
INDEXES = {
    'STAGES.json': ('name', TOP),
    'native/STEPS.json': ('step', NATIVE),
    'discovery/STAGES.json': ('name', COMMON + ('freeze',)),
    'strict/STAGES.json': ('name', COMMON + ('admission-controls', 'bit-controls')),
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def file_at(work, name):
    path = (work / name).resolve()
    require(path.is_relative_to(work) and path.is_file(), 'Missing or escaping file: ' + name)
    return path


def check(work):
    """Check a completed T37 directory without running or changing its contents."""
    work = Path(work).resolve()
    logs = {}
    for relative, (key, expected) in INDEXES.items():
        index = file_at(work, relative)
        stages = json.loads(index.read_bytes())
        require(type(stages) is list and all(type(s) is dict for s in stages),
                'Invalid stage index: ' + relative)
        names = tuple(s.get(key) for s in stages)
        allowed = (expected,)
        if relative == 'STAGES.json':
            allowed += (('baseline799-cold',) + expected,)
        require(names in allowed, 'Stage sequence differs: ' + relative)
        for stage in stages:
            name = (Path(relative).parent / (stage[key] + '.log')).as_posix()
            require(type(stage.get('exit_code')) is int and stage['exit_code'] == 0,
                    'Stage did not record integer success: ' + name)
            digest = sha256(file_at(work, name).read_bytes()).hexdigest()
            bound = relative != 'native/STEPS.json'
            if bound:
                require(stage.get('log_sha256') == digest, 'Stage log digest differs: ' + name)
            logs[name] = {'sha256': digest, 'producer_digest_checked': bound}
    return {
        'status': 'PASS_T37_STAGE_LOG_COVERAGE',
        'stage_indexes': len(INDEXES),
        'logs': logs,
        'producer_digest_checks': sum(v['producer_digest_checked'] for v in logs.values()),
        'presence_only_logs': sum(not v['producer_digest_checked'] for v in logs.values()),
        'scope': 'Ordered successful stage records and log coverage only. Native log '
                 'digests are observations, not producer commitments. No supplier replay, '
                 'execution authentication, mathematical acceptance or new kappa.',
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--work', type=Path, required=True)
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    result = check(args.work)
    if args.out:
        with args.out.open('x', encoding='utf-8') as stream:
            stream.write(json.dumps(result, sort_keys=True, indent=2) + '\n')
    print(result['status'], len(result['logs']), 'logs;',
          result['producer_digest_checks'], 'producer digests;',
          result['presence_only_logs'], 'presence-only')


if __name__ == '__main__':
    main()
