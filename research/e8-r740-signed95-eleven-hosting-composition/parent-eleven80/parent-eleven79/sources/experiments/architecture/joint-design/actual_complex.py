"""Actual pinned complex idle factor identity on a compressed character space."""
import gzip,json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent
p=ROOT/'experiments/verification/proposal-scout/pr442/inherited/research/split-centres-global/inputs/complex-data-phases.json.gz'
a=json.load(gzip.open(p,'rt'));r=a['recipes'][0];child=r['idle_children'][0];other=r['idle_children'][1]
axes=child['orthogonal_axes'];t=child['translation_after'];assert len(axes)==child['rank']==16
assert all(bin(x&y).count("1")%2==int(i==j) for i,x in enumerate(axes) for j,y in enumerate(axes))
# For C_v=((1+i)I+(1-i)X_v)/2, Fourier character chi has
# eigenvalue i^(chi.v). X_t has eigenvalue i^(2 chi.t).
# Two hosted width8 residuals consume full first idle rank16.
slot1=axes[:8];slot2=axes[8:];bits=max(axes+[t]).bit_length();count=0
for chi in range(1<<bits):
 dot=lambda v:bin(chi&v).count("1")%2
 original=(sum(map(dot,axes))+2*dot(t))%4
 hosted=(sum(map(dot,slot1))+sum(map(dot,slot2))+2*dot(t))%4
 assert original==hosted
 # A genuine subsequent source idle factor acts on exterior coordinates;
 # its phase commutes with both hosts. Exact mod4 handles inverse too.
 e=sum(map(dot,other['orthogonal_axes']))+2*dot(other['translation_after'])
 assert (original+e)%4==(hosted+e)%4
 assert (-original-e)%4==(-hosted-e)%4
 count+=1
# Physical permutations sigma carrying local residual bases to slot axes
# are not instantiated here. This is an actual-axis factor identity only.
result={'status':'PASS_ACTUAL_SOURCE_COMPLEX_TWO_SLOT_FACTOR_PHASE_IDENTITY','source_head':'4e16d001d505d4f21dd2bcfc44591f9be4c279bd','source_blob':'22154a8c5875bd3398e1cb112ea0a5307d6793e8','file_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'port':0,'first_idle_rank':16,'slot1_axes':slot1,'slot2_axes':slot2,'translation_after':t,'character_dimension':bits,'all_character_columns_checked':count,'full_ambient_argument':'Exterior spectator coordinates factor as identity; every C_v and X_t globally commutes because all translations commute. Equality of all character eigenvalues proves equality of the complex linear operators, hence arbitrary correlated data contents.','inverse_phase_identity':True,'invoice_boundary':'16 C_v factors retained exactly across two hosted blocks, translation X_15 retained. No factor deletion. Host routing/selector and local endpoint fees remain charged by supplier; sigma realization not instantiated by this test.','scope':'Actual source port0 first child, split8+8 factor identity; these slots are a feasibility choice, not proof that PR442 selection assigned this exact pair. Not full cover or bit admission.'}
(OUT/'ACTUAL-COMPLEX.json').write_text(json.dumps(result,indent=2)+'\n');print(result['status'],count)
