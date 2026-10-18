"""Focused admission and complete-word failure controls; Apache-2.0.

Eva Ayala / ToikY, with substantial OpenAI Codex assistance.
Run from any directory with Python 3.10+ and its standard library.
"""
import copy
import gzip
import importlib.util
import json
from pathlib import Path
import tempfile
from unittest import mock

spec = importlib.util.spec_from_file_location('ck_grid_audit', Path(__file__).resolve().parent/'verify.py')
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


def rejects(action, expected):
    try:
        action()
    except ValueError as error:
        if expected not in str(error):
            raise ValueError('unexpected rejection: ' + str(error)) from error
    else:
        raise ValueError('accepted failure control: ' + expected)


def run():
    census = audit.read(audit.HERE / 'CENSUS.json.gz')
    reference = audit.load(audit.ROOT / 'research/complex-dyadic-lowering/lower.py', 'control_reference')
    programs = audit.read(audit.DATA / 'LOCAL-PROGRAMS.json.gz')
    checks = audit.read(audit.DATA / 'LOCAL-CHECKS.json')['forward']
    inherited = audit.read(audit.DATA / 'INDEPENDENT-LOCAL-REPLAY.json')['local']['forward']

    # Alter the final target-writing addition rather than a preparation that
    # could be cancelled by a later inverse. The complete map must reject it.
    altered = copy.deepcopy(programs['forward'])
    indices = [i for i, event in enumerate(altered)
               if event[0] == 'scalar' and event[1][0] == 'add'
               and event[1][1][0] == 'L' and 112 <= event[1][1][1] < 224]
    if not indices:
        raise ValueError('no forward target addition')
    altered[indices[-1]][1][3] *= -1
    rejects(lambda: audit.replay('forward', altered, census, reference, checks, inherited),
            'full scalar endpoint')

    original_emit = audit.emit

    def omit_clear(op, *args):
        word = original_emit(op, *args)
        return word[:-1] if op[0] == 'add' else word

    with mock.patch.object(audit, 'emit', omit_clear):
        rejects(lambda: audit.replay('forward', programs['forward'], census, reference, checks, inherited),
                'work survived macro')

    # Pin admission happens before mathematical replay. A semantic source edit
    # must reject; a gzip-container change with the same payload remains valid.
    source_names = audit.read(audit.HERE / 'SOURCES.json')['payload_sha256']
    with tempfile.TemporaryDirectory(prefix='ck-grid-source-control-') as temporary:
        root = Path(temporary)
        changed_name = 'research/community-k492-audit/pr626/replay/mixed-global/base/providers/ck/LOCAL-PROGRAMS.json.gz'
        for name in source_names:
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            if name == changed_name:
                changed_programs = copy.deepcopy(programs)
                changed_programs['forward'][indices[-1]][1][3] *= -1
                path.write_bytes(gzip.compress(audit.canonical(changed_programs), mtime=7))
            else:
                path.symlink_to(audit.ROOT / name)
        with mock.patch.object(audit, 'ROOT', root):
            rejects(audit.verify, 'source pin ' + changed_name)

    with tempfile.TemporaryDirectory(prefix='ck-grid-census-control-') as temporary:
        here = Path(temporary)
        (here / 'SOURCES.json').symlink_to(audit.HERE / 'SOURCES.json')
        (here / 'synth.py').symlink_to(audit.HERE / 'synth.py')
        changed = copy.deepcopy(census)
        changed['1/64']['cost'] -= 1
        (here / 'CENSUS.json.gz').write_bytes(gzip.compress(audit.canonical(changed), mtime=0))
        with mock.patch.object(audit, 'HERE', here):
            rejects(audit.verify, 'census mismatch')

        # Same semantic census under a different gzip timestamp is accepted by
        # the payload reader and the independent checker.
        (here / 'CENSUS.json.gz').write_bytes(gzip.compress(audit.canonical(census), mtime=123))
        recompressed = audit.read(here / 'CENSUS.json.gz')
        if recompressed != census:
            raise ValueError('gzip recompression changed semantic census')
        independent = audit.load(audit.HERE / 'independent.py', 'recompression_independent')
        independent.check(recompressed)
    print('PASS_CK_GRID_PACKAGE full_word_rejections=2 admission_rejections=2 recompression=1')


if __name__ == '__main__':
    run()
