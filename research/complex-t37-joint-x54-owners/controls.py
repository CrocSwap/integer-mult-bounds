"""Reject malformed frozen flow inputs before accepting any reconstructed map."""
import copy
from construct import construct
from common import P,read,dump

def check(parent,word,out):
    flow=read(P/'data/FLOW.json.gz');order=read(P/'data/ORDER.json')
    result=[]
    for name in ('boolean_bin_count','negative_bin_count','duplicate_window','duplicate_flow',
                 'out_of_window_time','invalid_width','overfull_call','reordered_wave'):
        bad=copy.deepcopy(flow);badorder=copy.deepcopy(order)
        group=bad[0];pattern=next(p for p in group['patterns']if p['flow'])
        if name=='boolean_bin_count':group['patterns'][0]['count']=True
        elif name=='negative_bin_count':group['patterns'][0]['count']=-1
        elif name=='duplicate_window':group['physical_windows'].append(group['physical_windows'][0])
        elif name=='duplicate_flow':pattern['flow'].append(pattern['flow'][0].copy())
        elif name=='out_of_window_time':pattern['flow'][0][0]=333
        elif name=='invalid_width':pattern['flow'][0][1]=6
        elif name=='overfull_call':pattern['flow'][0][2]=pattern['count']+1
        else:badorder[0],badorder[1]=badorder[1],badorder[0]
        try:construct(parent,word,bad,badorder)
        except AssertionError:result.append(name)
        else:raise AssertionError('Accepted malformed flow: '+name)
    receipt=dict(status='PASS_FROZEN_FLOW_NEGATIVE_CONTROLS',rejected=result)
    dump(out,receipt);return receipt
