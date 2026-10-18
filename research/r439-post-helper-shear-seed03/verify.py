"""Exact independently checked post-star helper shear construction.
Apache-2.0. Prepared for @woklerx with substantial OpenAI Codex assistance.
"""
import argparse,ast,copy,gzip,hashlib,importlib.util,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(HERE))
import search
import independent as I
need=I.need
BASE='2921874911956718fcaaaf9396fe8267b3cfa9f0'
INPUTS=(search.SOURCE,'research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz',
        'research/e8-bit-p111-tuned/code/xcheck_p.py','research/e8-bit-p111-tuned/tune/EXPECTED.json',
        'research/e8-bit-p111-tuned/vendor/pr510/e8-r480-nine-stage/vendor/e8-r715-eleven-stage-whole/code/global_k.py')


def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False)


def load_bytes(raw):
    def pairs(items):
        d={}
        for k,v in items:need(k not in d,'duplicate key');d[k]=v
        return d
    def bad(x):raise ValueError('nonfinite JSON')
    return json.loads(raw,object_pairs_hook=pairs,parse_constant=bad)


def read(path):
    raw=path.read_bytes()
    return load_bytes(gzip.decompress(raw)if path.suffix=='.gz'else raw)


def pins_check(p):
    need(set(p)=={'base_commit','files'} and p['base_commit']==BASE,'source manifest')
    need(set(p['files'])==set(INPUTS),'source pin inventory')
    for name in INPUTS:need(hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==p['files'][name],'source hash')


def same(a,b,msg):need(canonical(a)==canonical(b),msg)


def guards(price):
    need(int(price['local_bound'])<1<<104,'local precision')
    need(int(price['nine_stage_bound'])<1<<192,'nine-stage precision')


def source_formula():
    tree=ast.parse((ROOT/INPUTS[4]).read_text())
    forms=[n.value for n in ast.walk(tree)if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='prefix'for t in n.targets)]
    expected=ast.parse('(1<<nb)*cf**(K+1)*cb**K',mode='eval').body
    need(len(forms)==1 and ast.dump(forms[0])==ast.dump(expected),'retained precision formula')
    bridge=ast.parse('nb==6*(K-1)',mode='eval').body
    need(any(isinstance(n,ast.Compare)and ast.dump(n)==ast.dump(bridge)for n in ast.walk(tree)),'bridge exponent')
    need(read(ROOT/INPUTS[3])['nine']['bit']['charged_prefix_bits']==192,'retained allocation')


