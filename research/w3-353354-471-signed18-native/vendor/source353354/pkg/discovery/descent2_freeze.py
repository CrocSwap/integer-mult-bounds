"""Freeze descent2-selection.json from a desc2_search output. usage: freeze.py postsink.pkl search.json OUT"""
import sys,pickle,json,hashlib
D=pickle.load(open(sys.argv[1],'rb'));S=json.load(open(sys.argv[2]))
ph=D['physical'];mass=sum(int(r)*c for r,c in ph['paid_histogram'].items())
sel=dict(status='FROZEN_POST_SINK_CONCAVE_DESCENT_FRAME_SELECTION',input_raw_sha256=hashlib.sha256(D['records']).hexdigest(),input_scalar_sha256=ph['scalar_projection_sha256'],
 source_record_count=S['source_record_count'],selected_gate_count=S['selected_gate_count'],move_types=S['moves'],expected_local_histogram_delta=S['local_delta'],expected_rank_mass=mass,
 expected_removed_calls=S['removed_calls'],expected_scalar_additions=ph['weighted_scalar_events'],predicted_local_phi_change=S['dL_local'],
 provenance="Derived on the post-sink word by discovery/descent2_search.py: greedy descent of sum r*ln(100/r) (PR #287's rule, rohanarun) with single-gate moves to operand-chain frames and constructed minimal-join / maximal-meet frames (PR #291), join with the operand span, and chain-adjacent pair/triple blocks moved to one common frame (PR #270-style connected blocks). Prepared with Anthropic Claude assistance.",
 entries=[{k:e[k] for k in ('record','scalar','category','old_dimension','old_basis_sha256','new_basis','new_dimension','constructed')} for e in S['entries']])
open(sys.argv[3],'w').write(json.dumps(sel,indent=1)+'\n');print('frozen',sel['selected_gate_count'],sel['expected_local_histogram_delta'],sel['expected_removed_calls'])
