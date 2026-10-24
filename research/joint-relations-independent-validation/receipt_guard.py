"""Bind newly generated checker outputs to both frozen literal-word claims."""
import hashlib,json
from fractions import Fraction as Q

def need(ok,msg):
    if not ok:raise ValueError(msg)
def fresh(root,name):return json.loads((root/name).read_bytes())
def positive(interval):return Q(interval[0])>0

def validate(root,claims,binding):
    indexed={c['pr']:c for c in claims['candidates']}; summaries={}
    for pr in (5383,5387):
        suffix='' if pr==5383 else '-5387';c=indexed[pr]
        a=fresh(root,f'agents/algebra/RESULT{suffix}.json')
        need(a['status']=='PASS_INDEPENDENT_JOINT_ALGEBRA','Partial algebra output')
        need((a['candidate_pr'],a['candidate_head'],a['candidate_payload_sha256'])==(pr,c['head'],c['word_payload_sha256']),'Algebra claim binding')
        need(a['relation_rank']==8 and a['all_16_unrestricted_identities_checked'] and len(a['source_identities'])==16,'Incomplete joint identities')
        need(a['simultaneous_snapshot_count']==8 and a['forward_entire_word_unchanged'] and a['canonical_operators_frames_unchanged'],'Incomplete literal word equality')
        need(a['candidate_replay']['independent_retained_inputs']==624 and a['candidate_replay']['arbitrary_owned_entry_inputs']==17,'Incomplete all-column algebra')
        need(a['independently_derived_pivots']==[225,227,229,230,241,245,257,c['last_pivot']],'Wrong retained-domain pivots')
        need(len(a['negative_controls'])==7,'Missing algebra controls')
        o=fresh(root,f'agents/ownership/RESULT{suffix}.json')
        need(o['status']=='PASS_EXACT_RUNTIME_OWNERSHIP' and o['candidate_head']==c['head'],'Incomplete candidate ownership')
        need(o['candidate_word_sha256']==binding['digests'][f"capsule/{'repository/'+c['package'] if pr==5383 else 'agents/sources/pr5387/'+c['package']}/WORD.json.gz"],'Owner output binds different word')
        for name,retained,owned in [('backward',624,17),('forward',632,1)]:
            item=o['result'][name];need(item['all_exact_endpoints_checked'] and item['all_owned_last_writes_are_clears'] and item['retained_arbitrary_columns']==retained and item['owned_arbitrary_columns']==owned,'Incomplete exact endpoints '+name)
        need(len(o['mutation_controls'])==12,'Missing owner controls')
        summaries[str(pr)]={'head':c['head'],'kappa':c['kappa'],'word_payload_sha256':c['word_payload_sha256'],'joint_rank':8,'retained':624,'owned':17}
    inv=fresh(root,'agents/prices/INVOICE.json');price=fresh(root,'agents/prices/RESULT.json')
    need(price['status']=='PASS_INDEPENDENT_EVENT_INVOICE_AND_EXACT_PRICES','Incomplete prices')
    need(inv['candidate_head']==indexed[5383]['head'] and inv['successor_head']==indexed[5387]['head'],'Invoice head identity')
    need(inv['candidate']['paid_calls']==64148 and inv['candidate']['productive_fields']==10800,'Incomplete invoice')
    need(inv['delta']=={'paid':{'1':-128,'8':-128},'targets':{'9':-128}},'Wrong complete invoice delta')
    need(price['invoice_sha256']==hashlib.sha256((root/'agents/prices/INVOICE.json').read_bytes()).hexdigest(),'Price/invoice mismatch')
    for label,c in [(f'PR{pr}',indexed[pr]) for pr in (5383,5387)]:
        v=price['variants'][label];need(Q(v['kappa'])==Q(c['kappa']) and positive(v['raw_margin']),'Price kappa/margin')
        need(Q(v['coarse_completed_upper'])<1 and Q(v['actual_completed_upper'])<1,'Unfunded completion')
    outer=fresh(root,'agents/outer/RESULT.json');need(outer['status']=='PASS_SCOPED_ARITHMETIC' and len(outer['candidates'])==2,'Incomplete outer replay')
    need({x['candidate'] for x in outer['candidates']}=={'PR5383','PR5387'},'Missing outer candidate')
    for o in outer['candidates']:
        c=indexed[int(o['candidate'][2:])];need(o['status']=='PASS_INDEPENDENT_OUTER_AND_FINITE_COMPILER_ARITHMETIC' and o['kappa']==c['kappa'],'Outer claim binding')
        need(Q(o['minimum_strict_slack'])>0 and all(o['compiler']['checks'].values()),'Outer/compiler failure')
        need(Q(o['BIT']['admitted'])==Q('17/5000'),'Wrong BIT supplier')
        # This checker publishes all strict and functional rows, not only a tally.
        rows=o['outer'];need(len(rows['strict_checks'])==54 and len(rows['functional_checks'])==4 and all(Q(v)>0 for v in [*rows['strict_checks'].values(),*rows['functional_checks'].values()]),'Incomplete 54+4 outer ledger')
    app=fresh(root,'run-6.stdout');need(app['status']=='PASS_SCOPED_APPLICABILITY_COUNTS_AND_GUARDS' and set(app['candidates'])=={'5383','5387'},'Incomplete applicability')
    for pr,c in app['candidates'].items():
        need(c['raw_controller_owned_LOCAL_banks']==274 and c['local']['backward']['owned']==17 and c['local']['backward']['simultaneous_snapshots']==8,'Incomplete expanded stock specialization')
        claim=indexed[int(pr)]; wordpath=f"capsule/{'repository/'+claim['package'] if pr=='5383' else 'agents/sources/pr5387/'+claim['package']}/WORD.json.gz"
        need(c['word_sha256']==binding['digests'][wordpath],'Applicability output binds a different word')
    mutants=fresh(root,'agents/falsifier/CONTROLS-FULL.json')
    need(mutants['status']=='PASS_SEMANTIC_MUTANTS_REJECTED' and len(mutants['controls'])==6,'Incomplete semantic falsification')
    need(all(x['status']=='REJECTED' and x['hash_changed'] and not x['old_digest_comparison_used_for_rejection'] for x in mutants['controls'].values()),'Semantic mutant was not independently rejected')
    return {'candidates':summaries,'paid':64148,'productive':10800,'outer_predicates_per_candidate':{'strict':54,'functional':4},'literal_same_premises':claims['assumptions']}
