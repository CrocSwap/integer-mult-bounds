"""Independent original-Git bindings and rational moment brackets for PR2865.
Does not admit the audited supplier or replace the complete word/fill replay.
"""
from pathlib import Path
from fractions import Fraction as F
import importlib.util, json, hashlib, subprocess
P=Path('/tmp/pr-efficient1800');R=Path('/tmp/integer-mult-efficient1100-20261015');pkg=P/'sources/2865/research/t74-2751-joint-twelve-audit'
spec=importlib.util.spec_from_file_location('joint_audit_metadata',pkg/'verify.py');a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
sources=json.loads((pkg/'SOURCES.json').read_text());rows=[];claims={}
def original(commit,path,blob,sha):
    oid=subprocess.check_output(['git','rev-parse',commit+':'+path],cwd=R,text=True).strip()
    raw=subprocess.check_output(['git','cat-file','blob',oid],cwd=R)
    assert oid==blob and hashlib.sha256(raw).hexdigest()==sha,(commit,path)
    return raw
remote={r['key']:r for r in sources['remote_sources']}
assert set(remote)==set(a.INPUTS)
for key,(pr,commit,path,blob,sha) in sorted(a.INPUTS.items()):
    r=remote[key];assert (r['pr'],r['commit'],r['path'],r['git_blob'],r['sha256'])==(pr,commit,path,blob,sha)
    raw=original(commit,path,blob,sha);rows.append(dict(key=key,commit=commit,path=path,git_blob=blob,sha256=sha))
    if key in ('claim2751','claim2733','claim2733_head'):claims[key]=json.loads(raw)
for r in sources['files']:
    original(sources['base_commit'],r['path'],r['git_blob'],r['sha256']);rows.append(dict(r,commit=sources['base_commit']))
vendors=[]
for r in sources['vendored_code'] if 'vendored_code' in sources else sources['vendored']:
    c=r['copied_from'];raw=original(c['commit'],c['path'],r['git_blob'],r['sha256']);assert raw==(pkg/r['path']).read_bytes()
    assert tuple(a.VENDOR[r['path']])==(r['module'],r['git_blob'],r['sha256'])
    if 'original' in r:
        o=r['original'];assert original(o['commit'],o['path'],r['git_blob'],r['sha256'])==raw
    vendors.append(dict(path=r['path'],git_blob=r['git_blob'],sha256=r['sha256'],copied_from=c,original=r.get('original')))
assert len(vendors)==6
reviewed_libraries=[]
for sub,source in [('pr2315/words_check.py','research/t74-2435-fill-independent-check/vendor/pr2315/words_check.py'),('pr2387/fill_check80.py','research/t74-2435-fill-independent-check/vendor/pr2387/fill_check80.py')]:
    raw=subprocess.check_output(['git','show','313287203187737c7f8f2394f1a167168e53b89e:'+source],cwd=R)
    assert raw==(pkg/'vendor'/sub).read_bytes()
    reviewed_libraries.append(dict(path=sub,reviewed_main_path=source,commit='313287203187737c7f8f2394f1a167168e53b89e',sha256=hashlib.sha256(raw).hexdigest()))
# Independent exact rational log/exp enclosures. Range reduction ensures z<=1/3.
def log_small(q,N=50):
    z=(q-1)/(q+1);assert 0<=z<=F(1,3)
    s=sum((2*z**(2*j+1)/F(2*j+1) for j in range(N)),F(0))
    return s,s+2*z**(2*N+1)/((2*N+1)*(1-z*z))
log2=log_small(F(2))
def logs(q):
    k=0
    while q>=2:q/=2;k+=1
    l,u=log_small(q);return l+k*log2[0],u+k*log2[1]
def rounded(q,up):
    n=q.numerator*10**45;d=q.denominator;return F((n+d-1)//d if up else n//d,10**45)
def exp_bounds(x,N=24):
    assert 0<=x<1
    t=s=F(1)
    for j in range(1,N+1):t=t*x/j;s+=t
    return s,s+(t*x/(N+1))/(1-x/(N+2))
def moment(profile,a):
    lo=hi=F(0)
    for r,n in profile.items():
        r=int(r);assert 0<r<73 and type(n) is int and n>=0
        l,u=logs(F(73,r));lo+=F(n*r,73)*exp_bounds(rounded(a*l,False))[0];hi+=F(n*r,73)*exp_bounds(rounded(a*u,True))[1]
    return lo,hi
brackets=[]
for key,c in claims.items():
    profile=c['profile'] if key=='claim2751' else c['global_profile'];a=F(c['complex_lower']);b=F(c['complex_upper']);assert b-a==F(1,10**24)
    low=moment(profile,a);high=moment(profile,b);assert low[1]<66304<high[0]
    assert low[1]-low[0]<F(1,10**30) and high[1]-high[0]<F(1,10**30)
    brackets.append(dict(claim=key,lower=str(a),upper=str(b),lower_accepted=True,upper_rejected=True,interval_width_below='1e-30'))
out=dict(status='passed',data_and_context_git_bindings=rows,vendor_original_bindings=vendors,prior_review_libraries=reviewed_libraries,independent_rational_brackets=brackets,scope='49 data inputs,2 historical context inputs,6 original vendor bindings and3 exact rational endpoint brackets. Source authentication alone does not replace library code review or complete PR2865 replay. No supplier or outer-theorem admission.')
(P/'provenance-2865.json').write_text(json.dumps(out,indent=2)+'\n')
print('PASS',len(rows),'data/context Git bindings;',len(vendors),'original vendor bindings;',len(brackets),'independent rational endpoint brackets')
