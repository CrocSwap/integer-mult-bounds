#!/usr/bin/env python3
"""Independent exact all649-column neutral B/F component; root executes.
Reuses only our authenticated field-word and phase engines. SourceP is the
accepted unrestricted632+9 macro. Actual400wholejobaliases are phase-bound and
collapsed; no author generator/evaluator or provider phase replay is imported.
"""
from pathlib import Path
from fractions import Fraction as F
from collections import Counter
from hashlib import sha256
import argparse,copy,importlib.util,json,sys
HERE=Path(__file__).resolve().parent

def module(name,p):
    s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
eng=module('our_field_words_neutral',HERE/'check_parametric_v14.py')
P_ROWS=[256,2,4,8,16,32,64,128,1];PG=2000

def need(x,s):
    if not x:raise ValueError(s)


def collapse(ops,aliases,cache):
    positions=[i for i,e in enumerate(ops)if e['op']=='PROVIDER_5402'];need(len(positions)==1,'one sourceP macro');i=positions[0]
    for side,block in [('pre',ops[i-400:i]),('post',ops[i+1:i+401])]:
        expected={f'owner{r}':g['forward_pre_input_monomial_word'if side=='pre'else'forward_post_output_monomial_word']for g in aliases['groups']for r in g['owners']}
        need(len(block)==400 and len({e.get('field')for e in block})==400 and {e.get('field')for e in block}==set(expected),'all400currenthelperaliases once perboundary')
        for e in block:need(e['op']=='MONOMIAL'and eng.signatures_match(e['word'],expected[e['field']],cache),'actual signed phase wholejob400alias')
    return ops[:i-400]+[ops[i]]+ops[i+401:]


