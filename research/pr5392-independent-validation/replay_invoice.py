#!/usr/bin/env python3
"""Regenerate the complete independent invoice in a private source adapter.

Only historical absolute provenance paths are adapted after byte comparison;
all literal charges, fields, chronology hashes and scientific fields must equal.
"""
from pathlib import Path
import contextlib,io,json,sys
h=Path(sys.argv[1]).resolve();sys.path.insert(0,str(h))
import invoice
old=invoice.read(h/'INVOICE-v1.json')
for n in ['INVOICE-v1.json','CHRONOLOGY-v1.json']:
 p=h/n
 if p.exists():p.unlink()
s=io.StringIO()
with contextlib.redirect_stdout(s):invoice.run()
fresh=invoice.read(h/'INVOICE-v1.json')
for name,row in fresh['authentication']['canonical'].items():
 expected=old['authentication']['canonical'][name]
 invoice.need(Path(row['path']).is_relative_to(h) and invoice.sha(Path(row['path']))==expected['sha256'],'private canonical fixture exact bytes')
 row['path']=expected['path']
invoice.need(fresh==old,'complete regenerated literal invoice differs')
invoice.need(invoice.sha(h/'CHRONOLOGY-v1.json')==old['chronology_sha256'],'complete regenerated chronology differs')
mutant=json.loads(json.dumps(old));mutant['histograms']['productive']['9']+=16
try:invoice.need(fresh==mutant,'unearned16H9 productive targets rejected by fresh literal census')
except ValueError as e:control=str(e)
else:raise ValueError('unearned productive credit accepted')
print(json.dumps(dict(status='PASS_COMPLETE_LITERAL_INVOICE_AND_CHRONOLOGY',result=fresh,control=control,producer_stdout=s.getvalue(),adapter='Only authenticated historical absolute canonical fixture paths normalized for full-object comparison; actual source/charge fields unchanged.'),sort_keys=True))
