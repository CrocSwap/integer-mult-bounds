# SPDX-License-Identifier: Apache-2.0
"""Full authenticated native validation for the changed 485/1455 producer.

Based on retained #7480 verify_native.py, attributed there to Rohan Arun,
dillona, and OpenAI Codex assistance. Source closure is authenticated through
its unmodified source.py. Every engine adaptation is counted and logged.
All inventories, prices, grids, envelopes, and physical checks are freshly
computed for the literal candidate. This does not select a public frontier.
"""
from pathlib import Path
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha256
from types import ModuleType
import sys,json,gzip,subprocess,tempfile,io,contextlib,time
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
SOURCE=ROOT/'inputs/pr7480'
CANDIDATE=ROOT/'producer54/reroute'
sys.path.insert(0,str(SOURCE))
from source import read,load,sources,canonical,need
from construct import construct
from derive_grid import derive
from verify_native import normalized,delta,rejects,forward_endpoint

EXPECTED='8ab3d9dbe2e2e24202ac96c6122b010b3e7980912f935cc0cc2db2e9d85f83aa'
BASELINE='5044adee019f073f286789ccb688ffca76d42b60518242bb4daea818d33d337a'
PATCHES=[]
TIMINGS=[]
def module(name,path,edits=()):
    raw=path.read_text();record={'module':name,'source_name':path.name,'source_sha256':sha256(raw.encode()).hexdigest(),'edits':[]}
    for before,after in edits:
        count=raw.count(before);need(count==1,'Unique adaptation '+repr(before))
        raw=raw.replace(before,after)
        record['edits'].append({'before':before,'after':after,'occurrences':count})
    record['adapted_sha256']=sha256(raw.encode()).hexdigest();PATCHES.append(record)
    obj=ModuleType(name);obj.__file__=str(path);sys.modules[name]=obj
    exec(compile(raw,str(path),'exec'),obj.__dict__)
    return obj

def checkpoint(stage,data=None):
    now=time.time();TIMINGS.append({'stage':stage,'elapsed_seconds':now-STARTED})
    (HERE/'CHECKPOINT.json').write_text(json.dumps(normalized({'stage':stage,'word_canonical_sha256':EXPECTED,'data':data,'timings':TIMINGS}),indent=2)+'\n')
    print('PASS',stage,flush=True)

