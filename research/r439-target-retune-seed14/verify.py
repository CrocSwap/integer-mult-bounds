"""Independent finite census, dirty-state replay and exact resource accounting.

No search.py imports. Set-valued matrices and literal ADD/COPY/ERASE replay.
Prepared for @woklerx with substantial OpenAI Codex assistance, Apache-2.0.
PR915/926 bitplane, PR967 theon199 and PR589/555 are credited in NOTICE.md.
"""
import argparse
import ast
import copy
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import struct
import subprocess
import sys
import tempfile

sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
BASE='2921874911956718fcaaaf9396fe8267b3cfa9f0'
ORIGINAL='research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz'
PARENT='research/r439-helper-stars-seed19/candidate.json.gz'
PCERT='research/r439-helper-stars-seed19/CERTIFICATE.json'
TCERT='research/r439-target-compensation/CERTIFICATE.json'
OWNER='research/e8-bit-p111-tuned/code/xcheck_p.py'
EXPORT='research/e8-bit-carrier-skeleton/code/bit/export_records.py'
FORMULA='research/e8-bit-p111-tuned/vendor/pr510/e8-r480-nine-stage/vendor/e8-r715-eleven-stage-whole/code/global_k.py'
CHARGE='research/e8-bit-p111-tuned/tune/EXPECTED.json'
SOURCES={ORIGINAL,PARENT,PCERT,TCERT,OWNER,EXPORT,FORMULA,CHARGE,
         'research/r439-helper-stars-seed19/README.md',
         'research/r439-helper-stars-seed19/PROOF.md',
         'research/r439-helper-stars-seed19/NOTICE.md'}


def need(value,reason):
    if not value:raise ValueError(reason)


def pairs(items):
    result={}
    for key,value in items:
        need(key not in result,'duplicate JSON key')
        result[key]=value
    return result


def load(path):
    path=Path(path)
    raw=path.read_bytes()
    if path.suffix=='.gz':raw=gzip.decompress(raw)
    return parse(raw)


def parse(raw):
    return json.loads(raw,object_pairs_hook=pairs,parse_constant=lambda value:need(False,'nonfinite JSON'))


def identity(certificate):
    need(type(certificate['seed']) is int and certificate['seed']==14 and certificate['base_commit']==BASE
         and certificate['format']=='r439-target-retune/1','certificate identity')


def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()


def same(a,b,reason):
    need(canonical(a)==canonical(b),reason)


def pins(manifest):
    need(manifest['base_commit']==BASE and set(manifest['files'])==SOURCES,'exact source inventory')
    for name,digest in manifest['files'].items():
        raw=(ROOT/name).read_bytes()
        if not name.endswith('.gz'):raw=raw.replace(b'\r\n',b'\n')
        need(hashlib.sha256(raw).hexdigest()==digest,'source digest: '+name)


def instructions(word,only_d=False):
    out=[]
    for section in ('D',) if only_d else ('D','A'):
        for _,d,sources in word[section]:
            out.extend(('add',d,s) for s in sources)
    if only_d:return out
    for j,center in enumerate(word['ret']):
        out.append(('copy',661,center))
        for i,sources in enumerate(word['scatter']):
            if j in sources:out.append(('add',111+i,661))
        out.append(('erase',661,center))
    for section in ('B','C'):
        for _,d,sources in word[section]:out.extend(('add',d,s) for s in sources)
    return out


def evaluate(word,reverse=False,only_d=False,positive=False):
    values=[1]*662 if positive else [{i} for i in range(661)]+[set()]
    maximum=1
    stream=instructions(word,only_d)
    for kind,d,s in reversed(stream) if reverse else stream:
        if reverse and kind!='add':kind='erase' if kind=='copy' else 'copy'
        if kind=='add':
            if positive:values[d]+=values[s]
            else:values[d].symmetric_difference_update(values[s])
        elif kind=='copy':
            if positive:values[d]=values[s]
            else:
                need(not values[d],'copy destination empty')
                values[d]=set(values[s])
        else:
            if positive:values[d]=0
            else:
                need(values[d]==values[s],'copy value restored before erase')
                values[d]=set()
        if positive:maximum=max(maximum,values[d])
    if positive:return maximum
    need(not values[-1],'private copy cleanup')
    return values[:-1]


