#!/usr/bin/env python3
"""Independent literal endpoint ledger, dense removed profiles and exact assembly.

Prepared for Thomas DiFiore with OpenAI Codex assistance. PR96 merged
profiles are credited to eumemic/Anthropic Claude. This checker independently
rebuilds all multiplicities and removed local profiles. Production verification
recomputes every merged profile; separate dense corner checks audit that formula.
"""
import argparse
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
from functools import lru_cache
from hashlib import sha256
import gzip
import importlib.util
import json
from math import comb,gcd
from pathlib import Path
import sys

if sys.flags.optimize:raise ValueError('Assertions required')
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent

def require(value,message):
    if not value:raise ValueError(message)
def digest(path):return sha256(path.read_bytes()).hexdigest()
def read(path):return json.loads(path.read_text())

def dense(core,cover,h,complement):
    c=core.bit_count();out=cover&~core;n=out.bit_count();s=3-c
    d=6*(h+1) if c==3 else 3*(h+1)*(s*s+(c-1)*n)
    require(c in (1,2,3) and not core&~cover and (c!=3 or core==cover),'Invalid local frame')
    result=[]
    for i in range(h):
        oi=(out>>i)&1;wi=3+((core>>i)&1);row=[]
        for j in range(h):
            oj=(out>>j)&1;zj=3*(h+1)*((core>>j)&1)-10
            x=wi*zj if c==3 else d*int(i==j)*oi+s*oi*zj+3*(h+1)*s*wi*oj+n*wi*zj-3*(h+1)*(c-1)*oi*oj
            row.append(d*int(i==j)-x if complement else x)
        result.append(row)
    return result

