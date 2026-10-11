from pathlib import Path
from collections import Counter
import gzip,json,hashlib
O=Path(__file__).resolve().parent;ROOT=O.parents[2];P=ROOT/'experiments/architecture/whole-owner-pooling-v4/bit60';f=P/'GLOBAL-TEMPLATE.json.gz';blob=gzip.decompress(f.read_bytes());T=json.loads(blob);assert hashlib.sha256(blob).hexdigest()=='c5e6d2524736e60586a2eb2d42caf4fab162c25120e4e0b2476f5266c287ec7d'
assert len(T['calls'])==88
counts=Counter();foreign=0
for call in T['calls']:
 s,r,p=call['stage'],call['replica'],call['pair'];counts[call['orientation']]+=1;owners=call['owners'];assert len(owners)==980
 for j,(family,route)in enumerate(owners[:240]):
  jj=(j+120)%240 if call['orientation']=='reverse' else j
  assert family==r*1200+p*240+jj and route==['data',s,j%120]
 for j,(family,route)in enumerate(owners[240:]):
  hostrep=family//1200;hostpair=(family%1200)//240;assert hostpair!=p and hostrep==call['helper_owner_replicas'][j];foreign+=hostrep!=r
 assert len({(family,tuple(route))for family,route in owners})==980
assert counts=={'forward':48,'reverse':40}
assert [(c['stage'],c['replica'])for c in T['calls']]==[(s,r)for s in range(11)for r in range(8)]
bridges=2*sum(e['kind']=='bridge'for e in T['schedule']);assert bridges==24
B=ROOT/'experiments/architecture/pr454-signed-extra-v4/with-prefix60/global/signed/GLOBAL-BOUND.json';B0=json.load(open(B));L=B0['local_majorants'];prefix=2**bridges*L['signed_forward']**6*L['signed_reverse']**5;assert prefix==int(B0['finite']['signed_prefix']) and prefix.bit_length()==159
out={'status':'PASS_CONDITIONAL_WHOLE_POOL_STAGE_CUT_PREFIX_LEMMA','template_sha256':hashlib.sha256(blob).hexdigest(),'template_file_sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'source_bound_sha256':hashlib.sha256(B.read_bytes()).hexdigest(),'calls':88,'foreign_owners':foreign,'literal_descriptor_injectivity_checked':True,'prefix':str(prefix),'prefix_bits':159,'allowed_bits':192,'conditions':['Every complete physical invocation preserves allprivatework and maps eachhelperowner ONLY byits specified D_U addresspermutation, independentofactivefreshsource.','Dataendpointusesonlyownreplica activepair data, under actualsignedcommonframe proof; nohelperdirt terms survive.','For eachfixedactive role/port, fullcover d->d*rho(stage,port) is bijective, so eachactivephysicalrow belongs toexactlyone completeinvocation atthatstage.','Concrete sigma cover-row injectivity is separatelychecked; descriptorinequality alone is notitsproof.'],'proof':'Atthestagecut allinactivefamilyrowmajorants arebounded byM. Eachcompletecallmaytemporarilymultiply bylocalL; its inactivehelperoutputs onlypermute addresses andreturn toboundM. Activeoutputsbelongtoone replica andcannotenter subsequenthelperinputs becauseallownerpairs excludeactivepair on everyreplica. Fullcoverbijectionprevents activeoperandreuse withinthesweep. Thus eachphasecostsonefactorL, not8factors. Eachbridgebulkupdate costs2; thereare24. Correlationofinitialrows isirrelevant tothis inducedrow-l1 argument.','scope':'Conditional finitecutlemma foractualtemplate. Doesnot independentlyproveinheritedphysicaldirtyslot/compiler theorem orliteral sigma identities. It supportsold192-bitreserve onlywhenalllistedconditionsarebound bythecompletecaller gate.'}
(O/'WHOLE-POOL60-PREFIX-CUT.json').write_text(json.dumps(out,indent=2)+'\n');print(out['status'],out['prefix_bits'])
