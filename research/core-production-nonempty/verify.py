"""Independent literal coordinates and exact original source-body controls."""
import argparse
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path

from guard import Window, has_interior, longest_run, uniform_guard
from production_sources import bind, authenticate, CORE, CARVE, REFERENCE


def require(ok, message):
    if not ok:
        raise ValueError(message)


def literal_source(source_size, excess):
    # Independent rational enumeration. No inverse-cut or longest-run formula.
    selected = {}
    for j in range(source_size):
        real = Q(excess * j, source_size)
        low = real.numerator // real.denominator
        phase = low + int(real - low >= Q(1, 2))
        selected[j + phase] = (j, phase)
    require(len(selected) == source_size, 'literal selected-coordinate injection')
    return selected


def one_window(selected, start, length):
    longest = current = 0
    previous = None
    for coordinate in range(start, start + length):
        item = selected.get(coordinate)
        if item is None:
            current = 0
        elif previous is not None and item == (previous[0] + 1, previous[1]):
            current += 1
        else:
            current = 1
        previous = item
        longest = max(longest, current)
    return longest


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--emit', action='store_true', help='emit regenerated receipt without the frozen-receipt comparison')
    cli = parser.parse_args()
    literal_run, source_asts = bind()
    digest = sha256()
    windows = empty_windows = endpoint_windows = phase_middle_windows = 0
    # Complete finite coverage: every e, start and positive ordinary target
    # window for 2<=S<=40. Incremental oracle shares no cut arithmetic.
    for s in range(2, 41):
        for e in range(1, s):
            target = s + e
            selected = literal_source(s, e)
            for a in range(target):
                current = best = 0
                previous = None
                for stop in range(a + 1, target + 1):
                    item = selected.get(stop - 1)
                    if item is None:
                        current = 0
                    elif previous is not None and item == (previous[0] + 1, previous[1]):
                        current += 1
                    else:
                        current = 1
                    previous = item
                    best = max(best, current)
                    actual = longest_run(Window(s, e, a, stop - a))
                    require(actual['maximum'] == best, 'closed maximum differs from literal source')
                    require(sum(a <= coordinate < stop for coordinate in selected)
                            == actual['stop_source'] - actual['first_source'],
                            'inverse selected interval count')
                    digest.update(bytes((s, e, a, stop - a, best)))
                    windows += 1
                    empty_windows += best == 0
                    endpoint_windows += a == 0 or stop == target
                    phase_middle_windows += actual['complete_middle_cells'] > 0

    # Literal Core.partition and carve, with the original Reference geometry
    # constructor prefix and interior method, for all original starts here.
    native_cases = native_nonempty = uniform_cases = 0
    source_fixture_rows = []
    for s in (*range(2, 19), 31, 63, 127):
        excesses = range(1, s) if s <= 18 else (1, 2, 3)
        for e in excesses:
            target = s + e
            lengths = [1 << k for k in range(1, target.bit_length()) if (1 << k) <= target]
            for width in (1, 2, 4):
                for cap in (1, 2, 4):
                    if 2 * cap > s:
                        continue
                    for length in lengths:
                        admitted = uniform_guard(s, e, width, length, cap)
                        # Larger fixtures retain all aligned original windows,
                        # endpoints and every near-boundary original origin.
                        starts = range(target - length + 1) if s <= 18 else sorted(
                            set(range(0, target - length + 1, length))
                            | {0, target - length, min(1, target-length)}
                            | {a for a in range(target - length + 1)
                               if a in (target // 2 - 2, target // 2 - 1, target // 2, target // 2 + 1)})
                        for start in starts:
                            _, pieces, cells = literal_run(s, e, start, length, width, cap)
                            window = Window(s, e, start, length)
                            predicted = has_interior(window, width, cap)
                            require(predicted == bool(cells), 'actual source carve admission differs')
                            require(not admitted or cells, 'uniform guard admitted an empty original context')
                            require(all(0 < len(c['indices']) <= cap
                                        and len(c['indices']) & (len(c['indices'])-1) == 0 for c in cells),
                                    'source interior cap/dyadic contract')
                            native_cases += 1
                            native_nonempty += bool(cells)
                            uniform_cases += admitted
                            if (s,e,width,cap,length,start) in ((127,1,4,4,64,0),(127,1,4,4,64,64)):
                                source_fixture_rows.append({'S':s,'e':e,'W':width,'cap':cap,'L':length,'start':start,
                                    'longest_run':longest_run(window)['maximum'],'interior_blocks':len(cells),
                                    'interior_rows':sum(len(c['indices']) for c in cells),
                                    'boundary_rows':sum(p['stop']-p['start'] for p in pieces if p['kind']=='B')})

    # Both simple sufficient guards are tight on ordinary target windows.
    thresholds = []
    for width in range(1, 17):
        s, e, length, start = 18*width+3, 3, 12*width+1, 3*width+3
        _, _, cells = literal_run(s,e,start,length,width,1)
        require(not cells and longest_run(Window(s,e,start,length))['maximum'] == 6*width,
                'length-minus-one witness')
        require(uniform_guard(s,e,width,length+1,1), 'funded uniform length threshold')
        s2, e2, l2 = 18*width+2, 3, 12*width+2
        _, _, cells2 = literal_run(s2,e2,0,l2,width,1)
        require(not cells2 and s2 == e2*(6*width+1)-1,
                'source-ratio-minus-one witness')
        require(s+e-length >= width and s2+e2-l2 >= width,
                'both sharp families retain the ordinary complementary gap')
        thresholds.append({'W':width,'length_minus_one':{'S':s,'e':e,'a':start,'L':length},
                           'source_guard_minus_one':{'S':s2,'e':e2,'a':0,'L':l2}})

    # Neither old source-coordinate units nor tie-to-even rounding may be used.
    selected = literal_source(14,1)
    actual = longest_run(Window(14,1,1,13))['maximum']
    require(actual == 6 and one_window(selected,1,13) == 6, 'retained target hole witness')
    wrong_source_run = max(sum(1 for j in range(1,14) if phase == (2*j+14)//28)
                           for phase in (0,1))
    require(wrong_source_run == 7 and wrong_source_run > actual, 'source/target coordinate confusion detected')
    require(round(Q(1,2)) == 0 and literal_source(14,1)[8] == (7,1),
            'half-up versus ties-even control')
    require(longest_run(Window(14,1,0,13))['maximum'] == 7
            and has_interior(Window(14,1,0,13),1,1)
            and not has_interior(Window(14,1,1,13),1,1), 'unpaid origin rebasing detected')
    _,_,actual_wide = literal_run(14,1,0,14,2,1)
    require(not actual_wide and uniform_guard(14,1,1,14,1),
            'substituting a smaller width for the actual carve width detected')
    controls = ['target_hole_must_not_be_deleted','half_up_ties_must_not_be_even',
                'original_origin_must_not_be_rebased','actual_carve_width_must_be_used']
    for args in ((True,1,0,1),(2,2,0,1),(4,1,-1,1),(4,1,0,0),(4,1,4,2)):
        try: Window(*args)
        except ValueError: controls.append('invalid_window')
        else: raise ValueError('invalid window accepted')
    for width,cap in ((0,1),(1,3),(1,32),(True,1),(1,True)):
        try: has_interior(Window(15,1,0,8),width,cap)
        except ValueError: controls.append('invalid_carve_parameters')
        else: raise ValueError('invalid carve parameters accepted')
    raw = authenticate()
    for path in (REFERENCE,CORE,CARVE):
        try: bind({path:raw[path]+b'\n# deliberately corrupted source\n'})
        except ValueError: controls.append('source_corruption_rejected')
        else: raise ValueError('corrupted source was admitted')

    # Very large descriptors exercise the constant-size formula without
    # constructing periods or enumerating cells. This is exact arithmetic only.
    huge = []
    for bits in (64,257,1024):
        s=(1<<bits)-1;e=(1<<(bits-8))+1;width=3;length=128
        require(uniform_guard(s,e,width,length,8), 'large-descriptor source guard')
        for start in (0,(s+e)//2,s+e-length):
            require(has_interior(Window(s,e,start,length),width,8), 'large-descriptor local decision')
        huge.append(bits)

    receipt={'status':'PASS_CORE_PRODUCTION_NONEMPTY','complete_small_window_checks':windows,
             'hole_only_windows':empty_windows,'period_endpoint_windows':endpoint_windows,
             'complete_middle_phase_windows':phase_middle_windows,
             'literal_partition_cases':native_cases,'literal_nonempty_cases':native_nonempty,
             'uniform_admitted_original_windows':uniform_cases,'source_fixture':source_fixture_rows,
             'sharp_threshold_families':thresholds,'negative_controls':controls,
             'large_descriptor_bits':huge,'source_ast_sha256':source_asts,
             'exact_window_digest':digest.hexdigest(),'no_new_kappa':True,
             'scope':'Exact source geometry and original partition/carve AST bodies only; no Gaussian numerical or native payload execution.'}
    expected=Path(__file__).with_name('RESULTS.json')
    if not cli.emit:
        require(expected.exists(), 'missing frozen scientific receipt')
        require(receipt==json.loads(expected.read_text()), 'committed scientific receipt changed')
    print(json.dumps(receipt,sort_keys=True))
    print('PASS_CORE_PRODUCTION_NONEMPTY')


if __name__=='__main__':
    main()
