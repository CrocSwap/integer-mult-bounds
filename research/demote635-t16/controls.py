"""Geometric and scalar failures, checked beyond construction hash pins.

Apache-2.0; prepared for seslly with substantial OpenAI Codex assistance.
"""
import argparse
import contextlib
import copy
import gzip
import importlib.util
import io
import json
from pathlib import Path

def read(path):
    raw=path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)

if not __debug__:
    raise RuntimeError('Assertions required; do not use -O')


def main():
    ap = argparse.ArgumentParser()
    for name in ('source', 'word', 'out', 'main', 'recipe'):
        ap.add_argument('--'+name, type=Path, required=True)
    a = ap.parse_args()
    loader = importlib.util.spec_from_file_location('independent_demotion_audit', a.source/'independent/audit_local.py')
    audit = importlib.util.module_from_spec(loader)
    loader.loader.exec_module(audit)
    word = read(a.word)
    recipe = read(a.recipe)
    a.out.mkdir()
    mutations = []
    for helper, before, after in recipe['entrances']:
        bad = copy.deepcopy(word)
        bad['start_extra'][str(helper)] = before
        mutations.append((f'old-entrance-{helper}', bad, ('frame not monotone',)))
    for section, index, before, after in recipe['frames']:
        bad = copy.deepcopy(word)
        bad[section][index][-1] = before
        mutations.append((f'old-frame-{section}-{index}', bad, ('frame not monotone','paid profile mismatch')))
    bad = copy.deepcopy(word)
    bad['start_extra']['635'] = [1,2,4,8]
    mutations.append(('wrong-entrance-plane', bad, ('frame not monotone',)))
    bad = copy.deepcopy(word)
    bad['report']['local_profile']['1'] += 1
    mutations.append(('unpaid-profile', bad, ('paid profile mismatch',)))
    bad = copy.deepcopy(word)
    bad['B'][372][3] *= -1
    mutations.append(('wrong-scalar-sign', bad, ('nonzero entrance response',)))
    rejected = []
    for name, bad, reason in mutations:
        path = a.out/(name+'.json.gz')
        path.write_bytes(gzip.compress(json.dumps(bad).encode(), mtime=0))
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                audit.run(path, a.out/(name+'-unexpected.json'), a.main)
        except RuntimeError as exc:
            assert any(r in str(exc) for r in reason), (name, str(exc))
            rejected.append(dict(name=name, reason=str(exc)))
        else:
            raise AssertionError('Mutation accepted: '+name)
        path.unlink()
    assert len(rejected) == 19
    (a.out/'RESULT.json').write_text(json.dumps(dict(status='PASS_DEMOTE635_FOCUSED_CONTROLS',
                                                   rejected=rejected), indent=2)+'\n')
    print('PASS_DEMOTE635_FOCUSED_CONTROLS', len(rejected))


if __name__ == '__main__':
    main()