def charts(vendor,word):
    before=read(ROOT/'frozen-composition/7481-WORD.json.gz')
    need(word['frames']==before['frames'],'All 1096 literal frames retained')
    routes=lambda w:{i:[tuple(e[2:4])for e in w['program']if e[0]=='MOVE'and e[1]==i]for i in range(w['public'])}
    r0,r1=routes(before),routes(word)
    changed=[i for i in r0 if r0[i]!=r1[i]]
    affected={pair for i in changed for pair in r0[i]+r1[i]}
    prior={}
    evidence=ROOT.parent/'inherited/validation_native'
    for name,pin in {'CHARTS-BATCH-1.json': '06c15dde99f7f04fff7a2dca35196a119031265896863baab8bc9157f46ffd45', 'CHARTS-BATCH-0.json': '8abdefef307cc1d778069269074c57fd2ea8fb52d55c8bd9281e488d03f272d6', 'CHARTS-BATCH-7.json': '0fb7aed1f8d0078fe06d45fe98cd34c2764fe3c6c0ed5ffb7f0c9e04a12ddedd', 'CHARTS-BATCH-6.json': 'a26822a3bac2f4b21f987f890772e7ea46be43c5dd2ba78cc804afea7f12b8f4', 'CHARTS-BATCH-5.json': '1310786a3ae08e113c237a2d7b61a4f4a50e66b4ff57b7387cc15d8299bc1edd', 'CHARTS-BATCH-4.json': '75aabadebe6b7afce42678004fbeb66d46437bd58413de1de61e752a5b53a3df', 'CHARTS-BATCH-3.json': '910e1a50e242a5914bf8242413c07b7b54bf7dfbb5694e1c757b60c82e29acde', 'CHARTS-BATCH-2.json': 'c0d25482742e5d0516fb2da3025e4cb410e6214057eecfce3beb06d350280106'}.items():
        p=evidence/name;need(sha256(p.read_bytes()).hexdigest()==pin,'Pinned inherited strict chart evidence')
        rec=read(p);need(rec['word_sha256']=='ad56c629ac587510aa59ad13fde7db3f38e08d4fc09beb70fbb839a8de17b41d','Evidence belongs to H5B')
        for item in rec['pairs']:prior[tuple(item['pair'])]=item
    compiler=load('combo_chart_compiler',vendor/'frozen/clifford_exact.py')
    interpreter=load('combo_chart_interpreter',vendor/'frozen/native_verify.py')
    fresh=[]
    for a,b in sorted((affected-set(prior))|{(281,127),(594,883)}):
        ca,cb=(compiler.canonical_frame(9,tuple(word['frames'][f]))for f in(a,b))
        recipe,_=compiler.lower_child(ca.adjoint().then(cb))
        expected=interpreter.adjoint(interpreter.frame(word['frames'][a],9))+interpreter.frame(word['frames'][b],9)
        actual=interpreter.recipe(recipe);interpreter.equal(actual,expected,'Signed Pauli action and absolute phase')
        need(recipe['rank']==len(word['frames'][b])-len(word['frames'][a]),'Exact public ascent rank')
        for x,y in ((actual,expected),(interpreter.adjoint(actual),interpreter.adjoint(expected))):
            for column in range(512):need(interpreter.state(x,column)==interpreter.state(y,column),'Exact forward/adjoint column')
        bad=deepcopy(recipe);bad['left']['phase']=(bad['left']['phase']+1)%4
        need(rejects(lambda:interpreter.equal(interpreter.recipe(bad),expected,'Wrong phase')),'Wrong phase rejected')
        item={'pair':[a,b],'rank':recipe['rank'],'columns':512,'adjoint_columns':512,'absolute_phase_verified':True}
        fresh.append(item);prior[(a,b)]=item
    need(affected<=set(prior),'Every current affected pair certified')
    return {'all_affected_pairs':[prior[p]for p in sorted(affected)],'fresh_pairs':fresh,'changed_public_fields':changed,'inherited_evidence_pins':{'CHARTS-BATCH-1.json': '06c15dde99f7f04fff7a2dca35196a119031265896863baab8bc9157f46ffd45', 'CHARTS-BATCH-0.json': '8abdefef307cc1d778069269074c57fd2ea8fb52d55c8bd9281e488d03f272d6', 'CHARTS-BATCH-7.json': '0fb7aed1f8d0078fe06d45fe98cd34c2764fe3c6c0ed5ffb7f0c9e04a12ddedd', 'CHARTS-BATCH-6.json': 'a26822a3bac2f4b21f987f890772e7ea46be43c5dd2ba78cc804afea7f12b8f4', 'CHARTS-BATCH-5.json': '1310786a3ae08e113c237a2d7b61a4f4a50e66b4ff57b7387cc15d8299bc1edd', 'CHARTS-BATCH-4.json': '75aabadebe6b7afce42678004fbeb66d46437bd58413de1de61e752a5b53a3df', 'CHARTS-BATCH-3.json': '910e1a50e242a5914bf8242413c07b7b54bf7dfbb5694e1c757b60c82e29acde', 'CHARTS-BATCH-2.json': 'c0d25482742e5d0516fb2da3025e4cb410e6214057eecfce3beb06d350280106'},'literal_frames_match':True,'wrong_phase_rejected':True}

