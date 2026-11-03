"""Independent literal tape/FSM oracle; no author or primary executable imports.

Petalas6495, Jose Manuel2697, Arias2753 and Tahir2877 retain their source credit.
ToikY with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from collections import Counter as Bag
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MANIFEST = 'f72e91cf10c4cd52be615c94a1dcfacbf4b3cf0ce0691f471408be712cb8eee6'
ZERO, ONE, LEFT, RIGHT, BLANK = range(5)
NS = tuple(range(258)) + (511,512,513,1023,1024,1025,2047,2048,2049,4095,4096,4097)
PADS = (0,1,4)


def need(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)


def decode(raw):
    def unique(items):
        out = {}
        for key,value in items:
            need(key not in out, 'duplicate JSON receipt key')
            out[key] = value
        return out
    def bad(value):
        raise ValueError('noninteger/nonfinite receipt number ' + value)
    return json.loads(raw, object_pairs_hook=unique, parse_float=bad, parse_constant=bad)


def authenticate():
    raw = (ROOT/'SOURCE-PINS.json').read_bytes()
    need(hashlib.sha256(raw).hexdigest() == MANIFEST, 'source manifest SHA256')
    pins = decode(raw)
    need(type(pins['schema_version']) is int and pins['schema_version'] == 1, 'source manifest schema')
    need(len(pins['files']) == 11, 'complete eleven-source custody')
    paths = set()
    for row in pins['files']:
        path = row['path']
        need(path.startswith('inputs/') and '..' not in path and path not in paths, 'unique package input')
        paths.add(path)
        data = (ROOT/path).read_bytes()
        need(type(row['bytes']) is int and len(data) == row['bytes'], 'source SHA256 length')
        need(hashlib.sha256(data).hexdigest() == row['sha256'], 'source SHA256 '+path)
        need(hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest() == row['git_blob'], 'source Git blob '+path)


class Tape:
    def __init__(self, cells=None):
        self.cells = [LEFT] if cells is None else list(cells)
        self.head = 1
        self.meter = [0,0,0]

    def read(self):
        self.meter[0] += 1
        return self.cells[self.head] if self.head < len(self.cells) else BLANK

    def write(self, symbol):
        need(type(symbol) is int and 0 <= symbol <= 13, 'fixed tape alphabet')
        self.meter[1] += 1
        self.cells += [BLANK]*max(0,self.head+1-len(self.cells))
        self.cells[self.head] = symbol

    def step(self, direction):
        need(direction in (-1,1), 'unit movement')
        self.head += direction
        need(self.head >= 0, 'left local boundary')
        self.meter[2] += 1

    def append(self, symbol):
        need(self.read() == BLANK, 'append at blank')
        self.write(symbol)
        self.step(1)

    def rewind(self):
        self.step(-1)
        while self.read() != LEFT:
            self.step(-1)
        self.step(1)

    def clear(self):
        self.rewind()
        while self.read() != BLANK:
            self.write(BLANK)
            self.step(1)
        self.rewind()

    def snapshot(self):
        return [self.cells[:],self.head]


def word(value, width):
    need(value >= 0 and value < 1<<width, 'fixture word extent')
    return Tape([LEFT]+[(value>>i)&1 for i in range(width)]+[RIGHT])


class CounterFSM:
    def __init__(self, source, direct):
        self.source,self.direct,self.tape = source,direct,Tape()
        source.rewind()
        while source.read() != RIGHT:
            self.tape.append(source.read())
            source.step(1)
        source.rewind()
        t = self.tape
        t.append(RIGHT)
        t.step(-1);t.step(-1)
        while t.read() == ZERO:
            t.write(RIGHT);t.step(1);t.write(BLANK);t.step(-1);t.step(-1)
        self.finished = t.read() == LEFT
        if self.finished:
            t.step(1);t.write(ZERO);t.step(1);t.write(RIGHT)
        t.rewind()

    def decrement(self, fault=None):
        need(not self.finished, 'positive countdown')
        t = self.tape
        digit = t.read()
        if self.direct and (digit == ONE or fault == 'borrow-shortcut'):
            t.write(ZERO);t.step(1)
            end = t.read() == RIGHT
            if end and fault != 'omit-finished':
                self.finished = True
            if fault == 'finish-every-odd':
                self.finished = True
            if fault == 'erase-right' and end:
                t.write(BLANK)
            if fault != 'omit-return':
                t.step(-1)
            return
        while digit == ZERO:
            t.write(ONE);t.step(1);digit = t.read()
        need(digit == ONE, 'canonical positive counter')
        t.write(ZERO);t.step(1)
        if t.read() == RIGHT:
            t.write(BLANK);t.step(-1);t.step(-1)
            if t.read() == LEFT:
                t.step(1);t.write(ZERO);t.step(1);t.write(RIGHT)
                self.finished = True
            else:
                t.step(1);t.write(RIGHT)
        t.rewind()

    def snapshot(self):
        return [self.tape.snapshot(),self.finished,self.source.snapshot()]

    def close(self):
        self.tape.clear()


def total(*meters):
    return [sum(row[i] for row in meters) for i in range(3)]


def delta(old,new):
    return [a-b for a,b in zip(old,new)]


def countdown(N,padding):
    width = max(1,N.bit_length())+padding
    left,right = word(N,width),word(N,width)
    old,new = CounterFSM(left,False),CounterFSM(right,True)
    need(old.snapshot() == new.snapshot(), 'initial whole allocated state')
    protected = left.snapshot()
    transcript = hashlib.sha256()
    for index in range(N):
        old.decrement();new.decrement()
        need(old.snapshot() == new.snapshot(), 'every complete private state/head/finished')
        need(left.snapshot() == protected == right.snapshot(), 'protected source word/head')
        need(new.finished == (index == N-1), 'literal completion time')
        transcript.update((canonical(new.snapshot())+'\n').encode())
    need(old.finished and new.finished, 'zero countdown finished')
    final = new.snapshot()
    old.close();new.close()
    need(old.snapshot() == new.snapshot(), 'closed whole private state')
    before,after = total(old.tape.meter,left.meter),total(new.tape.meter,right.meter)
    saving = delta(before,after)
    C = (N+1)//2
    need(saving == ([2*C+1,3,2*C+4] if N else [0,0,0]), 'derived complete traffic formula')
    return {'N':N,'padding':padding,'width':width,'old':before,'new':after,'saving':saving,
            'final':final,'closed':new.snapshot(),'states_sha256':transcript.hexdigest()}


def caller(M,B,S,pattern,direct):
    V = M*B*S
    payload = [((i*7+i//3+pattern)&1) for i in range(V)]
    source,out = Tape([LEFT]+payload),Tape()
    original = source.cells[:]
    words = [word(B,B.bit_length()+1),word(S,S.bit_length()+1),
             word(M-2,max(2,M.bit_length()+1)),word(M-1,max(2,M.bit_length()+1))]
    registry,inventory = [],[]
    def make(index,N):
        counter = CounterFSM(words[index],direct)
        registry.append(counter);inventory.append([N,len(words[index].cells)-2])
        return counter
    def copy():
        if S == 1:
            out.append(source.read());source.step(1)
        else:
            c = make(1,S)
            while not c.finished:
                out.append(source.read());source.step(1);c.decrement()
            c.close()
    def move(direction):
        blocks = make(2,M-2)
        while not blocks.finished:
            c = make(1,S)
            while not c.finished:
                source.step(direction);c.decrement()
            c.close();blocks.decrement()
        blocks.close()
    outer = make(0,B)
    while not outer.finished:
        copy();move(1)
        remaining = make(3,M-1)
        while not remaining.finished:
            copy();remaining.decrement()
            if not remaining.finished:
                for _ in range(2):
                    c = make(1,S)
                    while not c.finished:
                        source.step(-1);c.decrement()
                    c.close()
        remaining.close();move(1);outer.decrement()
    need(source.read() == BLANK, 'whole sign input consumed')
    source.rewind();out.rewind();source.rewind();outer.close()
    expected = [payload[(b*M+(-a)%M)*S+s] for b in range(B) for a in range(M) for s in range(S)]
    need(out.cells == [LEFT]+expected and source.cells == original, 'full opaque sign payload/source')
    need(source.head == out.head == 1, 'both source/output heads returned')
    need(all(c.tape.cells[0] == LEFT and all(x == BLANK for x in c.tape.cells[1:]) and c.tape.head == 1 for c in registry), 'every counter disposed')
    counters = total(*(c.tape.meter for c in registry),*(w.meter for w in words))
    return {'inventory':inventory,'counter_traffic':counters,'source_traffic':source.meter,
            'output_traffic':out.meter,'payload_sha256':hashlib.sha256(bytes(expected)).hexdigest(),
            'source_head':source.head,'output_head':out.head}


def callers():
    rows = []
    for M in (2,3,4,5,8,9):
        for B in (1,2,3):
            for S in (1,2,3,4,7,8,9):
                for pattern in (0,1):
                    old,new = caller(M,B,S,pattern,False),caller(M,B,S,pattern,True)
                    for key in ('inventory','source_traffic','output_traffic','payload_sha256','source_head','output_head'):
                        need(old[key] == new[key], 'complete caller unchanged '+key)
                    positive = [N for N,_ in old['inventory'] if N]
                    C = sum((N+1)//2 for N in positive)
                    saving = delta(old['counter_traffic'],new['counter_traffic'])
                    need(saving == [2*C+len(positive),3*len(positive),2*C+4*len(positive)], 'actual complete invocation saving')
                    rows.append({'M':M,'B':B,'S':S,'pattern':pattern,'old':old,'new':new,'saving':saving})
    need(len(rows) == 252, 'complete frozen sign caller domain')
    return rows


def controls():
    out = []
    for N,fault in ((1,'omit-return'),(3,'finish-every-odd'),(1,'omit-finished'),(1,'erase-right'),(2,'borrow-shortcut')):
        a,b = CounterFSM(word(N,5),False),CounterFSM(word(N,5),True)
        a.decrement();b.decrement(fault)
        need(a.snapshot() != b.snapshot(), 'actual bad return/flag/marker control')
        out.append({'N':N,'fault':fault,'expected':a.snapshot(),'actual':b.snapshot()})
    return out


def compute():
    authenticate()
    # Literal x=1 is first, before the complete frozen domain.
    first = countdown(1,4)
    rows = [countdown(N,pad) for N in NS for pad in PADS]
    need(len(rows) == 810, 'complete frozen counter domain')
    return {'schema_version':1,'source_manifest_sha256':MANIFEST,'first_falsification':first,
            'counters':rows,'callers':callers(),'controls':controls(),
            'scope':'Independent entire private FSM states, counter/input/payload traffic and full sign changed inventory/delta. Unchanged ring/Unsigned/Arena arithmetic absolute totals are primary-only. No inverse, all-dirty cleanup, optimality, runtime speedup, supplier or kappa claim.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--emit',action='store_true')
    args = parser.parse_args()
    result = compute()
    if args.emit:
        print(canonical(result))
    else:
        retained = decode((ROOT/'ORACLE.json').read_bytes())
        need(canonical(retained) == canonical(result), 'strict independent receipt drift')
        print('PASS_MARKED_COUNTDOWN_LITERAL_ORACLE')


if __name__ == '__main__':
    main()
