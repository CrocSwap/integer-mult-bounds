#!/usr/bin/env python3
"""Source-bound premises of the native two-ablation kernel inclusion.

Native recipe checks reuse credited PR2048 code and Sagar Thakrar's kernel;
the extended-label audit is credited to the retained whole-payload audit.
New causal-support argument/check: DLamdata with Codex, Apache-2.0.
"""
from pathlib import Path
import argparse, json, sys
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
sys.path.insert(0, str(Path(__file__).resolve().parent))
from source import HERE, canonical, digest, load, need

def prefix(data):
    key = lambda e: (e['time'], e['replica'], e['stage'], e['provider_id'])
    callmap = {key(c): c for c in data['template']['calls']}
    need(len(callmap) == 144, 'selected call inventory')
    events, calls = [], []
    for event in data['template']['execution_schedule']:
        events.append(event)
        if event['kind'] == 'local_cover_sweep':
            call = callmap[key(event)]
            calls.append(call)
            ow = call['owners']
            need(len(ow) == len({entry[0] for entry in ow}) == 704, 'injective family map')
            need(digest(canonical(data['programs'][call['orientation']])) ==
                 call['local_program_sha256'], 'call/program binding')
            if call['time'] == 10:
                break
    need([c['time'] for c in calls] == list(range(11)), 'first eleven chronological calls')
    need(Counter(e['kind'] for e in events) ==
         Counter(local_cover_sweep=11, bridge=4, idle_cover_sweep=4), 'complete prefix inventory')
    need([(calls[i]['replica'], calls[i]['stage'], calls[i]['orientation']) for i in (0,4,10)] ==
         [(0,0,'forward'), (0,1,'backward'), (0,2,'forward')], 'selected f0/b1/f2 binding')
    for index, stage in ((0,0), (4,1), (10,2)):
        need(calls[index]['owners'][:224] == [[p,[1,stage,p%112]] for p in range(224)],
             'same physical data families and side-equal routes')
    return events, calls

def causal_support(events, calls, forward_cuts, cancellation=True):
    """Upper supports of arbitrary native fields, never projected scalar values.

    Only the separately proved F0/B1 signed-gauge cancellation removes support.
    Helpers and idle maps retain support; bridges take unions. A coefficient
    zero in a common-frame row is a zero native block, including its input map.
    """
    live = set(range(112))
    history, helper_occurrences = [], []
    last_input = None
    for position, event in enumerate(events):
        kind = event['kind']
        if kind == 'local_cover_sweep':
            call = calls[event['time']]
            owners = [r[0] for r in call['owners']]
            source, target, helpers = set(owners[:112]), set(owners[112:224]), set(owners[224:])
            helper_occurrences.append([call['time'], len(live & helpers)])
            if call['time'] == 0:
                need(live == source, 'first source-only input')
                live |= target
            elif call['time'] == 4:
                need(live == source | target, 'F0/B1 uninterrupted source response')
                need(call['orientation'] == 'backward', 'cancelling orientation')
                if cancellation:
                    live -= source
            elif call['time'] == 10:
                last_input = [i for i,family in enumerate(owners) if family in live]
                need(not [(k,i) for k,row in enumerate(forward_cuts)
                          for i in last_input if row.get(i,0)],
                     'later centre has source-dependent input coefficient')
            else:
                need(not live & (source | target), 'intervening call has live data')
                # Complete local endpoints have no off-diagonal helper blocks.
        elif kind == 'bridge':
            base = 896*event['replica']
            src, dst = base+224*event['src'], base+224*event['dst']
            need(event['coefficient'] in (-1,1), 'signed bridge')
            before = set(live)
            for p in range(112):
                if src+p in before:
                    live.add(dst+p)
                if dst+112+p in before:
                    live.add(src+112+p)
        elif kind == 'idle_cover_sweep':
            # Invertible coordinate factors act within each existing family.
            pass
        else:
            raise ValueError('unknown prefix event')
        history.append({'position':position,'kind':kind,'time':event.get('time'),
                        'live_families':sorted(live)})
    need(last_input is not None, 'f2 reached')
    need(live == set(range(112,224)) | set(range(336,448)), 'complete causal support')
    need(len(last_input)==211 and sum(i>=224 for i in last_input)==99, 'live incidence')
    return {'prefix_events':len(events),'calls':len(calls),'bridges':4,'idle_sweeps':4,
            'f2_live_roles':last_input,'f2_live_targets':112,'f2_live_helpers':99,
            'zero_cut_coefficients_checked':8*len(last_input),
            'live_helper_occurrences':helper_occurrences,'support_history':history}