@lru_cache(None)
def local_profile(core,cover,h,complement):
    matrix=dense(core,cover,h,complement);pivots=[]
    for i,row in enumerate(matrix):
        j=next((j for j in range(h-1,-1,-1) if row[j]),None)
        if j is None:continue
        pivots.append((i,j))
        for k in range(i+1,h):
            if matrix[k][j]:
                a,b=row[j],matrix[k][j];factor=gcd(a,b);a//=factor;b//=factor
                matrix[k]=[a*x-b*y for x,y in zip(matrix[k],row)]
                factor=0
                for x in matrix[k]:factor=gcd(factor,x)
                if factor>1:matrix[k]=[x//factor for x in matrix[k]]
    rank=1 if core==cover else cover.bit_count()-core.bit_count()
    if complement:rank=h-rank
    require(len(pivots)==rank,'Dense removed rank differs from frame dimension')
    if rank<=2:return tuple([1]*rank)
    runs=[];run=0
    for k,(i,j) in enumerate(pivots):
        if k and i==pivots[k-1][0]+1 and j==pivots[k-1][1]+1:run+=1
        else:
            if run:runs.append(run)
            run=1
    if run:runs.append(run)
    return tuple(sorted(runs,reverse=True))

def selection_check(selection,word):
    R=word['R'];outputs={s for s,*_ in word['outputs']}
    a,b=selection['entrance'],selection['exit']
    require(a==sorted(set(a)) and b==sorted(set(b)),'Duplicate or unordered selected role')
    require(all(type(s)is int and 0<=s<R for s in a+b),'Selected role outside word')
    require(not set(a)&set(b),'Entrance and exit selected twice')
    require(not set(b)&outputs,'Output role selected for retirement')
    require(selection['R']==R and selection['h']==word['h'],'Selection dimensions differ')

def equal_counts(actual,expected,message):
    require({int(t):n for t,n in actual.items() if n}=={int(t):n for t,n in expected.items() if n},message)

def source_audit(root,package,research):
    path=package/'SOURCE.json'
    if not path.exists():
        require(research,'Missing SOURCE.json');return {}
    result={};seen=set()
    def visit(path,root_relative):
        path=path.resolve()
        if path in seen:return
        seen.add(path);result[str(path.relative_to(root))]=digest(path)
        manifest=read(path)
        for name,expected in manifest['files'].items():
            child=(root/name if root_relative else path.parent/name).resolve()
            require(child.is_relative_to(root),'Pinned path escapes root')
            require(digest(child)==expected,'Changed pinned source: '+name)
            result[str(child.relative_to(root))]=expected
            # Archive-root manifests describe the preserved executable closure.
            # Nested research manifests are original documentary Git blobs;
            # their paths refer to an original full repository, not this archive.
            if child.name=='SOURCE.json' and child.parent.parent==root/'references/frame-compiler':
                visit(child,False)
        if 'shared_dependency_manifest' in manifest:
            child=(path.parent/manifest['shared_dependency_manifest']).resolve()
            require(digest(child)==manifest['shared_dependency_manifest_sha256'],'Changed shared manifest')
            visit(child,False)
    visit(path,True)
    return result

def audit(package,root,axis_dir=None):
    numeric_path=root/'research/deferred-span-frames/independent_check.py'
    spec=importlib.util.spec_from_file_location('independent_numeric',numeric_path)
    numeric=importlib.util.module_from_spec(spec);spec.loader.exec_module(numeric)
    certificate=read(package/'certificate.json');bit=certificate['bit'];N=comb(23,3)*comb(25,3);m=575
    parts=dict(data=Counter({1:18*N,21:2*N,17:2*N,481:2*N}),endpoint_copy=Counter({1:N}))
    width=2*N;axes={};inputs=[package/'certificate.json',numeric_path,Path(__file__).resolve()]
    selections={};words={}
    for h,folder in ((23,'coordinate-23'),(25,'coordinate94-25')):
        word_path=(axis_dir/folder/'word.json.gz') if axis_dir else package/f'word-{h}.json.gz'
        profile_path=(axis_dir/folder/'word.bin.profiles.json') if axis_dir else package/f'profile-{h}.json'
        selected_path=package/f'selection-{h}.json';removed_path=package/f'removed-{h}.bin.profiles.json'
        word=json.loads(gzip.decompress(word_path.read_bytes()));profile=read(profile_path);selected=read(selected_path)
        selections[h]=selected;words[h]=word
        selection_check(selected,word)
        require(digest(word_path)==selected['word_sha256'],'Selection word hash differs')
        require(word['h']==h and word['v']==comb(h,3) and profile['R']==word['R'],'Axis dimensions differ')
        require(profile['crt_disagreements']==0 and profile['loss']==h*(h-1),'Axis exact profile failed')
        require(sum(t*n for t,n in enumerate(profile['blocks']))==profile['rank_sum']==h*word['R']+h*(h-1),'Axis mass differs')
        first={};last={}
        for slot,old,new in word['events']:
            require(0<=slot<word['R'] and 0<=new<len(word['frames']),'Bad event index')
            require(old==last.get(slot,-1),'Event trajectory discontinuity')
            first.setdefault(slot,new);last[slot]=new
        require(set(first)==set(range(word['R'])),'Missing physical role trajectory')
        keys=Counter(('entrance',first[s]) for s in selected['entrance'])
        keys.update(('exit',last[s]) for s in selected['exit'])
        require({f'{kind}:{frame}' for kind,frame in keys}==set(selected['merged_edges']),'Merged edge inventory differs')
        removed=Counter();merged=Counter();removed_mass=0
        for (kind,frame),count in keys.items():
            core,cover=word['frames'][frame]
            runs=local_profile(core,cover,h,kind=='exit')
            removed.update({t:n*count for t,n in Counter(runs).items()})
            removed_mass+=sum(runs)*count
            edge=selected['merged_edges'][f'{kind}:{frame}']
            require(edge['rank']==sum(edge['runs'])==sum(runs)+m-h,'Merged residual rank identity differs')
            require(all(type(t)is int and 0<t<m for t in edge['runs']),'Invalid merged child')
            merged.update({t:n*count for t,n in Counter(edge['runs']).items()})
        removed_profile=read(removed_path)
        equal_counts(dict(enumerate(removed_profile['blocks'])),removed,'Dense exact removed profile differs')
        require(removed_profile['rank_sum']==removed_mass and removed_profile['crt_disagreements']==0,'Removed profile mass differs')
        internal=Counter({t:n for t,n in enumerate(profile['blocks']) if n});internal.subtract(removed)
        require(all(n>=0 for n in internal.values()),'Removed child not present in original profile')
        roles=len(selected['entrance'])+len(selected['exit']);rep=N//word['v'];remaining=word['R']-roles
        require(sum(t*n for t,n in merged.items())==removed_mass+(m-h)*roles,'Merged total mass differs')
        width+=rep*word['R']
        parts[f'internal_{h}']=Counter({t:n*rep for t,n in internal.items() if n})
        parts[f'merged_{h}']=Counter({t:n*rep for t,n in merged.items() if n})
        parts[f'exterior_{h}']=Counter({h:remaining*rep,m-2*h:remaining*rep})
        parts[f'growth_{h}']=Counter({1:2*N,h-2:2*N})
        supplied=bit['axes'][str(h)]
        require(supplied['R']==word['R'] and supplied['entrance_roles']==len(selected['entrance']) and supplied['exit_roles']==len(selected['exit']),'Axis role summary differs')
        require(supplied['merged_edges']==len(keys) and supplied['removed_rank_mass']==removed_mass,'Axis edge summary differs')
        equal_counts(dict(enumerate(supplied['removed_blocks'])),removed,'Axis removed summary differs')
        require(supplied['word_sha256']==digest(word_path) and supplied['selection_sha256']==digest(selected_path),'Axis binding differs')
        axes[str(h)]=dict(roles=word['R'],entrance_roles=len(selected['entrance']),exit_roles=len(selected['exit']),
            exact_dense_removed_edge_profiles=len(keys),removed_rank_mass=removed_mass,remaining_exteriors=remaining)
        inputs += [word_path,profile_path,selected_path,removed_path]
        print('PASS independent exact removed profiles and literal endpoint ledger h',h,flush=True)
    require(set(parts)==set(bit['parts']),'Named paid part inventory differs')
    for name,rows in parts.items():equal_counts(bit['parts'][name],rows,'Paid part differs: '+name)
    rows=sum(parts.values(),Counter());equal_counts(bit['child_multiplicities'],rows,'Complete paid profile differs')
    total=sum(t*n for t,n in rows.items())
    require((bit['m'],bit['N'],bit['W'],bit['L'],bit['total_rank'],bit['deficit'],bit['maxchild'])==
        (m,N,width,N-1846900,total,1846900,max(rows)) and total==m*width-1846900,'Full rank ledger differs')
    require(max(rows)==552,'Unexpected largest merged child')
    bridge=certificate['finite_bridge'];numeric_bridge=deepcopy(bridge)
    numeric_bridge['complex'].pop('scalar_terms',None)
    numeric_bridge['rows'].pop('contract',None)
    require(numeric_bridge==certificate['assembly']['finite_bridge'],'Numeric bridge copies differ')
    require(bridge['bit']['W']==width and bridge['bit']['m']==m and bridge['bit']['maxchild']==max(rows),'Bridge/profile mismatch')
    inherited=read(root/'research/deferred-span-frames/certificate.json')['finite_bridge']
    require(bridge['complex']==inherited['complex'] and bridge['semantic']==inherited['semantic'],'Unchanged complex bridge differs')
    require(bridge['bit']['halving_degree']==17 and bridge['rows']['coefficient']==1059 and bridge['rows']['degree']==2200 and Q(bridge['rows']['degree_gap'])==Q(991,25) and bridge['rows']['suffix_slope']==8800,'Updated bridge constants differ')
    normalized=deepcopy(certificate);normalized['h']=normalized['assembly']['parameters']['h']
    for target in (normalized['finite_bridge'],normalized['assembly']['finite_bridge']):
        if 'contract' in target['rows']:require(type(target['rows'].pop('contract'))is str,'Bad bridge description')
    minimum,slacks,margins=numeric.independent_assembly(normalized)
    a=Q(certificate['bit_saving']);k=Q(certificate['kappa']);step=Q(1,10**18)
    require((a/step).denominator==(k/step).denominator==1,'Saving off exact grid')
    lo,hi=numeric.moment(m,width,rows,a);nlo,nhi=numeric.moment(m,width,rows,a+step)
    accepted=bit['moment'];rejected=bit['excluded_moment']
    require(Q(accepted['lower'])<=lo<=hi<=Q(accepted['upper'])<1,'Independent accepted moment fails')
    require(1<Q(rejected['lower'])<=nlo<=nhi<=Q(rejected['upper']),'Independent next bit grid fails')
    require(k<minimum<=k+step and Q(certificate['next_kappa'])==k+step and Q(certificate['bit_saving_excluded_above'])==a+step,'Next grid rejection differs')
    controls=[]
    def reject(name,callback):
        try:callback()
        except (ValueError,AssertionError):controls.append(name)
        else:raise ValueError('Negative control passed: '+name)
    bad=deepcopy(selections[23]);field='entrance' if bad['entrance'] else 'exit';bad[field].append(bad[field][0])
    reject('duplicate selected role',lambda:selection_check(bad,words[23]))
    bad=deepcopy(selections[23]);bad['exit']=sorted(set(bad['exit'])|{words[23]['outputs'][0][0]})
    reject('output role retirement',lambda:selection_check(bad,words[23]))
    omitted=dict(rows);first=next(iter(omitted));omitted[first]-=1
    reject('omitted paid child',lambda:equal_counts(omitted,rows,'Paid profile differs'))
    bad=deepcopy(normalized);bad['assembly']['constraints']['a_positive']='0'
    reject('falsified assembly slack',lambda:numeric.independent_assembly(bad))
    bad=deepcopy(normalized);bad['assembly']['finite_bridge']['bit']['halving_degree']=9
    reject('stale halving degree',lambda:numeric.independent_assembly(bad))
    bad=deepcopy(normalized);bad['assembly']['finite_bridge']['rows'].update(degree=2000,degree_gap='-4009/25',suffix_slope=8000)
    reject('stale row stock',lambda:numeric.independent_assembly(bad))
    pins=source_audit(root,package,axis_dir is not None)
    inputs.append(root/'research/deferred-span-frames/certificate.json')
    def name(path):
        try:return str(path.resolve().relative_to(root))
        except ValueError:return str(path.resolve())
    return dict(status='PASS independent dense removed profiles, literal paid ledger and exact assembly',
        kappa=str(k),bit_saving=str(a),width=width,maxchild=max(rows),total_rank=total,deficit=1846900,
        axes=axes,strict_constraints=len(slacks),strict_margins=len(margins),
        accepted_gap_at_least=str(numeric.positive_lower_bound(1-hi)),next_bit_gap_at_least=str(numeric.positive_lower_bound(nlo-1)),
        next_kappa_rejected=True,assembly_gap=str(minimum-k),negative_controls=controls,
        pinned_sources=pins,input_sha256={name(path):digest(path) for path in inputs},
        method='Dense integer local projectors; fraction-free top-row/rightmost-pivot elimination for every removed edge; separate40-term atanh logarithms and degree10 exponential; independent47 inequalities/seven margins and bridge formulas.',
        scope='Merged profiles must also be regenerated by the production selector and their low-rank formula has separate representative dense checks. Multiplicative endpoint gauges and arbitrary-dirty realization are separate proof/replay gates. Inherited analytic/all-size/tape/routing/precision/recovery hypotheses remain assumed.')

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package-dir',type=Path,default=HERE)
    parser.add_argument('--repo-root',type=Path)
    parser.add_argument('--axis-dir',type=Path,help='Research adapter for coordinate-23/coordinate94-25 artifacts')
    parser.add_argument('--record',action='store_true');parser.add_argument('--output',type=Path)
    args=parser.parse_args();package=args.package_dir.resolve();root=(args.repo_root or package.parents[1]).resolve()
    result=audit(package,root,args.axis_dir.resolve() if args.axis_dir else None)
    output=args.output or package/'independent-audit.json'
    if args.record:output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    else:require(result==read(output),'Independent receipt differs')
    print(result['status'],result['kappa'],flush=True)
