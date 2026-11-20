"""Exact logical common-grid execution; Python indexing is not tape work."""
from word import Word, turn


def require(ok, message):
    if not ok:
        raise ArithmeticError(message)


def depth(rank, base):
    result = 0
    while rank >= base:
        rank //= base
        result += 1
    return result


def execute(word, rows, axes, *, odd_exponent=None, guard_override=None,
            retire_odd=True, require_identity=True):
    require(isinstance(word, Word) and word.valid_syntax(), "invalid word")
    if require_identity:
        require(word.all_columns(), "failed all-column identity")
    require(rows and rows[0], "empty complete field")
    width = len(rows[0])
    require(width & (width-1) == 0, "field is not a complete Boolean cube")
    ambient = width.bit_length()-1
    require(axes and len(set(axes)) == len(axes), "empty or repeated axes")
    require(all(type(a) is int and 0 <= a < ambient for a in axes), "invalid axes")
    require(all(len(row)==width and all(len(z)==2 and all(type(v) is int for v in z)
                    for z in row) for row in rows), "invalid Gaussian integer fields")
    h,n,w,j = len(axes),word.dimension,word.productive,max(1,len(word.ops))
    d = depth(h,n)
    stock = w**d
    require(len(rows)>=stock, "insufficient productive row stock")
    original_count = len(rows)
    padded_count = ((original_count+stock-1)//stock)*stock
    source = [list(row) for row in rows]+[[(0,0)]*width for _ in range(padded_count-original_count)]
    odd,m = word.constants()
    budget = j*d if odd_exponent is None else odd_exponent
    guard = 8*(n+j*(m+2)+1)*(h+1) if guard_override is None else guard_override
    require(budget>=0 and guard>=h, "invalid lift budget")
    p = max(1,max(abs(v).bit_length() for row in source for z in row for v in z))
    capacity = p+2*guard+j*d*odd.bit_length()+4
    stats = {"rank":h,"depth":d,"D":odd,"J":j,"guard":guard,"capacity_bits":capacity,
             "original_rows":original_count,"padded_rows":padded_count,"max_bits":0,
             "paid_calls":0,"scalar_divisions":0,"C_divisions":0,"private_retired_values":0,
             "root_multiply_passes":budget,"root_divide_passes":budget if retire_odd else 0}

    def inspect(fields):
        bits = max((abs(v).bit_length() for row in fields for z in row for v in z),default=0)
        stats["max_bits"] = max(stats["max_bits"],bits)
        require(bits+1<=capacity,"capacity exceeded")

    def divide(z,q,kind):
        require(z[0]%q==0 and z[1]%q==0,"nonexact division")
        stats[kind] += 2
        return z[0]//q,z[1]//q

    def c_axis(fields,axis):
        mask = 1<<axis
        for row in fields:
            for a in range(width):
                if a & mask:
                    continue
                b = a|mask
                x,y = row[a],row[b]
                total = x[0]+y[0],x[1]+y[1]
                twist = -(x[1]-y[1]),x[0]-y[0]
                numer = (total[0]+twist[0],total[1]+twist[1])
                other = (total[0]-twist[0],total[1]-twist[1])
                inspect([[numer,other]])
                row[a],row[b] = divide(numer,2,"C_divisions"),divide(other,2,"C_divisions")

    lifted = [[(a<<guard,b<<guard) for a,b in row] for row in source]
    for _ in range(budget):
        lifted = [[(a*odd,b*odd) for a,b in row] for row in lifted]
    inspect(lifted)

    def visit(batch,active):
        f,r = divmod(len(active),n)
        for axis in active[n*f:]:
            c_axis(batch,axis)
        if f == 0:
            return batch
        require(len(batch)%w==0,"recursive productive stock")
        regs = [batch[k::w] for k in range(w)]
        regs += [[[(0,0)]*width for _ in regs[0]] for _ in range(word.owned)]
        blocks = [active[k*f:(k+1)*f] for k in range(n)]
        for op,reg,*args in word.ops:
            old = regs[reg]
            if op == "paid":
                stats["paid_calls"] += 1
                regs[reg] = visit(old,blocks[args[0]])
            elif op == "clear":
                stats["private_retired_values"] += len(old)*width
                regs[reg] = [[(0,0)]*width for _ in old]
            elif op in ("add","sub"):
                sign = 1 if op=="add" else -1
                regs[reg] = [[(a[0]+sign*b[0],a[1]+sign*b[1]) for a,b in zip(x,y)]
                             for x,y in zip(old,regs[args[0]])]
            elif op in ("scale","half","neg","i"):
                a,b,q = args if op=="scale" else (1,0,2) if op=="half" else (-1,0,1) if op=="neg" else (0,1,1)
                new = []
                for row in old:
                    result = []
                    for x,y in row:
                        numerator = a*x-b*y,b*x+a*y
                        inspect([[numerator]])
                        result.append(divide(numerator,q,"scalar_divisions"))
                    new.append(result)
                regs[reg] = new
            else:
                new = []
                for row in old:
                    result = [None]*width
                    for address,z in enumerate(row):
                        dest,phase = address,0
                        if op == "unit":
                            phase = f
                        elif op == "x":
                            for axis in blocks[args[0]]:
                                dest ^= 1<<axis
                        elif op == "s":
                            phase = sum((address>>axis)&1 for axis in blocks[args[0]])
                        elif op == "cz":
                            phase = 2*sum(((address>>a)&1)*((address>>b)&1)
                                          for a,b in zip(blocks[args[0]],blocks[args[1]]))
                        elif op == "cx":
                            for control,target in zip(blocks[args[0]],blocks[args[1]]):
                                dest ^= ((address>>control)&1)<<target
                        else:
                            raise ArithmeticError("unknown native operation")
                        result[dest] = turn(z,phase)
                    require(all(z is not None for z in result),"native permutation coverage")
                    new.append(result)
                regs[reg] = new
            inspect(regs[reg])
        require(all(z==(0,0) for bank in regs[w:] for row in bank for z in row),"nonzero private endpoint")
        return [row for group in zip(*regs[:w]) for row in group]

    result = visit(lifted,tuple(axes))
    stats["root_divisions"] = 0
    if retire_odd:
        for _ in range(budget):
            result = [[divide(z,odd,"root_divisions") for z in row] for row in result]
    result = [[divide(z,1<<(guard-h),"root_divisions") for z in row] for row in result]
    require(all(z==(0,0) for row in result[original_count:] for z in row),"nonzero padded output")
    return result[:original_count],stats