def run():
    pins=read(HERE/'SOURCES.json');pins_check(pins);source_formula()
    parent=read(ROOT/INPUTS[0]);original=read(ROOT/INPUTS[1])
    report,candidate=search.search(parent);need(candidate is not None,'no admitted witness')
    witness=report['winner'];d,s=witness['destination'],witness['source']
    need(type(d)is int and type(s)is int and d!=s and 0<=d<439 and 0<=s<439,'helper indices')
    same(candidate,I.make(parent,d,s),'independent source-row construction')
    same({k:v for k,v in candidate.items()if k!='D'},{k:v for k,v in parent.items()if k!='D'},'non-D drift')
    histogram,geometry=I.support_census(parent);same(histogram,report['gain_histogram'],'independent complete support scores')
    expected_d=I.d_rows(original);need(I.d_rows(candidate)==I.d_rows(parent)==expected_d,'semantic D on all661 columns')
    trial_checks=[]
    for trial in report['priced_trials']:
        trial_word=I.make(parent,trial['destination'],trial['source'])
        need(I.d_rows(trial_word)==expected_d,'trial semantic D')
        f,adds=I.check_full(trial_word);b,again=I.check_full(trial_word,True)
        price={'ADDs':adds,'D_ADDs':sum(len(g[2])for g in trial_word['D']),'F':f,'B':b,
            'local_bound':str((1<<6)*f**3*b**2),'nine_stage_bound':str((1<<18)*f**5*b**4),
            'admitted':(1<<6)*f**3*b**2<1<<104 and(1<<18)*f**5*b**4<1<<192}
        same(price,trial['bill'],'independent literal full-prefix price');need(adds==again,'reverse count')
        trial_checks.append({'destination':trial['destination'],'source':trial['source'],'ADDs':adds,'F':f,'B':b,'admitted':price['admitted']})
    guards(witness['bill']);before=search.bill(parent)
    spec=importlib.util.spec_from_file_location('pinned_bit_geometry',ROOT/INPUTS[2])
    owner=importlib.util.module_from_spec(spec);spec.loader.exec_module(owner)
    W,lab,full,H,C,info=owner.check(candidate)
    need(not H['H2_D_frame0_targets_from_helpers'] and not C['K_equals_D'],'semantic D scope')
    need(all(v for k,v in H.items()if not k.startswith('H2'))and all(v for k,v in C.items()if k!='K_equals_D'),'remaining interface checks')
    profile,paths=I.paid_profile(candidate,W.fdim);oldprofile,oldpaths=I.paid_profile(parent,W.fdim)
    same(profile,oldprofile,'paid profile');same(paths,oldpaths,'all register frame paths')
    same(profile,read(ROOT/INPUTS[3])['word']['local_histogram'],'selected paid profile')
    need(sum(int(r)*n for r,n in profile.items())==5129,'paid rank mass')
    controls=[]
    def reject(name,fn):
        try:fn()
        except ValueError:controls.append(name);return
        raise ValueError('negative control accepted: '+name)
    def boundary(w):need(I.d_rows(w)==expected_d,'wrong dirty D endpoint')
    for name,index in [('helper preparation',527),('helper restoration',639)]:
        bad=copy.deepcopy(candidate);bad['D'].pop(index)
        reject('omit '+name,lambda:boundary(bad))
    bad=copy.deepcopy(candidate);bad['D'][528:639]=copy.deepcopy(parent['D'][527:638])
    reject('omit middle column correction',lambda:boundary(bad))
    reject('reverse helper direction without matching column',lambda:boundary(dict(candidate,D=candidate['D'][:527]+[[0,222+s,[222+d]]]+candidate['D'][528:])))
    reject('first tied saving passes precision',lambda:guards(report['priced_trials'][0]['bill']))
    reject('strict192 equality',lambda:guards({'local_bound':'1','nine_stage_bound':str(1<<192)}))
    reject('omit restoration charge',lambda:need(witness['net_saving']==before['D_ADDs']-witness['bill']['D_ADDs']+1,'paid restoration'))
    missing=load_bytes(canonical(pins));del missing['files'][INPUTS[0]]
    reject('missing source pin',lambda:pins_check(missing))
    reject('duplicate JSON',lambda:load_bytes('{"n":1,"n":2}'))
    reject('nonfinite JSON',lambda:load_bytes('{"n":NaN}'))
    reject('Boolean receipt number',lambda:same({'n':1},{'n':True},'typed JSON'))
    result={'format':'r439-post-helper-shear/1','base_commit':BASE,'seed':3,'source_pins':pins,
       'status':'PASS_R439_POST_HELPER_SHEAR','search':report,'independent_support':geometry,
       'parent_bill':before,'candidate_bill':witness['bill'],'literal_trial_checks':trial_checks,
       'dirty_columns':661,'paid_profile':profile,'paid_rank_mass':5129,'owning_geometry':lab,
       'interface_hypotheses':H,'interface_conclusions':C,'controls_rejected':controls,
       'scope':'one cross-component post-PR967 helper transvection;32 full-price trials; no native or hosted-parent admission or new kappa'}
    return result,candidate


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--write-certificate',action='store_true');a=p.parse_args()
    result,candidate=run()
    if a.write_certificate:
        (HERE/'CERTIFICATE.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n',encoding='utf8')
        (HERE/'candidate.json.gz').write_bytes(gzip.compress(canonical(candidate).encode(),mtime=0))
    else:
        same(result,read(HERE/'CERTIFICATE.json'),'complete certificate mismatch')
        same(candidate,read(HERE/'candidate.json.gz'),'complete candidate mismatch')
    print('PASS_R439_POST_HELPER_SHEAR ADDs=11783->11769 pairs=192282 trials=32 columns=661 controls='+str(len(result['controls_rejected']))+' no_new_kappa')
if __name__=='__main__':main()
