# SPDX-License-Identifier: Apache-2.0
"""Independent checks added by the #7544 review; never searches for a word."""
import argparse, copy, gzip, importlib.util, json, sys
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import owned_boundary as boundary
R=boundary.require


def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


def read(path):
    def unique(pairs):
        d=dict(pairs);R(len(d)==len(pairs),'Duplicate JSON key');return d
    b=path.read_bytes()
    return json.loads(gzip.decompress(b) if b[:2]==b'\x1f\x8b' else b,object_pairs_hook=unique)


def invoice(word,caller,paid):
    """Literal fixed17 recount, adapted from the retained source-bound census."""
    R(caller['stages']==17,'Fixed17 caller')
    R(caller['types']['A']['ports']==word['hosted']['Dports'],'Actual typeA ports')
    R(sorted(caller['types']['B']['ports'])==[i for i in range(104) if i not in word['hosted']['Dports']],
      'Actual complementary typeB ports')
    main=set(word['live'])|{r+112 for r in word['live']}|set(word['hosted']['X2'])|set(word['hosted']['Y2'])
    R(len(main)==400,'Actual400 MAIN fields')
    helper=Counter()
    for r in range(word['public']):
        if r not in main:
            rank=len(word['frames'][word['final'][r]])-len(word['frames'][word['initial'][r]])
            R(rank>0,'Strict helper rank');helper[rank]+=1
    P,T=Counter(),Counter();stages=[]
    for e in caller['events']:
        if e[0]=='J':
            stages.append(e[1]);P.update(paid);T.update(helper)
        else:
            ports=len(caller['types'][e[0]]['ports'])
            if e[1]=='QUERY':P[1]+=ports
            elif e[1] in ('IDLE_ONE','IDLE_ODD'):P[8*len(e[3])+(e[1]=='IDLE_ODD')]+=ports
    R(stages==list(range(1,18)),'Literal17 J chronology')
    empty=0
    for ty in caller['types'].values():
        for d in ty['diagonal']:
            rank=d[0]%2+8*sum(d[2:]);R(rank>0,'No rankzero productive field')
            T[rank]+=len(ty['ports'])
            if not any(d[2:]):empty+=len(ty['ports'])
    S=sum(r*(T[r]-P[r]) for r in T.keys()|P.keys())
    return dict(P=dict(sorted(P.items())),T=dict(sorted(T.items())),S=S,empty_root_credits=empty,
                native_helpers=dict(sorted(helper.items())))


def mutation_controls(word,dense):
    cases=[
        ('terminal_coefficient',['ADD',1438,1439,'1',127],['ADD',1438,1439,'2',127]),
        ('omitted_terminal_read',['ADD',1438,311,'1',127],None),
        ('wrong_early_chart',['ADD',1266,761,'1/2',3],['ADD',1266,761,'1/2',1053]),
        ('wrong_MOVE_source',['MOVE',1077,729,808,False],['MOVE',1077,789,808,False]),
        ('omitted_902_correction',['ADD',994,902,'1/2',913],None),
        ('wrong_902_weight',['ADD',1495,902,'-3/2',595],['ADD',1495,902,'-1/2',595]),
        ('wrong_234_chart',['ADD',234,902,'1/4',3],['ADD',234,902,'1/4',595]),
    ]
    result={}
    for tag,event,replacement in cases:
        v=dict(word,program=list(word['program']))
        if tag=='omitted_902_correction':
            # PR7542 check.py uses list.remove(): its FIRST occurrence.
            # The composed word has two literal copies. Bind the retained
            # regression to its exact unique context, not an assumed count1.
            R(v['program'].count(event)==2,'Exact duplicated994 control census')
            context=[['MOVE',994,730,913,False],event,['ADD',902,985,'1/2',913]]
            sites=[i for i in range(1,len(v['program'])-1) if v['program'][i-1:i+2]==context]
            R(sites==[40962] and v['program'].index(event)==40962,'Original first994 correction context')
            k=sites[0]
        else:
            R(v['program'].count(event)==1,'Unique control anchor')
            k=v['program'].index(event)
        if replacement is None:v['program'].pop(k)
        else:v['program'][k]=replacement
        try:dense.run(v)
        except ValueError as exc:
            reason=str(exc);R(reason.startswith(('Wrong complete endpoint','Scalar frame','MOVE owner/source','Nonexact scaled product')),
                              'Unexpected corruption failure: '+reason)
            result[tag]=reason
        else:raise ValueError('Native word mutation survived: '+tag)
        print('PASS_REJECT',tag,flush=True)
    for tag,unit,mutation,prefix in (
        ('dirty_COPY',1125*2**25,'dirty_copy','Dirty COPY destination'),
        ('odd_grid375',375*2**25,None,'Nonexact scaled product'),
        ('fractional_grid24',1125*2**24,None,'Nonexact scaled product'),
    ):
        try:dense.run(word,unit,mutation)
        except ValueError as exc:
            R(str(exc).startswith(prefix),'Unexpected dense control failure');result[tag]=str(exc)
        else:raise ValueError('Dense control survived: '+tag)
        print('PASS_REJECT',tag,flush=True)
    return result


