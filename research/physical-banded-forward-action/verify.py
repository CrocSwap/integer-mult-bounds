"""Reproduce the actual broad-source and singular physical forward cases."""
from pathlib import Path
import argparse
from fractions import Fraction as Q
import importlib.util
import json
import sys

PACKAGE = Path(__file__).resolve().parent
sys.path.insert(0, str(PACKAGE))
_spec = importlib.util.spec_from_file_location('banded_action_sources', PACKAGE/'sources.py')
sources = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = sources
_spec.loader.exec_module(sources)
import pages
import reference_source
import independent_forward


def stable(value):
    if isinstance(value, Q):
        return str(value)
    if isinstance(value, dict):
        return {key: stable(item) for key, item in value.items() if key != 'seconds'}
    if isinstance(value, (tuple, list)):
        return [stable(item) for item in value]
    return value


def run():
    source_pins = sources.authenticated_inputs()
    raw = reference_source.authenticated_inputs(PACKAGE)
    reference = reference_source.make_reference(raw, (61, 3, 2, 1, 3, 32))
    broad, source = pages.broad_source(reference)
    source['independent_review'] = independent_forward.check_source(reference, broad)
    singular = tuple(tuple(Q(x, 3) for x in row) for row in ((1, -1, 0), (-1, 2, -1), (0, -1, 1)))
    pages.need(all(sum(row, Q()) == 0 for row in singular)
               and singular[0][0]*singular[1][1] != singular[0][1]*singular[1][0],
               'exact rank-two singular control')
    try:
        pages.factors(((Q(1), Q(), Q(1, 1 << 80)), (Q(), Q(1), Q()), (Q(), Q(), Q(1))), 4, 8)
    except ValueError as error:
        pages.need(str(error) == 'funded exact forward bandwidth before rounding', 'exact support control')
    else:
        raise ValueError('small off-band source coefficient hidden by rounding')
    print('SOURCE_VALIDATED', file=sys.stderr, flush=True)
    with sources.physical_runtime():
        from records import Tape
        from action import BandedAction
        from fixture import case, erased
        all_tapes = []
        original_init = Tape.__init__
        def tracked(tape):
            original_init(tape)
            all_tapes.append(tape)
        Tape.__init__ = tracked
        try:
            owner = BandedAction()
            pages.need({id(t) for t in all_tapes} == {id(t) for t in owner.forbidden()},
                       'complete constructor ownership census')
            first = case(owner, all_tapes, broad)
            print('BROAD_PASSED', file=sys.stderr, flush=True)
            second = case(owner, all_tapes, singular, precision=8, width=16)
            print('SINGULAR_PASSED', file=sys.stderr, flush=True)
            third = case(owner, all_tapes, ((Q(),),), block=1, precision=4, width=8,
                         columns=1, controls=False)
            erased(owner)
            print('HISTORY_PASSED', file=sys.stderr, flush=True)
            return dict(marker='PASS_PHYSICAL_BANDED_FORWARD_ACTION', source_pins=source_pins,
                        source=source, broad=first, singular=second, long_to_short=third,
                        owned_roles=len(owner.forbidden()), source_controls=['exact rank-two null vector',
                        'nongrid signed coefficient pre-round equivalence', 'tiny off-band before rounding'],
                        no_new_kappa=True,
                        scope='literal supplied band action; exact finite broad Reference Schur; no full broad window')
        finally:
            Tape.__init__ = original_init


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write-result', action='store_true')
    parser.add_argument('--emit', action='store_true')
    args = parser.parse_args()
    result = stable(run())
    if args.write_result:
        (PACKAGE/'RESULT.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    elif not args.emit:
        pages.need(result == json.loads((PACKAGE/'RESULT.json').read_text()), 'stable exact forward receipt')
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
