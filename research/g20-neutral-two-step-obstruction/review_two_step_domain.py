#!/usr/bin/env python3
"""Independent brute-interval domain and set-row normalization review.

Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
Imports no construction or prefix-replay implementation. No invoice re-audit.
"""
import argparse
from collections import Counter, defaultdict
from copy import deepcopy
import gzip
from hashlib import sha256
import json
from pathlib import Path

WORD_SHA='8dd441fdb9c8923df06eb5ebfda37d03e4539f2305763e688d8c7025d196c4b1'
ONE_STEP_SHA='ed99ab025914795eb07531cf9b83f213e3442ab965dac4ad7354115446fea948'

def require(ok,message):
    if not ok:raise ValueError(message)

def read(path):
    raw=path.read_bytes()
    return json.loads(gzip.decompress(raw) if raw[:2]==b'\x1f\x8b' else raw)

def expand(records,left,right):
    require(0<=left<right<len(records),'ordered outer indices')
    require(records[left][0]==records[right][0]=='ADD' and records[left][1:3]==records[right][1:3],'matching outer gates')
    a,b=records[left][1:3];extras={}
    for index in range(left+1,right):
        event=records[index]
        if event[0] in('ERASE','INIT'):
            if event[1] in(a,b):return None,None
            continue
        require(event[0]=='ADD','scalar opcode')
        d,s,frame=event[1:]
        # Rank-one identity TGT: E_ds plus delta_bd E_as + delta_sa E_db.
        if (d,s)==(b,a):return None,None
        if b==d:extras[index]=('ADD',a,s,frame)
        elif s==a:extras[index]=('ADD',d,b,frame)
    out=[]
    for index,event in enumerate(records):
        if index in(left,right):continue
        out.append(event)
        if index in extras:out.append(extras[index])
    return out,len(extras)

def scan_domain(records):
    groups=defaultdict(list)
    for index,event in enumerate(records):
        if event[0]=='ADD':groups[event[1:3]].append(index)
    recipes=set();all_pairs=0;barriers=Counter()
    for (a,b),positions in groups.items():
        for offset,left in enumerate(positions):
            for right in positions[offset+1:]:
                all_pairs+=1;contacts=0;blocked=None
                # Full chronological scan, independent of the indexed primary algorithm.
                for event in records[left+1:right]:
                    if event[0] in('ERASE','INIT'):
                        if event[1] in(a,b):blocked='owned';break
                    else:
                        d,s=event[1:3]
                        if(d,s)==(b,a):blocked='reversed';break
                        if d==b or s==a:contacts+=1
                if blocked:barriers[blocked]+=1
                else:recipes.add((left,right,a,b,contacts))
    return recipes,all_pairs,dict(sorted(barriers.items()))

def normalized(records,width,owned):
    rows=[{index} for index in range(width)];out=[];omitted=[]
    for index,event in enumerate(records):
        op,d=event[:2]
        if op=='ADD':
            s=event[2]
            if not rows[s]:omitted.append(index);continue
            rows[d]=rows[d].symmetric_difference(rows[s])
        else:
            require(op in('ERASE','INIT') and d in owned,'owned scalar event')
            require(op!='INIT' or not rows[d],'whole-zero owned initialization')
            rows[d]=set()
        out.append(event)
    return out,omitted

