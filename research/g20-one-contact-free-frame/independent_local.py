"""Independent finite check of the four-neighbour moved-frame formula.

Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
Separate reviewer: set-valued chronological oracle, no primary pricing imports.
The primary functions are loaded only as the subject being checked.
"""
from collections import Counter
from itertools import product
from pathlib import Path
from types import ModuleType
import json

path=Path(__file__).with_name('verify.py')
subject=ModuleType('moved_frame_subject');subject.__file__=str(path)
exec(compile(path.read_bytes(),str(path),'exec'),subject.__dict__)

def need(condition, reason):
    if not condition:raise ValueError(reason)

def full(records,start,final,owned,distances):
    rows=[{i} for i in range(len(start))];frames=list(start);paid=Counter()
    def visit(role,target):
        source=frames[role]
        if source is None:
            need(role in owned and not rows[role],'initialized paid row')
        elif source!=target and rows[role]:
            paid[distances[source][target]]+=1
        frames[role]=target
    live=[]
    for index,event in enumerate(records):
        op,destination=event[:2]
        if op=='ERASE':
            need(destination in owned,'owned reset')
            rows[destination]=set();frames[destination]=event[2]
        else:
            donor,frame=event[2:]
            if rows[donor]:
                live.append(index)
                visit(destination,frame);visit(donor,frame)
                rows[destination]^=rows[donor]
    for role,target in enumerate(final):
        if role in owned:need(not rows[role],'owned return')
        else:visit(role,target)
    return paid,[sum(1<<j for j in row) for row in rows],live

distance={a:{b:abs([0,1,3][a]-[0,1,3][b]) for b in range(3)} for a in range(3)}
alphabet=[('ADD',a,b,f) for a in range(3) for b in range(3) if a!=b for f in range(3)]
alphabet += [('ERASE',2,f) for f in (None,0,1,2)]
start,final,owned=[0,1,None],[2,0,None],{2}
words=moves=zero_destination=reset_successor=final_successor=0
for length in range(4):
    for middle in product(alphabet,repeat=length):
        records=[('ERASE',2,None),*middle,('ERASE',2,None)]
        paid,rows,live=full(records,start,final,owned,distance)
        trace,places,subject_rows=subject.traces(records,start,final,owned)
        need(subject_rows==rows and subject.histogram(trace,distance)==paid,'whole trace reference')
        for index in live:
            correction=records[index]
            neighbours=subject.local_neighbours(trace,places,index,correction)
            zero_destination+=not neighbours[0][1][1]
            reset_successor+=sum(after is not None and after[2]<len(records)
                                  and records[after[2]][0]=='ERASE' for _,_,after in neighbours)
            final_successor+=sum(after is not None and after[2]==len(records)
                                  for _,_,after in neighbours)
            for frame in range(3):
                changed=records[:];changed[index]=correction[:3]+(frame,)
                actual,changed_rows,_=full(changed,start,final,owned,distance)
                predicted=subject.moved_histogram(paid,neighbours,correction[3],frame,distance)
                need(actual==predicted and changed_rows==rows,'exact moved-frame invoice and rows')
                moves+=1
        words+=1
subject.check_decreasing_increments([[2,-1],[3,1],[4,1],[5,-1]],[[2,3],[4,5]])
for intervals in ([[2,3],[4,6]],[[4,5],[2,3]],[[0,1],[2,3]]):
    try:subject.check_decreasing_increments(subject.EXCEPTIONAL,intervals)
    except ValueError:pass
    else:raise ValueError('invalid increment proof accepted')
print(json.dumps({'words':words,'moved_frame_assignments':moves,'zero_destination_nodes':zero_destination,
                  'reset_successor_nodes':reset_successor,'public_final_successor_nodes':final_successor,
                  'increment_rejections':3},sort_keys=True))
