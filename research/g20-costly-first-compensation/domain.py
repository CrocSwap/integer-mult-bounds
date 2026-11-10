"""Independent bit-mask enumeration of legal A2 intervals.

The primary enumerator uses sorted position lists and binary searches. This
checker builds integer event masks and intersects each literal interval.
Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
"""
from collections import defaultdict

def candidates(records):
    positions=defaultdict(list)
    destinations=defaultdict(int);sources=defaultdict(int);barriers=defaultdict(int);gates=defaultdict(int)
    for i,event in enumerate(records):
        bit=1<<i;op,destination=event[:2]
        if op=='ADD':
            source=event[2]
            if destination==source:raise ValueError('distinct ADD roles')
            positions[destination,source].append(i)
            gates[destination,source]|=bit
            destinations[destination]|=bit;sources[source]|=bit
        elif op in ('INIT','ERASE'):barriers[destination]|=bit
        else:raise ValueError('scalar alphabet')
    for (a,b),indices in sorted(positions.items()):
        forbidden=barriers[a]|barriers[b]|gates[b,a]
        contacts=destinations[b]|sources[a]
        for offset,left in enumerate(indices):
            for right in indices[offset+1:]:
                interior=(1<<right)-(1<<(left+1))
                if forbidden&interior:continue
                active=contacts&interior;corrections={}
                while active:
                    bit=active&-active;index=bit.bit_length()-1;active^=bit
                    _,destination,source,frame=records[index]
                    corrections[index]=('ADD',a,source,frame) if destination==b else ('ADD',destination,b,frame)
                yield left,right,a,b,corrections
