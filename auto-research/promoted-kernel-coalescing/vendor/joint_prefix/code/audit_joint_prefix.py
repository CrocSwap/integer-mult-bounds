#!/usr/bin/env python3
"""Independently audit literal prefix composition and final omission coverage.

OpenAI Codex assistance; Apache-2.0. The literal recipe is derived from Dominik
Scholz's PR571 b7bdc5a8de18fcf418cfb9c7d83a2b1097a5e4a3. Imports no constructor,
search or frame engine. It verifies exact event retention, all fixed fields,
complete regenerated cleanup, prescribed entrances, and135 fresh final omission
cases (103distinct removed-position sets). All checks remain active under -O.
"""
import argparse,copy,gzip,hashlib,json
from fractions import Fraction
from pathlib import Path

COLD={494,495,506,507,518,519,530,531}
FULL=[1<<i for i in range(8,-1,-1)]
def require(test,message):
    if not test:raise ValueError(message)
def read(path):
    raw=path.read_bytes();return json.loads(gzip.decompress(raw)if path.suffix=='.gz'else raw)
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def payload(path):return hashlib.sha256(gzip.decompress(path.read_bytes())).hexdigest()
def inverse(event):
    event=copy.deepcopy(event)
    if event[0]=='add':event[3]=-event[3]
    else:event[2],event[3]=event[3],event[2]
    event[-1]=FULL.copy();return event

def check_word(source,word,recipe,variant):
    require(source.keys()==word.keys(),'Changed word schema')
    require((recipe['old_prefix_length'],recipe['new_prefix_length'])==(69,57),'Wrong prefix lengths')
    require([e[:-1]for e in source['A'][:69]]==recipe['old_scalar_prefix'],'Wrong original scalar prefix')
    previous={tuple(e[:-1]):e for e in source['A'][:69]}
    require(len(previous)==69,'Duplicate original prefix event')
    prefix=[previous[tuple(e)]for e in recipe['new_scalar_prefix']]
    require(len(prefix)==len({tuple(e[:-1])for e in prefix})==57,'Wrong replacement prefix')
    require(word['A']==prefix+source['A'][69:],'Changed prefix frame/scalar or A tail')
    for key in source:
        if key not in('A','cleanup','start_extra','report'):
            require(source[key]==word[key],'Changed fixed word field: '+key)
    entrances=copy.deepcopy(source['start_extra'])
    require(set(recipe['removed_start_frames'])=={'523','525','599','601'},'Wrong removed entrances')
    for key,frame in recipe['removed_start_frames'].items():
        require(entrances[key]==frame,'Wrong old entrance frame');del entrances[key]
    require(entrances==word['start_extra'],'Changed entrance outside recipe')
    cleanup=[inverse(e)for e in reversed(word['A']+word['B'])if not 112<=e[1]<224]
    require(word['cleanup']==cleanup,'Incorrect full regenerated cleanup')
    pin=recipe['variants'][variant];profile={int(r):n for r,n in pin['profile_after'].items()}
    widths={int(r):n for r,n in pin['width_inventory'].items()}
    report=copy.deepcopy(source['report'])
    report.update(local_profile={str(r):n for r,n in profile.items()},local_rank_mass=sum(r*n for r,n in profile.items()),
        entrance_rank=sum((9-r)*n for r,n in widths.items()),entering_helpers=sum(n for r,n in widths.items()if r<9),
        width_inventory={str(r):n for r,n in widths.items()})
    require(report==word['report'],'Changed or stale word report')

def expected_omissions(word,recipe):
    kernels=recipe['kernels'];pivots={k['pivot']for k in kernels}
    prefix_pivots={e[2]for e in word['A'][:57]}
    require(len(kernels)==len(pivots)==48 and len(prefix_pivots)==40,'Wrong kernel coverage')
    require(pivots==prefix_pivots|COLD and not(prefix_pivots&COLD),'Wrong prefix/cold pivot partition')
    occupied=set();expected=[]
    for kernel in kernels:
        require(word['start_extra'][str(kernel['pivot'])]==kernel['frame'],'Kernel entrance frame mismatch')
        positions=[]
        for gate in kernel['gates']:
            q=Fraction(gate['coefficient'])
            event=['add',gate['donor'],kernel['pivot'],-q.numerator,q.denominator,kernel['frame']]
            part,index=gate['part'],gate['index']
            require(part in('A','B')and type(index)is int and 0<=index<len(word[part]),'Bad kernel location')
            require(word[part][index]==event,'Incorrect stored kernel location/frame')
            hits=[(s,i)for s in('A','B')for i,e in enumerate(word[s])if e==event]
            require(hits==[(part,index)]and(part,index)not in occupied,'Nonunique kernel event')
            require(part==('B'if kernel['pivot']in COLD else'A'),'Wrong kernel section')
            occupied.add((part,index));positions.append([part,index])
        require(positions,'Empty kernel')
        for omitted in [[p]for p in positions]+[positions]:
            expected.append(dict(pivot=kernel['pivot'],omitted=omitted,forward_rejected=True,reflected_rejected=True))
    require({p for p in occupied if p[0]=='A'}=={('A',i)for i in range(57)},'Incomplete literal prefix coverage')
    require(len(occupied)==87 and len(expected)==135,'Wrong omission coverage')
    require(sum(c['pivot']in COLD for c in expected)==38,'Wrong cold omission coverage')
    require(len({tuple(map(tuple,c['omitted']))for c in expected})==103,'Wrong distinct omitted-position sets')
    return expected