def bill(word):
    f,b=evaluate(word,positive=True),evaluate(word,reverse=True,positive=True)
    return {'ADDs':sum(kind=='add' for kind,_,_ in instructions(word)),
            'D_ADDs':sum(len(g[2]) for g in word['D']),'F':f,'B':b,
            'local':str(64*f**3*b**2),'nine_stage':str((1<<18)*f**5*b**4)}


def guard(receipt):
    return int(receipt['local'])<1<<104 and int(receipt['nine_stage'])<1<<192


def recipe(original,parent):
    hcert,tcert=load(ROOT/PCERT),load(ROOT/TCERT)
    h=[[0,222+s['a'],[222+s['b']]] for s in hcert['steps']]
    e=[[0,111+s['destination'],[111+s['source']]] for s in tcert['steps']]
    need(len(h)==221 and len(e)==306,'frozen preparation lengths')
    matrix=[set() for _ in range(111)]
    for frame,d,src in original['D']:
        need(frame==0 and 111<=d<222 and all(222<=s<661 for s in src),'original direct D')
        matrix[d-111].symmetric_difference_update(s-222 for s in src)
    for _,d,src in e:matrix[d-111].symmetric_difference_update(matrix[src[0]-111])
    before_helper=[set(row) for row in matrix]
    for _,d,src in reversed(h):
        for row in matrix:
            if d-222 in row:row.symmetric_difference_update({src[0]-222})
    middle=[[0,111+i,[222+j for j in sorted(row)]] for i,row in enumerate(matrix)]
    same(h+e+middle+e[::-1]+h[::-1],parent['D'],'rederive PR967 mixed matrix and full D')
    same({k:v for k,v in original.items() if k!='D'}, {k:v for k,v in parent.items() if k!='D'},'parent non-D fields')
    return h,e,matrix,before_helper


def trial(parent,h,e,matrix,a,b):
    transformed=[set(row) for row in matrix]
    transformed[a].symmetric_difference_update(transformed[b])
    middle=[[0,111+i,[222+j for j in sorted(row)]] for i,row in enumerate(transformed)]
    q=[[0,111+a,[111+b]]]
    result=dict(parent)
    result['D']=h+e+q+middle+q+e[::-1]+h[::-1]
    return result


def formula_check():
    syntax=ast.parse((ROOT/FORMULA).read_text(encoding='utf-8'))
    assignments=[node.value for node in ast.walk(syntax) if isinstance(node,ast.Assign)
                 and any(isinstance(t,ast.Name) and t.id=='prefix' for t in node.targets)]
    need(len(assignments)==1 and ast.dump(assignments[0])==ast.dump(ast.parse('(1 << nb) * cf ** (K + 1) * cb ** K',mode='eval').body),'staged precision source formula')
    condition=ast.dump(ast.parse('nb == 6 * (K - 1)',mode='eval').body)
    need(any(isinstance(node,ast.Compare) and ast.dump(node)==condition for node in ast.walk(syntax)),'bridge exponent')
    need(load(ROOT/CHARGE)['nine']['bit']['charged_prefix_bits']==192,'staged precision charge')