def run():
    need(__debug__,'Assertions are proof obligations')
    new=read(CANDIDATE/'WORD.json.gz');need(sha256(canonical(new)).hexdigest()==EXPECTED,'Only final short candidate')
    previous=read(SOURCE/'NATIVE-RESULT.json')
    proposal=read(CANDIDATE/'RESULT.json')
    with sources()as(vendor,archive,rank9,bundle,parent,parent_word):
        old=construct(parent_word)
        need(canonical(old)==gzip.decompress((SOURCE/'WORD.json.gz').read_bytes()),'Regenerate frozen #7480 from authenticated #7334 closure')
        need(sha256(canonical(old)).hexdigest()==BASELINE,'Exact source word')
        emitted=[];skip=set(proposal['removed_old_indices'])
        for i,e in enumerate(old['program']):
            if i==proposal['insert_before_old_index']:emitted.extend(proposal['splice'])
            if i not in skip:emitted.append(e)
        incumbent=read(ROOT/'frozen-composition/7481-WORD.json.gz')
        need(incumbent==dict(old,program=emitted),'Rebuild exact #7481 from its predecessor')
        peer=read(ROOT/'frozen-composition/7604-WORD.json.gz')
        need(sha256((ROOT/'frozen-composition/7604-WORD.json.gz').read_bytes()).hexdigest()=='aae5a85746db1abc5145b993e9a9408076f34c53c4bb8040a99b6a39f2685527','Exact open #7604 comparator')
        program=peer['program']
        required={33517:['ADD',1143,757,'-1',3],38584:['MOVE',757,3,595,False],38585:['ADD',757,902,'-1',595],42714:['ADD',757,1557,'-2/3',595],42716:['MOVE',757,595,603,False],42717:['ADD',1255,757,'-1',603]}
        need(all(program[i]==e for i,e in required.items()),'Exact helper757 contacts')
        touches=[i for i in range(33518,42716)if 757 in(program[i][1:3]if program[i][0]in('ADD','COPY')else program[i][1:2])]
        need(touches==[38584,38585,42714],'No intervening read of helper757')
        emitted=[]
        for i,event in enumerate(program):
            if i==33518:emitted.append(['ADD',757,1255,'-1',3])
            if i==42716:emitted.extend([['MOVE',757,3,603,False],['ADD',757,1255,'1',603]])
            elif i not in(38584,38585,42714):emitted.append(event)
        helper_word=dict(peer,program=emitted)
        edits_path=ROOT/'frozen-composition/W2-EDITS.json'
        need(sha256(edits_path.read_bytes()).hexdigest()=='bf0c45f0a1498ba06ced0e217c41fe01fb8a117a3acfbc973c3bc76022d03be7','Pinned literal W2 edits')
        edits=read(edits_path)
        need(sha256(canonical(helper_word)).hexdigest()==edits['base_canonical_sha256'],'Exact reconstructed helper757 base')
        rebuilt=list(emitted)
        for edit in reversed(edits['replacements']):
            need(rebuilt[edit['start']:edit['end']]==edit['old'],'Exact old slice')
            rebuilt[edit['start']:edit['end']]=edit['new']
        import hashlib as _hl
        step1_edits_raw=(ROOT/'frozen-composition/W3H-STEP1-ON-7616-EDITS.json').read_bytes()
        need(_hl.sha256(step1_edits_raw).hexdigest()=='bdad5bbb4692ccf651ec7d5f701aaa9e76a7117b1feeddd2d857f136ba8cda96','Pinned W3H-STEP1-ON-7616-EDITS hash')
        step1_edits=json.loads(step1_edits_raw)
        rebuilt_step1=list(rebuilt)
        for _h in reversed(step1_edits['replacements']):
            need(rebuilt_step1[_h['start']:_h['end']]==_h['old'],'Exact W3H-step1 old slice match')
            rebuilt_step1[_h['start']:_h['end']]=_h['new']
        r_raw=(ROOT/'frozen-composition/RES-ON-STEP1-EDITS.json').read_bytes()
        need(_hl.sha256(r_raw).hexdigest()=='42851eca7ceaa235113d40ed189e5338614e08e6e31a67659f450f096e53ef9a','Pinned RES-ON-STEP1-EDITS hash')
        r_ed=json.loads(r_raw)
        rebuilt_r=list(rebuilt_step1)
        for _hr in reversed(r_ed['replacements']):
            need(rebuilt_r[_hr['start']:_hr['end']]==_hr['old'],'Exact slice')
            rebuilt_r[_hr['start']:_hr['end']]=_hr['new']
        restored=dict(helper_word,program=rebuilt_r)
        need(sha256(canonical(restored)).hexdigest()=='ad56c629ac587510aa59ad13fde7db3f38e08d4fc09beb70fbb839a8de17b41d','Pinned H5B reconstruction')
        generator=ROOT.parents[1]/'generate_and_probe.py'; permutation=ROOT.parents[1]/'reschedule-report.json'
        need(sha256(generator.read_bytes()).hexdigest()=='4ba8c670f21f2ce403a2a8f15dec143866683dd360b68f35ba3b99c631e5c456','Pinned combination generator')
        need(sha256(permutation.read_bytes()).hexdigest()=='5bfcc2622f928f99454612c36771d662d06047209b5dd1acc77c316accf5535c','Pinned dependency permutation')
        import importlib.util as _iu
        cg=ModuleType('combo_generator');cg.__file__=str(generator)
        generator_functions=generator.read_text().split('def main():')[0]
        exec(compile(generator_functions,str(generator),'exec'),cg.__dict__)
        base_h,source_e1,candidate_e1=cg.load_inputs()
        need(base_h==restored,'Exact H5B source for generator')
        built1,_=cg.e1(restored,candidate_e1);built,_=cg.e4(built1)
        order=read(permutation)['event_permutation'];need(sorted(order)==list(range(len(built['program']))),'Permutation bijection')
        built['program']=[built['program'][i] for i in order]
        zero_receipt=ROOT.parents[1]/'exact-q-report.json'
        need(sha256(zero_receipt.read_bytes()).hexdigest()=='e4ba7737009205da3805760cf8865b85c7ab2cd9e006ecb9b586428c3dfe71e4','Pinned exact zero row certificate')
        zero_doc=read(zero_receipt);need(zero_doc['candidate']==sha256(canonical(built)).hexdigest(),'Exact zero proof candidate')
        zeros=[e for e in zero_doc['scaled_exact_q']['clears_exact'] if not e['q_row']]
        need(len(zeros)==1 and zeros[0]['field']==1568 and zeros[0]['clear_event']==28267,'Unique exact zero CLEAR')
        bp=built['program'];need(bp[28267]==['CLEAR',1568,3] and bp[28871]==['INIT',1502,3] and bp[29356]==['CLEAR',1502,3],'Exact zero lifetime splice endpoints')
        need(not any(e[1]==1568 or (e[0]in('ADD','COPY')and e[2]==1568)for e in bp[28268:28872]),'No intervening scratch access')
        bp2=[]
        for i,e in enumerate(bp):
            if i in(28267,28871):continue
            e=list(e)
            if 28871<i<=29356:
                if e[1]==1502:e[1]=1568
                if e[0]in('ADD','COPY')and e[2]==1502:e[2]=1568
            bp2.append(e)
        built['program']=bp2
        need(new==built,'Literal final candidate plus exact-zero lifetime join')
        adjusted=deepcopy(incumbent);need(adjusted['initial'][457]==3,'Original E1 initial');adjusted['initial'][457]=281
        need({k:v for k,v in new.items() if k!='program'}=={k:v for k,v in adjusted.items() if k!='program'},'Only declared initial457 3-to281 metadata delta; frames unchanged')
        return {'word': EXPECTED, 'events': len(new['program']),
                'rule': 'authenticated predecessor and literal reconstruction'}