def bind_controls(control,expected,digest):
    require(control['status']=='PASS_EXACT_MULTICUT_KERNEL_OMISSION_CONTROLS','Wrong omission status')
    require(control['word_sha256']==digest,'Stale omission word binding')
    require(control['columns_each_orientation']==728 and control['correct_compensation_frozen']is True,
            'Incomplete scalar omission scope')
    require(control['controls']==expected,'Wrong omitted positions or rejection outcomes')

def rejected(name,callback,results):
    try:callback()
    except(ValueError,KeyError,TypeError,IndexError):results.append(name)
    else:raise ValueError('Accepted mutation: '+name)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in('source','word','recipe','kernel-recipes','controls','rank5-controls','promotion','selection','out'):
        parser.add_argument('--'+name,type=Path,required=True)
    parser.add_argument('--variant',choices=('eightcold','width7'),required=True)
    args=parser.parse_args();source,word,recipe=map(read,(args.source,args.word,args.recipe))
    pin=recipe['variants'][args.variant]
    require(payload(args.source)==pin['input_content_sha256'],'Changed source payload')
    require(payload(args.word)==pin['output_content_sha256'],'Changed final payload')
    check_word(source,word,recipe,args.variant)
    kernels,control=read(args.kernel_recipes),read(args.controls)
    require(kernels['provenance']['word_content_sha256']==pin['output_content_sha256'],'Wrong omission recipe payload')
    expected=expected_omissions(word,kernels);wordsha=sha(args.word)
    bind_controls(control,expected,wordsha)
    rank5=read(args.rank5_controls);promotion=read(args.promotion)
    pivots=[p for c in promotion['changes']for p in c['pivots']]
    require(len(pivots)==len(set(pivots))==8,'Wrong rank-five pivots')
    require(rank5['status']=='PASS_EXACT_RATIONAL_FORWARD_AND_INVERSE_TRANSPOSE'and
            rank5['word_sha256']==wordsha and rank5['selection_sha256']==sha(args.selection),'Stale rank-five controls')
    require(rank5['columns_each_orientation']==728 and rank5['kernel_pivots']==8 and
            rank5['controls']=={str(p):'REJECTED_OMITTED_PROMOTED_POSTCENTER_KERNEL_CORRECTION'for p in pivots},
            'Incomplete rank-five controls')
    require(rank5['compensations']==control['compensation_entries'],'Compensation count mismatch')
    controls=[]
    for name in('prefix_scalar','prefix_frame','A_tail','B_suffix','extra_entrance','cleanup_order'):
        mutant=copy.deepcopy(word)
        if name=='prefix_scalar':mutant['A'][0][3]+=1
        elif name=='prefix_frame':mutant['A'][0][-1]=[]
        elif name=='A_tail':mutant['A'][57],mutant['A'][58]=mutant['A'][58],mutant['A'][57]
        elif name=='B_suffix':next(e for e in mutant['B']if e[0]=='add')[3]+=1
        elif name=='extra_entrance':mutant['start_extra']['224']=[1]
        else:mutant['cleanup'].reverse()
        rejected(name,lambda:check_word(source,mutant,recipe,args.variant),controls)
    for name in('stale_word','missing_case','duplicate_case','wrong_omitted_position','accepted_reflection','unfrozen_compensation'):
        mutant=copy.deepcopy(control)
        if name=='stale_word':mutant['word_sha256']='0'*64
        elif name=='missing_case':mutant['controls'].pop()
        elif name=='duplicate_case':mutant['controls'][-1]=copy.deepcopy(mutant['controls'][0])
        elif name=='wrong_omitted_position':mutant['controls'][0]['omitted'][0][1]+=1
        elif name=='accepted_reflection':mutant['controls'][0]['reflected_rejected']=False
        else:mutant['correct_compensation_frozen']=False
        rejected(name,lambda:bind_controls(mutant,expected,wordsha),controls)
    for name in('wrong_recipe_index','wrong_recipe_frame','missing_recipe_kernel'):
        mutant=copy.deepcopy(kernels)
        if name=='wrong_recipe_index':mutant['kernels'][0]['gates'][0]['index']+=1
        elif name=='wrong_recipe_frame':mutant['kernels'][0]['frame']=[]
        else:mutant['kernels'].pop()
        rejected(name,lambda:expected_omissions(word,mutant),controls)
    require(len(controls)==15,'Missing controls')
    result=dict(status='PASS_INDEPENDENT_LITERAL_PREFIX_AND_FINAL_KERNEL_COVERAGE',variant=args.variant,
        source_sha256=sha(args.source),word_sha256=wordsha,source_content_sha256=payload(args.source),
        word_content_sha256=payload(args.word),recipe_sha256=sha(args.recipe),
        kernel_recipe_sha256=sha(args.kernel_recipes),omission_receipt_sha256=sha(args.controls),
        rank5_receipt_sha256=sha(args.rank5_controls),promotion_sha256=sha(args.promotion),selection_sha256=sha(args.selection),
        auditor_sha256=sha(Path(__file__)),old_prefix=69,new_prefix=57,
        unchanged_retained_event_frames=True,unchanged_A_tail_and_B=True,exact_regenerated_cleanup=True,
        removed_start_registers=sorted(map(int,recipe['removed_start_frames'])),prefix_kernels=40,cold_kernels=8,
        unique_kernel_gates=87,omission_cases=135,distinct_omitted_position_sets=103,cold_omission_cases=38,
        rank5_omission_cases=8,negative_controls_rejected=controls,
        scope='Independent literal construction and exact fresh receipt coverage. Forty current prefix kernels '
              'replace the old44; no obsolete44-kernel omission claim. Both scalar orientations are replayed '
              'by the full kernel auditor with correct compensation frozen. Full native frame, wrapper, phase, '
              'physical owner, invoice and moment admission remain separate.')
    args.out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(result['status'],args.variant,'mutants',len(controls))

if __name__=='__main__':main()