def source_and_records(parent,candidate):
    spec=importlib.util.spec_from_file_location('owning_r439_checker',ROOT/OWNER)
    owner=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(owner)
    source={}
    for name,word in (('parent',parent),('candidate',candidate)):
        _,labels,full,hypotheses,conclusions,info=owner.check(word)
        need({k for k,v in hypotheses.items() if not v}=={'H2_D_frame0_targets_from_helpers'},'expected syntactic H2 limitation')
        need({k for k,v in conclusions.items() if not v}=={'K_equals_D'},'expected literal K limitation')
        source[name]={'labels':labels,'full':full,'hypotheses':hypotheses,'conclusions':conclusions,'info':info}
    records={}
    with tempfile.TemporaryDirectory(prefix='verify-',dir=HERE) as work:
        need(Path(work).resolve().is_relative_to(HERE),'temporary directory containment')
        for name,path in (('parent',ROOT/PARENT),('candidate',HERE/'candidate.json.gz')):
            out=Path(work)/name
            result=subprocess.run([sys.executable,'-I','-B',str(ROOT/EXPORT),str(path),str(out)],capture_output=True,text=True)
            need(result.returncode==0,'unchanged exporter failed: '+result.stderr)
            records[name]=list(struct.iter_unpack('<6i',(out/'249-records.bin').read_bytes()))
        same([r for r in records['parent'] if r[0]!=1],[r for r in records['candidate'] if r[0]!=1],'all MOVE COPY ERASE records unchanged')
    summary={name:{'records':len(rs),'ADDs':sum(r[0]==1 for r in rs),'MOVE':sum(r[0]==0 for r in rs),
                    'COPY':sum(r[0]==2 for r in rs),'ERASE':sum(r[0]==3 for r in rs),
                    'rank_mass':sum(r[4] for r in rs if r[0]==0)+sum(r[5] for r in rs if r[0]==2)}
             for name,rs in records.items()}
    need(summary['candidate']['rank_mass']==5129,'paid rank mass')
    return source,summary


