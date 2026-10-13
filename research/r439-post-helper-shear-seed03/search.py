"""One post-star helper transvection, fixed target basis. Apache-2.0.
Prepared for @woklerx with substantial OpenAI Codex assistance.
"""
import copy,gzip,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
SOURCE='research/r439-helper-stars-seed19/candidate.json.gz'


def read_source():return json.loads(gzip.decompress((ROOT/SOURCE).read_bytes()))


def stream(word):
    result=[]
    for section in ('D','A'):
        for _,d,ss in word[section]:result.extend(('add',d,s)for s in ss)
    for j,c in enumerate(word['ret']):
        result.append(('copy',661,c))
        for i,ss in enumerate(word['scatter']):
            if j in ss:result.append(('add',111+i,661))
        result.append(('erase',661,c))
    for section in ('B','C'):
        for _,d,ss in word[section]:result.extend(('add',d,s)for s in ss)
    return result


def positive(ops,reverse=False):
    values=[1]*662;peak=1
    for tag,d,s in reversed(ops)if reverse else ops:
        if reverse and tag!='add':tag='erase'if tag=='copy'else'copy'
        if tag=='add':values[d]+=values[s]
        elif tag=='copy':values[d]=values[s]
        else:values[d]=0
        peak=max(peak,values[d])
    return peak


def bill(word):
    ops=stream(word);f=positive(ops);b=positive(ops,True)
    local=64*f**3*b**2;nine=(1<<18)*f**5*b**4
    return {'ADDs':sum(t=='add'for t,_,__ in ops),'D_ADDs':sum(len(g[2])for g in word['D']),
            'F':f,'B':b,'local_bound':str(local),'nine_stage_bound':str(nine),
            'admitted':local<(1<<104) and nine<(1<<192)}


def middle(word):
    if len(word['D'])!=1165:raise ValueError('PR967 frozen records')
    before=word['D'][:527];core=word['D'][527:638];after=word['D'][638:]
    if [x[1]for x in core]!=list(range(111,222)):raise ValueError('middle row order')
    columns=[0]*439
    for i,(f,d,ss)in enumerate(core):
        if f!=0 or any(not 222<=s<661 for s in ss):raise ValueError('middle shape')
        for s in ss:columns[s-222]^=1<<i
    return before,core,after,columns


def components(word):
    parent=list(range(439))
    def find(x):
        while parent[x]!=x:x=parent[x]
        return x
    for f,d,ss in word['D'][:221]:
        if f!=0 or len(ss)!=1:raise ValueError('helper edge')
        d-=222;s=ss[0]-222
        if not(0<=d<439 and 0<=s<439):raise ValueError('helper shape')
        parent[find(d)]=find(s)
    return [find(i)for i in range(439)]


def construct(word,d,s):
    before,core,after,cols=middle(word)
    changed=[]
    for f,t,ss in core:
        row=set(ss)
        if 222+d in row:row.symmetric_difference_update({222+s})
        changed.append([f,t,sorted(row)])
    out=copy.deepcopy(word);extra=[0,222+d,[222+s]]
    out['D']=copy.deepcopy(before)+[extra]+changed+[extra.copy()]+copy.deepcopy(after)
    return out


def search(word):
    cols=middle(word)[3];groups=components(word);candidates=[];hist={};pairs=0;cross=0
    for d in range(439):
        for s in range(439):
            if d==s:continue
            pairs+=1
            gain=cols[s].bit_count()-(cols[s]^cols[d]).bit_count()-2
            if groups[d]==groups[s]:continue
            cross+=1;hist[str(gain)]=hist.get(str(gain),0)+1
            if gain>0:
                tie=hashlib.sha256(('3:'+str(d)+':'+str(s)).encode()).hexdigest()
                candidates.append((-gain,tie,d,s))
    candidates.sort();trials=[];winner=None
    for neg,tie,d,s in candidates[:32]:
        out=construct(word,d,s);price=bill(out)
        trials.append({'destination':d,'source':s,'net_saving':-neg,'tie':tie,'bill':price})
        if winner is None and price['admitted']:
            winner={'destination':d,'source':s,'net_saving':-neg,'bill':price,'trial':len(trials)-1}
    return {'ordered_pairs_scored':pairs,'cross_component_pairs':cross,'positive_cross_pairs':len(candidates),
            'gain_histogram':hist,'priced_trials':trials,'winner':winner,
            'stopping_rule':'all ordered pairs scored; exactly first min(32,positive cross-component nominees) fully priced; choose first admitted'},(None if winner is None else construct(word,winner['destination'],winner['source']))

if __name__=='__main__':
    report,word=search(read_source());print(json.dumps(report,indent=2))
