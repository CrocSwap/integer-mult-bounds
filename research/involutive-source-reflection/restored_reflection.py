"""Source-restored shears transferring the involution F; not identity shears."""
from fractions import Fraction as Q
import reflection_unit as reflection
matrices=reflection.matrices

def produce(data,certificate,base):
 out=reflection.produce(data,certificate,base)
 # Original correction is +12PR for backward, -12PR for forward.
 # Negate it and remove the source preparation; the core transfers J.
 for key in ('backward_input','forward_output'):
  block=out['blocks'][key]
  for e in block:
   if e[0]=='scalar' and e[1][0]=='add' and e[1][1][0]=='L':
    e[1][3]=-e[1][3]
 out['blocks']['source_G']=[]
 out['blocks']['forward_source']=[]
 out['programs']={
  'backward':out['blocks']['backward_input']+data['clean_programs']['backward'],
  'forward':data['clean_programs']['forward']+out['blocks']['forward_output']}
 return out
