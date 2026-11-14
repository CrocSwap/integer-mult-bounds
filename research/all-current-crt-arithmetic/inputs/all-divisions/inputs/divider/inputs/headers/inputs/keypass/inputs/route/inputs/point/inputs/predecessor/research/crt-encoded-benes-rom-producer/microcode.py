"""Fixed bit-symbol microcode for the missing PR4192 scalar/arena boundary.

JoyboyBrian, substantial OpenAI assistance. Apache-2.0.
"""

class Builder:
    def __init__(self):
        self.code=[]; self.labels={}; self.serial=0
    def label(self, tag='l'):
        self.serial+=1; return f'{tag}_{self.serial}'
    def mark(self, label): self.labels[label]=len(self.code)
    def e(self, op, *args): self.code.append((op,*args))
    def branch(self, reg, value, yes, no): self.e('branch',reg,value,yes,no)
    def finish(self):
        out=[]
        for op,*a in self.code:
            if op=='jump': a[0]=self.labels[a[0]]
            if op=='branch': a[2]=self.labels[a[2]];a[3]=self.labels[a[3]]
            out.append((op,*a))
        return tuple(out)
    def rewind(self, role):
        loop,back,done=[self.label() for _ in range(3)]
        self.mark(loop);self.e('read',role,'s');self.branch('s','L',done,back)
        self.mark(back);self.e('move',role,-1);self.e('jump',loop);self.mark(done)
    def each(self, role, body):
        loop,more,done=[self.label() for _ in range(3)]
        self.e('move',role,1);self.mark(loop);self.e('read',role,'s');self.branch('s','R',done,more)
        self.mark(more);body();self.e('move',role,1);self.e('jump',loop)
        self.mark(done);self.rewind(role)
    def clear(self, role): self.each(role,lambda:self.e('write',role,'0'))
    def copy(self, src, dst):
        self.e('move',dst,1)
        def body():self.e('read',src,'bit');self.e('write_reg',dst,'bit');self.e('move',dst,1)
        self.each(src,body);self.rewind(dst)
    def xor1(self, role):
        self.e('move',role,1);self.e('read',role,'bit');self.e('not','bit','bit');self.e('write_reg',role,'bit');self.e('move',role,-1)
    def inc(self, role):
        loop,zero,one,overflow,done=[self.label() for _ in range(5)]
        self.e('move',role,1);self.mark(loop);self.e('read',role,'bit');self.branch('bit','R',overflow,zero+'_test')
        self.mark(zero+'_test');self.branch('bit','0',zero,one)
        self.mark(zero);self.e('write',role,'1');self.e('jump',done)
        self.mark(one);self.e('write',role,'0');self.e('move',role,1);self.e('jump',loop)
        self.mark(overflow);self.e('halt','overflow');self.mark(done);self.rewind(role)
    def dec(self, role):
        loop,zero,one,underflow,done=[self.label() for _ in range(5)]
        self.e('move',role,1);self.mark(loop);self.e('read',role,'bit');self.branch('bit','R',underflow,zero+'_test')
        self.mark(zero+'_test');self.branch('bit','0',zero,one)
        self.mark(one);self.e('write',role,'0');self.e('jump',done)
        self.mark(zero);self.e('write',role,'1');self.e('move',role,1);self.e('jump',loop)
        self.mark(underflow);self.e('halt','underflow');self.mark(done);self.rewind(role)
    def equal(self, left, right, flag):
        self.e('set',flag,'1');self.e('move',right,1)
        def body():
            same,diff,after=[self.label() for _ in range(3)]
            self.e('read',left,'a');self.e('read',right,'b');self.e('eq','a','b','test');self.branch('test','1',same,diff)
            self.mark(diff);self.e('set',flag,'0');self.e('jump',after);self.mark(same);self.mark(after);self.e('move',right,1)
        self.each(left,body);self.rewind(right)
    def zero(self, role, flag):
        self.e('set',flag,'1')
        def body():
            no,yes=[self.label() for _ in range(2)]
            self.e('read',role,'bit');self.branch('bit','0',yes,no);self.mark(no);self.e('set',flag,'0');self.mark(yes)
        self.each(role,body)
    def constant(self, role, value):
        self.clear(role)
        self.e('move',role,1)
        for bit in bin(value)[:1:-1]:self.e('write',role,bit);self.e('move',role,1)
        self.rewind(role)
    def access(self, keys, put=False):
        """Scan original PR4192 four-key/one-value records, all heads returned."""
        loop,record,end,missing=[self.label() for _ in range(4)]
        self.e('set','found','0');self.e('move','arena',1);self.mark(loop);self.e('read','arena','s');self.branch('s','R',end,record)
        self.mark(record);self.e('set','match','1')
        for key in keys:
            def body(key=key):
                same,diff,after=[self.label() for _ in range(3)]
                self.e('read',key,'a');self.e('read','arena','b');self.e('eq','a','b','test');self.branch('test','1',same,diff)
                self.mark(diff);self.e('set','match','0');self.e('jump',after);self.mark(same);self.mark(after);self.e('move','arena',1)
            self.each(key,body)
        selected,skip,after=[self.label() for _ in range(3)]
        self.branch('match','1',selected,skip);self.mark(selected)
        unique=self.label();self.branch('found','0',unique,missing);self.mark(unique);self.e('set','found','1')
        def valuebody():
            if put:self.e('read','value','bit');self.e('write_reg','arena','bit')
            else:self.e('read','arena','bit');self.e('write_reg','value','bit')
            self.e('move','arena',1)
        self.each('value',valuebody);self.e('jump',after);self.mark(skip)
        self.each('value',lambda:self.e('move','arena',1));self.mark(after);self.e('jump',loop)
        self.mark(end);self.rewind('arena');ok=self.label();self.branch('found','1',ok,missing)
        self.mark(missing);self.e('halt','missing_or_duplicate_record');self.mark(ok)


