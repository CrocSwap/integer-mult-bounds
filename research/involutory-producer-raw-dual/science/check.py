#!/usr/bin/env python3
"""One physical source-restored4935 raw dual. Apache-2.0; Codex assistance.
Pinned sources are read only. This script writes only here with --emit.
"""
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter
from hashlib import sha256
import ast,gzip,json,subprocess,sys,types
HERE=Path(__file__).resolve().parent
P4935='64c9f99693c92fb370096fb43dbc58a085b30e36'
P4929='361f5d4100640177d6a983dd2f336021c75bfd5e'
NATIVE='20bb93cd990d2ff683e4d0fc56b87a42cd5d3296'
PORTS=[0,7,20,23,86,93,108,111]
SPECS={
 'forward':(P4935,'research/native-involutive-port-transfer/INVOLUTIVE-WORD.json.gz'),
 'R':(P4935,'research/native-involutive-port-transfer/R.json'),
 'proof':(P4935,'research/native-involutive-port-transfer/PROOF.md'),
 'source4935':(P4935,'research/native-involutive-port-transfer/SOURCE-WORD.json.gz'),
 'coded':(P4929,'research/native-center-free-code/CODED-WORDS.json.gz'),
 'core':(P4929,'research/native-center-free-code/native_core.py'),
 'code':(P4929,'research/native-center-free-code/CODE.json'),
 'original':(NATIVE,'research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz'),
 'ce':(NATIVE,'research/t74-native-fast/vendor/native/new/code/borrow/vendor/clifford/clifford_exact.py'),
 'prune':(NATIVE,'research/kappa-function-composition/complex/prune_native.py'),
}
def need(c,m):
 if not c:raise ValueError(m)
def fetch(pin,path):return subprocess.check_output(['git','--no-replace-objects','show',pin+':'+path])
def module(name,data):
 m=types.ModuleType(name);m.__file__=name+'.py';sys.modules[name]=m
 exec(compile(data,name+'.py','exec'),m.__dict__);return m
