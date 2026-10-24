"""Conditional finite-handle inventory kernel; no native pointer-cost assumption.

JoyboyBrian, with substantial OpenAI Codex assistance. Apache-2.0.
"""

def need(ok, why):
    if not ok:
        raise ValueError(why)


def access_cost(words, width):
    return words * (12 * width + 3) + 3 * width + 1


def bounds(size):
    need(type(size) is int and size > 0, 'positive contract size')
    capacity = 64 * size
    width = capacity.bit_length()
    access = access_cost(capacity, width)
    return dict(capacity=capacity, width=width,
                accesses=1024*size, scalar=4096*size,
                bits=1024*size*access+4096*size*(16*width+16))


class Store:
    """Macro simulator: each word access pays a full sequential padded scan.

    Host indexing only fast-forwards that declared scan; it is not charged as
    one random access. The independent checker expands the bit instructions.
    """
    def __init__(self, size, width=None):
        self.limit = bounds(size)
        self.width = self.limit['width'] if width is None else width
        need(self.width >= self.limit['width'], 'handle width covers addresses')
        self.cells = []
        self.accesses = self.limit['capacity']  # initial complete zero fill
        self.scalar = 0

    def tick(self, count=1):
        self.scalar += count

    def allocate(self, values):
        values = list(values)
        need(len(self.cells)+len(values) <= self.limit['capacity'], 'metadata capacity')
        start = len(self.cells)
        for value in values:
            need(type(value) is int and 0 <= value < 1 << self.width, 'encoded finite handle')
            self.cells.append(value)
            self.accesses += 2  # read source word and write owned word
            self.tick(2)
        return start, len(values)

    def read(self, location):
        need(type(location) is int and 0 <= location < len(self.cells), 'bounded address')
        self.accesses += 1
        self.tick()
        return self.cells[location]

    def write(self, location, value):
        need(0 <= location < len(self.cells) and 0 <= value < 1 << self.width, 'bounded write')
        self.accesses += 1
        self.tick()
        self.cells[location] = value

    def finish(self):
        self.accesses += self.limit['capacity']  # complete owned cleanup
        self.cells[:] = [0]*len(self.cells)
        bits = self.accesses*access_cost(self.limit['capacity'], self.width)
        bits += self.scalar*(16*self.width+16)
        need(self.accesses <= self.limit['accesses'] and self.scalar <= self.limit['scalar'],
             'source-count upper bound')
        need(bits <= self.limit['bits'], 'bit-charge upper bound')
        return dict(accesses=self.accesses, scalar=self.scalar, bits=bits,
                    capacity=self.limit['capacity'], width=self.width)


def walk(store, graph):
    """Run a DFS over encoded nodes; word-addressed visited flags are charged."""
    rows = graph['rows']; edges = [] ; headers = []
    need(rows and graph['root'] == 0, 'canonical graph root')
    for tag, tape, children in rows:
        need(tag in (0,1) and (tag == 0 or not children), 'opaque tape body')
        need(all(type(c) is int and 0 <= c < len(rows) for c in children), 'graph child handle')
        headers.extend((tag, tape, len(edges), len(children)))
        edges.extend(children)
    h, _ = store.allocate(headers); e, _ = store.allocate(edges)
    seen, _ = store.allocate([0]*len(rows))
    stack, _ = store.allocate([0]*(len(edges)+1))
    out, _ = store.allocate([0]*len(rows))
    top=1; count=0
    while top:
        store.tick(8); top-=1; node=store.read(stack+top)
        if store.read(seen+node):
            continue
        store.write(seen+node,1)
        tag,tape,first,length=(store.read(h+4*node+i) for i in range(4))
        if tag:
            store.write(out+count,tape); count+=1
        else:
            for j in range(length-1,-1,-1):
                store.tick(8)
                need(top < len(edges)+1, 'bounded DFS stack')
                store.write(stack+top,store.read(e+first+j)); top+=1
    return [store.read(out+i) for i in range(count)]


