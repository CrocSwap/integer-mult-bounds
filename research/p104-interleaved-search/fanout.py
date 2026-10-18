#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Eight actual-query terms with 31 dirty fanout helpers: finite forward word.

The selected centre cut is replaced. Exact rational replay checks every one of
735 independent public input columns, common-chart scalar operations, monotone
public transports, and eight literal rank-seven owned-copy paths. A copy seeds
ordinary dirty helpers at L_a; those helpers ascend to public contact charts,
then are restored at FULL. Public dirt is compensated at frame zero.

This is not a multiplication supplier or a kappa improvement. Native lowering,
global ownership, the complete wrapper, and bit-side admission are separate.
The accompanying cost screen rejects this construction even optimistically.
Contact proposals are finite data, not an asserted search optimum.
"""
from collections import Counter, defaultdict
from copy import deepcopy
from fractions import Fraction as Q
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
PLANS_SHA256 = '0c2ae264694bbe7c15b9261ba8adf68c9552849effd423894713c68ad23d28ca'


def module(name):
    spec = importlib.util.spec_from_file_location(name, HERE / (name + '.py'))
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


QC, S, D = module('query_construction'), module('scalar_surgery'), module('delivery')
require, FULL, ZERO = D.require, D.FULL, frozenset({0})


def basis(frame):
    values, generated = [], ZERO
    for x in sorted(frame):
        if x not in generated:
            values.append(x)
            generated = D.join(generated, frozenset({0, x}))
    require(generated == frame, 'frame is not a binary subspace')
    return values


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


class NeedHelper(Exception):
    """The deterministic cumulative-frame allocator needs another dirty role."""


def construct(fault=None, fixed=None):
    """Derive the forward word. Mutations consume the baseline's fixed repairs."""
    inputs = QC.load_inputs()
    word, prototype = inputs['word'], inputs['coordinates']
    raw = (HERE / 'FANOUT-PLANS.json').read_bytes()
    require(hashlib.sha256(raw).hexdigest() == PLANS_SHA256, 'fanout plans byte pin')
    plans = json.loads(raw)['plans']
    require([tuple(p['pair']) for p in plans] == list(S.DECODER_ROOT_PAIRS), 'eight decoder pairs')
    v, oldn = word['v'], 2 * word['v'] + word['R']
    _, specs = QC.geometry(inputs)
    order, availability, _, _ = QC.schedule(word, specs)
    bword, cut = [word['B'][j] for j in order], max(availability.values())
    require(cut == 507, 'actual-query common availability cut')
    live = [i for i in range(v) if i not in QC.REMOVED]
    live_y = {v + t for t in live}
    frames = [QC.span(f) for f in word['frames']]
    labels = {i: x ^ (43 if (x & 43).bit_count() % 2 else 0)
              for i, x in enumerate(prototype['binary_ports'])}
    helpers, contacts = [], defaultdict(list)
    for p in plans:
        a, b = p['pair']
        qreg = specs[b]['register'] if b in specs else word['centers'][b]
        qscale = -Q(1, 4) if b in specs else Q(1, 2)
        lam = Q(1, 4 * S.dot(prototype['root_lines'][a], prototype['root_lines'][b])) / qscale
        offset = len(helpers)
        require(type(p['helpers']) is int and p['helpers'] > 0, 'helper allocation')
        for _ in range(p['helpers']):
            helpers.append(dict(a=a, b=b, source=qreg, lam=lam, line=QC.span([labels[a]])))
        for c in p['contacts']:
            require(cut <= c['event'] < len(bword), 'contact before actual source availability')
            require(0 <= c['register'] < oldn and 0 <= c['helper'] < p['helpers'], 'contact role')
            require(bool(Q(c['coefficient'])), 'zero contact')
            contacts[c['event']].append(dict(c, helper=offset + c['helper']))
    require(len(helpers) == 28, 'initial proposal allocation')
    cap = [frames[word['final'][r]] if r in live_y else FULL for r in range(oldn)]
    caps = []
    for event in reversed(bword):
        rr = QC.touched(event)
        both = cap[rr[0]]
        for r in rr:
            both &= cap[r]
        for r in rr:
            cap[r] = both
        caps.append(cap.copy())
    caps.reverse()

    def run(compensation=(), repairs=None, mutation=None):
        n = oldn + len(helpers)
        rows = QC.identity(n)
        current = [frames[i] for i in word['start']] + [ZERO] * len(helpers)
        for t in QC.REMOVED:
            current[t] = ZERO
        paid, copy_paid, edges, events = Counter(), Counter(), [], []
        response = [{} for _ in range(oldn)]
        qrows, query_records, cleanup, ghost_restores = {}, [], [], []
        private_paths, private_rows, private_frames = [], {}, {}
        routed_contacts = []

        def transport(r, target, phase, private=False):
            old = private_frames[r] if private else current[r]
            require(target <= old if private else old <= target, 'nonmonotone literal transport')
            if not private and r in live_y:
                require(target <= frames[word['final'][r]], 'live Y endpoint frame exceeded')
            rank = abs(D.dimension(target) - D.dimension(old))
            if rank:
                (copy_paid if private else paid)[rank] += 1
                edge = dict(occurrence=len(edges), register=r, source_frame=basis(old),
                            target_frame=basis(target), rank=rank, private=private, phase=phase)
                edges.append(edge)
                events.append(dict(kind='transport', occurrence=edge['occurrence'], phase=phase))
            if private:
                private_frames[r] = target
            else:
                current[r] = target

        def scalar_add(target, source, coefficient, phase, private_source=False):
            source_frame = private_frames.get(source) if private_source else current[source]
            require(source_frame is not None and current[target] == source_frame,
                    'scalar ADD crosses charts or reads an uninitialized private copy')
            source_row = private_rows.get(source) if private_source else rows[source]
            require(source_row is not None, 'private COPY read without initialization')
            S.add_row(rows[target], source_row, coefficient)
            events.append(dict(kind='add', registers=[target, source], coefficient=str(coefficient),
                               frame=basis(current[target]), phase=phase))

        def apply(event, phase):
            rr, frame = QC.touched(event), frames[event[-1]]
            for r in rr:
                frame = D.join(frame, current[r])
            for r in rr:
                transport(r, frame, phase)
            if event[0] == 'add':
                coefficient = Q(event[3], event[4])
                scalar_add(event[1], event[2], coefficient, phase)
                S.add_row(response[event[1]], response[event[2]] if event[2] < oldn else {}, coefficient)
            else:
                require(event[0] == 'scale' and bool(Q(event[2], event[3])), 'invalid scale')
                QC.apply(event, rows)
                response[event[1]] = {j: x * Q(event[2], event[3]) for j, x in response[event[1]].items()}
                events.append(dict(kind='scale', registers=[event[1]], coefficient=str(Q(event[2], event[3])),
                                   frame=basis(frame), phase=phase))

        for phase, sequence in [('entry compensation', compensation), ('precondition', word['precondition']),
                                ('old compensation', word['compensation']), ('A', word['A']),
                                ('B query prefix', bword[:cut])]:
            for event in sequence:
                apply(event, phase)
        # At the common cut, seed one decoder term at a time. Each private copy
        # is initialized, used at Hb, transported once to La, read only at La,
        # and discarded before the next owned copy is created: peak is one.
        for term, (a, b) in enumerate(S.DECODER_ROOT_PAIRS):
            js = [j for j, h in enumerate(helpers) if (h['a'], h['b']) == (a, b)]
            meta = helpers[js[0]]
            source, line = meta['source'], meta['line']
            hb = frozenset(x for x in range(512) if not (x & labels[b]).bit_count() % 2)
            require(current[source] == hb, 'actual query source is not in Hb')
            require(line <= hb and (D.dimension(hb), D.dimension(line)) == (8, 1), 'rank-seven copy endpoints')
            qrows.setdefault(source, rows[source].copy())
            query_records.append(dict(pair=[a,b], source=source, frame=basis(hb), coefficient=str(meta['lam']),
                                      scalar_row_sha256=QC.row_digest(rows[source]), fanout_helpers=js))
            owned = n + term
            if not (mutation == 'missing_private_initialization' and term == 0):
                private_rows[owned], private_frames[owned] = {}, hb
                events.append(dict(kind='private_init', register=owned, frame=basis(hb), phase='owned query copy'))
                require(private_frames[owned] == current[source], 'COPY source chart mismatch')
                private_rows[owned] = rows[source].copy()
                events.append(dict(kind='private_copy', registers=[owned,source], coefficient='1', frame=basis(hb), phase='owned query copy'))
                coefficient = meta['lam'] + (1 if mutation == 'query_coefficient' and term == 0 else 0)
                private_rows[owned] = {j: coefficient*x for j,x in private_rows[owned].items()}
                events.append(dict(kind='scale', registers=[owned], coefficient=str(coefficient), frame=basis(hb), phase='owned query scaling'))
                transport(owned, line, 'owned Hb to La', True)
                private_paths.append([edges[-1]])
            for j in js:
                transport(oldn+j, line, 'fanout helper entrance')
                scalar_add(oldn+j, owned, Q(1), 'fanout helper seed', True)
            events.append(dict(kind='private_discard', register=owned, frame=basis(line), phase='owned copy end'))
            del private_rows[owned], private_frames[owned]
        require(not private_rows and not private_frames, 'private copy left live')
        for k in range(cut, len(bword)):
            for c in sorted(contacts[k], key=lambda z: (int(z['lower']).bit_count(), z['helper'], z['register'])):
                r, term = c['register'], helpers[c['helper']]['a']
                cap_here = caps[k][r]
                require(current[r] <= cap_here, 'public reader already exceeds future endpoint cap')
                eligible = [j for j,h in enumerate(helpers) if h['a'] == term and current[oldn+j] <= cap_here]
                if not eligible:
                    raise NeedHelper(c['helper'])
                j = max(eligible, key=lambda z: D.dimension(current[oldn+z]))
                helper = oldn+j
                frame = D.join(current[helper], current[r])
                require(frame <= cap_here, 'cumulative helper frame exceeds contact cap')
                transport(helper, frame, 'fanout contact')
                transport(r, frame, 'fanout contact')
                scalar_add(r, helper, Q(c['coefficient']), 'fanout contact')
                response[r][j] = response[r].get(j, Q(0)) + Q(c['coefficient'])
                routed_contacts.append(dict(event=k, target=r, helper=j, coefficient=c['coefficient'], frame=basis(frame)))
            apply(bword[k], 'B suffix')
        for event in word['tail']:
            apply(event, 'tail')
        for r, q in qrows.items():
            require(rows[r] == q, 'actual query bank changed before helper restoration')
        for j in range(len(helpers)):
            transport(oldn+j, FULL, 'fanout helper endpoint')
        if repairs is None:
            for r, rr in enumerate(response):
                if r not in live_y:
                    cleanup.extend([r, oldn+j, str(-c)] for j,c in rr.items() if c)
        else:
            cleanup = deepcopy(repairs['cleanup'])
        applied_cleanup = cleanup[1:] if mutation == 'missing_response_cleanup' else cleanup
        for r,h,c in applied_cleanup:
            transport(r, FULL, 'response cleanup')
            scalar_add(r,h,Q(c),'response cleanup')
        for j,h in enumerate(helpers):
            transport(h['source'], FULL, 'query bank endpoint')
            scalar_add(oldn+j,h['source'],-h['lam'],'helper restoration')
            require(rows[oldn+j] == {oldn+j:Q(1)}, 'dirty helper not restored')
        for event in word['cleanup']:
            apply(event, 'old cleanup')
        if repairs is None:
            for t in QC.REMOVED:
                r = v+t
                transport(r,FULL,'ghost Y endpoint')
                require(rows[r].get(r) == 1,'ghost Y diagonal changed')
                for i,c in list(rows[r].items()):
                    if i == r:
                        continue
                    require(rows[i] == {i:Q(1)}, 'ghost restoration reads a nonidentity source')
                    transport(i,FULL,'ghost restoration')
                    scalar_add(r,i,-c,'ghost restoration')
                    ghost_restores.append([r,i,str(-c)])
        else:
            ghost_restores = deepcopy(repairs['ghost_restoration'])
            for r,i,c in ghost_restores:
                transport(r,FULL,'ghost Y endpoint')
                require(rows[i] == {i:Q(1)}, 'fixed ghost restoration reads a nonidentity source')
                transport(i,FULL,'ghost restoration')
                scalar_add(r,i,Q(c),'ghost restoration')
        for r in range(oldn):
            endpoint = FULL if v <= r < 2*v and r-v in QC.REMOVED else frames[word['final'][r]]
            transport(r,D.join(current[r],endpoint),'final public boundary')
        return dict(rows=rows, final=current, paid=paid, copy_paid=copy_paid, transport_edges=edges,
                    scalar_operations=events, private_paths=private_paths, query_records=query_records,
                    cleanup=cleanup, ghost_restoration=ghost_restores, contacts=routed_contacts)

    clones = []
    if fixed is None:
        while True:
            try:
                preliminary = run()
                break
            except NeedHelper as missing:
                helpers.append(helpers[missing.args[0]].copy())
                clones.append([helpers[-1]['a'],helpers[-1]['b']])
                require(len(helpers) <= 31, 'bounded allocator exceeded recorded helper stock')
        require(clones == [[3,113],[2,47],[4,57]], 'deterministic helper cloning changed')
        compensation = []
        for t in live:
            row = preliminary['rows'][v+t]
            require(all(row.get(i,0) == Q(i==t) for i in live), 'wrong initial-live-X transfer')
            for i,c in row.items():
                if i in (t,v+t):
                    continue
                require(i >= oldn or i in QC.REMOVED or frames[word['start'][i]] == ZERO,
                        'dirty coefficient cannot be compensated at frame zero')
                compensation.append(['add',v+t,i,-c.numerator,c.denominator,0])
        repairs = dict(cleanup=preliminary['cleanup'], ghost_restoration=preliminary['ghost_restoration'])
    else:
        helpers = deepcopy(fixed['helpers'])
        compensation, repairs, clones = deepcopy(fixed['compensation']), deepcopy(fixed['repairs']), fixed['clones']
    applied_compensation = compensation[1:] if fault == 'missing_entry_compensation' else compensation
    built = run(applied_compensation, repairs, fault)
    require(len(helpers) == 31 and len(built['rows']) == 735, 'exact public stock')
    require(not S.endpoint_failures(built['rows'],v,live),'full 735-column endpoint identity failed')
    require(built['copy_paid'] == Counter({7:8}), 'eight complete rank-seven owned copies')
    public_recount = Counter(e['rank'] for e in built['transport_edges'] if not e['private'])
    require(public_recount == built['paid'], 'public transport occurrence invoice mismatch')
    expected = {'1':2611,'2':514,'3':378,'4':132,'5':81,'6':15,'7':6}
    require(D.profile(built['paid']) == expected,'recorded public invoice changed')
    require(len(built['private_paths']) == 8, 'missing private path')
    final_widths = [D.dimension(built['final'][r])-D.dimension(ZERO if r >= oldn or r in QC.REMOVED else frames[word['start'][r]])
                    for r in range(735)]
    # Added public helpers start at ZERO, outside the original start array.
    report = dict(schema='p104-fanout-forward-report-v1',
                  scope='Finite forward 735-column identity and literal frame word; not a global supplier or exponent improvement.',
                  sources={relative:sha for relative,sha in QC.INPUTS.values()}, plans_sha256=PLANS_SHA256,
                  ordinary_fanout_helpers=31, public_registers=735, live_ports=104,
                  private_copies_created=8, peak_private_copies=1, source_availability_B_prefix=cut,
                  query_sources=built['query_records'], deterministic_clones=clones,
                  contact_count=len(built['contacts']), entry_compensation_additions=len(compensation),
                  response_cleanup_additions=len(repairs['cleanup']), ghost_restoration_additions=len(repairs['ghost_restoration']),
                  candidate_public_profile=D.profile(built['paid']), private_COPY_profile=D.profile(built['copy_paid']),
                  public_rank_mass=sum(k*n for k,n in built['paid'].items()),
                  full_735_column_identity_verified=True, all_new_helpers_restored=True,
                  compensation_only_initial_frame_zero=True, all_public_scalar_adds_common_chart=True,
                  actual_query_Hb_frames_verified=True, complete_public_widths=final_widths,
                  contact_schedule_sha256=digest(built['contacts']), scalar_operation_word_sha256=digest(built['scalar_operations']),
                  transport_occurrences_sha256=digest(built['transport_edges']),
                  native_phase_compilation_verified=False, global_hosting_verified=False,
                  completed_full_multiplication_supplier=False, kappa_improvement_claimed=False)
    built.update(report=report, fixed=dict(helpers=helpers, compensation=compensation, repairs=repairs, clones=clones),
                 ports=[word['ports'][t] for t in live])
    return built


