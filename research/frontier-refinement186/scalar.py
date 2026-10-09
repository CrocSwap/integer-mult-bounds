#!/usr/bin/env python3
"""Full raw46-sink formal map using the unchanged reviewed signed scalar core."""
from pathlib import Path
import json,sys
from source_binding import HERE,ROOT,check_sources,require
EXPECTED_EVENT_SHA256='955c165a922de2a901e6b9a2c2ee71836443379d56e3f355b89c0b5c29209f7d'
def raw_inputs():
    check_sources();sys.path.insert(0,str(ROOT/'research/paired-cube-scalar-audit'))
    import independent_bit as B
    folder=ROOT/'research/coordinated-frames-and-entrance-banks/selected/complex'
    data=[B.load(folder/(name+'.json.gz')) for name in ('graph','word','frames','physical-frames','physical-pairs')]
    records=json.loads((folder/'sinks.json').read_bytes())['sinks']
    require(len(records)==46 and all(type(z)is dict and type(z['role'])is int and type(z['pivot'])is int for z in records),'46 sink role/pivot schema')
    return data+[[[z['role'],z['pivot']] for z in records]]
def main():
    values=raw_inputs();import independent_sinks as C
    result=C.audit_raw(*values,seconds=180)
    require((result['role_count'],result['retained_dirty'],result['sink_count'],len(result['controls']))==(13042,10686,46,5),'fresh scalar dimensions/controls')
    require(result['event_sha256']==EXPECTED_EVENT_SHA256,'source-bound literal scalar events drift')
    check_sources();print(json.dumps(result,indent=2,sort_keys=True))
if __name__=='__main__':main()
