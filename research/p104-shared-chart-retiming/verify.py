"""Read-only complete-boundary and new-native-edge replay."""
import argparse,copy,hashlib,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import model as M

def check_native(payload,edges,I,all_columns=True):
    records=payload['transports']
    expected={tuple(e['new']):[x['source_event'] for x in edges if x['new']==e['new']] for e in edges}
    actual={tuple(r['new']):r for r in records}
    M.need(len(actual)==len(records) and set(actual)==set(expected),'native edge inventory')
    columns=0;occurrences=0
    for frame,record in actual.items():
        M.need(record['source_events']==expected[frame],'native occurrence inventory')
        recipe=record['recipe'];M.need(type(recipe['rank']) is int and recipe['rank']==len(frame),'native rank')
        gates=M.recipe_gates(recipe,I)
        target=M.conjugate(I.frame(frame,9))
        I.equal(gates,target,'new direct positive child')
        z_images=[x for x,_,_ in I.tableau(target)[9:] if x]
        M.need(len(M.canonical(z_images))==recipe['rank'],'intrinsic positive rank')
        if all_columns:
            for column in range(512):
                M.need(I.state(gates,column)==I.state(target,column),'native Gaussian column')
                columns+=1
        occurrences+=len(record['source_events'])
    return {'distinct_recipes':len(records),'occurrences':occurrences,'complete_gaussian_columns':columns,
            'signed_pauli_and_phase_comparisons':len(records),'new_occurrence_ranks':[e['rank'] for e in edges]}

def boundary_check(source,word):
    baseline,old=M.replay(source);result,new=M.replay(word)
    M.need(old==new,'complete all-input boundary')
    M.need(result['boundary_coefficients']==128164,'all public columns')
    M.need(result['zero_erasures']==baseline['zero_erasures']==8,'eight exact erasures')
    # Only the four declared ADD frame annotations may change; coefficients,
    # chronological operands, signs and private operations stay literal.
    for tag in ('add','sign','zero','erase'):
        a=[e[:4] if tag=='add' else e for e in source['program'] if e[0]==tag]
        b=[e[:4] if tag=='add' else e for e in word['program'] if e[0]==tag]
        M.need(a==b,'retained scalar/private chronology')
    old_add=[e for e in source['program'] if e[0]=='add'];new_add=[e for e in word['program'] if e[0]=='add']
    M.need(sum(a!=b for a,b in zip(old_add,new_add))==4,'four changed ADD frames')
    return baseline,result

def rejects(name,function,contains):
    try:function()
    except ValueError as error:
        M.need(contains in str(error),'wrong failure for '+name+': '+str(error));return name
    raise ValueError('accepted fault '+name)

def controls(source,word,payload,edges,I):
    rejected=[]
    fault=copy.deepcopy(source)
    fault['program'][981]=['transport','Y0',[],source['program'][981][3],5]
    del fault['program'][104]
    rejected.append(rejects('unilateral source retiming',lambda:M.replay(fault),'ADD common frame'))
    fault=copy.deepcopy(word)
    idx=next(i for i,e in enumerate(fault['program']) if e[0]=='transport' and e[1]=='N33')
    del fault['program'][idx]
    rejected.append(rejects('unpaid N33 line entry',lambda:M.replay(fault),'ADD common frame'))
    fault=copy.deepcopy(word)
    idx=next(i for i,e in enumerate(fault['program']) if e[:3]==['add','N33','Y1'])
    fault['program'][idx][3]='0'
    rejected.append(rejects('changed dirty compensation',lambda:boundary_check(source,fault),'arbitrary helper restoration'))
    fault=copy.deepcopy(word)
    idx=next(i for i,e in enumerate(fault['program']) if e[0]=='add' and e[1]=='X0')
    fault['program'][idx][3]=0
    rejected.append(rejects('changed public update',lambda:boundary_check(source,fault),'complete all-input boundary'))
    fault=copy.deepcopy(source)
    fault['program'][200]=['add','X0','Y0','1',[]]
    rejected.append(rejects('undeclared crossed source read',lambda:M.construct(fault),'undeclared star access'))
    fault=copy.deepcopy(payload)
    fault['transports'][0]['recipe']['after'].append(['phase',1])
    rejected.append(rejects('new native global phase',lambda:check_native(fault,edges,I,False),'exact global phase'))
    fault=copy.deepcopy(payload)
    before=fault['transports'][0]['recipe']['before']
    del before[next(i for i,g in enumerate(before) if g[0]=='X')]
    rejected.append(rejects('missing conjugate-child X',lambda:check_native(fault,edges,I,False),'signed Pauli'))
    fault=copy.deepcopy(payload);fault['transports'][0]['recipe']['rank']+=1
    rejected.append(rejects('understated or wrong child rank',lambda:check_native(fault,edges,I,False),'native rank'))
    fault=copy.deepcopy(payload);fault['transports'][0]['source_events'].pop()
    rejected.append(rejects('missing native occurrence',lambda:check_native(fault,edges,I,False),'native occurrence inventory'))
    equivalent=copy.deepcopy(word)
    e=next(e for e in equivalent['program'] if e[0]=='transport' and e[1]=='N2' and len(e[3])==2)
    e[3][0]^=e[3][1]
    M.need(M.replay(equivalent)[0]==M.replay(word)[0],'equivalent-frame presentation')
    return rejected

def verify(regenerate=False):
    pins=M.authenticate();source=M.read(M.HERE/'source/PR2662-WORD.json')
    word=M.read(M.HERE/'WORD.json');native=M.read(M.HERE/'NATIVE.json')
    rebuilt,edges=M.construct(source)
    M.need(M.same(word,rebuilt),'complete literal regeneration')
    baseline,result=boundary_check(source,word)
    inherited=M.read(M.HERE/'source/PR2662-RESULT.json')['candidate']
    for key in ('events','counts','profile','rank_mass','boundary_coefficients'):
        M.need(M.same(baseline[key],inherited[key]),'predecessor invoice '+key)
    M.need(result['events']==5266 and result['counts']['transport']==1938 and result['rank_mass']==3542,'new complete invoice')
    I=M.load_interpreter();native_result=check_native(native,edges,I)
    if regenerate:M.need(M.same(native,M.native_payload(edges,I)),'native recipe regeneration')
    rejected=controls(source,word,native,edges,I)
    return {'schema_version':1,'status':'PASS','baseline':baseline,'candidate':result,'native':native_result,'sources_authenticated':pins,
            'rank_delta':{str(r):result['profile'].get(r,0)-baseline['profile'].get(r,0) for r in sorted(set(result['profile'])|set(baseline['profile'])) if result['profile'].get(r,0)!=baseline['profile'].get(r,0)},
            'controls':rejected,'positive_controls':['equivalent binary frame basis'],
            'moment_difference':'[2*(2^p-2)+(5^p-1-4^p)+(7^p-1-6^p)]/m^p < 0 for 0<p<1, m>0; zero at p=1',
            'limits':'Finite same-boundary retiming; inherits unchanged native edges. No global owners/idle/precision/all-size supplier or new kappa.'}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--regenerate',action='store_true');ap.add_argument('--out',type=Path);args=ap.parse_args()
    result=verify(args.regenerate)
    M.need(M.same(result,M.read(M.HERE/'RESULT.json')),'complete typed result receipt')
    if args.out:
        with args.out.open('x',encoding='utf-8') as file:file.write(json.dumps(result,indent=2)+'\n')
    print('PASS_P104_SHARED_CHART_RETIMING inputs=358 events=5266 transports=1938 mass=3542 new_native=3/4 controls=9')
if __name__=='__main__':main()
