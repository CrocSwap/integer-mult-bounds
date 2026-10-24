"""One physical centre0 source derivation; no producer/caller execution/emitter."""
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter
import json,subprocess,gzip,os,hashlib
P=Path(__file__).resolve().parent;HEAD='86e474038e05f99a76d41f71d81946ad2327e4a4';REPO=P.parent.parent/'integer-mult-bounds';BASE='research/native-involutive-dual/'
def read(n):return subprocess.check_output(['git','-C',str(REPO),'show',HEAD+':'+BASE+n],env=os.environ|{'GIT_NO_LAZY_FETCH':'1'})
old=json.loads((P/'INITIAL-DERIVATION.json').read_text());a=json.loads(gzip.decompress(read('INVOLUTIVE-WORD.json.gz')));s=json.loads(gzip.decompress(read('SOURCE-WORD.json.gz')));R=[[Q(x)for x in row]for row in json.loads(read('R.json'))];J=a['selected_ports'];c=a['canonical'];ip=a['program'];
U=[[(1-12*(i in J))*R[k][i]/4 for k in range(8)]for i in range(112)]
G=[[Q(i==j)-sum(U[i][k]*R[k][j]for k in range(1,8))for j in range(112)]for i in range(112)]
F=[[Q(v)for v in row]for row in a['F']]
assert all(G[i][j]==F[i][j]+U[i][0]*R[0][j]for i in range(112)for j in range(112))
assert all(sum(R[k][i]*U[i][l]for i in range(112))==2*(k==l)for k in range(8)for l in range(8))
start=6596+len(s['programs']['forward']);retunes=[]
for z,i in enumerate(J):
 b=ip[start+57*z:start+57*(z+1)];assert len(b)==57
 coeff={e[1][2][1]:Q(e[1][3],e[1][4])for e in b if e[0]=='scalar'and e[1][0]=='add'and e[1][1]==['C',0]}
 assert coeff=={j:3*sum(R[k][i]*R[k][j]for k in range(8))for j in range(112)if sum(R[k][i]*R[k][j]for k in range(8))}
 new={j:3*sum(R[k][i]*R[k][j]for k in range(1,8))for j in range(112)if sum(R[k][i]*R[k][j]for k in range(1,8))}
 change=[[j,str(coeff.get(j,Q())),str(new.get(j,Q()))]for j in sorted(set(coeff)|set(new))if coeff.get(j,Q())!=new.get(j,Q())]
 retunes.append({'port':i,'affected':bool(R[0][i]),'block_range':[start+57*z,start+57*(z+1)],'old_ADDs':len(coeff),'new_ADDs':len(new),'old_rank1_event':[e for e in b if e[0]=='center'][0],'new_rank1_event':'Retain same literal event and rank1 native circuit','coefficient_changes':change,'new_coefficients':{str(j):str(v)for j,v in new.items()}})
assert sum(r['affected']for r in retunes)==4
# Incoming/outgoing charts and autonomous endpoint census, all original fields.
helper_delta=Counter(len(c['frames'][c['final'][i]])-len(c['frames'][c['start'][i]])for i in range(224,632))
maincharts={'X_start':Counter(c['start'][:112]),'X_final':Counter(c['final'][:112]),'Y_start':Counter(c['start'][112:224]),'Y_final_dimensions':Counter(len(c['frames'][x])for x in c['final'][112:224])}
paid=Counter()
for e in ip:
 if e[0]=='climb':paid[e[5]]+=1
 elif e[0]=='center':paid[e[4]]+=1