def replay(data,direction,p,m,signs,aliases,cache):
    mode=p['mode_owners'];helpers=sorted(set(range(224,632))-set(mode))
    mapping={**{f'x{i}':i for i in range(112)},**{f'y{i}':112+i for i in range(112)},**{f'h{k}':r for k,r in enumerate(mode)},**{f'owner{r}':r for r in helpers},**{f'c{k}':632+k for k in range(9)},**{f't{k}':641+k for k in range(8)}}
    need(len(mapping)==649 and set(mapping.values())==set(range(649))and data['physical_field_bindings']==mapping,'actual632original+17owned independentIDs')
    original={f:{(j,0,()):F(1)}for f,j in mapping.items()};rows=copy.deepcopy(original);ground={};paid=Counter();paid_fields=[];counts=Counter();t_route_counts=Counter();mode_alias_count=0
    for e in collapse(data['operations'],aliases,cache):
        op=e['op'];counts[op]+=1
        if op=='CLEAR':
            f=e['field'];need(f in rows and f[0]in('t','c')and e.get('owned')is True,'CLEAR only17declaredowned');rows[f]={};ground[f]=False
        elif op=='ZERO_RETAG':
            f=e['field'];need(f in rows and f[0]in('t','c')and not rows[f]and e['new_chart']=='ground','complete649-column ownedzero groundretag');ground[f]=True
        elif op=='SWAP':
            a,b=e['fields'];need(a in rows and b in rows and a!=b and e.get('includes_chart')is True,'actual wholefield/chartSWAP')
            if a.startswith('h')or b.startswith('h'):
                t=a if a.startswith('t')else b;need(t.startswith('t')and not rows[t]and ground.get(t)is True,'h moves into genuinelyzero ownedT beforeinputerasure')
            rows[a],rows[b]=rows[b],rows[a];ground[a],ground[b]=ground.get(b,False),ground.get(a,False)
        elif op=='ADD':
            need(e['dst']in rows and e['src']in rows and e['dst']!=e['src'],'ADD actual distinct field IDs');rows[e['dst']]=eng.add(rows[e['dst']],rows[e['src']],F(e['coefficient']))
        elif op=='SCALE':
            need(e['field']in rows and F(e['coefficient'])==-1,'external field minus sign is actualscalar');rows[e['field']]={key:-v for key,v in rows[e['field']].items()}
        elif op=='MONOMIAL':
            f=e['field'];word=e['word'];need(f in rows,'monomial field declared')
            if word==[['P',P_ROWS]]:
                rows[f]=eng.app(rows[f],w=(PG,))
                if f.startswith('t'):t_route_counts[f]+=1
                if f.startswith('h'):mode_alias_count+=1
            elif word==[['X',1]]:rows[f]=eng.app(rows[f],r=2,w=(-1,-1))
            elif word==[['X',511]]:rows[f]=eng.app(rows[f],r=2) # control uses a legal but wrong native translation
            else:
                bank=f[0];j=int(f[1:]);idx=j if bank in('x','y')else 112+j
                need(bank in('x','y','h','t')and 0<=idx<120,'old K physical owner binding')
                sig=eng.old.map_signature(word)
                if sig==signs[idx]:letter=idx+2
                elif sig==eng.old.inverse_signature(signs[idx]):letter=-(idx+2)
                else:raise ValueError('literalmonomialdiffersfromactualK/explicitroutes;scalarphaseisnotanexteriorsign')
                rows[f]=eng.app(rows[f],w=(letter,))
        elif op=='GAUSSIAN':
            need(e['field'].startswith('t')and e['rank']==8 and e['operator']=='C_rank8_bits0to7_positive'and e.get('paid')is True,'actualpositivepaidcanonicalC8job')
            rows[e['field']]=eng.app(rows[e['field']],w=(PG,1,PG));paid[8]+=1;paid_fields.append(e['field'])
        elif op=='PROVIDER_5402':
            need(e['provider_sha256']==sha256(eng.old.PROVIDER.read_bytes()).hexdigest(),'exact accepted sourcePbytes');need(e['owned_fields']==[f'c{k}'for k in range(9)],'exact9sourceownedfields')
            need(all(not rows[f'h{k}']for k in range(8)),'sourcehinputcomplete649-column zero; originalhretainedinT')
            before=copy.deepcopy(rows)
            for i in range(112):
                row=eng.add(eng.app(before[f'x{i}'],w=(1,)),eng.app(before[f'y{i}'],r=1),-1)
                for k in range(8):
                    if m[k][i]:row=eng.add(row,eng.app(before[f'h{k}'],r=1,w=(-(i+2),114+k)),F(m[k][i],2))
                rows[f'x{i}']=row;rows[f'y{i}']=eng.app(before[f'y{i}'],w=(1,))
            for k in range(8):
                row=before[f'h{k}']
                for i in range(112):
                    if m[k][i]:row=eng.add(row,eng.app(before[f'y{i}'],w=(-(114+k),i+2)),F(-m[k][i],2))
                rows[f'h{k}']=eng.app(row,w=(1,))
            for k in range(9):rows[f'c{k}']={};ground[f'c{k}']=False
            for owner in helpers:rows[f'owner{owner}']={(owner,0,(10000+owner,)):F(1)} # accepted actualpositive400aliases
        else:raise ValueError('unrecognizedneutraloperation '+op)
    expected={f'c{k}':{}for k in range(9)};expected.update({f't{k}':{}for k in range(8)})
    for i in range(112):
        expected[f'x{i}']=eng.app(original[f'x{i}'],w=(1,))
        expected[f'y{i}']=eng.app(original[f'y{i}'],w=(1,))
        if direction=='B':expected[f'x{i}']=eng.add(expected[f'x{i}'],eng.app(original[f'y{i}'],r=1),-1)
        else:expected[f'y{i}']=eng.add(expected[f'y{i}'],eng.app(original[f'x{i}'],r=3,w=(1,1)))
    for k in range(8):expected[f'h{k}']=eng.app(original[f'h{k}'],w=(PG,1,PG))
    for owner in helpers:expected[f'owner{owner}']={(owner,0,(10000+owner,)):F(1)}
    need(rows==expected,'all649-column exact uncoded '+direction+' endpoint/ownedreturn mismatch')
    need(paid==Counter({8:8})and sorted(paid_fields)==[f't{k}'for k in range(8)],'eightliteralpaidH8jobs notmetadata')
    need(t_route_counts==Counter({f't{k}':2 for k in range(8)})and mode_alias_count==16,'all16paidD8routeand16newmodecanonicalaliasmaps')
    hist=Counter(len(canonical['frames'][canonical['final'][j]])-len(canonical['frames'][canonical['start'][j]])for j in helpers);hist[8]+=8
    declared={int(k):v for k,v in data['productive_helpers'].items()};need(hist==Counter(declared)==Counter({4:28,7:7,8:55,9:318}),'actual408positivehelperprofile')
    native=Counter({int(k):v for k,v in p['paid'].items()});total=native+paid;need(total==Counter({int(k):v for k,v in data['complete_paid_local_profile'].items()}),'complete literalnative+extra paidprofile')
    return {'status':'PASS_UNCODED_'+direction,'independent_original_columns':632,'arbitrary_owned_columns':17,'owned_zero_outputs':17,'main_fields':224,'positive_helpers':408,'helper_profile':dict(hist),'native_paid':dict(native),'extra_paid':dict(paid),'complete_paid':dict(total),'listed_outer_counts':dict(Counter(e['op']for e in data['operations'])),'collapsed400alias_maps':800,'rawmoment_delta_vs_accepted_complete_profile':'8paidH8−8targetH8 cancels rankwise for every exponent; no rawprice gain','scope':'All649symboliccolumns under accepted unrestrictedsourceP plus bound400wholejobphasealiases; no sourceproviderreplay.'}


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--backward',type=Path,required=True);ap.add_argument('--forward',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args();global canonical
    p,m,signs=eng.old.initialize();eng.old.INVO.add(PG)
    cp=eng.old.BASE/'swarm-provider-audit-sol-high-20261024/repository/research/native-center-free-code/SOURCE-WORD.json.gz'
    import gzip
    need(sha256(cp.read_bytes()).hexdigest()=='7679daa4ec6a40f56fc7f0202379a6f454310e94945aba4f48beaaaafb838d05','exact native canonical source');canonical=json.loads(gzip.decompress(cp.read_bytes()))['canonical']
    aliases_path=HERE/'CURRENT-HELPER-ALIASES-v2.json';aliases=json.loads(aliases_path.read_text());accepted=json.loads((HERE/'HELPER-ALIAS-RESULT-v2.json').read_text());need(accepted['aliases_sha256']==sha256(aliases_path.read_bytes()).hexdigest(),'executed alias result binds actual wholejob words')
    phpath=eng.old.BASE/'swarm-provider-audit-sol-high-20261024/agents/algebra/phase_exact.py';need(sha256(phpath.read_bytes()).hexdigest()=='15e90b63c5659090f02902cb38951ec4ab252352fb0b967b411ed547c501e2ba','independentphaseenginepin');ph=module('our_neutral_child_phase',phpath)
    P=(('P',tuple(P_ROWS)),);D=tuple(('C',1<<j,1)for j in range(1,9));C8=tuple(('C',1<<j,1)for j in range(8));R=tuple(('C',1<<j,1)for j in range(9))
    need(ph.equal(P+C8+P,D)and ph.equal(P+D+P,C8)and ph.equal(P+R,R+P),'independent full phase and allPauli childroute/targetalias/Rintertwining')
    cache={};docs={'B':json.loads(args.backward.read_text()),'F':json.loads(args.forward.read_text())};results={d:replay(a,d,p,m,signs,aliases,cache)for d,a in docs.items()};controls=[]
    def reject(label,d,change):
        a=copy.deepcopy(docs[d]);change(a)
        try:replay(a,d,p,m,signs,aliases,cache)
        except(ValueError,KeyError,IndexError)as ex:controls.append({'name':label,'rejected':True,'reason':str(ex)});return
        raise ValueError('acceptedneutralmutant '+label)
    reject('actualHplusTsignchanged','B',lambda a:next(e for e in a['operations']if e['op']=='ADD'and e['dst'].startswith('h')).__setitem__('coefficient','-1'))
    reject('missingTownedinitialCLEAR','B',lambda a:a['operations'].pop(next(i for i,e in enumerate(a['operations'])if e['op']=='CLEAR')))
    reject('originalpersistenthnotmoved','B',lambda a:a['operations'].pop(next(i for i,e in enumerate(a['operations'])if e['op']=='SWAP'and e['fields'][0].startswith('h'))))
    reject('paidC8rankforged','B',lambda a:next(e for e in a['operations']if e['op']=='GAUSSIAN').__setitem__('rank',7))
    reject('paidC8free','B',lambda a:next(e for e in a['operations']if e['op']=='GAUSSIAN').__setitem__('paid',False))
    reject('oneactualpaidD8routemapremoved','B',lambda a:a['operations'].pop(next(i for i,e in enumerate(a['operations'])if e['op']=='MONOMIAL'and e['field'].startswith('t')and e['word']==[['P',P_ROWS]])))
    reject('canonicalhmodepostaliasremoved','B',lambda a:a['operations'].pop(max(i for i,e in enumerate(a['operations'])if e['op']=='MONOMIAL'and e['field'].startswith('h')and e['word']==[['P',P_ROWS]])))
    reject('TownedfinalCLEARmissing','B',lambda a:a['operations'].pop(max(i for i,e in enumerate(a['operations'])if e['op']=='CLEAR')))
    reject('forwardq²wrongnativeXmask','F',lambda a:next(e for e in a['operations']if e['op']=='MONOMIAL'and e['word']==[['X',1]]).__setitem__('word',[['X',511]]))
    reject('wholeSWAPwithoutchart','F',lambda a:next(e for e in a['operations']if e['op']=='SWAP').__setitem__('includes_chart',False))
    def tensor_sign(a):
        e=next(e for e in a['operations']if e['op']=='SCALE');field=e['field'];e.clear();e.update(op='MONOMIAL',field=field,word=[['phase',2]])
    reject('exteriorMINUSonechangedtonativetensorphase','F',tensor_sign)
    need((-1)**2==1 and F(-1)!=1,'width2nativephasecannotstandforfieldscalarminus1')
    result={'schema':'independent-neutral-all649-BF/v16c','status':'PASS_COMPLETE_LOCAL_STANDARD_B_AND_F_WITH408POSITIVE_HELPERS','results':results,'controls':controls,'packet_sha256':{'backward':sha256(args.backward.read_bytes()).hexdigest(),'forward':sha256(args.forward.read_bytes()).hexdigest()},'child_route_proof':{'paid_primitive':'canonicalpositiveC8axes0through7','D8_realization':'Pswap0/8 C8 Pswap0/8 = D_axes1through8','new8target_realization':'Pswap0/8 D8 Pswap0/8 = canonicalpositiveC8','proof':'independent complete signedPauli+fullzero_columnincludingabsolutephase','paid_D8_route_maps':16,'newmode_target_alias_maps':16,'R_intertwining_of_coordinate_swap':True},'exterior_sign_width2_control':{'nativephase2tensor':1,'requiredfieldscalar':-1,'rejected':True},'checker_sha256':sha256(Path(__file__).read_bytes()).hexdigest(),'reused_independent_engines':{q.name:sha256(q.read_bytes()).hexdigest()for q in[HERE/'check_parametric_v14.py',HERE/'check_literal_local.py',phpath]},'aliases_sha256':sha256(aliases_path.read_bytes()).hexdigest(),'all_width':'Free operator identities retain exterior rational coefficients and native square/tensor phases; exact9axis childroute identities tensor columnwise. All632original and17arbitraryowned directions included.','scientific_limit':'Complete local B/F components only. Fullcaller literalinvoice,precision/stock/compiler/outerfunding and anykappaheadroom needseparateverification. Rawrecursivepriceunchanged.','complete_caller':False,'new_kappa':None}
    need(not args.output.exists(),'immutable result exists');args.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,sort_keys=True))
if __name__=='__main__':main()
