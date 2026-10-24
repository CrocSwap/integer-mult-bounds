"""Actual full-width setup and separate complete small packet calibration."""
import json,argparse
from types import SimpleNamespace
from unittest.mock import patch
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from binding import load,need
from observer import observed
from ledger import bound

def setup(v,m,warm,validation_cap=4):
 # Reuses Ross Richardson's exact first-node fixture, not its abstract replay.
 with observed(m,()) as c:
  f=v.caller_fixture(m,True,1,64,2,3);c.arenas=(f.residues,f.indices)
  for a,n in zip(c.arenas,warm):
   values=[a.zero() for _ in range(n)];a.free_many(*values)
  old=m.records.Tape();m.directory.append_tape(f.fields.tape,old);m.directory.append_tape(f.fields.tape,old);old.rewind()
  f.counts[0].close();f.counts[0]=m.cardinal_counts.Count.literal(2)
  source=m.records.Tape();entry=tuple(v.state(a) for a in c.arenas)
  allocation=tuple(len(a.words) for a in c.arenas);live=tuple(len(a.live) for a in c.arenas)
  allowance=bound(old_prefixes=2,highs=1,depth=2,code_bits=8,residue_bits=f.residues.bits,index_bits=f.indices.bits,
    fibre=3**128,program_backing=len(f.program.tape.cells),allocated=allocation,live=live,q=3)
  cut={};c.start()
  def stop(source,events,layout,directory,prefix_count,field_count,coefficient,observe=None):
   c.phase='validated_packet_entry';c.sample()
   live_tapes=list(c.tapes.items())
   stacks=[t for ident,t in live_tapes if ident not in c.baseline and c.labels[ident]==('records','__init__','Stack')]
   need(len(stacks)==4 and all(len(t.cells)==1 for t in stacks),'validation stacks retained')
   need(sum(len(t.cells) for t in stacks)<=validation_cap,'validation stack budget')
   cut.update(directory=len(directory.cells),retained_validation_stack_cells=4)
   need(len(directory.cells)==allowance['directory'],'actual directory serialization')
   event=next(events);cut['first_event']=event.kind;events.close()
   return source
  with patch.object(m.packet_engine,'run',stop):
   result=f.consumer.apply(source,0,True,f.spec.low,old,f.counts[0],*f.counts[1:])
  need(result is source and tuple(v.state(a) for a in c.arenas)==entry,'setup live ownership restored')
  for ident,(raw,head) in c.baseline.items():
   need(ident in c.tapes and bytes(c.tapes[ident].cells)==raw and c.tapes[ident].head==head,'setup borrowed arrays restored')
  need(set(c.tapes)==set(c.baseline),'setup releases every new record/count Tape')
  need(c.peak<=c.k0+allowance['extra'],'complete envelope covers actual setup')
  return {'warm':list(warm),'k0':c.k0,'peak':c.peak,'phase_peaks':c.phases,'max_count_roots':c.max_counts,
          'cut':cut,'source_width':64,'rank':1,'depth':2,'modulus':3,'old_prefixes':2,
          'actual_fibre':str(3**128),'allowance':allowance,'allocation_sites':sorted(c.record_sites)}

def packet(v,m,modulus,events):
 with observed(m,()) as c:
  arena=m.words.Arena(modulus.bit_length()+1,128);ix=m.words.Arena(8,128);c.arenas=(arena,ix)
  ring=m.words.Ring(arena.literal(modulus));source=m.records.Tape();n=2;fibre=modulus**2
  data=[(j*j+j//3+1)%2 for j in range(n*fibre)]
  for bit in data:source.append(bit)
  source.rewind();high=[[0]*64 for _ in range(64)]
  directory=m.records.Fields.fixture(ix,arena,[(0,high)]*n,code_bits=8).tape
  prefix_count=m.cardinal_counts.Count.literal(n);field_count=ix.literal(1)
  borrowed=tuple(v.state(a) for a in c.arenas)
  class Layout:
   def __init__(self):self.ring=ring;self.q=3;self.geometry=SimpleNamespace(parent_identity=object())
   def fibre(self):return m.cardinal_counts.Count.literal(fibre)
   def extents(self,first,second=None):
    raw=[m.cardinal_counts.Count.literal(x) for x in ((1,modulus) if second is None else (1,1,1))]
    result=[x.marginal() for x in raw]
    for x in raw:x.close()
    return result
  layout=Layout();c.start()
  def sequence():
   for tag in events:
    c.phase=tag
    yield SimpleNamespace(kind=tag,first=0,second=1,request=None)
  out=m.packet_engine.run(source,sequence(),layout,directory,prefix_count,field_count,lambda *_:arena.copy(ring.one))
  actual=list(out.cells[1:]);expected=list(data)
  for tag in events:
   after=[0]*len(expected)
   for p in range(n):
    for a in range(modulus):
     for b in range(modulus):
      aa,bb=(a,(b+a)%modulus) if tag=='add' else (b,a) if tag=='atom_swap' else ((-a)%modulus,b)
      after[p*fibre+aa*modulus+bb]=expected[p*fibre+a*modulus+b]
   expected=after
  need(actual==expected,'independent complete packet permutation')
  need(tuple(v.state(a) for a in c.arenas)==borrowed,'packet numerical ownership restored')
  for ident,(raw,head) in c.baseline.items():need(bytes(c.tapes[ident].cells)==raw and c.tapes[ident].head==head,'packet borrowed bytes and heads')
  private=[t for ident,t in c.tapes.items() if ident not in c.baseline]
  need(private==[out],'sole returned packet ownership')
  return {'modulus':modulus,'prefixes':n,'fibre':fibre,'events':events,'k0':c.k0,'peak':c.peak,
          'phases':c.phases,'max_count_roots':c.max_counts,'endpoint_sha256':__import__('hashlib').sha256(bytes(actual)).hexdigest(),
          'allocation_sites':sorted(c.record_sites)}

def run():
 v=load()
 with v.runtime() as m:
  setups=[setup(v,m,(0,0)),setup(v,m,(4500,80))]
  packets=[packet(v,m,q,tags) for q in (3,9) for tags in (['add'],['atom_swap'],['sign'],['add','atom_swap','sign','add'])]
  need(setups[1]['k0']>setups[0]['k0'],'warm entry backing charged')
  try:setup(v,m,(0,0),validation_cap=3)
  except RuntimeError as e:need(str(e)=='validation stack budget','only intended control rejection')
  else:raise RuntimeError('three-cell validation budget accepted')
  count=m.cardinal_counts.Count.literal(8);counter=m.stream.Counter(count);size=len(counter.tape.cells);counter.close()
  need(len(counter.tape.cells)==size and size>1,'closed counter backing retained')
  count.close()
  return {'status':'PASS_COMPLETE_FIRST_NODE_SOURCE_RESERVE','setup':setups,'small_complete_packets':packets,
          'three_cell_validation_budget_rejected':True,'closed_counter_backing_retained':True,'full_gl64_payload_executed':False,'physical_supplier_admitted':False}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--emit',action='store_true');a=p.parse_args();result=run()
 if not a.emit:need(json.dumps(result,sort_keys=True)==json.dumps(json.loads((Path(__file__).parent/'RESULT.json').read_text()),sort_keys=True),'complete typed receipt')
 print(json.dumps(result,indent=2))