assert paid==Counter({1:2209,2:412,3:510,4:127,5:40})
paid[8]+=1
# Actual helper input rows and centre suffix have no non-Y output, as initial
# extraction proves. Existing CODE normalizers remain literal, not scalarized.
row0=[str(v)for v in G[0]];col0=[str(row[0])for row in G]
x=[row[0]for row in G];xx=[sum(row[j]*x[j]for j in range(112))for row in G]
assert xx==[Q(i==0)for i in range(112)]
asym=next((i,j)for i in range(112)for j in range(i+1,112)if G[i][j]!=G[j][i])
result={'source_head':HEAD,'status':'SOURCE_DERIVED_ONE_CENTRE_RESTORE_ALL_EIGHT_RANK1_REPAIRS_RETAINED','formula':'G = I - U (I-e0e0^T) R = F + U[:,0] R[0,:]','U':'R^T/4 - 12P; P equals R^T/4 on selected rows J and zero elsewhere','selected_ports_J':J,'helper_precomp':'Use unchanged initial derivation update old - (R0^T/4) h0. 45 independent helper inputs;2520 coefficient deltas;7202 nonzero ground-chart ADDs.','source_restore':old['constructible_edit_spec']['center_restore'],'repair_retunes':retunes,'retained_rank1_calls':8,'paid_profile':dict(sorted(paid.items())),'repair_ADDs_old':sum(r['old_ADDs']for r in retunes),'repair_ADDs_new':sum(r['new_ADDs']for r in retunes),'full_independent_inputs':{'X':112,'Y':112,'helpers':408,'total':632,'helper_native_target_rank_profile':dict(sorted(helper_delta.items()))},'maincharts':maincharts,'row0':row0,'col0':col0,'e0_square_check':True,'first_asymmetry':{'i':asym[0],'j':asym[1],'Gij':str(G[asym[0]][asym[1]]),'Gji':str(G[asym[1]][asym[0]])},'F_actual':[[str(v)for v in row]for row in G],'scope':'Literal edit specification and algebra under authenticated inherited source. No emitted changed word, full native replay, caller integration, decoder, pricing/root, outer transfer or new kappa.'}
(P/'CORRECTED-DERIVATION.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items()if k not in ('F_actual','row0','col0','repair_retunes','maincharts')},indent=2))
# Source-bound raw-dual edits. The inverse-transpose literal source is a
# separate frozen program with conjugated native frames, never an unchanged
# forward native chart.
b=json.loads(gzip.decompress(read('BACKWARD-WORD.json.gz')));bp=b['program'];sp=s['programs']['backward'];bcenter=next(n for n,e in enumerate(sp)if e==['center',0,0,254,8])
assert bp[6596+bcenter]==['scalar',['clear',['C',0]],254]
# The backwards helper prelude is exactly minus the transpose of the forward
# prelude coefficient dictionary, and retuned backward tails use negative
# transpose rows at their actual conjugate physical exit frames.
fpre={};bpre={}
for e in ip[:6596]:
 g=e[1];fpre[(g[1][1],g[2][1])]=Q(g[3],g[4])
for e in bp[:6596]:
 g=e[1];bpre[(g[1][1],g[2][1])]=Q(g[3],g[4])
assert bpre=={(j,i):-q for(i,j),q in fpre.items()}
bretunes=[]
for z,r in enumerate(retunes):
 block=bp[start+57*z:start+57*(z+1)];assert block[2][0]=='center'and block[2][4]==1
 oldco={e[1][1][1]:Q(e[1][3],e[1][4])for e in block if e[0]=='scalar'and e[1][0]=='add'}
 fr=ip[start+57*z:start+57*(z+1)]
 fco={e[1][2][1]:Q(e[1][3],e[1][4])for e in fr if e[0]=='scalar'and e[1][0]=='add'and e[1][1]==['C',0]}
 assert oldco=={j:-q for j,q in fco.items()}
 bretunes.append({'port':r['port'],'block_range':r['block_range'],'center':block[2],'new_coefficients':{j:str(-Q(q))for j,q in r['new_coefficients'].items()},'fixed_order':'Clear owned C at conjugate(V_i);COPY unchanged Y_i;retained rank1 raising to conjugate(T);ADD negative retuned coefficients to X_j;clear owned C.'})
result['backward']={'endpoint':'X -> X - G^T Y; Y -> Y; all408helpers unchanged','source_restore':{'source_index':bcenter,'backward_word_index':6596+bcenter,'old':bp[6596+bcenter],'new':sp[bcenter]},'helper_precomp':'Each original backward coefficient is negative transpose of forward precomp. Apply negative transpose to all corrected forward coefficients;7202 ADDs, actual ground entrance frames.','repair_retunes':bretunes,'paid_profile':dict(sorted(paid.items())),'frames':'Retain actual entrywise-conjugate source frames; all8 existing rank1 raising circuits retained including absolute phases.'}
result['all_width_argument']='The inherited source identities hold over Q[FreeGroup72]. The centre0 input/output factorizations contain empty native words, with actual source frame254 -> ground and inverse-transpose ground -> frame254. New precomp/repair coefficients are dyadic scalar maps in actual common ground/full frames. Thus the exact counterpart extends to all positive column widths under the retained native implementation. Each of112 actual K_i normalizers is retained in diag(K_i)^-1 G diag(K_i); no commutation with central Q or scalar F substitution is asserted.'
result['normalizers_sha256']=hashlib.sha256(read('NORMALIZERS.json')).hexdigest()
(P/'CORRECTED-DERIVATION.json').write_text(json.dumps(result,indent=2)+'\n')
print('backward bound',result['backward']['source_restore'])
