"""Apply the exact #6916 type-A constant blocks inside #6917's mixed caller."""
from copy import deepcopy
from linear import HERE,load,need,read


def construct():
    original=read(HERE/'retained/data/caller.json')
    before=read(HERE/'retained/caller-blocks/data/caller-before.json')
    after=read(HERE/'retained/caller-blocks/data/caller-after.json')
    checker=load(HERE/'retained/caller-blocks/check.py','retained_caller_block_check')
    need(checker.equivalent(before,after)==(38,60800),'38 source-bound block identities')
    extracted=[];bblocks=[[]];joints=[]
    for e in original['events']:
        if e[0]=='J':
            extracted.append(['HOST2',e[1],*e[2]]);joints.append(e);bblocks.append([])
        elif e[0]=='A':extracted.append(e[1:])
        else:
            need(e[0]=='B','Known port type');bblocks[-1].append(e)
        if e[0]!='J':
            meta=original['types'][e[0]];lo=meta['offset'];hi=lo+meta['roles']
            touched=e[2:4] if e[1] in ('ADD','SWAP','QUERY') else [e[2]]
            need(all(lo<=r<hi for r in touched),'All interleaved caller operations use disjoint type fields')
    need(extracted==before['events'],'Exact source A event stream')
    need(original['types']['A']['diagonal']==before['diagonal'] and original['types']['A']['roles']==before['roles'] and original['ambient_rank']==before['ambient_rank'],'A metadata matches the checked block replacement')
    ablocks=[[]];hosts=[]
    for e in after['events']:
        if e[0]=='HOST2':hosts.append(e);ablocks.append([])
        else:ablocks[-1].append(['A',*e])
    need(hosts==[['HOST2',e[1],*e[2]] for e in joints],'Every joint boundary retained in order')
    out=deepcopy(original);out['events']=[]
    for i,(a,b) in enumerate(zip(ablocks,bblocks)):
        out['events']+=a+b
        if i<len(joints):out['events'].append(joints[i])
    need([e for e in out['events'] if e[0] in ('B','J')]==[e for e in original['events'] if e[0] in ('B','J')],'Every B event and joint retained verbatim')
    need(len(original['events'])-len(out['events'])==1298,'Exact event reduction')
    return out


if __name__=='__main__':
    import json
    result=construct();(HERE/'CALLER-COMPRESSED.json').write_text(json.dumps(result,separators=(',',':'))+'\n')
    print('PASS_MIXED_CALLER_COMPRESSION events',len(result['events']),'ordinary saving',1298*32*40*96)
