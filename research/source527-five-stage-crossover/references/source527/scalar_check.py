"""Fresh F2 source proof, independent literal projection/inverse and controls.
No saved execution receipt is accepted. Uses the actual clean source context
and freshly emitted local physical records. Assisted with ChatGPT.
"""
from collections import Counter
import hashlib,json,time

EXPECTED_EVENT='b266e69af903698cd8c10d8928525d5e9a3ef6241a44924801cf1d275038cf34'


def events(records,reverse=False):
    center=None
    for k in (range(len(records)-6,-1,-6) if reverse else range(0,len(records),6)):
        op,a,b,c,f,z=records[k:k+6]
        if op==1:
            if b==20107:
                assert center is not None
                b=center
            assert 0<=a<20107 and 0<=b<20107 and a!=b
            yield a,b,-c if reverse else c
        elif op==(3 if reverse else 2):
            assert center is None and b==20107
            center=a
        elif op==(2 if reverse else 3):
            assert center==a and b==20107
            center=None
    assert center is None


def replay_projection(records,reverse=False):
    n=20107;v=1760
    columns=[1<<i for i in range(n)];norms=[1]*n
    wanted=columns[:]
    for i in range(v):wanted[v+i]^=1<<i
    largest=1;counts=Counter();digest=hashlib.sha256();count=0
    for a,b,c in events(records,reverse):
        if c&1:columns[a]^=columns[b]
        norms[a]+=abs(c)*norms[b];largest=max(largest,norms[a])
        counts[abs(c)]+=1
        digest.update(json.dumps([a,b,c],separators=(',',':')).encode());digest.update(b'\n');count+=1
    assert columns==wanted,'independent literal all-column endpoint'
    assert count==2569817 and counts=={1:785301,2:1783196,3:1320}
    if not reverse:assert digest.hexdigest()==EXPECTED_EVENT
    return dict(all_formal_columns=n,all_source_and_dirty_restored=True,
                arbitrary_target_contents_preserved=True,
                event_sha256=digest.hexdigest(),weighted_additions=count,
                coefficient_counts=dict(counts),literal_unit_additions=sum(c*n for c,n in counts.items()),
                max_intermediate_row_l1=largest,final_source_row_l1=max(norms[:v]),
                final_target_row_l1=max(norms[v:2*v]),final_dirty_row_l1=max(norms[2*v:]))



def run(context,records,progress=lambda text:None):
    import gc
    started=time.monotonic();ns=dict(context);source=ns['SOURCE_TEXT']
    assert hashlib.sha256(source.encode()).hexdigest()=='e675d4eb9d90ff0b44279fae0b46f1a8b39f65421cc38454b70a6b75d0e10b42'
    exec(compile(source,'source527 exact scalar word','exec'),ns)
    progress('Checking all20107 source, target and arbitrary dirty F2 columns')
    exact=ns['replay']('F2');assert exact['formal_columns']==20107 and exact['all_targets']and exact['all_source_and_dirty_restored']
    progress('Checking independent literal physical projection and inverse')
    forward=replay_projection(records);inverse=replay_projection(records,True)
    assert forward['max_intermediate_row_l1']==64360 and inverse['max_intermediate_row_l1']==9747166
    bound=ns['replay']('bound');bits=8*((bound.bit_length()+2+7)//8);assert 1<<bits>2*bound
    progress('Checking the signed integer source decoder and dirty restoration')
    integer=[]
    for direction in(1,-1):integer.append(ns['replay']('Z',direction,bits));gc.collect()
    controls={}
    for mutation in ['omit_sparse_anchor','wrong_sparse_sign','omit_pair_initialization','omit_pair_restoration','wrong_pair_restore_sign','subtract_paired_alias','omit_transformed_source_mix','omit_transformed_source_read','omit_echelon_setup','omit_echelon_inverse','flip_echelon_sign','omit_rank_setup','omit_rank_inverse','repeat_rank_read','omit_aggregation_setup','omit_aggregation_inverse','repeat_aggregation_read','omit_extra_mix','omit_extra_compensation','omit_early_mix','old_adjoint','undo_before_restore','omit_gauge_mix','omit_gauge_compensation','late_phase1_gauge']:
        try:ns['replay']('Z'if mutation in('flip_echelon_sign','wrong_pair_restore_sign','wrong_sparse_sign')else'F2',bits=bits,mutation=mutation)
        except AssertionError as error:controls[mutation]=dict(rejected=True,reason=str(error))
        else:raise AssertionError('invalid source mutation accepted: '+mutation)
    return dict(status='PASS_FRESH527_F2_SIGNED_DECODER_INDEPENDENT_INVERSE_AND_25_CONTROLS',F2=exact,integer=integer,majorant=dict(residual_bound=bound,packing_bits=bits),forward=forward,inverse=inverse,controls=controls,source_sha256=hashlib.sha256(source.encode()).hexdigest(),seconds=time.monotonic()-started,scope='Fresh source527 F2 all-column supplier and both signed defining integer decoders, independently projected literal word/inverse majorants. Five-stage signed lift uses the literal primitive inverse; the F2 endpoint specifies its supplier property.')
