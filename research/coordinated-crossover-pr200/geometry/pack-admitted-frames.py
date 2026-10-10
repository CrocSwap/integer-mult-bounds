"""Compose admitted frame-only changes with concrete stage-private entrance banks.
Reconstructs every modified frame/physical paid chain, audits all actual prime
witnesses, and independently recomputes two exact paid bank moment engines.
The referenced frame receipt provides the full dirty-column terminal replay.
"""
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter
import sys,json,gzip,hashlib,argparse,importlib.util
sys.set_int_max_str_digits(0);sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('geometry_bank_pr200',HERE/'pack-pr200.py');G=importlib.util.module_from_spec(spec);spec.loader.exec_module(G)
need=G.need
ap=argparse.ArgumentParser();ap.add_argument('--candidate',required=True);a=ap.parse_args()
D=Path(a.candidate);record=json.loads((D/'checked/verification.json').read_text());frames=D/'opframe-bases.json';primefile=D/'checked/prime-witnesses.json.gz'
need(record['status']=='FULL_FINITE_REPLAY_PASS','complete independent frame dirty-word admission')
for path,want in record['input_pins'].items():need(hashlib.sha256(Path(path).read_bytes()).hexdigest()==want,'actual immutable input pin '+path)
need(record['word_scalar_ops_unchanged'] and record['gauge_endpoint_and_aliases_unchanged'],'unchanged whole-word endpoint classes')
word=G.proof.Candidate();before={k:word.w[k] for k in ['gauges','pairs','rootroles','root_frame','source_frame','sources','reads']};changes=json.loads(frames.read_text())
for index,B in changes:word.opframe[index]=word.register(B)
word.changed_frames=[i for i,(x,y) in enumerate(zip(word.original_opframe,word.opframe)) if x!=y];word.endframe={s:word.opframe[xs[-1]] for s,xs in word.role_ops.items()}
word.exact_frames();row=word.row()
need(G.encode(row)==record['baseline_profile'],'independent complete modified physical baseline ledger')
need(before=={k:word.w[k] for k in before},'bank source/gauge/endpoints truly unchanged')
need(Counter({int(k):v for k,v in record['terminal']['child_delta'].items()})==Counter({3:-102,21:-102}),'paid34terminal child substitution unchanged')
H={int(k):v for k,v in row['child_histogram'].items()};H[3]-=102;H[21]-=102
need(H=={int(k):v for k,v in record['profile']['child_histogram'].items()},'independent terminal-paid complete histogram')
prime=G.raw_prime_certificate(word);need(prime==json.loads(gzip.decompress(primefile.read_bytes())),'independent allused modifiedframe prime witness audit')
packed=G.packed(record['profile'],word.w);coarse=G.proof.certify(packed['scaled_moment_profile'])
from base_two_moment import moment as alternate
q=packed['scaled_moment_profile'];hist=list(q['child_histogram'].items());W=q['W_per_vertex'];a0=coarse['coarse_saving'];fallback=32*72**2*sum(n for r,n in hist)
_,upper=alternate(72,W,hist,a0);_,bad=alternate(72,W,[(1,fallback)],a0);need(upper+Q(1,10**16)*bad<1,'independent paid moment accepted')
lower,_=alternate(72,W,hist,a0+Q(1,10**18));badlower,_=alternate(72,W,[(1,fallback)],a0+Q(1,10**18));need(lower+Q(1,10**16)*badlower>1,'independent adjacent paid moment rejected')
allocation=G.literal_allocation(word.w);endpoints=G.endpoint_checks()
for path,want in record['input_pins'].items():need(hashlib.sha256(Path(path).read_bytes()).hexdigest()==want,'inputs remain identical')
out=dict(status='PASS_ADMITTED_FRAME_BANK_COMPOSITION',frame_receipt_sha256=hashlib.sha256((D/'checked/verification.json').read_bytes()).hexdigest(),opframe_override_sha256=hashlib.sha256(frames.read_bytes()).hexdigest(),opframe_changes=len(changes),profile=packed,coarse=coarse,literal_allocation=allocation,endpoints=endpoints,prime_witness_sha256=hashlib.sha256(primefile.read_bytes()).hexdigest(),all_used_frame_prime_audit={k:v for k,v in prime.items() if k!='frame_witnesses'},whole_word_receipt=record['status'],unchanged_entrance_alias_and_terminal_classes=True,scope='Sufficient finite dirty-bank composition of independently admitted full frame word. Original allsize supplier interfaces retained; parent owns finalbalanced assembly.')
name='packed-'+D.name+'.json';(HERE/name).write_text(json.dumps(G.encode(out),indent=2,sort_keys=True))
print(json.dumps(G.encode(dict(status=out['status'],output=str(HERE/name),changed_ops=len(changes),stock=packed['W_per_vertex'],rank=packed['rank_per_vertex'],coarse=coarse['coarse_saving'],ordinary=coarse['ordinary_saving'],ordinary_float=float(coarse['ordinary_saving']),frames=prime['total_used_frames'])),indent=2))