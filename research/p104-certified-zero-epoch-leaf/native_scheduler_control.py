#!/usr/bin/env python3
"""Exercise the retained PoweredWord.native tensor iterator at toy power 3.

Only the raw-source *prefix dependency* is stubbed: two inputs copy genuine
rank-8 helper tags, the third copies a rank-64 root as a positive control.
This validates the live scheduler/loan shape and demonstrates why the v=268
family needs a zero-preservation proof; it is not an independent physical
#8035 replay and does not execute the 36-call source.
"""
import sys,json
from pathlib import Path
from itertools import product
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from upstream import install
install()
from periodic import Job
from powered import Port,PoweredWord

H0=('helper',4,222);H1=('helper',4,223);R=('root',1,0)
J0=('move',4,2,630);J1=('move',4,5,631);JR=('diagnostic-root-copy',)
targets=(Port(H0,8),Port(H1,8),Port(R,64))
paid=(Port(J0,1),Port(J1,1),Port(JR,2))
class Physical:
    def __init__(self):self.values={};self.next=0;self.fresh_paths=[];self.raw_closes=0
    def make(self,value,axes):
        i=self.next;self.next+=1;self.values[i]=value;return Job(i,tuple(range(axes)))
    def fresh(self,exemplar,rank,tag):
        self.fresh_paths.append(tag);return self.make(0,rank)
    def retire(self,job):
        assert self.values.pop(job.owner)==0
    def raw(self,inputs,columns):
        assert [x[0] for x in inputs]==[H0,H1,R]
        for i,p in enumerate(paid):
            temp=self.make(self.values[inputs[i][1].owner],p.rank*columns)
            yield p.tag,temp
            self.values.pop(temp.owner)
        self.raw_closes+=1

def check(floor):
    w=PoweredWord(134,targets,paid,3,floor,12,12)
    physical=Physical()
    productive=[]
    for port,keep in w.target_paths():
        if keep:productive.append(physical.make(1,port.rank))
    assert len(productive) in (19,27)
    blocks=[]
    for block,job in zip(w.paid_paths(),w.native(productive,1,physical),strict=True):
        value=physical.values[job.owner]
        low=all(tag in (J0,J1) for tag in block.tags)
        if floor==15:
            assert value==(0 if low else 1)
        else:
            assert value==1
        blocks.append((block,value))
    assert len(physical.values)==len(productive)
    assert len(blocks)==27
    return {'floor':floor,'retained_target_paths':len(productive),
            'fresh_target_paths':len(physical.fresh_paths),
            'emitted_blocks':len(blocks),
            'selected_low_rank_blocks':sum(all(t in (J0,J1) for t in b.tags) for b,_ in blocks),
            'selected_low_rank_zero_blocks':sum(all(t in (J0,J1) for t in b.tags) and v==0 for b,v in blocks),
            'positive_control_nonzero_blocks':sum(v!=0 for _,v in blocks),
            'cleanup_all_fresh_returned_zero':True}
result=[check(15),check(8)]
assert result[0]['selected_low_rank_zero_blocks']==8
assert result[1]['selected_low_rank_zero_blocks']==0
print(json.dumps(result,indent=2))
print('PASS_ACTUAL_POWERED_ITERATOR_TOY_PREFIX_CONTROL')
