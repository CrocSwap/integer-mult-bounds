"""Optional ~251s actual finite packet regeneration; never needed by replay."""
import sys,time,json,hashlib
from pathlib import Path
from sandwich_sources import opened
if len(sys.argv)!=2:raise SystemExit('usage: prepare_fixture.py OUTPUT_FILE')
output=Path(sys.argv[1])
if output.exists():raise SystemExit('output must not exist')
start=time.monotonic()
with opened() as state:
 from cardinal_counts import Count
 from ring_check_words import tape,word_bits
 from router_metadata import owned
 from tensor_catalogue import TensorPreparation
 from tensor_plan import TensorPlan
 from records import Tape
 from expansion_check_block import packet_bytes
 from check_support import no_decode
 from session import erase_marker
 sources=tape(word_bits(5,3)+word_bits(7,3));flags=tape(bytes((1,)))
 with owned(*(Count.literal(v) for v in (1,3,48,2,1,80,4,1,8,1,1))) as parameters:
  plan=TensorPlan(sources,flags,*parameters,Tape)
  print('PLAN_PASS',time.monotonic()-start,flush=True);plan.close()
  if True:
   prep=TensorPreparation()
   with no_decode(): result=prep.run(sources,flags,*parameters)
   raw=packet_bytes(result)
   output.write_bytes(raw)
   receipt=dict(seconds=time.monotonic()-start,size=len(raw),sha256=hashlib.sha256(raw).hexdigest(),counts=prep.last_counts)
   print('FINITE_PRODUCER_PASS',receipt,flush=True)
   result.clear();erase_marker(result);prep.idle()