def cycle_program():
    """One exact PR4192 pop and its ordered two-neighbour visits; no host scalars."""
    b=Builder();keys=('node','kind','layer','index')
    def get(kind,index,dst,node='root'):
        b.copy(node,'node');b.constant('kind',kind);b.clear('layer');b.copy(index,'index');b.access(keys);b.copy('value',dst)
    def put(kind,index,src,node='root'):
        b.copy(node,'node');b.constant('kind',kind);b.clear('layer');b.copy(index,'index');b.copy(src,'value');b.access(keys,True)
    b.dec('top');get(4,'top','x','zero');put(4,'top','n','zero')
    for edge in (0,1):
        if edge==0:b.copy('x','other');b.xor1('other')
        else:get(0,'x','other');b.xor1('other');get(1,'other','other')
        get(2,'x','opposite');b.xor1('opposite');get(2,'other','color')
        b.equal('color','n','uncolored');fresh,old,done=[b.label() for _ in range(3)]
        b.branch('uncolored','1',fresh,old);b.mark(fresh)
        put(2,'other','opposite');put(4,'top','other','zero');b.inc('top');b.e('jump',done)
        b.mark(old);b.equal('color','opposite','consistent');good=b.label();b.branch('consistent','1',good,'inconsistent');b.mark(good);b.mark(done)
    b.e('halt','accept');b.mark('inconsistent');b.e('halt','inconsistent_color')
    return b.finish()


def execute(program, tapes, max_steps=20000000):
    """Only fixed-symbol instructions; host objects are emulator configurations."""
    heads={r:0 for r in tapes};regs={};pc=steps=0
    while steps<max_steps:
        op,*a=program[pc];pc+=1;steps+=1
        if op=='read':regs[a[1]]=tapes[a[0]][heads[a[0]]]
        elif op=='write':tapes[a[0]][heads[a[0]]]=a[1]
        elif op=='write_reg':tapes[a[0]][heads[a[0]]]=regs[a[1]]
        elif op=='move':
            heads[a[0]]+=a[1]
            if heads[a[0]]<0:raise ValueError('head before origin')
            if heads[a[0]]==len(tapes[a[0]]):tapes[a[0]].append('_')
        elif op=='set':regs[a[0]]=a[1]
        elif op=='copybit':regs[a[1]]=regs[a[0]]
        elif op=='not':
            if regs[a[0]] not in ('0','1'):raise ValueError('not a bit')
            regs[a[1]]='1' if regs[a[0]]=='0' else '0'
        elif op=='eq':regs[a[2]]='1' if regs[a[0]]==regs[a[1]] else '0'
        elif op=='branch':pc=a[2] if regs[a[0]]==a[1] else a[3]
        elif op=='jump':pc=a[0]
        elif op=='halt':return {'status':a[0],'steps':steps,'heads':heads,'registers':regs}
        else:raise ValueError('unknown instruction')
    raise ValueError('watchdog; not a machine exit')

