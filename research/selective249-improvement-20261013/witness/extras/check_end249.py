"""Independent exact raw249 scalar isolation, frame, and focused mutation checks.
Chi Zhao, with substantial OpenAI Codex assistance. Apache-2.0.
No construction or admission modules are imported.
"""
import argparse,copy,gzip,hashlib,json
from pathlib import Path
from fractions import Fraction as F
from collections import Counter

ENDS=(233,249,265,425,441)
U=(256,128,64,32,16,8,6,1)
EXPECTED={'jp8':{1:2528,2:397,3:448,4:169,5:63,6:4}}
def need(ok,message):
    if not ok:raise ValueError(message)
def basis(vs):
    p={}
    for x in vs:
        while x:
            k=x.bit_length()-1
            if k in p:x^=p[k]
            else:p[k]=x;break
    return tuple(p.values())
def check(w,provider):
    n=716
    need((w['report']['v'],w['report']['R'])==(112,492),'native shape')
    P=[{i:F(1)}for i in range(n)]
    def apply(e):
        need(e[0] in ('add','scale'),'scalar primitive')
        if e[0]=='scale':P[e[1]]={j:v*F(e[2],e[3])for j,v in P[e[1]].items()}
        else:
            t,s=e[1:3];c=F(e[3],e[4])
            for j,v in list(P[s].items()):
                z=P[t].get(j,F(0))+c*v
                if z:P[t][j]=z
                else:P[t].pop(j,None)
    early={i for i,_ in w['early_cleanup']}
    tail=[w['cleanup'][i][:-1]+[f]for i,f in w['early_cleanup']]
    for e in w['A']+w['cut']+w['B']+tail:apply(e)
    ended=set(map(int,w['helper_final']))
    for h in ended:
        need(P[h]=={h:F(1)},'ended row isolation')
        need(all(not P[j].get(h)for j in range(n)if j!=h),'ended column isolation')
    for i,e in enumerate(w['cleanup']):
        if i not in early:apply(e)
    need(all(P[j]=={j:F(1)}for j in range(n)if not 112<=j<224),'non-target FULL restoration')
    cur=[()for _ in range(n)]
    for j,v in enumerate(w['ports']):cur[j]=(v,)
    for h,f in w['start_extra'].items():cur[int(h)]=basis(f)
    profile=Counter()
    def climb(r,f):
        f=basis(f)
        need(len(basis(cur[r]+f))==len(f),'monotone frame containment')
        if len(f)>len(cur[r]):profile[len(f)-len(cur[r])]+=1
        cur[r]=f
    for e in w['A']+w['B']+tail:
        for j in (e[1:3]if e[0]=='add' else e[1:2]):climb(j,tuple(e[-1]))
    for h in ENDS:
        need(str(h) not in w['start_extra'],'new helper cold')
        need(len(cur[h])==len(basis(cur[h]+U))==8,'new terminal frame')
        need(tuple(w['helper_final'][str(h)])==U,'declared new terminal frame')
    for h in range(n):
        if 112<=h<224:continue
        climb(h,tuple(w['helper_final'].get(str(h),[1<<j for j in range(9)])))
    need(dict(profile)==EXPECTED[provider],'independent climb profile')
    return {'ended_rows_columns':len(ended),'new_ends':list(ENDS),'new_terminal_rank':8,'climb_profile':dict(sorted(profile.items()))}
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--word',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--provider',choices=EXPECTED,required=True);ap.add_argument('--negative-controls',action='store_true');a=ap.parse_args()
    raw=a.word.read_bytes();raw=gzip.decompress(raw)if a.word.suffix=='.gz'else raw;w=json.loads(raw)
    report={'status':'PASS_INDEPENDENT_END249_ISOLATION_FRAMES_AND_RESTORATION','provider':a.provider,'word_content_sha256':hashlib.sha256(raw).hexdigest(),**check(w,a.provider),'rejected_controls':[],'scope':'Separate Fraction replay of all ended row/column isolation and remaining non-target cleanup; GF2 monotone frames and paid climbs. Native compensation, wrappers, phases and global admission are separate.'}
    if a.negative_controls:
        pi=next(i for i,e in enumerate(w['A'])if e==['scale',249,1,2,[]])
        ti=next(i for i,e in enumerate(w['A'])if e[0]=='add' and 112<=e[1]<224 and e[2]==249)
        ai=next(i for i,_ in w['early_cleanup']if w['cleanup'][i][:5]==['add',31,29,-2,1])
        ci=next(i for i,_ in w['early_cleanup']if w['cleanup'][i][:5]==['add',249,25,-4,1])
        di=next(i for i,_ in w['early_cleanup']if w['cleanup'][i][:5]==['add',255,249,1,4])
        def omit_scale(q):q['A'].pop(pi)
        def flip_scale(q):q['A'][pi][2]*=-1
        def omit_target(q):q['A'].pop(ti)
        def omit_accumulator(q):q['cleanup'][ai][3]=0
        def double_accumulator(q):q['cleanup'][ai][3]*=2
        def omit_carrier(q):q['cleanup'][ci][3]=0
        def omit_column_clear(q):q['cleanup'][di][3]=0
        def wrong_terminal(q):q['helper_final']['249']=[256,128,64,32,16,8,4,2]
        for name,mutate,reason in [('omit_new_premix_scale',omit_scale,'ended row isolation'),('flip_new_premix_scale',flip_scale,'ended row isolation'),('omit_new_target_cancellation',omit_target,'ended column isolation'),('omit_accumulator_term',omit_accumulator,'ended row isolation'),('double_accumulator_term',double_accumulator,'ended row isolation'),('omit_lifted_carrier',omit_carrier,'ended row isolation'),('omit_column_clear',omit_column_clear,'ended column isolation'),('wrong_dim8_terminal',wrong_terminal,'declared new terminal frame')]:
            q=copy.deepcopy(w);mutate(q)
            try:check(q,a.provider)
            except ValueError as e:
                need(str(e)==reason,'wrong mutation rejection reason '+name+': '+str(e));report['rejected_controls'].append({'name':name,'reason':str(e)})
            else:raise ValueError('accepted mutant '+name)
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(report,indent=2)+'\n');print(report['status'],a.provider,len(report['rejected_controls']),'mutations rejected')
if __name__=='__main__':main()
