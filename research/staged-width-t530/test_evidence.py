# SPDX-License-Identifier: Apache-2.0
"""Semantic corruptions of stored receipts, without changing frozen evidence."""
import importlib.util,json,copy,subprocess,sys
from pathlib import Path
P=Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location('stored',P/'verify_evidence.py');v=importlib.util.module_from_spec(sp);sp.loader.exec_module(v)
E=P/'evidence';names=['RESULT.json','RELEASE-RECEIPT.json','NATIVE-RECEIPT.json','PREFIX-AND-INVOICE.json','INDEPENDENT-OWNERS.json'];original=[json.loads((E/n).read_bytes())for n in names]
v.semantic_check(*original);v.check(E)
controls=[('empty strict inventory',lambda a:a[3].update(strict_checks={})),('missing strict check',lambda a:a[3]['strict_checks'].pop('precision')),('nonboolean check',lambda a:a[3]['strict_checks'].update(mass=1)),('rounded kappa',lambda a:a[0].update(kappa_decimal='.00173007186470577988254')),('one unpaid child',lambda a:a[0]['profile'].__setitem__('1',a[0]['profile']['1']+1)),('missing private buffer',lambda a:a[3].update(private_zero_buffers=90)),('missing stage',lambda a:a[0]['stages'].pop()),('different native word',lambda a:a[2]['providers']['base'].update(word_sha256='0'*64)),('wrong stock',lambda a:a[3]['blocknorm'].update(stock_l2_bits=1323)),('different source clock',lambda a:a[0].update(order_sha256='0'*64))]
for name,mutate in controls:
 a=copy.deepcopy(original);mutate(a)
 try:v.semantic_check(*a)
 except (ValueError,KeyError):pass
 else:raise RuntimeError('accepted '+name)
r=subprocess.run([sys.executable,'-I','-O','-B',str(P/'verify_evidence.py')],capture_output=True);v.need(r.returncode!=0,'optimized mode accepted')
print('PASS_STORED_EVIDENCE_CONTROLS',len(controls)+1)