def run():
    data, module = load()
    audit = module('credited_extended_label_audit',
                   'research/centre-native-observation-dimension/audit.py').audit
    native = module('credited_selected_native_checks',
                    'research/selected-centre-native-lift/verify.py')
    C = module('credited_exact_clifford','research/frontier1094-recipes-exact-seed76/clifford.py')
    word, programs = data['word'], data['programs']
    audits = {o:audit(word,programs[o],o) for o in ('forward','backward')}
    merged = {'edges':set().union(*(a['edges'] for a in audits.values())),
              'wrapped':set().union(*(a['wrapped'] for a in audits.values()))}
    native_receipt, _, adapters = native.check_operators(
        word,data['recipes'],data['residuals'],merged,C)
    events,calls = prefix(data)
    causal = causal_support(events,calls,audits['forward']['cuts'])
    pivots = [0,1,2,3,4,5,6,12]
    matrix = [[row.get(p,Q(0)) for p in pivots] for row in audits['forward']['cuts']]
    inv,det = native.inverse_and_det(matrix)
    need(det==32,'credited first-transcript minor')
    controls = {}
    def rejects(name, action, expected):
        try:
            action()
        except ValueError as error:
            need(expected in str(error),'wrong failure '+name+': '+str(error))
            controls[name]=str(error)
        else:
            raise ValueError('ineffective control: '+name)
    rejects('omit_B1_cancellation',lambda:causal_support(events,calls,audits['forward']['cuts'],False),
            'later centre has source-dependent input coefficient')
    bad_cuts=deepcopy(audits['forward']['cuts'])
    live_helper=next(i for i in causal['f2_live_roles'] if i>=224)
    bad_cuts[0][live_helper]=Q(1)
    rejects('read_a_live_helper',lambda:causal_support(events,calls,bad_cuts),
            'later centre has source-dependent input coefficient')
    rejects('omit_bridges',lambda:causal_support([e for e in events if e['kind']!='bridge'],
            calls,audits['forward']['cuts']),'complete causal support')
    bad=deepcopy(programs['backward'])
    operation=next(e for e in bad if e[0]=='scalar' and e[1][0]=='add')
    operation[1][3]*=-1
    rejects('reverse_one_backward_ADD',lambda:audit(word,bad,'backward'),'complete scalar endpoint')
    bad=deepcopy(programs['forward'])
    event=next(e for e in bad if e[0]=='scalar' and e[1][0]=='add' and e[2]!=0)
    event[2]=0
    rejects('wrong_native_common_frame',lambda:audit(word,bad,'forward'),'common frame')
    record=deepcopy(adapters['source',0]['left']);record['phase']=(record['phase']+1)%4
    need(not C.same_operator([('C',word['ports'][0],1)]+C.monomial(record),
         C.canonical_frame(word['frames'][word['start'][0]])),'global phase fault')
    controls['wrong_adapter_global_phase']='full exact operator differs'
    return {'status':'PASS_CENTRE_NATIVE_TERMINAL_PREMISES',
            'scientific_base':'a1bfbc677fdcbc2a27a9b3bf6c78cac8fd6da9e2',
            'local_audits':{o:{k:a[k] for k in ('events','scalar_columns','bill','conversions')}
                            for o,a in audits.items()},
            'native_operator_checks':native_receipt,'causal_support':causal,
            'first_cut_pivots':pivots,'first_cut_determinant':str(det),
            'first_cut_inverse':[[str(x) for x in row] for row in inv],'controls':controls,
            'scope':'Premises for source-response kernel inclusion through eight full native fields. '
                    'Global view/hosting semantics inherited; boundary phases separately checked. '
                    'No sharp terminal rank, paid decoder, full dirty residual or new kappa.'}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--write',type=Path);args=parser.parse_args()
    if args.write and args.write.exists():
        raise FileExistsError(args.write)
    result=run()
    if args.write:
        with args.write.open('x',encoding='utf-8',newline='\n') as out:
            out.write(json.dumps(result,indent=2,sort_keys=True)+'\n')
    else:
        expected=json.loads((HERE/'RESULT.json').read_bytes())
        need(canonical(expected)==canonical(result),'complete receipt mismatch')
    print('PASS_CENTRE_NATIVE_TERMINAL_PREMISES calls=11 events=19 live_helpers=99 '
          'native_recipes=2896 factor_fields=8 controls=6 no_new_kappa')

if __name__=='__main__':
    main()
