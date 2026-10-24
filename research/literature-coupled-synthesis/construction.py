"""Compose candidate contracts without assigning zero to unknown work."""
from fractions import Fraction as F
from algebra import need,eye,mm,add,replay,coupled_program
from junction import check as check_junctions

def build(f):
    H=f.H;P=eye(120)
    for k in range(112,120):P[k][k]=0
    # The real controller changes main fields and leaves helpers alone. A
    # whole-encoded-bank ADD silently changes eight independent helper inputs.
    transport=mm(mm(H,P),H)
    need(mm(transport,transport)==transport,'transported restricted ADD is a projection')
    need(transport!=eye(120),'whole-bank ADD is not the actual controller ADD')
    W=f.W;Z=f.Z;WZ=mm(W,Z)
    expected=[]
    for i in range(112):
        expected.append([F(i==j)+12*WZ[i][j] for j in range(112)] + [-13*F(-4)*W[i][k] for k in range(8)])
    for k in range(8):expected.append([-13*3*Z[k][i] for i in range(112)]+[F(-168*(k==j)) for j in range(8)])
    need(transport==expected,'actual main-only ADD transport formula')
    # A concrete complete ordinary implementation is decode both 120-field
    # banks, ADD 112 main coordinates, and encode both. This is an upper bound,
    # not the desired fused implementation, and uses no fresh scratch.
    conservative={'ADD':4*1344+112,'SCALE':4*16,'MONOMIAL':4*240,'new_owned_fields':0,'paid_H':0}
    # Conditional local exit, fully verified on arbitrary adapter input columns.
    program=f.old.exit_program(f.m,'compressed')
    exit_check=f.old.check_exit_program(f.m,'compressed',program)
    local_contract=f.old.exit_contract(f.m)
    junctions=check_junctions(f.m)
    q=f.ce.cgate(9,1)
    lowered=q.then(f.ce.xgate(9,1));inverse_q=q.adjoint()
    need(lowered.tab==inverse_q.tab and lowered.zero_state()==inverse_q.zero_state(),
         'positive H1 plus bit translation lowers inverse query with exact phase')
    # Source-typed observer admission. A wrong owner, version or transform
    # cannot be silently substituted for b. This is a syntactic contract, not
    # a theorem that more complicated algebraic recovery is impossible.
    required=('Y_at_provider_exit','current','Z Q')
    candidates=[('conditional_joint_observer',required,'hypothesis'),
                ('existing_thin_query',('X_plus_neighbor','current','Q^-1'),'wrong_source_and_map'),
                ('forward_paid_helper_bank',('independent_xi','entrance','Q'),'wrong_source_and_version'),
                ('stale_Y_observer',('Y_at_provider_exit','previous','Z Q'),'wrong_version')]
    admission=[]
    for name,signature,status in candidates:
        accepted=signature==required
        need(accepted==(status=='hypothesis'),'typed observer control')
        admission.append({'candidate':name,'required_type_match':accepted,
                          'physical_supplier_proved':False,'reason':status})
    return {'status':'PARTIAL_CONSTRUCTION_WITH_EXPLICIT_OPEN_BRIDGE',
        'seed_boundary':{'fields':120,'main_fields':112,'arbitrary_mode_fields':8,
                         'formula':'H(a,b)=[[I-WZ,aW],[bZ,13I]], ab=-12',
                         'gauge':[-4,3],'program':'BALANCED-PROGRAM.json','involution':True},
        'common_frame_main_only_ADD':{'transformed_matrix':'H P H = [[I+12WZ,-13aW],[-13bZ,-168I]]',
                              'all_120_input_columns_checked':True,
                              'whole_bank_ADD_rejected':True,
                              'conservative_complete_ordinary_upper_bill':conservative},
        'required_compressed_exit':exit_check,
        'conditional_local_exit_identity':local_contract,
        'coupled_ADD_junctions':junctions,
        'observer_type_checks':admission,
        'composition_order':[
            'Preserve all 632 independent native originals and owned-zero return obligations.',
            'Use the balanced boundary on a declared 112+8 block; derive its place in the full 232-field X/Y/mode interface.',
            'Carry generation-tagged displacement/observation state through the first two backward FULLs and their actual thin contacts.',
            'Synthesize a two-sided native paid observer for current-version Z Q Y; retain the ordinary thin query unless displaced by proof.',
            'Use the verified catalytic ADD and retained-thin-query junctions when the declared block types match; prove their disjoint ownership and placement in the shared-helper native interface.',
            'Terminate every borrowed history value and restore original targets using one shared recursive allowance.',
            'Compile precision, tape motion, volume, endpoints and ordinary work; then run independent outer admission.'],
        'stop_conditions':[
            'Stop a candidate if its observer plus termination exceeds the exact source-relative moment allowance.',
            'Stop eight-mode stationary rebasing: the second-generation witness already rejects it.',
            'Stop one-shared-Gaussian passive aggregation in the measured right-coset model: all 112 columns differ.',
            'Do not pursue a kappa claim until unknown supplier/compiler/admission costs are discharged.'],
        'new_kappa':None}