def run():
    manifest=load(HERE/'SOURCES.json')
    pins(manifest)
    original,parent,candidate=load(ROOT/ORIGINAL),load(ROOT/PARENT),load(HERE/'candidate.json.gz')
    certificate=load(HERE/'CERTIFICATE.json')
    identity(certificate)
    h,e,matrix,before_helper=recipe(original,parent)
    baseline=bill(parent)
    same(baseline,certificate['baseline'],'independent parent bill')
    census,nominees=[],[]
    for a in range(111):
        for b in range(111):
            if a==b:continue
            gain=len(matrix[a])-len(matrix[a]^matrix[b])-2
            tie=hashlib.sha256(('14:'+str(a)+':'+str(b)).encode()).hexdigest()
            census.append([a,b,gain,tie])
            if gain>0:
                receipt=bill(trial(parent,h,e,matrix,a,b))
                need(receipt['ADDs']==baseline['ADDs']-gain,'both target operations paid')
                nominees.append({'a':a,'b':b,'gain':gain,'tie':tie,'bill':receipt,'admitted':guard(receipt)})
    nominees.sort(key=lambda row:(-row['gain'],row['tie']))
    need(len(census)==certificate['ordered_pairs']==12210,'complete ordered-pair domain')
    need(hashlib.sha256(canonical(census)).hexdigest()==certificate['census_sha256'],'all directed scores and ties')
    same(nominees,certificate['nominees'],'independent full nominee pricing')
    accepted=[row for row in nominees if row['admitted']]
    need(len(nominees)==certificate['positive_gain_pairs']==12 and len(accepted)==certificate['admitted_positive_pairs']==10,'positive and guarded census')
    same(accepted[0],certificate['selected'],'best admitted one-insertion word')
    a,b=accepted[0]['a'],accepted[0]['b']
    need((a,b,accepted[0]['gain'])==(24,35,3),'selected unique best')
    same(trial(parent,h,e,matrix,a,b),candidate,'independent complete candidate construction')
    candidate_bill=bill(candidate)
    need(candidate_bill['ADDs']==11780 and candidate_bill['D_ADDs']==5560 and guard(candidate_bill),'complete candidate cost and guards')
    expected=[{i,i-111} if 111<=i<222 else {i} for i in range(661)]
    boundary=evaluate(original,only_d=True)
    for word in (parent,candidate):
        for reverse in (False,True):
            need(evaluate(word,reverse,only_d=True)==boundary,'arbitrary-dirt D boundary')
            need(evaluate(word,reverse)==expected,'all 661 full endpoint columns')
    formula_check()
    controls=[]
    def rejected(label,fn):
        try:fn()
        except ValueError:controls.append(label)
        else:raise ValueError('accepted negative control: '+label)
    for name,index in (('omit target preparation',527),('omit target restoration',639)):
        changed=copy.deepcopy(candidate)
        changed['D'].pop(index)
        rejected(name,lambda:need(evaluate(changed,only_d=True)==boundary,'dirty target boundary'))
    changed=copy.deepcopy(candidate)
    changed['D'][528+a]=copy.deepcopy(parent['D'][527+a])
    rejected('omit middle row transformation',lambda:need(evaluate(changed,only_d=True)==boundary,'mixed middle boundary'))
    changed=copy.deepcopy(candidate)
    changed['D'][527]=[0,111+b,[111+a]]
    rejected('transpose target preparation',lambda:need(evaluate(changed,only_d=True)==boundary,'target orientation'))
    changed=copy.deepcopy(candidate)
    incorrect=matrix[a]^before_helper[b]
    changed['D'][528+a][2]=[222+j for j in sorted(incorrect)]
    rejected('use donor before helper mixing',lambda:need(evaluate(changed,only_d=True)==boundary,'coupled mixed term'))
    rejected('omit both gate charges',lambda:need(len(matrix[a])-len(matrix[a]^matrix[b])==accepted[0]['gain'],'paid saving'))
    for nominee in nominees:
        if not nominee['admitted']:
            need(int(nominee['bill']['local'])<1<<104,'rejected candidate still local-admissible')
            rejected('nine-stage overrun '+str((nominee['a'],nominee['b'])),lambda:need(guard(nominee['bill']),'strict staged bound'))
    rejected('strict guard equality',lambda:need(guard({'local':'1','nine_stage':str(1<<192)}),'strict guard'))
    badpins=copy.deepcopy(manifest)
    del badpins['files'][PARENT]
    rejected('removed source pin',lambda:pins(badpins))
    badpins=copy.deepcopy(manifest)
    badpins['files'][PARENT]='0'*64
    rejected('changed source hash',lambda:pins(badpins))
    badcert=copy.deepcopy(certificate)
    badcert['seed']=14.0
    rejected('noninteger certificate seed',lambda:identity(badcert))
    rejected('duplicate JSON key',lambda:parse('{"seed":14,"seed":15}'))
    rejected('nonfinite JSON',lambda:parse('{"bad":NaN}'))
    neutral=copy.deepcopy(candidate)
    neutral['D'][:0]=[[0,111,[112]],[0,111,[112]]]
    need(evaluate(neutral,only_d=True)==boundary and bill(neutral)['ADDs']==11782,'neutral pair restores dirt and costs two')
    source,records=source_and_records(parent,candidate)
    need(records['candidate']['ADDs']==candidate_bill['ADDs'],'exported ADD bill')
    return {'status':'PASS_R439_TARGET_RETUNE_S14','source_pins':manifest,'census_pairs':12210,
            'positive_pairs':12,'admitted_positive_pairs':10,'chosen':[a,b],
            'baseline':baseline,'candidate':candidate_bill,'middle_row_before':sorted(matrix[a]),
            'middle_row_after':sorted(matrix[a]^matrix[b]),
            'pre_helper_gain_of_selected_step':len(before_helper[a])-len(before_helper[a]^before_helper[b])-2,
            'full_columns':661,'word_directions':4,'boundary':'semantic D; original syntactic H2 and literal K extraction remain false',
            'owning_source_checks':source,'exported_records':records,'negative_controls':controls,
            'positive_controls':['neutral target pair preserves arbitrary dirt and costs two ADDs'],
            'limitations':'Local finite construction only. No native multistage, hosted supplier, new recursive profile or new kappa claim.'}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-receipt',action='store_true')
    args=parser.parse_args()
    result=run()
    if args.write_receipt:(HERE/'EXPECTED.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    else:same(result,load(HERE/'EXPECTED.json'),'complete receipt')
    print('PASS_R439_TARGET_RETUNE_S14 pairs=12210 positive=12 admitted=10 ADDs=11783->11780 F=72847 B=10394084 columns=661 controls='+str(len(result['negative_controls'])))


if __name__=='__main__':main()
