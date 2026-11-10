"""Fixed finite microcontrol; construction precedes runtime payload input.

Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
from dataclasses import dataclass


def need(ok, message):
    if not ok:
        raise ValueError(message)


@dataclass(frozen=True)
class Program:
    ports: int
    source_rows: int
    states: tuple
    initial: int = 0


def validate(table, ports):
    need(type(ports) is int and ports >= 1, 'positive fixed ports')
    need(type(table) in (tuple,list) and len(table) > 0, 'nonempty fixed table')
    n = len(table)
    def index(x):
        need(type(x) is int and 0 <= x < n, 'closed row target')
    def port(x):
        need(type(x) is int and 0 <= x < ports, 'fixed physical port')
    out = []
    for pc,row in enumerate(table):
        need(type(row) in (tuple,list) and row and type(row[0]) is str, 'row shape')
        op = row[0]
        lengths = {'goto':2,'branch':4,'write':3,'move':3,'halt':1,'reject':2}
        need(op in lengths and len(row) == lengths[op], 'exact six-opcode grammar')
        if op == 'goto':
            index(row[1])
        elif op == 'branch':
            port(row[1]); index(row[3])
            need(type(row[2]) in (tuple,list), 'fixed branch pairs')
            keys = set()
            for pair in row[2]:
                need(type(pair) in (tuple,list) and len(pair) == 2, 'branch pair')
                symbol,target = pair
                need(type(symbol) is int and 0 <= symbol <= 6 and symbol not in keys,
                     'unique seven-symbol keys')
                keys.add(symbol); index(target)
        elif op in ('write','move'):
            port(row[1]); index(pc+1)
            need(type(row[2]) is int, 'literal integer')
            need(0 <= row[2] <= 6 if op == 'write' else row[2] in (-1,1),
                 'write alphabet or unit direction')
        elif op == 'reject':
            need(type(row[1]) is str, 'fixed reject label')
        out.append(tuple(row))
    return tuple(out)


def compile_table(table, ports):
    table = validate(table,ports)
    n = len(table); states = [None]*n
    def emit(node):
        states.append(tuple(node)); return len(states)-1
    success = emit(('stop','success',''))
    bad_code = emit(('stop','reject','whole virtual codeword'))
    unused_code = emit(('stop','reject','unused virtual codeword'))
    left_error = emit(('stop','reject','native routine crossed its local origin'))
    def chain(actions,nxt):
        for action in reversed(actions):
            nxt = emit(tuple(action)+(nxt,))
        return nxt
    def write_code(port,value,nxt):
        actions = []
        for shift in (2,1,0):
            actions.extend((('write',port,(value>>shift)&1),('move',port,1)))
        actions.extend([('move',port,-1)]*3)
        return chain(actions,nxt)
    def coded_read(port,destinations):
        def bit(j,value):
            if j == 3:
                target = unused_code if value == 7 else destinations[value]
                return chain([('move',port,-1)]*3,target)
            edges = [bad_code]*7
            for digit in (0,1):
                edges[digit] = emit(('move',port,1,bit(j+1,2*value+digit)))
            return emit(('read',port,tuple(edges)))
        first = bit(0,0)
        edges = [first]*7; edges[6] = destinations[4]
        return emit(('read',port,tuple(edges)))
    def coded_move(port,direction,nxt):
        if direction == 1:
            after = chain([('move',port,1)]*3,nxt)
            materialize = write_code(port,4,after)
            edges = [after]*7; edges[6] = materialize
            return emit(('read',port,tuple(edges)))
        ordinary = chain([('move',port,-1)]*2,nxt)
        restore = emit(('move',port,1,left_error))
        edges = [ordinary]*7; edges[2] = restore
        test = emit(('read',port,tuple(edges)))
        return emit(('move',port,-1,test))
    cleanup = success
    for port in reversed(range(ports)):
        start = len(states); states.extend([None]*3)
        states[start] = ('move',port,-1,start+1)
        states[start+1] = ('read',port,tuple(start+2 if s == 2 else start for s in range(7)))
        states[start+2] = ('move',port,1,cleanup)
        cleanup = start
    for pc,row in enumerate(table):
        op = row[0]
        if op == 'goto': target = row[1]
        elif op == 'halt': target = cleanup
        elif op == 'reject': target = emit(('stop','reject',row[1]))
        elif op == 'write': target = write_code(row[1],row[2],pc+1)
        elif op == 'move': target = coded_move(row[1],row[2],pc+1)
        else:
            cases = dict(row[2])  # construction only; unique fixed keys
            target = coded_read(row[1],tuple(cases.get(s,row[3]) for s in range(7)))
        states[pc] = ('nop',target)
    need(all(s is not None for s in states), 'all microstates defined')
    program = Program(ports,n,tuple(states))
    check_program(program)
    need(len(states) <= 48*n+3*ports+4, 'finite state bound')
    return program


def check_program(program):
    count = len(program.states)
    need(type(program.ports) is int and program.ports >= 1, 'positive ports')
    need(type(program.initial) is int and 0 <= program.initial < count, 'initial state')
    for node in program.states:
        op = node[0]
        if op == 'stop':
            need(len(node) == 3 and node[1] in ('success','reject') and type(node[2]) is str,
                 'finite terminal label')
            continue
        if op == 'nop':
            need(len(node) == 2, 'nop shape'); targets = (node[1],)
        elif op == 'read':
            need(len(node) == 3 and type(node[2]) is tuple and len(node[2]) == 7,
                 'total seven-symbol read'); targets = node[2]
        else:
            need(op in ('write','move') and len(node) == 4, 'action shape')
            need(type(node[2]) is int and (0 <= node[2] <= 6 if op == 'write' else node[2] in (-1,1)),
                 'action domain'); targets = (node[3],)
        if op != 'nop':
            need(type(node[1]) is int and 0 <= node[1] < program.ports, 'port range')
        need(all(type(x) is int and 0 <= x < count for x in targets), 'closed micro targets')
    return True
