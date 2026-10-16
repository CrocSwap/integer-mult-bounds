"""Fresh exact endpoint charts and changed alias split-projectors.
Uses only our original rational helper, never upstream executable code.
"""
from fractions import Fraction as Q
from collections import Counter,defaultdict
from functools import lru_cache
import json,gzip,hashlib
import context as c
c.verify()
import chart_rational as rat

def gram(a,b):return 9*sum(x*y for x,y in zip(a,b))-sum(a)*sum(b)
def basis(frame):
    if frame is None:return []
    return frame['b']if 'b'in frame else rat.nullspace(frame['a'])
def ann(frame):
    if frame is None:return []
    return frame['a']if 'a'in frame else rat.nullspace(frame['b'])
def canon(rows):
    R,p=rat.rref(rows);return tuple(tuple(rat.primitive(row))for row in R[:len(p)])
def chart(BD,AE):
    BD=[list(x)for x in BD];AE=[list(x)for x in AE]
    assert all(sum(x*y for x,y in zip(a,b))==0 for a in AE for b in BD)
    gd=[[9*x-sum(row)for x in row]for row in BD]
    residual=rat.nullspace(AE+gd)
    outside=[rat.primitive([11*x-sum(a)for x in a])for a in AE]
    rank=20-len(AE)-len(BD);assert len(residual)==rank>=0
    columns=residual+BD+outside
    assert len(columns)==20 and len(rat.rref(columns)[1])==20
    assert all(gram(a,b)==0 for a in residual for b in BD+outside)
    assert all(gram(a,b)==0 for a in BD for b in outside)
    B=[list(x)for x in zip(*columns)];f=rat.factor(B)
    assert f['count']<=400 and max(f['max_numerator'],f['max_denominator'])<2**80
    inv=[[Q(i==j)for j in range(20)]for i in range(20)]
    for op,i,j,q in f['factors']:
        if op=='swap':inv[i],inv[j]=inv[j],inv[i]
        elif op=='scale':inv[i]=[x*q for x in inv[i]]
        else:inv[i]=[x+q*y for x,y in zip(inv[i],inv[j])]
    for L,R in((B,inv),(inv,B)):
        cols=list(zip(*R))
        assert all(sum(x*y for x,y in zip(row,col))==int(i==j)for i,row in enumerate(L)for j,col in enumerate(cols))
    # On a full basis, the first-block projector fixes E intersect D-perp
    # and kills D + E-perp. This uniquely identifies P_E-P_D.
    return dict(rank=rank,donor_dimension=len(BD),recipient_dimension=20-len(AE),basis_columns=columns,inverse=inv,**f)
def save(name,obj):
    raw=(json.dumps(rat.serial(obj),separators=(',',':'))+'\n').encode()
    with gzip.GzipFile(filename=str(c.OUTPUT/name),mode='wb',mtime=0)as out:out.write(raw)
def run():
    word,frames,roles,physical,entrances,ends,widths,origin=c.inventory()
    programs=[];registry={};uses=[]
    for role in roles:
        if entrances[role]is None:assert ends[role]is None;continue
        key=(canon(basis(entrances[role])),canon(ann(ends[role])))
        if key not in registry:
            registry[key]=len(programs);programs.append(dict(program_id=len(programs),**chart(*key)))
            if len(programs)%100==0:print('Endpoint programs',len(programs),flush=True)
        program=programs[registry[key]];assert program['rank']==widths[role]
        uses.append(dict(role=role,physical=physical[role],rank=widths[role],program_id=registry[key],origin=origin[role],restored=ends[role]is not None))
    assert len(uses)==2317 and sum(x['restored']for x in uses)==240
    endpoint=dict(status='PASS_ALL_CURRENT_ENDPOINT_CHARTS',head=c.HEAD,word_sha256=c.WORD_SHA,checker_sha256=c.sha(__file__),source_manifest_sha256=c.sha(c.MANIFEST),rational_checker_sha256=c.sha(c.RATIONAL),context_sha256=c.sha(c.HERE/'context.py'),
        nontrivial_endpoint_uses=len(uses),identity_endpoint_uses=len(roles)-len(uses),programs=len(programs),max_factors=max(x['count']for x in programs),max_numerator=max(x['max_numerator']for x in programs),max_denominator=max(x['max_denominator']for x in programs),retained_chart_bound=400,normalizer_bound=599,exact_inverse_products=True,exact_factor_replay=True,metric='9I-J',exterior_formula='11*a-sum(a)',factor_programs=programs,role_uses=uses)
    save('endpoint-charts.json.gz',endpoint)
    old=c.source('bitword/selected/bit/word_p10.json.gz');oldpairs=set(map(tuple,old['pairs']))
    ps=set(word['phase1']);order=word['phase1']+[i for i in range(len(word['ops']))if i not in ps];times={i:j for j,i in enumerate(order)};visits=defaultdict(list)
    for i in order:
        for role in word['ops'][i][:2]:visits[role].append(i)
    gauges={e['role']:e for e in word['gauges']};seams=[];sprograms=[];registry={}
    for donor,recipient in word['pairs']:
        if(donor,recipient)in oldpairs:continue
        donorframe=word['op_frame'][visits[donor][-1]];recipientframe=gauges[recipient]['frame'];D=frames[donorframe];E=frames[recipientframe]
        assert times[visits[donor][-1]]<word['reads'][str(recipient)]==times[visits[recipient][0]]
        key=(donorframe,recipientframe)
        if key not in registry:
            registry[key]=len(sprograms);sprograms.append(dict(program_id=len(sprograms),donor_end_frame=donorframe,recipient_gauge_frame=recipientframe,**chart(basis(D),ann(E))))
        p=sprograms[registry[key]];assert p['rank']==E['dim']-D['dim']
        # Positive seam occurs verbatim in the paid helper dimension path.
        seams.append(dict(donor=donor,recipient=recipient,physical_stream=physical[donor],read_order=word['reads'][str(recipient)],donor_last_order=times[visits[donor][-1]],donor_end_frame=donorframe,recipient_gauge_frame=recipientframe,rank=p['rank'],program_id=registry[key]))
    assert len(seams)==63
    census=Counter(x['rank']for x in seams)
    seam=dict(status='PASS_EXACT_CHANGED_ALIAS_SEAM_PROJECTORS',head=c.HEAD,word_sha256=c.WORD_SHA,checker_sha256=c.sha(__file__),context_sha256=c.sha(c.HERE/'context.py'),source_manifest_sha256=c.sha(c.MANIFEST),changed_seams=len(seams),programs=len(sprograms),positive_seams=sum(v for k,v in census.items()if k),rank_census=dict(sorted(census.items())),max_factors=max(x['count']for x in sprograms),max_numerator=max(x['max_numerator']for x in sprograms),max_denominator=max(x['max_denominator']for x in sprograms),exact_inverse_products=True,exact_split_projectors=True,factor_programs=sprograms,role_uses=seams)
    save('seam-charts.json.gz',seam)
    summary=dict(endpoint={k:v for k,v in endpoint.items()if k not in('factor_programs','role_uses')},seams={k:v for k,v in seam.items()if k not in('factor_programs','role_uses')},outputs={n:c.sha(c.OUTPUT/n)for n in('endpoint-charts.json.gz','seam-charts.json.gz')})
    (c.OUTPUT/'chart-receipt.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
if __name__=='__main__':run()