def validate_joint(joint,expected):
    branches=joint['branches']
    keys=[tuple(branch['first']) for branch in branches]
    require(len(keys)==len(set(keys)) and set(keys)==set(expected),'complete unique neutral-first branches')
    total=0
    for branch in branches:
        key=tuple(branch['first']);actual=[tuple(row[:5]) for row in branch['outcomes']]
        require(len(actual)==len(set(actual)),'unique second recipes')
        require(set(actual)==expected[key]['recipes'],'complete exact second domain')
        require(branch['counts']['candidates']==len(actual),'branch candidate count')
        require(branch['counts']['zero_contact']==sum(row[4]==0 for row in actual),'zero-contact count')
        total+=len(actual)
    require(total==joint['counts']['candidates'],'total candidate count')
    return total

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--word',type=Path,required=True);parser.add_argument('--one-step',type=Path,required=True);parser.add_argument('--two-step',type=Path,required=True);args=parser.parse_args()
    require(sha256(args.word.read_bytes()).hexdigest()==WORD_SHA,'pinned source word')
    require(sha256(args.one_step.read_bytes()).hexdigest()==ONE_STEP_SHA,'frozen complete one-step certificate')
    word,one,joint=map(read,(args.word,args.one_step,args.two_step))
    records=[tuple(event) for event in word['records'] if event[0] not in('Q','ZERO_Q')];owned=set(word['owned']);width=len(word['start'])
    firsts=[(row['first'],row['last'],*row['gate'],row['contacts']) for row in one['outcomes'] if row['sign']=='zero']
    require(len(firsts)==22 and len(set(firsts))==22,'all22 first attainers')
    require({row['sign'] for row in one['outcomes']}=={'zero','strict_loss'} and len(one['outcomes'])==2270,'one-step theorem domain')
    base_normal,base_omitted=normalized(records,width,owned)
    require(base_normal==records and not base_omitted,'source already emitter normalized')
    expected={};summaries=[]
    for first in firsts:
        rewritten,contacts=expand(records,first[0],first[1]);require(rewritten is not None and contacts==first[4],'correct first rewrite')
        normal,omitted=normalized(rewritten,width,owned)
        require(normal==rewritten and not omitted,'literal and emitted first chronology identical')
        recipes,all_pairs,barriers=scan_domain(rewritten)
        expected[first]={'recipes':recipes}
        summaries.append({'first':first,'scalar_records':len(rewritten),'omitted_zero_source_adds':len(omitted),'equal_pairs':all_pairs,'barriers':barriers,'eligible':len(recipes),'zero_contact':sum(row[4]==0 for row in recipes)})
    total=validate_joint(joint,expected);require(total==49865,'frozen joint count')
    controls=[]
    def reject(name,mutant):
        try:validate_joint(mutant,expected)
        except ValueError:controls.append(name)
        else:raise ValueError('accepted domain mutant '+name)
    mutant=deepcopy(joint);mutant['branches'].pop();reject('omitted_first_branch',mutant)
    mutant=deepcopy(joint);mutant['branches'][0]['outcomes'].pop();reject('omitted_second_recipe',mutant)
    mutant=deepcopy(joint);mutant['branches'][0]['outcomes'].append(mutant['branches'][0]['outcomes'][0]);reject('duplicate_second_recipe',mutant)
    mutant=deepcopy(joint);mutant['branches'][0]['outcomes'][0][4]+=1;reject('wrong_contact_count',mutant)
    mutant=deepcopy(joint);mutant['branches'][0]['outcomes'][0][0]+=1;reject('wrong_second_index',mutant)
    toy=[('ERASE',1,0),('ADD',0,1,2)]
    norm,omitted=normalized(toy,2,{1});require(norm==toy[:1] and omitted==[1],'normalizer really omits zero-source ADD')
    controls.append('zero_source_omission_positive_control')
    dirty=[('ADD',0,1,2)];require(normalized(dirty,2,set())==(dirty,[]),'dirty independent source retained');controls.append('dirty_independent_source_retained')
    print(json.dumps({'status':'PASS_INDEPENDENT_NATIVE_TWO_STEP_DOMAIN','first_branches':len(firsts),'second_candidates':total,'zero_contacts':sum(row['zero_contact'] for row in summaries),'normalization_omissions':0,'branches':summaries,'controls':controls,'scope':'independent brute second-interval coverage and set-row first normalization; no independent all-invoice replay'},sort_keys=True,indent=2))

if __name__=='__main__':main()
