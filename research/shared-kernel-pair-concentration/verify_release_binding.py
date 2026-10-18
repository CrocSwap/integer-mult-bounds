#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Bind the literal profile, exact independent comparison and full strict release."""
import argparse,hashlib,json
from fractions import Fraction as Q
from pathlib import Path
HERE=Path(__file__).resolve().parent
def need(ok,s):
 if not ok:raise ValueError(s)
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--admission',type=Path,required=True);ap.add_argument('--moment',type=Path,required=True);ap.add_argument('--baseline',type=Path,required=True);a=ap.parse_args();result=read(a.admission/'RESULT.json');release=read(a.admission/'release/RELEASE-RECEIPT.json');moment=read(a.moment);base=read(a.baseline);claim=read(HERE/'CLAIM.json')
 need(result['status']=='PASS_REPLICA_ORDER_FILL_DERIVATIVE_COMPLETE_RELEASE' and release['status']=='PASS_RELEASE','full release');need(base['status']=='PASS_SHARED_KERNEL_PORTABLE_COMPLETE_REPLAY','reproduced baseline')
 k=Q(moment['kappa_rational']);b=Q(base['kappa']);need(k==Q(result['kappa'])==Q(release['kappa_decimal'])==Q(claim['kappa']),'exact headline binding');need(k>b and k-b==Q(moment['gain_rational'])==Q(claim['gain']),'exact strict current-baseline improvement')
 need(Q(moment['baseline_rational'])==b,'right baseline');need(result['release_receipt_sha256']==sha(a.admission/'release/RELEASE-RECEIPT.json'),'release receipt SHA');need(release['manifest_sha256']==sha(a.admission/'package/MANIFEST.json'),'package manifest SHA')
 package=a.admission/'package';need({p.relative_to(package).as_posix():sha(p) for p in package.rglob('*') if p.is_file() and p!=package/'MANIFEST.json'}==read(package/'MANIFEST.json'),'complete final source tree')
 spec=read(package/'new/SPEC.json');need(Q(spec['expected']['complex_lower'])==Q(moment['complex_lower']),'exact endpoint');need({int(r):n for r,n in spec['expected']['global_profile'].items()}=={int(r):n for r,n in moment['profile'].items()},'full actual profile');need(spec['expected']['live']==66304 and spec['expected']['physical']==66794,'live and physical stock')
 print('PASS_EXACT_CURRENT_BASELINE_AND_COMPLETE_RELEASE_BINDING',str(k),'gain',str(k-b))
if __name__=='__main__':main()
