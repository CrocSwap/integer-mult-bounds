"""Dense interpreter of literal Graphs; observers never drive control. Apache-2.0."""
from dataclasses import dataclass
SYMBOLS={s:i for i,s in enumerate('_01^|$')}


class Rejected(ValueError):pass
class MonitorViolation(ValueError):pass


@dataclass
class State:
    tapes:list
    heads:list
    origins:list
    lows:list
    highs:list
    entry_lows:list
    entry_highs:list
    writes:list
    steps:int=0

    def clone(self):
        return State([bytearray(t) for t in self.tapes],self.heads.copy(),self.origins.copy(),
                     self.lows.copy(),self.highs.copy(),self.entry_lows.copy(),self.entry_highs.copy(),
                     self.writes.copy(),self.steps)


def initial(payloads,tape_count,*,old_history=0):
    if len(payloads)!=2 or len(payloads[0])!=len(payloads[1]) or not payloads[0]:
        raise ValueError('two complete same-F source homes')
    f=len(payloads[0]);capacity=16*(f+128)+256
    origins=[17+(t%7) for t in range(tape_count)]
    text='^'+'|'.join(payloads)+'|$'
    tapes=[bytearray(capacity) for _ in range(tape_count)]
    for tape,o in zip(tapes,origins):
        tape[o]=SYMBOLS['^'];tape[o-3:o]=bytes([2,1,4]);tape[-3:]=bytes([1,4,2])
    o=origins[0];tapes[0][o:o+len(text)]=bytes(SYMBOLS[s] for s in text)
    lows=origins.copy();highs=origins.copy();highs[0]=o+len(text)-1
    if old_history:highs[-1]=origins[-1]+old_history
    return State(tapes,origins.copy(),origins,lows.copy(),highs.copy(),lows,highs,[0]*tape_count)


class Program:
    def __init__(self,graph):
        names=list(graph.rules);self.labels={name:i for i,name in enumerate(names)}
        self.labels['HALT']=-1;self.start=self.labels[graph.start];self.rows=[]
        for name in names:
            rules=[(tuple((t,SYMBOLS[s]) for t,s in r.tests),
                    tuple((t,SYMBOLS[s]) for t,s in r.writes),r.moves,
                    self.labels[r.target]) for r in graph.rules[name]]
            if rules and all(len(r[0])==1 and not r[1] and not r[2] for r in rules) and len({r[0][0][0] for r in rules})==1:
                branch=[-2]*6
                for r in rules:branch[r[0][0][1]]=r[3]
                self.rows.append((0,rules[0][0][0][0],branch))
            elif len(rules)==1 and not rules[0][0]:
                _,writes,moves,nxt=rules[0]
                if len(writes)==1 and not moves:self.rows.append((1,writes[0][0],(writes[0][1],nxt)))
                elif len(moves)==1 and not writes:self.rows.append((2,moves[0][0],(moves[0][1],nxt)))
                elif not moves and not writes:self.rows.append((3,nxt,None))
                else:self.rows.append((4,rules,None))
            else:self.rows.append((4,rules,None))

    def run(self,state,*,start=None,stop=None,budget=100000000):
        pc=self.start if start is None else self.labels[start]
        stop_pc=None if stop is None else self.labels[stop]
        rows=self.rows;tapes=state.tapes;heads=state.heads
        lows=state.lows;highs=state.highs;writes=state.writes
        while pc!=-1 and pc!=stop_pc:
            op,t,arg=rows[pc]
            if op==0:
                pc=arg[tapes[t][heads[t]]]
                if pc==-2:raise Rejected('literal scanned-symbol rejection')
            elif op==1:
                value,pc=arg
                if heads[t]==state.origins[t] and value!=3:
                    raise MonitorViolation('attempted permanent B origin marker overwrite')
                tapes[t][heads[t]]=value;writes[t]+=1
            elif op==2:
                delta,pc=arg
                if delta not in (-1,0,1):raise ValueError('nonunit emitted move')
                heads[t]+=delta
                if not 0<=heads[t]<len(tapes[t]):raise ValueError('finite verifier capacity exhausted')
                lows[t]=min(lows[t],heads[t]);highs[t]=max(highs[t],heads[t])
            elif op==3:pc=t
            else:
                self._general(state,t)
                pc=state.next_pc
            state.steps+=1
            if state.steps>budget:raise ValueError('finite execution budget')
        return state

    def _general(self,state,rules):
            tapes=state.tapes;heads=state.heads;lows=state.lows;highs=state.highs;writes=state.writes
            found=None
            for rule in rules:
                if all(tapes[t][heads[t]]==symbol for t,symbol in rule[0]):
                    if found is not None:raise ValueError('nondeterministic emitted table')
                    found=rule
            if found is None:raise Rejected('literal scanned-symbol rejection')
            for t,value in found[1]:
                if heads[t]==state.origins[t] and value!=SYMBOLS['^']:
                    raise MonitorViolation('attempted permanent B origin marker overwrite')
                tapes[t][heads[t]]=value;writes[t]+=1
            for t,delta in found[2]:
                if delta not in (-1,0,1):raise ValueError('nonunit emitted move')
                heads[t]+=delta
                if not 0<=heads[t]<len(tapes[t]):raise ValueError('finite verifier capacity exhausted')
                lows[t]=min(lows[t],heads[t]);highs[t]=max(highs[t],heads[t])
            state.next_pc=found[3]


def fields(state,count=2):
    tape=state.tapes[0];pos=state.origins[0]+1;result=[];reverse='_01^|$'
    for _ in range(count):
        bits=[]
        while tape[pos] in (1,2):bits.append(reverse[tape[pos]]);pos+=1
        if tape[pos]!=4:raise ValueError('HOME delimiter changed')
        pos+=1;result.append(''.join(bits))
    if tape[pos]!=5:raise ValueError('HOME endpoint changed')
    return tuple(result)


def check_retired(state):
    if state.heads!=state.origins:raise ValueError('head failed to return to B origin')
    for tape,o in zip(state.tapes,state.origins):
        if tape[o]!=3 or bytes(tape[o-3:o])!=bytes([2,1,4]) or bytes(tape[-3:])!=bytes([1,4,2]):
            raise ValueError('origin or opaque exterior changed')
    for tape,o in zip(state.tapes[1:],state.origins[1:]):
        if any(tape[o+1:-3]):raise ValueError('private body or native guard not retired')
