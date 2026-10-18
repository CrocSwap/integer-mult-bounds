#!/usr/bin/env python3
"""Verify the frozen E8 low-read package and exact receipts."""
from pathlib import Path
import hashlib,json,tarfile,subprocess,sys
from fractions import Fraction as F
D=Path(__file__).resolve().parent
rd=lambda p:json.loads((D/p).read_text())
sha=lambda p:hashlib.sha256((D/p).read_bytes()).hexdigest()
def req(x,msg): assert x,msg
for line in (D/'MANIFEST.sha256').read_text().splitlines():
    h,rel=line.split('  ',1); assert sha(rel)==h, rel
r=rd('proof/price/kappa.json'); req(r['kappa']=='3618278388573/4000000000000000','kappa')
req(r['binding']=='bit' and r['bit_coarse']=='905388584776183/1000000000000000000','bit rate')
f=rd('proof/price/finite.json'); req(f['coefficient']==1916288151501 and f['coefficient_bits']==41,'finite coefficient')
req(f['positive_rank_children']==22020 and f['rank_mass']==53680 and f['payload_prefix_bits']==60,'finite profile')
leg=rd('proof/check/leg.json'); col=rd('proof/check/col.json')
req(leg['status']=='PASS_INDEPENDENT_COHORT_LEGALITY_SOURCE_OWNERS_AND_LIFECYCLE','legality')
req(leg['copies']==9 and leg['erasures']==9 and leg['rank_mass']==8672,'ledgers')
req(col['status']=='PASS_NEW_COHORT249_ALL_FIVE_STAGE_FORMAL_COLUMNS_AND_PREFIX_BILL','columns')
req(col['formal_columns_checked']==1345 and col['independent_dirty_registers']==865,'columns dims')
sig=rd('proof/signed-source/RESULT.json'); req(sig['status']=='PASS_EXACT_SIGNED_DEFINING_DECODER_AND_LITERAL_PARITY_PROJECTION','signed')
req(sig['arbitrary_helper_dirt_restored_exactly'] and sig['forward_then_signed_inverse_identity'] and sig['target_decoder_mod2_identity'],'signed dirt')
req(sig['forward_and_reflected_ledgers'][0]==sig['forward_and_reflected_ledgers'][1],'reflected ledgers')
ch=rd('geometry/CHART-RECEIPT.json'); req(ch['status']=='PASS_ALL_E8_MOVE_COPY_PROJECTORS_AND_REFLECTED_CHARTS','charts')
req(ch['all_frame_projectors']==944 and ch['unique_move_copy_gaps']==3334 and ch['max_chart_factors']<=22,'chart bounds')
lo=rd('geometry/lowering/LOWERING-BANKS.json'); req(lo['status']=='PASS_SOURCE_BOUND_E8_FIVE_STAGE_LOWERING_AND_ACTUAL_BANK_ASSIGNMENT','lowering')
req(lo['linked_move_charts']==4203 and lo['paid_calls']==22020 and lo['rank_mass']==53680 and lo['deficit']==120,'lowering linkage')
req(sha('geometry/lowering/GLOBAL-PROGRAM.bin')==lo['program_sha256'],'program hash')
cx=rd('complex/b3.json'); gx=rd('complex/complex-guard-b3.json'); req(cx['b']=='932783231884153/1000000000000000000' and gx['status'].startswith('PASS_'),'complex')
rec=rd('proof/REPLAY-RECEIPTS.json'); req(all(v['actual_exit']==0 for v in rec.values()),'observed exits')
full=rd('provenance/FULL-REPLAY-RECEIPTS.json'); req(full['status']=='PASS_TWO_FRESH_COMPLETE_SOURCE_REPLAYS_OBSERVED_EXIT0','full replays')
req(full['cp312']['actual_exit']==0 and full['cp311']['actual_exit']==0 and full['cp312']['kappa']==full['cp311']['kappa']=='875481145306751/1000000000000000000','replay equality')
req(full['source_tar_sha256']==sha('provenance/lowread-full-replay-source.tar.gz'),'replay source tar')
req(sha('source/candidate-certificate.tar.gz')=='827c0b6859f2b1ff7e5f5fbac955d61ecb25c828e7a0ff4dbc279ba6854d6a9d','candidate archive')
# Re-run the exact assembly and require its receipt.
subprocess.run([sys.executable,str(D/'assemble.py')],check=True)
asm=rd('proof/assembly.json'); req(asm['status']=='PASS_EXACT_47_CONSTRAINT_ASSEMBLY' and asm['adjacent_grid_point_rejected'],'assembly')
print('PASS E8 low-read seven-stage-complex package',r['kappa'])