def main():
    parser=argparse.ArgumentParser();parser.add_argument('source',type=Path);parser.add_argument('--out',type=Path,required=True)
    a=parser.parse_args();src=a.source;out=a.out;out.mkdir(parents=True,exist_ok=True)
    old=read(src/'bench/inputs/7481-WORD.json.gz');new=read(src/'expected/COMPOSED-WORD.json.gz')
    R({k:v for k,v in old.items() if k!='program'}=={k:v for k,v in new.items() if k!='program'},'Complete literal header')
    R(sha256(boundary.canonical(new)).hexdigest()=='2acc6bfd2807239fafdb3f9e09ff8ad34703df958496590ab657ef0b9ac93aef',
      'Exact candidate canonical word')
    controls=boundary.controls()
    paired=boundary.paired(old,new,{(1557,1):{902:Q(-3,2),985:Q(-3,2)}})
    R(paired['lifetimes']==74 and paired['unchanged_pre_CLEAR_rows']==73,'All74 erasure operands')
    change=paired['changes'][0]
    R((change['before_clock'],change['after_clock'],change['frame'])==(42558,42570,595),'Exact changed CLEAR clocks')
    R(len(change['reads'])==len(change['observations'])==5 and len(change['writes'])==2,'Owned1557 write/read inventory')
    R(change['coframed_at_CLEAR']==[450,451,572,746,757,1557],'Actual final erasure coframe bank')
    R(all(not v['target_after_delta'] for v in change['observations']),'Each of five observer target rows is restored immediately')
    R((paired['before_peak'],paired['after_peak'])==(50,50),'Owned peak')
    R((paired['before_COPY'],paired['after_COPY'])==([33814],[33816]),'Strict COPY sites')
    # The complete trace requires valid literal public endpoints before comparing
    # scratch rows. Hence this specifically detects a hidden erasure difference.
    print('PASS_ALL74_PRE_CLEAR_ROWS',flush=True)
    sys.path.insert(0,str(HERE/'oracles'))
    dense=load('review_dense7164',HERE/'oracles/check_dense_native.py')
    exact=dense.run(new)
    R((exact['public'],exact['owned'],exact['lifetimes'],exact['peak_owned'])==(1501,68,74,50),'Independent dense inventory')
    R(exact['required_grid']==1125*2**25,'Exact grid minimality')
    R(exact['scaled_row_mass']=='841374570120675/8192' and exact['mass_witness']==[66254,'stored'],'Independent global mass')
    R({int(k):v for k,v in exact['paid'].items()}==paired['paid_after'],'Independent literal paid recount')
    print('PASS_DENSE_ALL_PUBLIC_COLUMNS_GRID_MASS',flush=True)
    controls['native_mutations']=mutation_controls(new,dense)
    caller=read(src/'bench/inputs/7113-CALLER.json')
    before=invoice(old,caller,paired['paid_before']);after=invoice(new,caller,paired['paid_after'])
    R(before['T']==after['T'] and before['S']==after['S']==1424,'Fixed targets and rank surplus')
    R(after['empty_root_credits']==0 and sum(after['P'].values())==110485 and sum(after['T'].values())==22461,
      'Complete no-empty-credit signed invoice')
    R(after['native_helpers'][9]==616 and sum(after['native_helpers'].values())==1101,'Actual helper cohort including319')
    delta={r:after['P'].get(r,0)-before['P'].get(r,0) for r in before['P'].keys()|after['P'].keys()
           if after['P'].get(r,0)!=before['P'].get(r,0)}
    R(delta=={1:-34,5:-17,7:17},'Actual signed paid delta')
    # Match independently recounted data to the author receipt; do not import its invoice.
    author=read(src/'expected/SIGNED.json')['price']['after']
    for field in ('P','T'):
        R({str(k):v for k,v in after[field].items()}==author[field],'Fresh signed '+field+' binding')
    bad=copy.deepcopy(after);bad['P'][7]-=1
    try:R(bad['P']==after['P'],'Every literal paid job bound')
    except ValueError as exc:controls['omitted_paid_job']=str(exc)
    else:raise ValueError('Omitted paid job survived')
    p=load('review_directed_decimal',src/'bench/inputs/pricing.py')
    g=load('review_directed_integer',src/'engines/interval_gate.py')
    claim=Q('0.003647969120276');quotes={}
    for name,inv in [('7481',before),('7544',after)]:
        hist=Counter(inv['T']);hist.subtract(inv['P'])
        q1=p.cost(hist,claim);q2=tuple(Q(x,g.B) for x in g.moment(hist,claim))
        R(max(q1[0],q2[0])<=min(q1[1],q2[1]),'Independent directed price overlap')
        R((q1[0]>0 and q2[0]>0) if name=='7544' else (q1[1]<0 and q2[1]<0),'Claim comparison '+name)
        quotes[name]=dict(at=str(claim),decimal_engine=list(map(str,q1)),integer_engine=list(map(str,q2)))
    result=dict(status='PASS_INDEPENDENT7544_REVIEW',boundary=paired,dense=exact,
                invoice_before=before,invoice_after=after,signed_paid_delta=delta,
                quotes=quotes,controls=controls,
                gain_over7481=str(claim-Q('0.003647081039689')),
                limitations=['Normalized finite public-input maps, conditional on physical frame premise.',
                             'All74 pre-CLEAR operands checked;1557 changes, arbitrary-content owned_erasure retained.',
                             'Source replay supplies full physical/caller/resource/outer validation; those engines are reused, not newly independent.'])
    (out/'REVIEW.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print('PASS_INDEPENDENT7544_REVIEW',flush=True)


if __name__=='__main__':main()
