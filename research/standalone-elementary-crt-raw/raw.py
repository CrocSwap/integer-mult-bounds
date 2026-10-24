"""Actual fixed u2/t2/y8/back2 compact word, with standalone exchanges."""
from elementary import Elementary,Physical,transfer,ZERO,ONE,LEFT,RIGHT,BLANK,need
from rotation import Runner,compile_rotation

def constant(value):
    """Offline fixed caller descriptor; writes and head return remain charged."""
    tape=Physical()
    for bit in reversed(bin(value)[2:]):tape.append(int(bit))
    tape.append(RIGHT);tape.rewind();return tape

def dispose(tape):
    tape.clear();tape.step(-1);need(tape.read()==LEFT,'owned origin');tape.write(BLANK);tape.step(1)

class Raw:
    def __init__(self):
        self.engine=Elementary()
        self.u=tuple(constant(v) for v in (2,1,1024,12))
        self.t=tuple(constant(v) for v in (2,4,256,12))
        self.runner=Runner(Physical)
        self.programs={k:compile_rotation(k) for k in ('y_first','y_second','t_plus','t_minus','u_plus','u_minus')}
        self.calls=0;self.closed=False
    def shuttle(self,data,descriptor):
        out=self.engine.run(data,*descriptor)
        data.clear();transfer(out,data);out.clear();self.calls+=1
    def rotation(self,data,rom,kind):
        out=self.runner.run(data,rom,self.programs[kind])
        data.clear();transfer(out,data);out.clear()
    def run(self,data,rom):
        need(not self.closed and data is not rom,'live disjoint raw inputs')
        # This is a fixed source word, not an input-dependent host schedule.
        for kind in ('y_first','t_plus','y_second','t_minus','u_plus',
                     'y_first','t_plus','y_second','t_minus','u_minus'):
            if kind.startswith('t_'):
                self.shuttle(data,self.t);self.rotation(data,rom,kind);self.shuttle(data,self.t)
            elif kind.startswith('u_'):
                self.shuttle(data,self.u);self.rotation(data,rom,kind);self.shuttle(data,self.u)
            else:self.rotation(data,rom,kind)
        return data
    def close(self):
        need(not self.closed,'one raw owner')
        self.engine.close()
        for tape in (*self.u,*self.t,self.runner.left,self.runner.right,self.runner.output):dispose(tape)
        self.closed=True
