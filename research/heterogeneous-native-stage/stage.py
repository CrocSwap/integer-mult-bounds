"""Exploratory paid native stage with 60 reduced fresh-axis port endpoints.

Apache-2.0; Cinna Davis / 1337isnot1337, substantial OpenAI Codex assistance.
Reuses Cao Yifan's source and the credited PR5144 model without editing them.
"""
from collections import Counter
import importlib.util
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
spec = importlib.util.spec_from_file_location(
    'partial_stage_predecessor', ROOT / 'research/owned-kernel-shared-map/shared_maps.py')
S = importlib.util.module_from_spec(spec)
spec.loader.exec_module(S)
M = S.M


def build(payload, forms):
    M.need(forms == [1], 'One explicit heterogeneous stage, not an axis census')
    model = S.build(payload, forms)
    c = payload['canonical']
    frames = c['frames']
    eligible = [i for i, f in enumerate(c['start'][:112])
                if (frames[f][0] & forms[0]).bit_count() % 2 == 0]
    M.need(len(eligible) == 60, 'Actual source has60 eligible central lines')
    end_start = len(model['nodes']) - 8 - 632
    forced = {end_start + r for i in eligible for r in (i, i + 112)}
    for i in eligible:
        x, y = c['final'][i], c['final'][i + 112]
        q = frames[c['start'][i]][0]
        X, Y = model['new_spaces'][x], model['new_spaces'][y]
        M.need(M.dimension(X) == 8 and M.dimension(Y) == 7,
               'Fresh-axis endpoint dimensions8 and7')
        M.need(X >> q & 1 and not (Y >> q & 1), 'Central direction retained outside reduced Y')
        M.need(X == (Y | M.mask(v ^ q for v in range(512) if Y >> v & 1)),
               'Reduced X splits into central line and reduced Y')
    M.need(forced <= set(model['fixed']), 'All changed endpoints remain fixed choices')
    def table(a, b, ranks):
        return [ranks[(i ^ int(a in forced)) + 2 * (j ^ int(b in forced))]
                for i, j in ((0, 0), (1, 0), (0, 1), (1, 1))]
    model['edges'] = [(kind, a, b, table(a, b, ranks))
                      for kind, a, b, ranks in model['edges']]
    model['helpers'] = [(role, a, b, table(a, b, ranks))
                        for role, a, b, ranks in model['helpers']]
    model['forced_endpoints'] = sorted(forced)
    model['eligible_ports'] = eligible
    return model


def discover(seconds=120):
    spec = importlib.util.spec_from_file_location(
        'partial_stage_discovery', ROOT / 'research/general-gaussian-contact-search/discover.py')
    prior = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(prior)
    prior.M = M
    M.build = build
    result = prior.solve(S.SOURCE, [1], seconds, 'none', 'kernel')
    model = build(S.payload(), [1])
    result.update(eligible_ports=model['eligible_ports'], forced_endpoints=model['forced_endpoints'],
                  source_paid={1:2201, 2:412, 3:510, 4:127, 5:40, 8:8},
                  source_helpers={4:28, 7:7, 8:47, 9:326},
                  scope='EXPLORATORY_HETEROGENEOUS_ENDPOINT_RANK_MODEL_ONLY_NOT_NATIVE_ADMISSION')
    return result


if __name__ == '__main__':
    result = discover()
    (HERE / 'DISCOVERY.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('selected_nodes','forced_endpoints','eligible_ports')}, sort_keys=True))