def validate(snapshot, size, width=None):
    """Execute complete cached engine/external/storage membership predicates."""
    need(set(snapshot) == {'graphs','saved','external','auxiliary','storage','acquired'},
         'complete snapshot fields')
    need(len(snapshot['graphs']) == 3 and len(snapshot['saved']) == 2, 'three exact owners')
    total = sum(len(g['rows'])+sum(len(r[2]) for r in g['rows'])+g['attributes']
                for g in snapshot['graphs'])
    total += sum(map(len,snapshot['saved']))
    total += sum(len(snapshot[k]) for k in ('external','auxiliary','storage','acquired'))+1
    need(total <= size, 'bounded source graph contract')
    store=Store(size,width)
    store.tick(32*total)  # complete finite input/shape/range bookkeeping
    current=[walk(store,g) for g in snapshot['graphs']]
    lists=[*current,*snapshot['saved'],snapshot['external'],snapshot['auxiliary'],
           snapshot['storage'],snapshot['acquired']]
    need(all(type(x) is int and x > 0 for row in lists for x in row), 'positive tape handles')
    largest=max((x for row in lists for x in row),default=0)
    need(largest <= size, 'bounded tape handle universe')
    marks,_=store.allocate([0]*(largest+1))
    def clear():
        for i in range(largest+1):store.tick(2);store.write(marks+i,0)
    def insert(row, unique):
        at,n=store.allocate(row)
        for i in range(n):
            store.tick(6); x=store.read(at+i)
            old=store.read(marks+x)
            need(not unique or not old,'distinct physical inventory')
            store.write(marks+x,1)
    def same(left,right):
        need(len(left)==len(right),'same engine cardinality')
        clear();insert(left,True)
        at,n=store.allocate(right)
        for i in range(n):
            store.tick(6); x=store.read(at+i)
            need(store.read(marks+x)==1,'complete engine membership')
            store.write(marks+x,0)
    for i in range(2):same(snapshot['saved'][i],current[i])
    combined=snapshot['saved'][0]+snapshot['saved'][1]
    clear();insert(combined,True)
    at,n=store.allocate(current[2])
    for i in range(n):
        store.tick(6);need(store.read(marks+store.read(at+i))==0,'producer separated')
    expected=combined+snapshot['auxiliary']; external=snapshot['external']
    need(len(expected)==len(external),'complete external length')
    a,_=store.allocate(expected);b,_=store.allocate(external)
    for i in range(len(expected)):
        store.tick(4);need(store.read(a+i)==store.read(b+i),'ordered external binding')
    clear();insert(snapshot['storage']+snapshot['acquired']+external,True)
    return store.finish()


def exchange(roles, old, new, size):
    """The actual cache substitution, with every lookup/copy charged."""
    need(len(roles)+3 <= size and old != new, 'bounded exchange domain')
    store=Store(size); at,n=store.allocate(roles); out,_=store.allocate([0]*n)
    found=0
    for i in range(n):
        store.tick(8); value=store.read(at+i)
        need(value != new,'replacement absent')
        found += value == old
        store.write(out+i,new if value == old else value)
    need(found==1,'one replaced handle')
    result=[store.read(out+i) for i in range(n)]
    return result,store.finish()


def complete_bound(size, gamma, returns_per_gamma=511014, service_per_gamma=336):
    need(type(gamma) is int and gamma>0, 'positive cover size')
    need(returns_per_gamma==511014 and service_per_gamma==336, 'complete source census')
    c=returns_per_gamma*gamma; s=service_per_gamma*gamma
    # Constructor check + before/after at every return. No test-only final check.
    checks=1+2*c
    exchanges=c+s  # one native exchange always; service exchange on service calls
    u=bounds(size)['bits']
    # One paid finite installation/dispatch/rebinding budget per return and init.
    binding=(c+1)*u
    return dict(validations=checks, cache_exchanges=exchanges,
                residual_binding_budgets=c+1,
                control_upper=(checks+exchanges+c+1)*u,
                tape_saving_coefficient=11*c,tape_saving_constant=4*c)
