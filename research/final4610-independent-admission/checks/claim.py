"""Bind the presented CLAIM to the actual audited source and selected baseline.
Apache-2.0; substantial OpenAI Codex assistance. Metadata is not an admission proof.
"""
from copy import deepcopy
from fractions import Fraction as F
import gzip,json
from . import source
HEAD='20bb93cd990d2ff683e4d0fc56b87a42cd5d3296'
WORD='cfcd36b40326d7a5815e1db5313444379b3fb756b27d5201c561574c085cc0dd'
PATH='research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz'

def validate(claim,selected,payload):
    need=source.need
    need(claim['candidate_head']==HEAD,'claim candidate attribution head')
    need(payload==claim['word_payload_sha256']==WORD,'claim does not identify audited native payload')
    need(F(claim['baseline_selected_kappa'])==F(selected['kappa']),'claim baseline selected kappa')
    need(F(claim['baseline_selected_decimal'])==F(selected['decimal'])==F(selected['kappa']),'claim baseline selected decimal')
    need(claim['assumptions']==selected['assumptions'],'candidate silently changed selected assumptions')
    need(F(claim['kappa'])==F('0.0030217758'),'claim audited candidate kappa')
    need(F(claim['kappa'])-F(selected['kappa'])==F(claim['gain_over_selected'])==F('0.0000016258'),'exact claimed gain')
    need(F(claim['decimal'])==F(claim['kappa']) and F(claim['gain_decimal'])==F(claim['gain_over_selected']),'claim decimal encodings')
    need(claim['same_selected_assumptions_required'] is True,'same-premise scope flag')
    need(claim['selected_record_changed'] is False,'no selected-record update claimed')
    need(claim['new_unconditional_or_Lean_theorem'] is False,'no unconditional or Lean theorem claimed')
    need(claim['uniform_word_materialized'] is False,'no materialized uniform word claimed')

def run(claim):
    selected=source.js('certificates/selected-result.json')
    payload=source.digest(gzip.decompress(source.raw(PATH)))
    validate(claim,selected,payload)
    mutations=[('wrong_candidate_head',dict(candidate_head='0'*40)),
               ('wrong_payload',dict(word_payload_sha256='0'*64)),
               ('wrong_baseline_kappa',dict(baseline_selected_kappa='1/1000')),
               ('wrong_baseline_decimal',dict(baseline_selected_decimal='.001')),
               ('wrong_candidate_decimal',dict(decimal='.0032')),
               ('wrong_gain',dict(gain_over_selected='1/1000')),
               ('changed_assumptions',dict(assumptions=claim['assumptions'][:-1])),
               ('unconditional_claim',dict(new_unconditional_or_Lean_theorem=True)),
               ('claimed_selection_update',dict(selected_record_changed=True)),
               ('claimed_materialized_word',dict(uniform_word_materialized=True)),
               ('weakened_same_assumptions',dict(same_selected_assumptions_required=False))]
    controls=[]
    for name,patch in mutations:
        bad=deepcopy(claim);bad.update(patch)
        # Recompute the mutant's own bytes/hash: rejection must be semantic.
        mutant_hash=source.digest(json.dumps(bad,sort_keys=True,separators=(',',':')).encode())
        try:validate(bad,selected,payload)
        except ValueError as e:controls.append(dict(name=name,recomputed_mutant_sha256=mutant_hash,semantic_rejection=str(e)))
        else:raise ValueError('claim metadata mutation accepted '+name)
    return {'status':'PASS_CLAIM_IDENTIFIES_ACTUAL_AUDITED_CONSTRUCTION_AND_BASELINE','actual_payload_sha256':payload,'candidate_head':HEAD,'baseline_selected_kappa':selected['kappa'],'semantic_mutations_with_recomputed_hash':controls}
