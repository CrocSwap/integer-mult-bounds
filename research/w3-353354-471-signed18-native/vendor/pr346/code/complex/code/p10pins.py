"""Re-pinning helper for the p = 10 port of the complex checks: structural constants come from the pin file; every
regression count is either checked against the pin file or, in record mode (absent key), recorded for review."""
import json, os
PATH=os.environ.get('CX_PINS','')
PINS=json.load(open(PATH)) if PATH and os.path.exists(PATH) else {}
RECORD={}
def norm(x):
    if isinstance(x,dict): return {str(k):norm(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)): return [norm(v) for v in x]
    return x
def pin(key,value,msg):
    value=norm(value)
    if PINS.get(key) is not None:
        if PINS[key]!=value: raise ValueError(msg+' (pin %s: expected %r got %r)'%(key,PINS[key],value))
    else: RECORD[key]=value