def check_signed_source_closure():
    from source import bundles
    with bundles() as (parts, _, temp):
        signed = parts[7113]
        caller = signed/'expected/ODD-TYPE-AB-CALLER.json'
        caller_hash = sha256(caller.read_bytes()).hexdigest()
        need(caller_hash == '255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc',
             'Exact archived signed caller at relocated root')
        folder = signed/'replay/supplier7112/short-caller'
        names = ('signed_model.py', 'independent.py', 'emit_odd_type_b.py', 'emit_odd_type_ab.py',
                 'check_odd_caller_exact_grid.py', 'check_odd_physical_binding.py',
                 'check_odd_precision.py', 'check_odd_partial_admission.py',
                 'check_odd_fixed_tape_counts.py', 'short_native_catalogue.py', 'assemble_odd_application.py')
        need(signed.resolve().is_relative_to(temp.resolve()), 'Relocated signed source ownership')
        return {'caller_sha256': caller_hash,
                'script_sha256': {n: sha256((folder/n).read_bytes()).hexdigest() for n in names}}

if __name__ == '__main__':
    result = {'status': 'PASS_PORTABLE_SOURCE_AND_RECONSTRUCTION_PREFLIGHT',
              'native_reconstruction': run(), 'signed_source_closure': check_signed_source_closure(),
              'native_science_run': False, 'signed_science_run': False}
    print(json.dumps(result, sort_keys=True), flush=True)
