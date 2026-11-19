#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Refine a productive helper on the exact post-overlay complex graph."""

from fractions import Fraction
from pathlib import Path
import argparse
import gzip
import json
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from birth_replay import (arbitrary_inputs, canonical, charges, digest, endpoint_map, locked_source,
                          one_column, require, row_wire, subspace, transpose_rows, write_word)


def load(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if raw.startswith(b'\x1f\x8b') else raw)


def replay(source_root, word_path, layout_path, out):
    journal = load(HERE/'FINAL-BIRTH.json')
    donor, count = locked_source(source_root, journal)
    sys.path.insert(0, str(donor))
    import supplier
    from birth_event import apply_split

    graph, layout = load(word_path), load(layout_path)
    source = journal['source']
    require(digest(graph) == source['graph_sha256'] and digest(layout) == source['layout_sha256'],
            'exact post-overlay graph and layout')
    before = supplier.Network(graph['first_output'], graph['initial'], graph['final'],
                              {k:(a,b) for k,a,b in graph['moves']},
                              {k:{i:Fraction(q) for i,q in row} for k,row in graph['forms']})
    frames = graph['frames']
    require(digest(supplier.dump_graph(before, frames)) == source['graph_sha256'],
            'complete source row, chart and schedule inventory')
    event = journal['event']
    old, fresh = event['role'], len(before.initial)
    chart = event['split_chart']
    a, b = before.initial[old], before.final[old]
    spans = [subspace(tuple(frame)) for frame in frames]
    required, mains = endpoint_map(layout, fresh)
    require(old not in mains and (a,b) == (event['source_chart'],event['return_chart'])
            and spans[a] < spans[chart] < spans[b], 'positive nested targets on the same original owner')
    label = 1+max(layout['source_labels'])
    require(journal['owners'] == {'retired_role':old, 'retired_label':layout['source_labels'][old],
                                  'new_role':fresh, 'new_label':label}, 'independent owner allocation')
    revised_layout = dict(layout, public=fresh+1, source_labels=layout['source_labels']+[label])
    edited = apply_split(before, event)
    require(len(edited.initial) == len(edited.final) == fresh+1
            and all((edited.initial[i],edited.final[i]) == (before.initial[i],before.final[i])
                    for i in range(fresh) if i != old)
            and (edited.initial[old],edited.final[old],edited.initial[fresh],edited.final[fresh]) == (a,chart,chart,b),
            'restore every prescribed source and return chart')
    require(edited.moves == before.moves and digest(graph['moves']) == journal['paid_manifest_sha256'],
            'every paid MOVE and its rank is retained')
    changed = [k for k in sorted(edited.forms.keys() | before.forms.keys())
               if edited.forms.get(k) != before.forms.get(k)]
    require(digest([[k,row_wire(before.forms.get(k)),row_wire(edited.forms.get(k))]
                    for k in changed]) == journal['changed_row_delta_sha256'], 'exact changed read and sender rows')
    width = max(max(abs(q.numerator).bit_length(),q.denominator.bit_length())
                for k in changed for q in edited.forms.get(k,{}).values())
    require(width == journal['max_changed_coefficient_bits'] <= 24, 'bounded introduced scalar components')
    final = supplier.dump_graph(edited, frames)
    result = journal['result']
    require(digest(final) == result['graph_sha256'] and digest(revised_layout) == result['layout_sha256'],
            'exact final carrier and caller layout')
    required.append({fresh: Fraction(1)})
    arbitrary_inputs(edited, required)
    arbitrary_inputs(edited.transpose(), transpose_rows(required))

    expect_fresh = {fresh:'1'}
    omitted = apply_split(before, dict(event,pulse=[]))
    omitted_row = one_column(omitted, fresh)
    require(omitted_row != expect_fresh, 'fresh owner pulse omission control')
    terminal = edited.first_output + old
    wrong = edited.forms | {terminal: edited.forms[terminal] | {~fresh:Fraction(1)}}
    contaminated = type(edited)(edited.first_output, edited.initial, edited.final, edited.moves, wrong)
    contaminated_row = one_column(contaminated,fresh)
    require(~fresh not in edited.forms[terminal] and contaminated_row == {old:'1',fresh:'1'}
            and one_column(edited,fresh) == expect_fresh, 'independent old readout rejects distinct fresh input')
    expect_old = {old:'1'}
    observed_old = one_column(edited,old)
    require(observed_old == expect_old, 'arbitrary retired-owner basis column returns at its new chart')
    inventory = charges(edited,frames,spans,mains)
    require(canonical(inventory) == canonical(result['native_inventory']), 'actual final native paid and target counts')

    out.mkdir(parents=True,exist_ok=True)
    write_word(out/'WORD.json.gz',final)
    write_word(out/'LAYOUT.json.gz',revised_layout)
    receipt = dict(source=source,result=result,source_files=count,owners=journal['owners'],
                   checked_each_orientation=(fresh+1)**2,changed_rows=len(changed),scalar_bits=width,
                   unchanged_paid_moves=len(edited.moves),original_basis_column=observed_old,
                   expected_fresh_basis_column=expect_fresh,omitted_pulse_column=omitted_row,
                   contaminated_readout_column=contaminated_row)
    (out/'FINAL-BIRTH-REPLAY.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    return receipt


if __name__=='__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source-root',type=Path,required=True)
    p.add_argument('--word',type=Path,required=True)
    p.add_argument('--layout',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    a = p.parse_args()
    v = replay(a.source_root,a.word,a.layout,a.out)
    print(v['result']['graph_sha256'],v['checked_each_orientation'],v['unchanged_paid_moves'])