def encode(x):return (json.dumps(x,indent=2,sort_keys=True)+'\n').encode()
def main():
 raw={k:fetch(*v)for k,v in SPECS.items()}
 need(sha256(raw['original']).hexdigest()=='7679daa4ec6a40f56fc7f0202379a6f454310e94945aba4f48beaaaafb838d05','native source hash')
 need(sha256(raw['R']).hexdigest()=='7b33b6dfb494c6eafe6d87a08d6a2c2e0681e56429495b2b27949040f0f63cd1','4935 R source hash')
 need(sha256(raw['ce']).hexdigest()=='2982ead07721e83358dc67c6f49c2b4c16a236a6bebdfd72f58221be1f5d0962','native compiler hash')
 need(gzip.decompress(raw['source4935'])==gzip.decompress(raw['original']),'4935 exact underlying source')
 V=module('rawdual4935_native_core',raw['core']);ce=module('rawdual4935_exact',raw['ce'])
 definitions=[x for x in ast.parse(raw['prune']).body if isinstance(x,ast.FunctionDef)and x.name=='conjugate']
 env={};exec(compile(ast.Module(body=definitions,type_ignores=[]),'pinned_conjugate','exec'),env)
 bar=lambda op:env['conjugate'](ce,op)
 forward=json.loads(gzip.decompress(raw['forward']));coded=json.loads(gzip.decompress(raw['coded']));original=json.loads(gzip.decompress(raw['original']))
 c=coded['canonical'];need(c['frames']==original['canonical']['frames'] and c['start']==original['canonical']['start'] and c['final']==original['canonical']['final'],'native boundary identity')
 need(forward['canonical']==c or all(forward['canonical'][k]==c[k]for k in ('frames','start','final','ports')),'4935 unchanged physical boundaries')
 need(forward['selected_ports']==PORTS,'source-restored selected ports')
 A=[[Q(x)for x in row]for row in json.loads(raw['code'])['A']]
 F=[[Q(x)for x in row]for row in forward['F']]
 R=[[Q(x)for x in row]for row in json.loads(raw['R'])]
 correction=[[12*sum((R[k][j]/4)*R[k][i]for k in range(8)) if j in PORTS else Q(0)for i in range(112)]for j in range(112)]
 need(F==[[A[j][i]+correction[j][i]for i in range(112)]for j in range(112)],'exact source-restored F=A+12PR')
 need(F!=[list(x)for x in zip(*F)],'transpose distinction is nontrivial')
 def target(matrix,back):
  out=[V.identity(i)for i in range(632)]
  for j in range(112):
   for i,v in enumerate(matrix[j]):
    if v:V.add(out[i]if back else out[112+j],V.identity(112+j)if back else V.identity(i),-v if back else v)
  return out
 oldrows,oldpaid,oldmax=V.replay(c,coded['programs']['backward'],True)
 need([oldrows[i]for i in range(632)]==target(A,True),'fresh all632 coded backward endpoint')
 frows,fpaid,fmax=V.replay(forward['canonical'],forward['program'],False)
 need([frows[i]for i in range(632)]==target(F,False),'fresh all632 source-restored4935 forward endpoint')
 suffix=[];lifts=[];allcoeff=[]
 for j in PORTS:
  fi=c['final'][112+j];need(c['final'][:112]==[1]*112,'common full X exits')
  # Chronological inverse source-Y frame then full frame, then actual bar.
  op=bar(ce.canonical_frame(9,c['frames'][fi]).adjoint().then(ce.canonical_frame(9,c['frames'][1])))
  cert,compiled=ce.lower_child(op)
  need(cert['rank']==1 and op.tab==compiled.tab and op.zero_state()==compiled.zero_state(),'raw-dual lifting including global phase')
  lifts.append({'port':j,'source_owner':112+j,'from':fi,'to':1,'rank':1,'lowering':cert,'literal_circuit':compiled.circuit,'actual_raw_dual_conjugation':True})
  suffix += [['scalar',['clear',['C',0]],fi],['scalar',['copy',['C',0],['L',112+j]],fi],['center',0,fi,1,1]]
  for i,v in enumerate(correction[j]):
   if v:
    z=-v;allcoeff.append(z);suffix.append(['scalar',['add',['L',i],['C',0],z.numerator,z.denominator],1])
  suffix.append(['scalar',['clear',['C',0]],0])
 program=coded['programs']['backward']+suffix
 rows,paid,maxnorm=V.replay(c,program,True);expected=target(F,True)
 need([rows[i]for i in range(632)]==expected,'all632 exact rawinverse-transpose endpoint')
 need(all(rows[i]==V.identity(i)for i in range(112,632)),'Y and all408 independent helpers unchanged logically')
 need(paid==Counter({1:2209,2:412,3:510,4:127,5:40}) and paid==fpaid,'complete paid profile matches forward')
 need(Counter(map(str,allcoeff))==Counter({'-12':8,'-6':268,'6':148}),'424 fixed dyadic scatter coefficients')
 # Every coefficient of the normalized transpose product is checked directly:
 # forward upper/lower shear cancellation is exact with arbitrary F.
 need(all(expected[i].get((112+j,()),Q(0))+F[j][i]==0 for i in range(112)for j in range(112)),'all12544 transpose coefficients')
 controls={}
 bad=json.loads(json.dumps(program));k=next(i for i in range(len(coded['programs']['backward']),len(bad))if bad[i][0]=='scalar'and bad[i][1][0]=='add');bad[k][1][3]*=-1
 rr,_,_=V.replay(c,bad,True);controls['repair_sign']=any(rr[i]!=expected[i]for i in range(632))
 bad=[e for e in program if not(e[0]=='center'and e[4]==1)]
 try:V.replay(c,bad,True)
 except ValueError:controls['omit_rank1_lift']=True
 else:controls['omit_rank1_lift']=False
 controls['wrong_transpose']=expected!=target([list(x)for x in zip(*F)],True)
 controls['erase_repair']=any(oldrows[i]!=expected[i]for i in range(632))
 need(all(controls.values()),'semantic controls')
 artifact={'schema_version':1,'scope':'Source-restored4935physicalrawdual; source-mutatingvariant excluded','canonical':c,'program':program,'selected_ports':PORTS,'target_F':[[str(x)for x in row]for row in F],'native_lifts':lifts,'repair_suffix':suffix}
 artifact=json.loads(json.dumps(artifact));word=gzip.compress(json.dumps(artifact,sort_keys=True,separators=(',',':')).encode(),mtime=0)
 tariff=lambda z:3+abs(z.numerator).bit_length()-1+abs(z.numerator).bit_count()+z.denominator.bit_length()-1
 result={'status':'PASS_ONE_ACTUAL632_SOURCE_RESTORED_RAWDUAL_NOT_CALLER','pins':{'4935':P4935,'4929':P4929,'native':NATIVE},'arbitrary_original_inputs':632,'independent_helpers_retained':408,'Y_owners_retained':112,'source_X_mutation':False,'owned_C0_final_zero':True,'extra_owned_arrays':0,'added_rank1_calls':8,'paid':dict(paid),'source_backward_paid':dict(oldpaid),'source_backward_prefix_l1':str(oldmax),'new_prefix_l1':str(maxnorm),'forward_prefix_l1':str(fmax),'events':len(program),'suffix_events':len(suffix),'suffix_census':{'COPY':8,'CLEAR':16,'GaussianH1':8,'ADD':424},'scatter_coefficient_counts':dict(Counter(map(str,allcoeff))),'scatter_scalar_primitive_allowance':sum(tariff(z)for z in allcoeff),'single_word_phase_checks':8,'all12544_transpose_coefficients_checked':True,'all632_forward_and_backward_rows_checked':True,'word_sha256':sha256(word).hexdigest(),'controls':controls,'new_kappa':False,'full_caller':False,'compiler_or_outer_funded':False}
 sources={'schema_version':1,'consumed':{k:{'commit':SPECS[k][0],'path':SPECS[k][1],'sha256':sha256(v).hexdigest()}for k,v in raw.items()},'checker_sha256':sha256(Path(__file__).read_bytes()).hexdigest()}
 outputs={'RAWDUAL-WORD.json.gz':word,'RESULT.json':encode(result),'SOURCES.json':encode(sources)}
 for name,data in outputs.items():
  if '--emit' in sys.argv:(HERE/name).write_bytes(data)
  else:need((HERE/name).read_bytes()==data,'frozen bytes '+name)
 print(json.dumps(result,sort_keys=True))
if __name__=='__main__':main()
