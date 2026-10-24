#!/usr/bin/env python3
"""Static packet emitter only: copy pinned words and lower scalar instructions."""
from collections import Counter
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
import json

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
CALLER=ROOT/'swarm-coupled-caller-sol-high-20261024/agents/caller'
ACTIVE=[0]+list(range(9,17))

def digest(path):return sha256(path.read_bytes()).hexdigest()
def lifted_mask(n):return sum(1<<ACTIVE[j] for j in range(9) if n>>j&1)
def lifted_word(word):
    out=[]
    for op in word:
        if op[0]=='P':
            basis=[1<<j for j in range(25)]
            for j,v in enumerate(op[1]):basis[ACTIVE[j]]=lifted_mask(v)
            out.append(['P',basis])
        elif op[0]=='D':
            quad=[0]*25;linear=[0]*25
            for j,v in enumerate(op[1]):quad[ACTIVE[j]]=lifted_mask(v)
            for j,v in enumerate(op[2]):linear[ACTIVE[j]]=v
            out.append(['D',quad,linear])
        elif op[0]=='X':out.append(['X',lifted_mask(op[1])])
        elif op[0]=='phase':out.append(op)
        else:raise ValueError('unknown pinned monomial token')
    return out

def main():
    fsrc=CALLER/'PUBLIC-PROMOTED-CANDIDATE-v13.json'
    isrc=CALLER/'PUBLIC-PROMOTED-INVERSE-v13.json'
    hsrc=CALLER/'PARAMETRIC-HCODE-v14.json'
    nsrc=ROOT/'swarm-provider-audit-sol-high-20261024/repository/research/coded-native-caller/NORMALIZERS.json'
    psrc=ROOT/'swarm-provider-audit-sol-high-20261024/repository/research/native-rank8-helper-provider/PROVIDER.json'
    a_src=ROOT/'swarm-coupled-caller-sol-high-20261024/agents/challenge/CURRENT-HELPER-ALIASES-v2.json'
    astra=ROOT/'race-kappa0033-sol-high-20261024/consultants/astra-decoder/BALANCED-J-NATIVE-PLACEMENT-v1.md'
    public=ROOT/'outputs/pr5419-v4b-junction-fit-20261024/upstream'
    files=[fsrc,isrc,hsrc,nsrc,psrc,a_src,astra,public/'SYNTHESIS.md',public/'junction.py',
           CALLER/'PARAMETRIC-BACKWARD-v14.json',CALLER/'PARAMETRIC-INVERSE-v14.json',
           ROOT/'swarm-coupled-caller-sol-high-20261024/agents/algebra/three_factor_caches.py']
    source_pins={str(p.relative_to(ROOT)):digest(p) for p in files}
    forward=json.loads(fsrc.read_bytes());inverse=json.loads(isrc.read_bytes())
    hcode=json.loads(hsrc.read_bytes());normal=json.loads(nsrc.read_bytes());provider=json.loads(psrc.read_bytes())
    fi=next(i for i,x in enumerate(forward['operations']) if x['op']=='PROVIDER_5402')
    ii=next(i for i,x in enumerate(inverse['operations']) if x['op']=='PROVIDER_5411_INVERSE')
    fp=[x for x in forward['operations'][:fi] if x['op']=='MONOMIAL' and ('source_owner' in x or x.get('whole_job_boundary')=='before provider')]
    fq=forward['operations'][fi+1:]
    ip=inverse['operations'][:ii]
    iq=[x for x in inverse['operations'][ii+1:] if x['op']=='MONOMIAL' and ('source_owner' in x or x.get('whole_job_boundary')=='after raw inverse')]
    if any(len(x)!=400 for x in (fp,fq,ip,iq)):raise ValueError('exact direction-specific400 alias maps')

    def maps(records):
        return [{**op,'source_word9':op['word'],'word':lifted_word(op['word']),'lift':'same prescribed columnwise lift; phase exponent not exterior scalar'} for op in records]
    def frames(part):
        records=hcode['operations'][:120] if part=='entry' else hcode['operations'][-120:]
        return maps([{**x,'field':('y'+x['field'][1:]) if x['field'].startswith('x') else ('h'+x['field'][1:])} for x in records])
    def scalar(c,label):
        # Every listed ADD has coefficient1,-1 or-1/2; no SCALE opcode.
        coefficients={Fraction(-4):[-1]*5,Fraction(4):[1]*3,
                      Fraction(1,2):[Fraction(-1,2)],Fraction(-1,2):[Fraction(-1,2)]*3}[Fraction(c)]
        out=[]
        for j in range(8):
            h=f'h{j}';owned=f'c{j+1}'
            out.extend([{'op':'CLEAR','field':owned,'owned':True},
                {'op':'ZERO_RETAG','field':owned,'chart':f'exact current frame of {h}','premise':'immediately preceding owned CLEAR'},
                {'op':'COPY','dst':owned,'src':h,'owned_zero_destination':True}])
            out.extend({'op':'ADD','dst':owned,'src':h,'coefficient':str(x)} for x in coefficients)
            out.extend([{'op':'SWAP','fields':[h,owned],'includes_chart':True},
                {'op':'CLEAR','field':owned,'owned':True},
                {'op':'ZERO_RETAG','field':owned,'chart':'ground','premise':'immediately preceding owned CLEAR'}])
        return {'label':label,'kind':'OWNED_SCALAR_LOWERING','coefficient':str(Fraction(c)),'operations':out}
    def query(sign,label):
        out=[]
        for j in range(8):
            owned=f'c{j+1}'
            out.extend([{'op':'CLEAR','field':owned,'owned':True},
                {'op':'ZERO_RETAG','field':owned,'chart':f'exact current frame of h{j}','premise':'immediately preceding owned CLEAR'},
                {'op':'COPY','dst':owned,'src':f'h{j}','owned_zero_destination':True},
                {'op':'GAUSSIAN_Q','field':owned,'rank':1,'axis':0,'sign':1,'paid':True},
                {'op':'ADD','dst':f'k{j}','src':owned,'coefficient':str(sign)},
                {'op':'CLEAR','field':owned,'owned':True},
                {'op':'ZERO_RETAG','field':owned,'chart':'ground','premise':'immediately preceding owned CLEAR'}])
        return {'label':label,'kind':'QUERY_OLD_H','operations':out,'query_input_version':'original independent h' if sign<0 else 'fully recovered OLD h after both shears and both final half-scalings'}
    def shear(kind,sign,label):
        out=[]
        for k,row in enumerate(normal['mode_columns']):
            for i,v in enumerate(row):
                if v:out.append({'op':'ADD','dst':f'h{k}' if kind=='Z' else f'y{i}',
                    'src':f'y{i}' if kind=='Z' else f'h{k}', 'coefficient':str(Fraction(sign*v,2))})
        return {'label':label,'kind':'COMMON_FRAME_SHEAR_'+kind,'sign':sign,'operations':out}
    def alias(records,label):return {'label':label,'kind':'INHERITED_ALIAS_WORDS','operations':maps(records)}
    def native(op,label):
        return {'label':label,'kind':'COMPRESSED_PINNED_NATIVE_PROVIDER','operations':[{**op,'stage_embedding':ACTIVE,
            'compressed_not_expanded':True,'not_a_new_fullphase_census':True}],
            'interpretation':'Together with the adjacent exact alias lists, use only the accepted direction-specific main ABI and392positivehelper boundary. No atomic promoted H8 movement.'}
    common_entry={'label':'common_K_entry','kind':'COMMON_K_FRAME_ENTRY','operations':frames('entry')}
    common_exit={'label':'common_K_exit','kind':'COMMON_K_FRAME_EXIT','operations':frames('exit')}
    fs=[query(-1,'query_original_h'),common_entry,scalar(-4,'h_times_minus4'),
        shear('Z',-1,'h_minus_Z_y'),shear('W',1,'y_plus_W_UPDATED_h'),common_exit,
        alias(fp,'forward_alias_pre'),native(forward['operations'][fi],'actual5402_raw_provider'),alias(fq,'forward_alias_post'),
        scalar(Fraction(1,2),'output_h_half1'),scalar(Fraction(1,2),'output_h_half2')]
    ins=[scalar(4,'input_h_times4'),alias(ip,'inverse_alias_pre'),native(inverse['operations'][ii],'actual5411_raw_main_inverse'),
         alias(iq,'inverse_alias_post'),common_entry,shear('W',-1,'y_minus_W_hP'),
         shear('Z',1,'hP_plus_Z_UPDATED_y'),scalar(Fraction(-1,2),'recovered_h_negative_half'),
         scalar(Fraction(1,2),'recovered_h_half'),common_exit,query(1,'query_recovered_OLD_h')]
    def census(segments):return dict(Counter(op['op'] for seg in segments for op in seg['operations']))
    packet={'schema':'balanced-J-fused-native-main-interface/v1','status':'EMITTED_NO_SCIENTIFIC_EXECUTION',
        'source_pins':source_pins,'stage_geometry':{'logical_ambient_axes':25,'s':1,'central':0,'private_axes':list(range(9,17)),
            'source9_to_stage_axes':ACTIVE,'spectators_unchanged':list(range(1,9))+list(range(17,25)),
            'R':'qD_s=product positiveC on central0 and eight private axes','all_width_lift':'source-prescribed columnwise lift; M coefficients exterior; monomial phases lift per column'},
        'main_banks':{'u':'x112,k8','v':'y112,h8'},'original_count':632,'main_original_count':240,
        'coupled_h_owners':provider['mode_owners'],'promoted_old_H8_owners':forward['promoted_original_owners'],
        'remaining_helper_count':392,'remaining_helper_profile':{'4':28,'7':7,'8':39,'9':318},
        'owned':{'fields':[f'c{j}' for j in range(9)],'all9_arbitrary_entry':True,'all9_zero_exit':True,
            'reused_scalar_and_query_fields':[f'c{j}' for j in range(1,9)],'new_scratch_fields':0,
            'native_c0':'may be arbitrary until native provider clears it; never read by client boundary'},
        'source_operator_definitions':{'W':'diag(Kp^-1) M diag(Km)/2','Z':'diag(Km^-1) M^T diag(Kp)/2',
            'C':'I-WZ','ZW':'14I8','J':[['C','-4W'],['3Z','13I8']],
            'intertwining':'R_pW=WR_h and R_hZ=ZR_p; never separate[D,W/Z]=0 or[q,W/Z]=0'},
        'raw_forward_promoted_main_ABI':{'x':'D*x-R*y+R*W*hP','k':'D*k','y':'D*y','h':'D*(hP-Z*y)'},
        'raw_inverse_promoted_main_ABI':{'x':'D^-1X+qC D^-1Y-qW D^-1H','k':'D^-1K','y':'D^-1Y','hP':'D^-1H+Z D^-1Y'},
        'forward_segments':fs,'inverse_segments':ins,'forward_counts':census(fs),'inverse_counts':census(ins),
        'expected_forward':'T_s(u,v)=(D_su-R_sv,D_sJ_sv)',
        'expected_main_inverse':'v=J_s D_s^-1 Vprime;u=D_s^-1 A+qv',
        'inverse_scope':'Both main products Tinv*T and T*Tinv are I on240originalmain directions. Remaining392jobs are positiveC_r in each direction, NOT inverse helper identity.',
        'inherited_paid_profile':provider['paid'],'supplementary_H1_per_direction':8,
        'boundary_counts_before_inherited_aliases':{'ADD':960,'MONOMIAL':240,'COPY':32,'SWAP':24,'CLEAR':64,'ZERO_RETAG':64,'GAUSSIAN_Q':8},
        'inherited_alias_MONOMIAL_per_direction':800,
        'scope':'Literal boundary and compressed pinned kernel/alias contract only. Not expanded21473native-word replay or new fullphase census. No autonomous main Gaussian target or kappa claim.',
        'optional_consumer_CONDITION_ONLY':{'source_stage':1,'destination_stage':2,'required_paid_current_source_queries':120,
            'source':'E_s=qCURRENTVprime=J_sR_sv; all112port+8modequeries charged, no preludeqh reuse',
            'destination':'E_t=J_t A','conditional_public_action':'E_t+=J_t P J_s E_s; E_s returned unchanged;P=diag(I112,0_8)',
            'logical_endpoint':'E_t=J_t[D_su-(I-P)R_sv]','executed_or_admitted_here':False,
            'public_scalar_alphabet_and_lowering':'Public5419consumer is an additional conditional interface, not silently lowered or priced as the960ADDnative boundary.'},
        'credit':'zxv PR5419 cross-chart consumer/gauge; Dugongue PR4935 involutive completion; Dillon/Ali/native/helper/Clifford/compiler predecessors. Codex-assisted new native placement.','complete_caller':False,'gain_claimed':False}
    out=HERE/'BALANCED-J-NATIVE-v1.json';out.write_text(json.dumps(packet,indent=2)+'\n')
    print(json.dumps({'packet_sha256':digest(out),'forward_counts':packet['forward_counts'],'inverse_counts':packet['inverse_counts']}))

if __name__=='__main__':main()