class Compiler(Builder):
    def init_like(self, dst, src='h'):
        self.e('write',dst,'L');self.e('move',dst,1)
        self.each(src,lambda:(self.e('write',dst,'0'),self.e('move',dst,1)))
        self.e('write',dst,'R');self.rewind(dst)
    def erase(self, role):
        loop,more,end=[self.label() for _ in range(3)]
        self.e('move',role,1);self.mark(loop);self.e('read',role,'s');self.branch('s','R',end,more)
        self.mark(more);self.e('write',role,'_');self.e('move',role,1);self.e('jump',loop)
        self.mark(end);self.e('write',role,'_');self.rewind(role);self.e('write',role,'_')
    def half(self, role):
        loop,more,end=[self.label() for _ in range(3)]
        self.e('move',role,1);self.mark(loop);self.e('move',role,1);self.e('read',role,'bit');self.branch('bit','R',end,more)
        self.mark(more);self.e('move',role,-1);self.e('write_reg',role,'bit');self.e('move',role,1);self.e('jump',loop)
        self.mark(end);self.e('move',role,-1);self.e('write',role,'0');self.rewind(role)
    def double(self, role):
        self.e('set','carry','0')
        def body():
            self.e('read',role,'bit');self.e('write_reg',role,'carry');self.e('copybit','bit','carry')
        self.each(role,body);ok=self.label();self.branch('carry','0',ok,'reject');self.mark(ok)
    def less(self,left,right,flag):
        self.e('set',flag,'0');self.e('move',right,1)
        def body():
            same,diff,after=[self.label() for _ in range(3)]
            self.e('read',left,'a');self.e('read',right,'b');self.e('eq','a','b','test');self.branch('test','1',same,diff)
            self.mark(diff);self.e('copybit','b',flag);self.e('jump',after);self.mark(same);self.mark(after);self.e('move',right,1)
        self.each(left,body);self.rewind(right)
    def while_ne(self,left,right,body):
        loop,more,end=[self.label() for _ in range(3)]
        self.mark(loop);self.equal(left,right,'condition');self.branch('condition','1',end,more)
        self.mark(more);body();self.e('jump',loop);self.mark(end)
    def while_nz(self,role,body):
        loop,more,end=[self.label() for _ in range(3)]
        self.mark(loop);self.zero(role,'condition');self.branch('condition','1',end,more)
        self.mark(more);body();self.e('jump',loop);self.mark(end)
    def repeat(self,counter,limit,body):
        self.clear(counter)
        self.while_ne(counter,limit,lambda:(body(),self.inc(counter)))
    def get(self,kind,index,dst,node='cur_node',layer='zero'):
        self.copy(node,'node');self.constant('kind',kind);self.copy(layer,'layer');self.copy(index,'index')
        self.access(('node','kind','layer','index'));self.copy('value',dst)
    def put(self,kind,index,src,node='cur_node',layer='zero'):
        self.copy(node,'node');self.constant('kind',kind);self.copy(layer,'layer');self.copy(index,'index')
        self.copy(src,'value');self.access(('node','kind','layer','index'),True)
    def append_word(self,src,dst):
        self.each(src,lambda:(self.e('read',src,'bit'),self.e('write_reg',dst,'bit'),self.e('move',dst,1)))
    def append_record(self):
        for role in ('cur_node','init_kind','init_layer','init_index','init_value'):self.append_word(role,'arena')
    def check_header(self,role):
        self.e('read',role,'bit');entry=self.label();self.branch('bit','L',entry,'reject');self.mark(entry)
        self.e('move',role,1)
        def body():
            good,other=[self.label() for _ in range(2)]
            self.e('read',role,'bit');self.branch('bit','0',good,other);self.mark(other);self.branch('bit','1',good,'reject');self.mark(good);self.e('move',role,1)
        self.each('h',body);self.e('read',role,'bit');ok=self.label();self.branch('bit','R',ok,'reject');self.mark(ok);self.rewind(role)

