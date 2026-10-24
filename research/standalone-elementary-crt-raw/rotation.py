"""Fixed-geometry physical cyclic-fiber program; compiler and executor separated."""
from dataclasses import dataclass
# All lengths and ROM addresses below are compile-time control constants.
@dataclass(frozen=True)
class Fiber:
    zero: tuple
    one: tuple
    rom_address: int | None = None


def fiber(cut,radix,tail):
    a=(radix-cut%radix)*tail; b=(cut%radix)*tail
    return ((0,1,a),(0,2,b),(2,3,b),(1,3,a))


def compile_rotation(kind):
    result=[]
    if kind in ('y_first','y_second'):
        for u in range(4):
            for t in range(4):
                z=u&1
                cut=(2*z*t if kind=='y_first' else z*(1-2*t))*4
                result.append(Fiber(fiber(cut,256,48),fiber(cut,256,48)))
    elif kind in ('t_plus','t_minus'):
        # After t/back interchange: u,back,y,t. Back is a spectator.
        for u in range(4):
            for back in range(4):
                for y in range(256):
                    cut=((y>>2)&1) if kind=='t_plus' else -(((y>>2)&1)^(u&1))
                    result.append(Fiber(fiber(cut,4,12),fiber(cut,4,12)))
    elif kind in ('u_plus','u_minus'):
        # After u/back interchange: back,t,y,u. ROM omits target bit2.
        for back in range(4):
            for t in range(4):
                for y in range(256):
                    result.append(Fiber(fiber(0,4,12),fiber(1 if kind=='u_plus' else -1,4,12),y&31))
    else: raise ValueError(kind)
    return tuple(result)


# Fixed finite-state predecessor table; no runtime scalar decrement.
PREVIOUS=tuple(max(0,n-1) for n in range(196609))


class Runner:
    def __init__(self,Tape):
        self.left,self.right,self.output=Tape(),Tape(),Tape()
        self.control=0;self.rom_reads=0
    def copy(self,source,dest,state):
        # state belongs to this fixed program's finite 196609-symbol control.
        while state:
            symbol=source.read();dest.append(symbol);source.step(1)
            state=PREVIOUS[state];self.control+=1
        self.control+=1
    def run(self,source,rom,program):
        roles=(source,self.left,self.right,self.output)
        for node in program:
            self.control+=1
            code=node.zero
            if node.rom_address is not None:
                state=node.rom_address
                while state:
                    rom.step(1);state=PREVIOUS[state];self.control+=1
                symbol=rom.read();self.rom_reads+=1
                if symbol==1:code=node.one
                elif symbol!=0:raise ValueError('ROM bit')
                rom.rewind()
            first,second,third,fourth=code
            self.copy(roles[first[0]],roles[first[1]],first[2])
            self.copy(roles[second[0]],roles[second[1]],second[2])
            self.left.rewind();self.right.rewind()
            self.copy(roles[third[0]],roles[third[1]],third[2])
            self.copy(roles[fourth[0]],roles[fourth[1]],fourth[2])
            self.left.clear();self.right.clear()
        source.rewind();self.output.rewind()
        return self.output
