#!/usr/bin/env python3
"""Independent phase acceptance of proposed inverse-helper positive aliases.
Root executes. Source lower_child is a proposal generator ONLY; our previously
independent signed-Pauli/full-zero-column interpreter is the oracle. No native
provider or 2847-class/1240-boundary census is replayed.
"""
from pathlib import Path
from hashlib import sha256
from collections import defaultdict,Counter
import argparse,copy,gzip,importlib.util,json,sys
HERE=Path(__file__).resolve().parent;BASE=HERE.parents[2]
SCI=BASE/'swarm-provider-audit-sol-high-20261024/repository/research'
PH=BASE/'swarm-provider-audit-sol-high-20261024/agents/algebra/phase_exact.py'
CE=SCI/'coded-native-caller/clifford_exact.py'


def need(ok,msg):
    if not ok:raise ValueError(msg)


def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m


def decode(rec):
    return (('D',tuple(rec['quadratic_rows']),tuple(rec['linear_Z4'])),('P',tuple(rec['matrix_rows'])),('X',rec['offset']),('phase',rec['phase']))


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);ap.add_argument('--aliases',type=Path,required=True);args=ap.parse_args()
    need(sha256(PH.read_bytes()).hexdigest()=='15e90b63c5659090f02902cb38951ec4ab252352fb0b967b411ed547c501e2ba','retained independent phase oracle bytes')
    need(sha256(CE.read_bytes()).hexdigest()=='2982ead07721e83358dc67c6f49c2b4c16a236a6bebdfd72f58221be1f5d0962','pinned proposal compiler bytes')
    ph=module('independent_helper_phase_oracle',PH);ce=module('helper_alias_proposal_compiler',CE)
    cp=SCI/'native-center-free-code/SOURCE-WORD.json.gz';pp=SCI/'native-rank8-helper-provider/PROVIDER.json';c=json.loads(gzip.decompress(cp.read_bytes()))['canonical'];p=json.loads(pp.read_text());owners=set(range(224,632))-set(p['mode_owners']);need(len(owners)==400,'current400originalhelperdirections')
    groups=defaultdict(list)
    for owner in sorted(owners):
        start,end=c['start'][owner],c['final'][owner];rank=len(c['frames'][end])-len(c['frames'][start]);need(rank>0,'positive current helper rank');groups[start,end,rank].append(owner)
    need(len(groups)==17,'17 actual layouts derived from all400owners')
    def conj(op):
        out=ce.ident(9)
        for e in op.circuit:
            if e[0]=='P':q=ce.perm(9,e[1])
            elif e[0]=='D':q=ce.diag(9,e[1],tuple(-v%4 for v in e[2]))
            elif e[0]=='C':q=ce.cgate(9,e[1],-e[2])
            elif e[0]=='X':q=ce.xgate(9,e[1])
            elif e[0]=='phase':q=ce.Op(9,ce.identity(9),[('phase',-e[1]%4)])
            else:raise ValueError('proposal primitive alphabet')
            out=out.then(q)
        return out
    aliases=[];controls=[];ranks=Counter();monomial_gates=Counter()
    for (start,end,rank),roles in sorted(groups.items()):
        # Actual native backward source: bar(Fout) bar(Fin)^-1.
        # Its inverse is bar(Fin) bar(Fout)^-1; .then applies left circuit first.
        src_in=conj(ce.canonical_frame(9,c['frames'][start]));src_out=conj(ce.canonical_frame(9,c['frames'][end]));proposal_op=src_out.adjoint().then(src_in)
        rec,_unused_candidate_compiled=ce.lower_child(proposal_op)
        need(rec['rank']==rank and rec['right']is not None,'proposed rank equals actual layout difference')
        left,right=decode(rec['left']),decode(rec['right'])
        raw=ph.adjoint(ph.conjugate(ph.frame(c['frames'][end])))+ph.conjugate(ph.frame(c['frames'][start]))
        positive=tuple(('C',1<<j,1)for j in range(rank))
        actual_sig=ph.signature(raw)
        need(actual_sig==ph.signature(right+positive+left),'independent complete raw inverse = L positiveCr R')
        pre=ph.adjoint(right);post=ph.adjoint(left)
        need(ph.signature(pre+raw+post)==ph.signature(positive),'independent complete positive alias identity')
        # All proposed adapter gates are unit-modulus signed monomials.
        need(all(e[0]in('D','P','X','phase')for e in pre+post),'no Gaussian hidden in normalizers')
        for word in [pre,post]:
            for e in word:
                monomial_gates[e[0]]+=len(roles)
                if e[0]=='P':need(len(e[1])==9 and ph.rank(e[1])==9,'invertible actual nine-axis normalizer')
        forward_raw=ph.adjoint(raw);forward_pre=left;forward_post=right+(('X',(1<<rank)-1),)
        need(ph.signature(forward_pre+forward_raw+forward_post)==ph.signature(positive),'independent current forward helper positive alias')
        anchor=actual_sig[1];j=next(j for j,z in enumerate(anchor)if z!=(0,0))
        aliases.append({'source_entry_chart':start,'source_exit_chart':end,'inverse_entry_chart':end,'inverse_exit_chart':start,'rank':rank,'owners':roles,'raw_inverse_word':raw,'raw_forward_word':forward_raw,'forward_pre_input_monomial_word':forward_pre,'forward_post_output_monomial_word':forward_post,'pre_input_monomial_word':pre,'post_output_monomial_word':post,'proposed_child_factorization':rec,'independent_tableau_sha256':sha256(json.dumps(actual_sig[0]).encode()).hexdigest(),'independent_complete_zero_column_sha256':sha256(json.dumps([actual_sig[1],actual_sig[2]]).encode()).hexdigest(),'absolute_phase_anchor':{'index':j,'numerator':anchor[j],'denominator_power2':actual_sig[2]}})
        ranks[rank]+=len(roles)
        bad_left=left+(('phase',2),)
        need(ph.signature(right+positive+bad_left)!=actual_sig,'actual proposed adapter phase mutation rejected')
        controls.append({'name':'actual left normalizer absolute phase changed','entry':end,'exit':start,'rejected':True})
    need(ranks==Counter({9:318,8:47,7:7,4:28}),'all400 exact owner alias coverage')
    # Backward conjugation orientation is substantive, not a chart-name choice.
    start,end,rank=next(k for k in groups if k[0]==0 and k[2]==9)
    row=next(a for a in aliases if a['source_entry_chart']==start and a['source_exit_chart']==end)
    wrong=ph.adjoint(ph.frame(c['frames'][end]))+ph.frame(c['frames'][start])
    need(ph.signature(tuple(map(tuple,row['pre_input_monomial_word']))+wrong+tuple(map(tuple,row['post_output_monomial_word'])))!=ph.signature(tuple(('C',1<<j,1)for j in range(rank))),'unconjugated backward orientation rejected')
    controls.append({'name':'unconjugated source frame orientation','rejected':True})
    declared=[j for a in aliases for j in a['owners']]
    def validate_owners(values):need(len(values)==400 and len(set(values))==400 and set(values)==owners,'unique actual current owner census excludes all coupled modes')
    validate_owners(declared)
    forbidden=p['mode_owners'][0];bad=list(declared);bad[0]=forbidden
    try:validate_owners(bad)
    except ValueError as ex:controls.append({'name':'coupled original mode substituted into helper aliases','rejected':True,'reason':str(ex)})
    else:raise ValueError('coupled owner alias incorrectly accepted')

    # Public cheap120 promotion uses eight actual former autonomous rank8 jobs.
    # This is an alternative392-helper contract, never eight additional targets.
    promoted={449,455,482,483,451,453,492,502}
    need(promoted<=owners and len(promoted)==8,'all promoted owners belong to current autonomous set')
    need({c['start'][j]for j in promoted}=={114,115}and all(c['final'][j]==1 for j in promoted),'actual promoted two-layout endpoints')
    need(c['frames'][114]==[51]and c['frames'][115]==[30],'actual even-weight birth lines; no odd-port centralizer assumption')
    P=(('P',(256,2,4,8,16,32,64,128,1)),)
    X8=(('X',255),);D8=tuple(('C',1<<j,1)for j in range(1,9));promoted_aliases=[]
    for start in(114,115):
        record=next(a for a in aliases if a['source_entry_chart']==start and a['source_exit_chart']==1 and a['rank']==8)
        selected=sorted(promoted & set(record['owners']));need(len(selected)==4,'four promoted original owners per exact layout')
        L,R=decode(record['proposed_child_factorization']['left']),decode(record['proposed_child_factorization']['right'])
        raw_forward=ph.adjoint(ph.conjugate(ph.frame(c['frames'][start])))+ph.conjugate(ph.frame(c['frames'][1]))
        need(ph.signature(ph.adjoint(raw_forward))==ph.signature(record['raw_inverse_word']),'actual forward/inverse source orientation')
        pre=P+L;post=R+X8+P
        need(ph.signature(pre+raw_forward+post)==ph.signature(D8),'independent full signed phase promoted positiveD8 alias')
        need(all(g[0]in('P','D','X','phase')for g in pre+post),'promoted aliases only ordinary monomials')
        need(ph.signature(pre+raw_forward+post+(('phase',2),))!=ph.signature(D8),'promoted target phase mutant rejected')
        controls.append({'name':'promoted D8 absolute phase changed','birth_layout':start,'rejected':True})
        # Omitting the active-axis permutation must fail: canonicalC8 uses0..7.
        need(ph.signature(L+raw_forward+R+X8)!=ph.signature(D8),'canonicalC8 cannot be substituted for D_axes1..8')
        controls.append({'name':'promoted canonicalC8 axes mistaken for D8 axes','birth_layout':start,'rejected':True})
        promoted_aliases.append({'owners':selected,'source_entry_chart':start,'source_exit_chart':1,'source_entry_basis':c['frames'][start],'source_exit_basis':c['frames'][1],'rank':8,'positive_target_axes':list(range(1,9)),'raw_forward_word':raw_forward,'pre_input_monomial_word':pre,'post_output_monomial_word':post,'actual_backward_orientation':'bar(Fout) bar(Fin)^-1','construction':'From Uinv=L Cr8 R derive U=R^-1 Cr8^-1 L^-1; pre=L P^-1,post=P X8 R, P swaps0and8','coupled_mode_inputs_touched':False})
    remain=owners-promoted;remaining_profile=Counter(len(c['frames'][c['final'][j]])-len(c['frames'][c['start'][j]])for j in remain)
    need(remaining_profile==Counter({9:318,8:39,7:7,4:28}),'392 remaining autonomous targets after promotion debit')

    document={'schema':'current400-inverse-positive-helper-aliases/v1','status':'INDEPENDENT_SIGNED_PHASE_AND_FULL_ANCHOR_VERIFIED','source_inverse_head':'123ffa6aa7c1866ac60c67739841f71d95b3edf7','raw_orientation':'bar(Fin) bar(Fout)^-1','program_policy':'Apply listed pre_input map to each named autonomous helper before the WHOLE inverse invocation and listed post_output map after it. Main240directions remain untouched. No partial native job normalization.','promoted8_forward_D8_alias_groups':promoted_aliases,'promoted8_pre_input_maps':[{'op':'MONOMIAL','owner':r,'word':a['pre_input_monomial_word'],'whole_job_boundary':'before original autonomous sourcejob becomes part of120main ABI'}for a in promoted_aliases for r in a['owners']],'promoted8_post_output_maps':[{'op':'MONOMIAL','owner':r,'word':a['post_output_monomial_word'],'whole_job_boundary':'after original autonomous sourcejob, before coupling main correction'}for a in promoted_aliases for r in a['owners']],'promotion_admission_boundary':'Promoted8become main coordinates and lose their8H8autonomous targetcredit. Remaining392aliases exclude theseowners. Original400inverse list is an alternative contract, not combined productive credit.','remaining392_inverse_pre_input_maps':[{'op':'MONOMIAL','owner':r,'word':a['pre_input_monomial_word']}for a in aliases for r in a['owners']if r in remain],'remaining392_inverse_post_output_maps':[{'op':'MONOMIAL','owner':r,'word':a['post_output_monomial_word']}for a in aliases for r in a['owners']if r in remain],'remaining392_forward_pre_input_maps':[{'op':'MONOMIAL','owner':r,'word':a['forward_pre_input_monomial_word']}for a in aliases for r in a['owners']if r in remain],'remaining392_forward_post_output_maps':[{'op':'MONOMIAL','owner':r,'word':a['forward_post_output_monomial_word']}for a in aliases for r in a['owners']if r in remain],'remaining392_profile':dict(remaining_profile),'groups':aliases,'pre_input_maps':[{'op':'MONOMIAL','owner':r,'word':a['pre_input_monomial_word'],'whole_job_boundary':'before complete inverse invocation'}for a in aliases for r in a['owners']],'post_output_maps':[{'op':'MONOMIAL','owner':r,'word':a['post_output_monomial_word'],'whole_job_boundary':'after complete inverse invocation'}for a in aliases for r in a['owners']],'owner_count':400,'normalizer_field_maps':800,'positive_profile':dict(ranks),'recursive_calls_added':0,'owned_fields_added':0,'norm_geometry':'Both pre/post maps are square unitary signed monomials; arbitrary spectator tensor columns preserved.','all_width':'Exact phase-bearing nine-axis operator identities tensor columnwise at every positive width; coefficients remain native unit phases, no exterior scalar/tensor phase substitution.'}
    need(not args.aliases.exists()and not args.output.exists(),'immutable alias outputs exist');args.aliases.write_text(json.dumps(document,indent=2)+'\n')
    result={'schema':'independent400inversehelperaliasreview/v1','status':'PASS_17_INVERSE_CLASSES_AND_2_PROMOTED_FORWARD_D8_CLASSES','layouts':17,'actual_current_owners':400,'promoted_forward_D8_layouts':2,'promoted_main_owners':sorted(promoted),'promoted_normalizer_field_maps':16,'remaining392_profile':dict(remaining_profile),'promotion_target_debit':{'8':8},'profile':dict(ranks),'normalizer_field_maps':800,'normalizer_primitive_gate_occurrences':dict(monomial_gates),'additional_Gaussian_calls':0,'additional_owned_fields':0,'controls':controls,'independence':'Source lower_child proposes L/R only. Independent retained phase_exact constructs actual raw inverse from source chart bases and checks full signedPauli + complete zero column including absolute phase. No author/candidate evaluator as oracle, no native provider replay.','source_hashes':{str(x.relative_to(BASE)):sha256(x.read_bytes()).hexdigest()for x in[PH,CE,cp,pp]},'checker_sha256':sha256(Path(__file__).read_bytes()).hexdigest(),'aliases_sha256':sha256(args.aliases.read_bytes()).hexdigest(),'remaining':'Whole caller must actually install all800maps and pay movement/storage/normalizer tariffs and precision. This component is not a complete globalcaller or newkappa.','complete_caller':False,'new_kappa':None}
    args.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,sort_keys=True))

if __name__=='__main__':main()
