"""Fresh F2 source proof, independent literal projection/inverse and controls.
No saved execution receipt is accepted. Uses the actual clean source context
and freshly emitted local physical records. Assisted with ChatGPT.
"""
from collections import Counter
import hashlib,json,time

EXPECTED_EVENT='e74e43692685ad5f716b41b363acb8b443c2c90096634a55f0e3728980713944'


def events(records,reverse=False):
    center=None
    for k in (range(len(records)-6,-1,-6) if reverse else range(0,len(records),6)):
        op,a,b,c,f,z=records[k:k+6]
        if op==1:
            if b==20163:
                assert center is not None
                b=center
            assert 0<=a<20163 and 0<=b<20163 and a!=b
            yield a,b,-c if reverse else c
        elif op==(3 if reverse else 2):
            assert center is None and b==20163
            center=a
        elif op==(2 if reverse else 3):
            assert center==a and b==20163
            center=None
    assert center is None


def replay_projection(records,reverse=False):
    n=20163;v=1760
    columns=[1<<i for i in range(n)];norms=[1]*n
    wanted=columns[:]
    for i in range(v):wanted[v+i]^=1<<i
    largest=1;counts=Counter();digest=hashlib.sha256(b'[');count=0
    for a,b,c in events(records,reverse):
        if c&1:columns[a]^=columns[b]
        norms[a]+=abs(c)*norms[b];largest=max(largest,norms[a])
        counts[abs(c)]+=1
        if count:digest.update(b',')
        digest.update(json.dumps([a,b,c],separators=(',',':')).encode());count+=1
    digest.update(b']')
    assert columns==wanted,'independent literal all-column endpoint'
    assert count==2569626 and counts=={1:785130,2:1783176,3:1320}
    if not reverse:assert digest.hexdigest()==EXPECTED_EVENT
    return dict(all_formal_columns=n,all_source_and_dirty_restored=True,
                arbitrary_target_contents_preserved=True,
                event_sha256=digest.hexdigest(),weighted_additions=count,
                coefficient_counts=dict(counts),literal_unit_additions=sum(c*n for c,n in counts.items()),
                max_intermediate_row_l1=largest,final_source_row_l1=max(norms[:v]),
                final_target_row_l1=max(norms[v:2*v]),final_dirty_row_l1=max(norms[2*v:]))


def run(context,records,progress=lambda text:None):
    started=time.monotonic();ns=dict(context)
    text=ns['SOURCE_TEXT'];body=text[text.index('def replay('):text.index("if __name__=='__main__':")]
    exec(compile(body,'pinned PR210 source471 scalar checker','exec'),ns)
    progress('Checking every source, target and arbitrary dirty F2 column')
    exact=ns['replay']('F2')
    assert exact['formal_columns']==20163 and exact['all_targets']and exact['all_source_and_dirty_restored']
    progress('Checking the independently projected literal word and inverse')
    forward=replay_projection(records);inverse=replay_projection(records,True)
    assert forward['max_intermediate_row_l1']==37623
    assert inverse['max_intermediate_row_l1']==9430154
    controls={}
    for mutation in ['omit_early_mix','old_adjoint','undo_before_restore','omit_gauge_mix','omit_gauge_compensation','late_phase1_gauge']:
        try:ns['replay']('F2',mutation=mutation)
        except AssertionError as error:controls[mutation]=dict(rejected=True,reason=str(error))
        else:raise AssertionError('invalid source mutation accepted: '+mutation)
    return dict(status='PASS_FRESH_F2_COLUMNS_INVERSE_AND_SIX_CONTROLS',F2=exact,
                forward=forward,inverse=inverse,controls=controls,
                source_sha256=hashlib.sha256(text.encode()).hexdigest(),seconds=time.monotonic()-started,
                scope='New F2 supplier scalar proof and signed literal-lift majorants; no old defining-Z identity is imposed.')
