"""Whole original Node pending-Word grant, not a physical tape tariff.
JoyboyBrian with substantial OpenAI assistance. Apache-2.0.
"""
PHASES={
 'constructor':(0,6), 'preflight':(20492,17), 'fresh_rows':(6,2),
 'peel':(20492,29), 'selection':(6,0), 'route':(16400,0),
 'consumer_adapter':(37672,34), 'consumer_child':(20494,41),
 'numerical_neutral':(0,0),
}
BOUND=tuple(max(row[j] for row in PHASES.values()) for j in range(2))

def require(ok,message):
 if not ok:raise ValueError(message)

def capacities(allocated,live,bits):
 for row in (allocated,live,bits):
  require(type(row) in (tuple,list) and len(row)==2,'two arenas')
  require(all(type(x) is int and x>=0 for x in row),'typed nonnegative counts')
 require(all(l<=k for k,l in zip(allocated,live)),'live subset of allocated')
 require(all(b>=2 for b in bits),'fixed word widths')
 caps=tuple(max(k,l+b) for k,l,b in zip(allocated,live,BOUND))
 return {'capacities':list(caps),'backing_cells':sum((c+1)*(b+2) for c,b in zip(caps,bits))}