REGS=('zero','one','two','root','n','remaining','depth','height','low','high','size','cur_node',
      'init_kind','init_layer','init_index','init_value','limit','xloop','yloop','px','py',
      'node','kind','layer','index','value','x','other','opposite','color','initial','top',
      'off','permuted','addition','child','child_index','inverse','last','outlayer','layloop',
      'layers_count','column','check')


def producer_program():
    b=Compiler()
    # Validate the supplied bit record before using its width to lay out scratch.
    b.e('read','h','bit');entry=b.label();b.branch('bit','L',entry,'reject');b.mark(entry)
    for _ in range(4):
        b.e('move','h',1);b.e('read','h','bit');good,other=b.label(),b.label()
        b.branch('bit','0',good,other);b.mark(other);b.branch('bit','1',good,'reject');b.mark(good)
    loop,more,end=b.label(),b.label(),b.label();b.mark(loop);b.e('move','h',1);b.e('read','h','bit');b.branch('bit','R',end,more);b.mark(more)
    good,other=b.label(),b.label();b.branch('bit','0',good,other);b.mark(other);b.branch('bit','1',good,'reject');b.mark(good);b.e('jump',loop);b.mark(end);b.rewind('h')
    b.e('read','offsets','bit');entry=b.label();b.branch('bit','L',entry,'reject');b.mark(entry)
    for role in REGS:b.init_like(role)
    for role in ('modulus','selected_layer'):b.check_header(role)
    b.constant('one',1);b.constant('two',2);b.constant('root',1)
    b.zero('h','condition');nonzero=b.label();b.branch('condition','0',nonzero,'reject');b.mark(nonzero)
    b.copy('h','remaining');b.copy('one','n')
    b.while_nz('remaining',lambda:(b.double('n'),b.dec('remaining')))
    b.copy('n','check');b.double('check');b.double('check');b.clear('check')
    b.zero('modulus','condition');ok=b.label();b.branch('condition','0',ok,'reject');b.mark(ok)
    b.less('n','modulus','condition');ok=b.label();b.branch('condition','0',ok,'reject');b.mark(ok)
    b.copy('h','layers_count');b.double('layers_count');b.dec('layers_count')
    b.less('selected_layer','layers_count','condition');ok=b.label();b.branch('condition','1',ok,'reject');b.mark(ok)
    b.e('write','spool','L');b.e('move','spool',1);b.e('move','offsets',1);b.e('set','has_offset','0')
    offset_loop,offset_more,offset_end=[b.label() for _ in range(3)]
    b.mark(offset_loop);b.e('read','offsets','bit');b.branch('bit','R',offset_end,offset_more);b.mark(offset_more)
    # Read exactly W binary bits, then one separator. No decoded list length.
    def offset_bit():
        good,other=[b.label() for _ in range(2)]
        b.e('read','offsets','bit');b.branch('bit','0',good,other);b.mark(other);b.branch('bit','1',good,'reject');b.mark(good)
        b.e('write_reg','off','bit');b.e('move','offsets',1)
    b.each('off',offset_bit);b.e('read','offsets','bit');ok=b.label();b.branch('bit','|',ok,'reject');b.mark(ok);b.e('move','offsets',1)
    b.less('off','modulus','condition');ok=b.label();b.branch('condition','1',ok,'reject');b.mark(ok)
    b.e('set','has_offset','1')
    # The predecessor's heap-node arena, with one shared N-slot stack.
    b.e('write','arena','L');b.e('move','arena',1)
    b.copy('n','size');b.copy('h','height');b.copy('one','low');b.copy('two','high')
    def init_depth():
        b.copy('low','cur_node')
        def init_node():
            for kind in (0,1,2):
                b.constant('init_kind',kind);b.clear('init_layer');b.copy('n' if kind==2 else 'zero','init_value')
                b.repeat('init_index','size',b.append_record)
            b.constant('init_kind',3);b.copy('height','limit');b.double('limit');b.dec('limit');b.clear('init_value')
            b.repeat('init_layer','limit',lambda:b.repeat('init_index','size',b.append_record));b.inc('cur_node')
        b.while_ne('cur_node','high',init_node);b.double('low');b.double('high');b.half('size');b.dec('height')
    b.repeat('depth','h',init_depth)
    b.clear('cur_node');b.constant('init_kind',4);b.clear('init_layer');b.copy('n','init_value');b.repeat('init_index','n',b.append_record)
    b.e('write','arena','R');b.rewind('arena')
    # Generate the padded rotation directly into root P.
    def rotation_entry():
        b.copy('xloop','permuted');b.less('xloop','modulus','condition')
        rotate,keep,done=[b.label() for _ in range(3)];b.branch('condition','1',rotate,keep);b.mark(rotate)
        b.copy('off','addition')
        def addstep():
            b.inc('permuted');b.equal('permuted','modulus','condition');wrap,no=[b.label() for _ in range(2)]
            b.branch('condition','1',wrap,no);b.mark(wrap);b.clear('permuted');b.mark(no);b.dec('addition')
        b.while_nz('addition',addstep);b.e('jump',done);b.mark(keep);b.mark(done);b.put(0,'xloop','permuted',node='root')
    b.repeat('xloop','n',rotation_entry)
    # Top-down routing. P is a permutation by padded-rotation and child induction.
    b.copy('n','size');b.copy('h','height');b.copy('one','low');b.copy('two','high')
    def compile_depth():
        b.copy('low','cur_node')
        def compile_node():
            b.equal('size','two','condition');leaf,internal,done=[b.label() for _ in range(3)];b.branch('condition','1',leaf,internal)
            b.mark(leaf);b.get(0,'zero','px');b.put(3,'zero','px');b.put(3,'one','px');b.e('jump',done)
            b.mark(internal)
            b.repeat('xloop','size',lambda:(b.get(0,'xloop','px'),b.put(1,'px','xloop')))
            def component():
                b.get(2,'initial','color');b.equal('color','n','condition');new,old=[b.label() for _ in range(2)];b.branch('condition','1',new,old);b.mark(new)
                b.put(2,'initial','zero');b.clear('top');b.put(4,'top','initial',node='zero');b.inc('top')
                def pop():
                    b.dec('top');b.get(4,'top','x',node='zero');b.put(4,'top','n',node='zero')
                    for edge in (0,1):
                        if edge==0:b.copy('x','other');b.xor1('other')
                        else:b.get(0,'x','other');b.xor1('other');b.get(1,'other','other')
                        b.get(2,'x','opposite');b.xor1('opposite');b.get(2,'other','color');b.equal('color','n','uncolored')
                        fresh,seen,after=[b.label() for _ in range(3)];b.branch('uncolored','1',fresh,seen);b.mark(fresh)
                        b.put(2,'other','opposite');b.less('top','n','condition');capacity=b.label();b.branch('condition','1',capacity,'reject');b.mark(capacity)
                        b.put(4,'top','other',node='zero');b.inc('top');b.e('jump',after);b.mark(seen)
                        b.equal('color','opposite','consistent');good=b.label();b.branch('consistent','1',good,'reject');b.mark(good);b.mark(after)
                b.while_nz('top',pop);b.mark(old)
            b.repeat('initial','size',component)
            def outputs():
                b.get(2,'xloop','color');b.copy('color','px');b.e('move','xloop',1);b.e('read','xloop','parity');b.e('move','xloop',-1)
                flip,keep=[b.label() for _ in range(2)];b.branch('parity','1',flip,keep);b.mark(flip);b.xor1('px');b.mark(keep);b.put(3,'xloop','px')
                b.get(1,'xloop','inverse');b.get(2,'inverse','last')
                b.e('move','xloop',1);b.e('read','xloop','parity');b.e('move','xloop',-1)
                flip,keep=[b.label() for _ in range(2)];b.branch('parity','1',flip,keep);b.mark(flip);b.xor1('last');b.mark(keep)
                b.copy('height','outlayer');b.double('outlayer');b.dec('outlayer');b.dec('outlayer');b.put(3,'xloop','last',layer='outlayer')
                b.copy('cur_node','child');b.double('child');b.zero('color','condition');add,no=[b.label() for _ in range(2)];b.branch('condition','0',add,no);b.mark(add);b.inc('child');b.mark(no)
                b.copy('xloop','child_index');b.half('child_index');b.get(0,'xloop','px');b.half('px');b.put(0,'child_index','px',node='child')
            b.repeat('xloop','size',outputs);b.mark(done);b.inc('cur_node')
        b.while_ne('cur_node','high',compile_node);b.double('low');b.double('high');b.half('size');b.dec('height')
    b.repeat('depth','h',compile_depth)
    # Bottom-up child interleaving (start with the parents of leaves).
    b.copy('h','depth');b.dec('depth');b.copy('n','low');b.half('low');b.copy('n','high');b.copy('two','size');b.copy('one','height')
    def assemble_depth():
        b.dec('depth');b.half('low');b.half('high');b.double('size');b.inc('height');b.copy('low','cur_node')
        def assemble_node():
            b.copy('height','limit');b.double('limit');b.dec('limit');b.dec('limit');b.dec('limit')
            def childlayer():
                def childbit():
                    b.copy('cur_node','child');b.double('child');b.e('move','xloop',1);b.e('read','xloop','parity');b.e('move','xloop',-1)
                    add,no=[b.label() for _ in range(2)];b.branch('parity','1',add,no);b.mark(add);b.inc('child');b.mark(no)
                    b.copy('xloop','child_index');b.half('child_index');b.get(3,'child_index','px',node='child',layer='layloop')
                    b.copy('layloop','outlayer');b.inc('outlayer');b.put(3,'xloop','px',layer='outlayer')
                b.repeat('xloop','size',childbit)
            b.repeat('layloop','limit',childlayer);b.inc('cur_node')
        b.while_ne('cur_node','high',assemble_node)
    b.while_nz('depth',assemble_depth)
    def serialize_layer():
        def serialize_bit():
            b.get(3,'xloop','px',node='root',layer='layloop');b.e('move','px',1);b.e('read','px','bit');b.e('move','px',-1);b.e('write_reg','spool','bit');b.e('move','spool',1)
        b.repeat('xloop','n',serialize_bit)
    b.repeat('layloop','layers_count',serialize_layer);b.erase('arena');b.e('jump',offset_loop)
    b.mark(offset_end);b.rewind('offsets');ok=b.label();b.branch('has_offset','1',ok,'reject');b.mark(ok)
    b.e('write','spool','R');b.rewind('spool')
    b.e('write','layers','L');b.e('move','layers',1);b.e('write','rom','L');b.e('move','rom',1)
    def transpose_layer():
        b.equal('outlayer','selected_layer','selected_bit');b.e('move','spool',1)
        def transpose_group():
            def transpose_one():
                b.equal('layloop','outlayer','take')
                def copybit():
                    take,skip,done=[b.label() for _ in range(3)];b.e('read','spool','bit');b.branch('take','1',take,skip);b.mark(take)
                    b.e('write_reg','layers','bit');b.e('move','layers',1);yes,no=[b.label() for _ in range(2)];b.branch('selected_bit','1',yes,no);b.mark(yes);b.e('write_reg','rom','bit');b.e('move','rom',1);b.mark(no);b.e('jump',done)
                    b.mark(skip);b.mark(done);b.e('move','spool',1)
                b.repeat('column','n',copybit)
            b.repeat('layloop','layers_count',transpose_one)
        b.e('move','offsets',1);loop,more,done=b.label(),b.label(),b.label()
        b.mark(loop);b.e('read','offsets','bit');b.branch('bit','R',done,more);b.mark(more)
        transpose_group()
        b.each('h',lambda:b.e('move','offsets',1));b.e('move','offsets',1);b.e('jump',loop)
        b.mark(done);b.rewind('offsets');b.rewind('spool');b.e('write','layers','|');b.e('move','layers',1)
    b.repeat('outlayer','layers_count',transpose_layer)
    b.e('write','layers','R');b.rewind('layers');b.e('write','rom','R');b.rewind('rom');b.erase('spool')
    for role in REGS:b.erase(role)
    b.e('halt','accept');b.mark('reject');b.e('halt','reject')
    return b.finish()


def run_producer(headers, max_steps=2000000000):
    """Caller admission: four distinct borrowed roles; fixed blank owned bank.

    No header value or length is decoded here. Allocation models the stated
    initially blank fixed-tape ownership premise, not an unpriced ROM producer.
    """
    names=('h','modulus','selected_layer','offsets')
    if set(headers)!=set(names) or len({id(headers[n]) for n in names})!=4:
        raise ValueError('four distinct borrowed tape roles required')
    tapes={r:['_'] for r in REGS+('arena','spool','layers','rom')}
    tapes.update(headers)
    return execute(producer_program(),tapes,max_steps),tapes


def disposal_program():
    b=Compiler()
    for role in ('layers','rom'):b.erase(role)
    b.e('halt','accept')
    return b.finish()