def native_witness(built=None):
    built = construct() if built is None else built
    edges = [dict(register=str(e['register']), old=e['source_frame'], new=e['target_frame'],
                  occurrence=e['occurrence'], private=e['private'], rank=e['rank']) for e in built['transport_edges']]
    by_occurrence = {e['occurrence']:e for e in edges}
    return dict(transports=edges,
                private_paths=[[by_occurrence[e['occurrence']] for e in path] for path in built['private_paths']],
                scalar_operations=built['scalar_operations'], ports=built['ports'],
                scalar_operation_word_sha256=digest(built['scalar_operations']),
                transport_occurrences_sha256=digest(built['transport_edges']),
                public_profile=built['report']['candidate_public_profile'], private_profile=built['report']['private_COPY_profile'])


def verify():
    built = construct()
    controls = {}
    for fault in ('query_coefficient','missing_private_initialization','missing_response_cleanup','missing_entry_compensation'):
        try:
            construct(fault=fault,fixed=built['fixed'])
        except (ValueError,NeedHelper) as error:
            controls[fault] = str(error)
        else:
            raise D.VerificationError('fixed-repair negative control accepted: '+fault)
    built['report']['negative_controls_repairs_held_fixed'] = controls
    return built['report']


if __name__ == '__main__':
    print(json.dumps(verify(),indent=2,sort_keys=True))
