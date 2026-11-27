"""Fixed-tape Toom-3. Only the tape simulator and fixtures see absolute positions."""
from dataclasses import dataclass, field
import json
import random

BLANK, HOME, RIGHT = ".", "^", "|"
LEFT = ("L", 0, 0)
PART, CHILD, OUTPUT, A0, A1, A2, B0, B1, B2 = range(9)
AV, BV, V0, V1, VM, V2, VI, C2, SUM13, U, C3, C1, RESULT = range(9, 22)
STAGES = (
    (((A0,1),), ((B0,1),), V0),
    (((A0,1),(A1,1),(A2,1)), ((B0,1),(B1,1),(B2,1)), V1),
    (((A0,1),(A1,-1),(A2,1)), ((B0,1),(B1,-1),(B2,1)), VM),
    (((A0,1),(A1,2),(A2,4)), ((B0,1),(B1,2),(B2,4)), V2),
    (((A2,1),), ((B2,1),), VI),
)


@dataclass
class Tape:
    data: dict = field(default_factory=lambda: {-1: HOME})
    head: int = 0
    ticks: int = 0
    low: int = 0
    high: int = 0

    def read(self):
        self.ticks += 1
        return self.data.get(self.head, BLANK)

    def put(self, symbol):
        self.ticks += 1
        if symbol == BLANK:
            self.data.pop(self.head, None)
        else:
            self.data[self.head] = symbol

    def step(self, delta):
        assert delta in (-1, 1)
        self.ticks += 1
        self.head += delta
        self.low = min(self.low, self.head)
        self.high = max(self.high, self.head)


def at_left(symbol):
    return isinstance(symbol, tuple)


def front(t):
    while t.read() != HOME:
        t.step(-1)
    t.step(1)


def clear(t):
    front(t)
    while t.read() != BLANK:
        t.put(BLANK)
        t.step(1)
    front(t)


def frame_home(f):
    while not at_left(f.read()):
        f.step(-1)


def bit(col, reg):
    return (col >> reg) & 1


def replace(col, reg, value):
    return (col & ~(1 << reg)) | (value << reg)


def linear(f, dst, terms):
    carry = 0
    f.step(1)
    while (col := f.read()) != RIGHT:
        value = carry + sum(coef*bit(col, reg) for reg, coef in terms)
        f.put(replace(col, dst, value % 2))
        carry = value // 2
        f.step(1)
    frame_home(f)


def high_sign(f, reg):
    f.step(1)
    sign = 0
    while (col := f.read()) != RIGHT:
        sign = bit(col, reg)
        f.step(1)
    frame_home(f)
    return sign


def divide(f, reg, divisor):
    f.step(1)
    while f.read() != RIGHT:
        f.step(1)
    rem = 0
    f.step(-1)
    while not at_left(col := f.read()):
        q, rem = divmod(2*rem+bit(col, reg), divisor)
        f.put(replace(col, reg, q))
        f.step(-1)
    assert rem == 0

def mark_extent(f, tape, reg, copies=1, extra=0):
    f.step(1)
    for _ in range(copies):
        while tape.read() != BLANK:
            f.put(replace(f.read(), reg, 1))
            f.step(1)
            tape.step(1)
        front(tape)
    for _ in range(extra):
        f.put(replace(f.read(),reg,1))
        f.step(1)
    frame_home(f)


def enter_frame(f, x, y, ruler):
    f.put(LEFT)
    f.step(1)
    for _ in range(8):
        while x.read() != BLANK:
            f.put(0)
            f.step(1)
            x.step(1)
        front(x)
    for _ in range(64):
        f.put(0)
        f.step(1)
    f.put(RIGHT)
    frame_home(f)
    mod3 = 0
    while x.read() != BLANK:
        if mod3 == 0:
            ruler.put(1)
            ruler.step(1)
        mod3 = (mod3 + 1) % 3
        x.step(1)
    front(x)
    front(ruler)
    mark_extent(f,ruler,PART)
    mark_extent(f,ruler,CHILD,extra=3)
    mark_extent(f,x,OUTPUT,copies=2)
    for ar, br in ((A0,B0),(A1,B1),(A2,B2)):
        f.step(1)
        while bit(col := f.read(), PART):
            for reg, tape in ((ar,x),(br,y)):
                z = tape.read()
                if z != BLANK:
                    col = replace(col, reg, z)
                    tape.step(1)
            f.put(col)
            f.step(1)
        frame_home(f)
    clear(x)
    clear(y)
    clear(ruler)


def issue(f, x, y, stage):
    left, right, _ = STAGES[stage]
    linear(f, AV,left)
    linear(f, BV,right)
    sx, sy = high_sign(f,AV), high_sign(f,BV)
    if sx:
        linear(f,AV,((AV,-1),))
    if sy:
        linear(f,BV,((BV,-1),))
    f.put(("L",stage,sx ^ sy))
    f.step(1)
    while bit(col := f.read(),CHILD):
        x.put(bit(col,AV))
        y.put(bit(col,BV))
        x.step(1)
        y.step(1)
        f.step(1)
    front(x)
    front(y)
    while f.read() != RIGHT:
        f.step(1)
    f.step(1)


