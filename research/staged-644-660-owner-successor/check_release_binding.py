"""Bind exact historical release evidence to newly recomputed owners/arithmetic.

This authenticates the recorded complete release. It does not substitute receipt
strings for fresh bounded owner/moment/dual computation or rerun the long release.
"""
from pathlib import Path
from fractions import Fraction as Q
import argparse,gzip,hashlib,io,json,tarfile
P=Path(__file__).resolve().parent
def need(v,s):
 if not v:raise ValueError(s)
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--fresh',type=Path,required=True);a=ap.parse_args()
 m=json.loads((P/'evidence/MANIFEST.json').read_bytes());z=(P/'evidence/ACTUAL-RELEASE.tar.gz').read_bytes();need(sha(z)==m['archive_sha256'],'immutable historical evidence archive')
 raw=gzip.decompress(z);need(sha(raw)==m['payload_sha256'],'historical evidence payload');docs={};blobs={}
 with tarfile.open(fileobj=io.BytesIO(raw),mode='r:') as t:
  members=t.getmembers();need(len(members)==len(m['files']) and {x.name for x in members}==set(m['files']),'complete evidence inventory')
  for x in members:
   need(x.isfile() and not x.name.startswith('/') and '..' not in Path(x.name).parts,'safe evidence path')
   b=t.extractfile(x).read();need(len(b)==m['files'][x.name]['bytes'] and sha(b)==m['files'][x.name]['sha256'],'exact raw evidence '+x.name);blobs[x.name]=b;docs[x.name]=json.loads(b)
 c=json.loads((P/'CLAIM.json').read_bytes());fresh=json.loads((a.fresh/'RESULT.json').read_bytes());owner=json.loads((a.fresh/'INDEPENDENT-OWNERS.json').read_bytes())
 get=lambda n:docs['full-release/candidate/'+n]
 review=docs['conditional-review/FINAL-RELEASE-REVIEW.json'];release=get('release/RELEASE-RECEIPT.json');summary=get('release/verify/RESULT.json');audit=get('release/verify/strict/global/audit/ASYNC-AUDIT.json');invoice=get('release/verify/strict/global/audit/PREFIX-AND-INVOICE.json');idle=get('release/verify/strict/global/audit/IDLE-REMAINDER-FRAMES.json');ledger=get('package/outer/LEDGER.json');recovery=docs['full-release/RECOVERY-RELEASE.json']
 for name,digest in review['input_sha256'].items():
  if name in blobs:need(sha(blobs[name])==digest,'independent review exact binding '+name)
 need(sha(blobs['conditional-review/FINAL-RELEASE-REVIEW.json'])==c['final_review_sha256'] and sha(blobs['full-release/candidate/release/RELEASE-RECEIPT.json'])==c['release_receipt_sha256'],'authoritative final hashes')
 need(release['status']=='PASS_RELEASE' and release['manifest_sha256']==c['generated_package_manifest_sha256'],'complete recorded release')
 need(recovery['execution']['exit_code']==0 and recovery['release_receipt_sha256']==c['release_receipt_sha256'],'distinct successful unchanged release retry')
 need(Q(c['kappa'])==Q(release['kappa_decimal'])==Q(fresh['kappa'])==Q(review['kappa']),'same fresh and released exact K')
 need(Q(c['kappa'])==Q(c['complex_lower'])-Q(1,10**46)-Q(1,10**70),'declared modern outer map')
 need(Q(c['exact_gain_over_PR3605'])==Q(c['kappa'])-(Q('.001730006549538841847005')-Q(1,10**46)-Q(1,10**70))>0,'strict exact predecessor comparison')
 need(c['histogram']==fresh['profile']==owner['profile']==review['histogram']==audit['complex_profile'],'complete fresh and released profile')
 need(c['idle']==fresh['idle']==idle['rank_profile'],'actual three rank-seven idle children')
 need(audit['physical']==c['physical']==663549 and audit['complex_live']==c['live']==663040 and audit['complex_hosted_residuals']==owner['roles']==2717280,'whole physical/live invoice')
 need(audit['actual_orthogonal_73column_maps']==8758 and len(audit['mutations_rejected'])==25,'all actual charts and controller controls')
 need(invoice['global_prefix_bits']==summary['prefix_bits']==c['prefix_bits']==1479 and invoice['charged_prefix_bits']==c['charged_prefix_bits']==2048,'actual paid prefix')
 row=ledger['rows']['struct_boundary_radix_union'];controls=ledger['rejecting_controls']['struct_boundary_radix_union']
 need(Q(row['kappa']['rational'])==Q(c['kappa']) and len(row['strict_checks'])==63 and all(Q(v['rational'])>0 for v in row['strict_checks'].values()),'released modern outer rows')
 need(len(controls)==17 and all(v and all(Q(z['rational'])<=0 for z in v.values()) for v in controls.values()),'released rejecting controls')
 print('PASS_RECORDED_FULL_RELEASE_BOUND_TO_FRESH_LITERAL_AND_ARITHMETIC')
if __name__=='__main__':main()