def receive(f, out, stage, sign):
    dst = STAGES[stage][2]
    f.step(1)
    while (v := out.read()) != BLANK:
        f.put(replace(f.read(),dst,v))
        out.put(BLANK)
        out.step(1)
        f.step(1)
    front(out)
    frame_home(f)
    if sign:
        linear(f,dst,((dst,-1),))


def shifted_add(f, temp, reg):
    # RESULT <- 2^m RESULT + reg with a signed-width scratch word.
    f.step(1)
    while (col := f.read()) != RIGHT:
        temp.put(bit(col,RESULT))
        temp.step(1)
        f.step(1)
    front(temp)
    frame_home(f)
    carry = 0
    f.step(1)
    while (col := f.read()) != RIGHT:
        old = 0
        if not bit(col,PART):
            old = temp.read()
            temp.step(1)
        val = old+bit(col,reg)+carry
        f.put(replace(col,RESULT,val % 2))
        carry = val//2
        f.step(1)
    frame_home(f)
    clear(temp)


def interpolate(f, out, temp):
    linear(f,C2,((V1,1),(VM,1)))
    divide(f,C2,2)
    linear(f,C2,((C2,1),(V0,-1),(VI,-1)))
    linear(f,SUM13,((V1,1),(VM,-1)))
    divide(f,SUM13,2)
    linear(f,U,((V2,1),(V0,-1),(C2,-4),(VI,-16)))
    divide(f,U,2)
    linear(f,C3,((U,1),(SUM13,-1)))
    divide(f,C3,3)
    linear(f,C1,((SUM13,1),(C3,-1)))
    linear(f,RESULT,((VI,1),))
    for reg in (C3,C2,C1,V0):
        shifted_add(f,temp,reg)
    f.step(1)
    while bit(col := f.read(),OUTPUT):
        out.put(bit(col,RESULT))
        out.step(1)
        f.step(1)
    front(out)
    while f.read() != RIGHT:
        f.step(1)
    f.put(BLANK)
    f.step(-1)
    while not at_left(f.read()):
        f.put(BLANK)
        f.step(-1)
    f.put(BLANK)

def small(x, y, out):
    a = b = n = 0
    while n<9 and (digit := x.read())!=BLANK:
        a |= digit << n
        b |= y.read() << n
        n += 1
        x.step(1)
        y.step(1)
    front(x)
    front(y)
    if n==9:
        return False
    c = 0
    for _ in range(8):
        if b % 2:
            c = (c+a) % 65536
        b //= 2
        a = (2*a) % 65536
    for _ in range(2*n):
        out.put(c % 2)
        out.step(1)
        c //= 2
    front(out)
    clear(x)
    clear(y)
    return True


def multiply(f,x,y,out,ruler,temp):
    # The physical frame tape stores every continuation.
    entering = True
    while True:
        if entering:
            if not small(x,y,out):
                enter_frame(f,x,y,ruler)
                issue(f,x,y,0)
                continue
            entering=False
        f.step(-1)
        if f.read()==HOME:
            f.step(1)
            return
        frame_home(f)
        _, stage, negative = f.read()
        receive(f,out,stage,negative)
        if stage<4:
            issue(f,x,y,stage+1)
            entering=True
        else:
            interpolate(f,out,temp)


def check(w,x,y):
    f, a, b, out, ruler, temp = tapes = [Tape() for _ in range(6)]
    for tape,value in ((a,x),(b,y)):
        tape.data.update({i:(value>>i)&1 for i in range(w)})
    multiply(*tapes)
    expected={-1:HOME}
    expected.update({i:(x*y>>i)&1 for i in range(2*w)})
    assert out.data==expected
    assert all(t.head==0 for t in tapes)
    assert all(t.data=={-1:HOME} for t in (f,a,b,ruler,temp))
    ticks=sum(t.ticks for t in tapes)
    visited=sum(t.high-t.low+1 for t in tapes)
    assert ticks*ticks <= (2**28)**2*(w+1)**3
    assert visited<=256*(w+1)
    return ticks,visited


def main():
    rng=random.Random(2608)
    cases=[]
    for w in (1,2,3,4):
        cases.extend((w,x,y) for x in range(1<<w) for y in range(1<<w))
    for w in (7,8,9,10,11,15,17,23,24,25,26,31,48,64,81):
        mask=(1<<w)-1
        m=(w+2)//3
        cases.extend([(w,0,mask),(w,mask,mask),(w,((1<<m)-1)<<m,1)])
        cases.extend((w,rng.getrandbits(w),rng.getrandbits(w)) for _ in range(2))
    receipts=[check(*case) for case in cases]
    print(json.dumps({"word_pairs":len(cases),"largest_width":max(w for w,_,_ in cases),
          "max_single_action_count":max(t for t,_ in receipts),
          "max_cells":max(v for _,v in receipts)},sort_keys=True))


if __name__=="__main__":
    main()
