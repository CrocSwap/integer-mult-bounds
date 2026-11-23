"""Value-exact finite-alphabet images of decoder-owned control.

Native iterator bodies are resident services identified by bounded slot numbers;
this module does not serialize or price those bodies.  The immutable event tape
and fixed chart dictionary are separately counted by the written storage theorem.
"""
from dataclasses import dataclass
from source_loader import library, load, need


class Writer:
    def __init__(self):
        self.data=bytearray(); self.pending=0; self.count=0; self.bits=0
    def put(self,value,width):
        need(isinstance(value,int) and 0<=value<(1<<width),'unsigned field overflow')
        self.pending=(self.pending<<width)|value; self.count+=width; self.bits+=width
        while self.count>=8:
            self.count-=8; self.data.append((self.pending>>self.count)&255)
        self.pending &= (1<<self.count)-1
    def finish(self):
        if self.count: self.data.append(self.pending<<(8-self.count))
        return bytes(self.data),self.bits


class Reader:
    def __init__(self,data,bits):
        need(0<=bits<=8*len(data) and len(data)==(bits+7)//8,'bad packed length')
        if bits%8: need(not(data[-1]&((1<<(8-bits%8))-1)),'nonzero padding')
        self.data=data; self.bits=bits; self.offset=0
    def get(self,width):
        need(width>=0 and self.offset+width<=self.bits,'truncated field')
        value=0; remaining=width
        while remaining:
            i,j=divmod(self.offset,8); take=min(8-j,remaining)
            value=(value<<take)|((self.data[i]>>(8-j-take))&((1<<take)-1))
            self.offset+=take; remaining-=take
        return value
    def finish(self): need(self.offset==self.bits,'trailing packed fields')


@dataclass(frozen=True)
class Limits:
    n:int
    field_bits:int
    owner_cap:int
    contexts:int
    pending:int
    targets:int
    rows:int
    @property
    def axis_bits(self): return (self.n-1).bit_length()
    @property
    def job_bits(self): return 4*self.field_bits+1+self.n*self.axis_bits


class Codec:
    def __init__(self,limits):
        self.limits=limits; self.ns=load(); self.words,self.library_bytes=library()
        need(limits.n>=2 and limits.field_bits>=1,'positive codec dimensions')
        need(max(limits.owner_cap,limits.contexts,limits.pending,limits.targets,limits.rows,len(self.words),limits.n)<1<<limits.field_bits,'limits do not fit scalar fields')
    def lift(self,index,columns):
        need(0<=index<len(self.words) and 1<=columns<=self.limits.n,'invalid basis token')
        coordinate=self.ns['coordinate_word']
        result=tuple(item for op in self.words[index] for j in range(columns)
                     for item in coordinate((op,),lambda k,j=j:k*columns+j))
        for op,i,*args in result:
            need(0<=i<self.limits.n and (op=='scale' or 0<=args[0]<self.limits.n),'basis coordinate outside ambient')
        return result
    def basis_token(self,basis):
        if not basis: return 0,1
        for index,word in enumerate(self.words[1:],1):
            if len(basis)%len(word): continue
            columns=len(basis)//len(word)
            if 1<=columns<=self.limits.n:
                try: candidate=self.lift(index,columns)
                except ValueError: continue
                if candidate==basis:return index,columns
        raise ValueError('basis is outside the literal paid chart library')
    def describe(self,job):
        n=self.limits.n; Axis=self.ns['Axis']
        need(isinstance(job.owner,int) and 0<=job.owner<self.limits.owner_cap,'owner outside bound')
        need(len(job.axes)<=n,'axis list too long')
        if all(isinstance(a,int) for a in job.axes):
            kind,index,columns,axes=0,0,1,tuple(job.axes)
        else:
            need(bool(job.axes) and all(isinstance(a,Axis) for a in job.axes),'mixed axis types')
            basis=job.axes[0].basis
            need(all(a.basis==basis for a in job.axes),'mixed ordered bases')
            index,columns=self.basis_token(basis)
            kind,axes=1,tuple(a.column for a in job.axes)
        need(all(isinstance(a,int) and 0<=a<n for a in axes),'coordinate outside ambient')
        return job.owner,kind,index,columns,axes
    def restore(self,description):
        owner,kind,index,columns,axes=description
        need(kind in (0,1),'unknown axis kind')
        if kind==0:
            need(index==0 and columns==1,'noncanonical integer basis')
            job=self.ns['Job'](owner,tuple(axes))
        else:
            need(bool(axes),'empty noncanonical typed axis list')
            basis=self.lift(index,columns)
            job=self.ns['Job'](owner,tuple(self.ns['Axis'](basis,a) for a in axes))
        self.describe(job)
        return job
    def put_job(self,out,job):
        owner,kind,index,columns,axes=self.describe(job); w=self.limits.field_bits
        out.put(owner,w); out.put(kind,1); out.put(index,w); out.put(columns,w); out.put(len(axes),w)
        for axis in axes: out.put(axis,self.limits.axis_bits)
    def get_job(self,src):
        w=self.limits.field_bits
        owner=src.get(w);kind=src.get(1);index=src.get(w);columns=src.get(w);length=src.get(w)
        need(length<=self.limits.n,'axis length exceeds ambient')
        axes=tuple(src.get(self.limits.axis_bits) for _ in range(length))
        return self.restore((owner,kind,index,columns,axes))
    def pack(self,rows,live,pending,group,round_no):
        lim=self.limits;w=lim.field_bits
        need(len(rows)==lim.rows and len(live)<=lim.contexts and len(pending)<=lim.pending,'table capacity')
        out=Writer()
        for x in (group,round_no,len(rows),len(live),len(pending)):out.put(x,w)
        for job in rows:self.put_job(out,job)
        for ident,(slot,zeros) in sorted(live.items()):
            need(0<=slot<lim.contexts and len(zeros)<=lim.targets,'context capacity')
            for x in (ident,slot,len(zeros)):out.put(x,w)
            for job in zeros:self.put_job(out,job)
        for serial,job in sorted(pending.items()):
            out.put(serial,w);self.put_job(out,job)
        return out.finish()
    def unpack(self,image):
        lim=self.limits;w=lim.field_bits;src=Reader(*image)
        group,round_no,nrows,nlive,npend=(src.get(w) for _ in range(5))
        need(nrows==lim.rows and nlive<=lim.contexts and npend<=lim.pending,'packed capacity')
        rows=[self.get_job(src) for _ in range(nrows)]
        live={};pending={};last=-1;slots=set()
        for _ in range(nlive):
            ident,slot,length=(src.get(w) for _ in range(3))
            need(ident>last and 0<=slot<lim.contexts and slot not in slots and length<=lim.targets,'invalid context order or slot')
            live[ident]=(slot,[self.get_job(src) for _ in range(length)]);last=ident;slots.add(slot)
        last=-1
        for _ in range(npend):
            serial=src.get(w);need(serial>last,'invalid pending order')
            pending[serial]=self.get_job(src);last=serial
        src.finish()
        return rows,live,pending,group,round_no
    def pack_records(self,records):
        records=list(records);out=Writer();w=self.limits.field_bits
        out.put(len(records),w)
        for row in records:
            op=row[0];need(op in (0,1,2),'unknown event opcode')
            if op==0:
                need(len(row)>=3,'short open record');cursor=3
                for _ in range(self.limits.targets):
                    need(cursor<len(row),'missing port binding');kind=row[cursor]
                    need(kind in (0,1,2),'unknown port binding')
                    cursor+=4 if kind==2 else 2
                need(cursor==len(row),'extra open fields')
            else:need(len(row)==(5 if op==1 else 2),'event record arity')
            for value in row:out.put(value,w)
        return out.finish()
    def unpack_records(self,image):
        src=Reader(*image);w=self.limits.field_bits;count=src.get(w);rows=[]
        for _ in range(count):
            op=src.get(w);need(op in (0,1,2),'unknown event opcode');row=[op,src.get(w)]
            if op==0:
                row.append(src.get(w))
                for _ in range(self.limits.targets):
                    kind=src.get(w);need(kind in (0,1,2),'unknown port binding');row.append(kind)
                    row.extend(src.get(w) for _ in range(3 if kind==2 else 1))
            elif op==1:row.extend(src.get(w) for _ in range(3))
            rows.append(tuple(row))
        src.finish();return rows
    def transfer_roundtrip(self,job,controls):
        need(len(controls)<=20,'transfer control count');out=Writer();w=self.limits.field_bits
        out.put(len(controls),w)
        for value in controls:out.put(value,w)
        self.put_job(out,job);image=out.finish();src=Reader(*image)
        restored=tuple(src.get(w) for _ in range(src.get(w)))
        result=self.get_job(src);src.finish()
        need(restored==tuple(controls),'transfer header roundtrip')
        return result,restored,image[1]
    def state_bound(self):
        L=self.limits;J=L.job_bits;w=L.field_bits
        return 5*w+L.rows*J+L.contexts*(3*w+L.targets*J)+L.pending*(w+J)


def decode_packed(plan,rows,round_no,group,machine,records,codec,receipt=None):
    """Mirror the source transitions, forcing an exact packed boundary each event.

    The service dictionary holds only native iterator bodies. It is explicitly
    outside the decoder-owned byte image and outside the claimed bit allowance.
    Its slots are bounded, counted scalar references within the image.
    """
    live,pending,services={},{},{}
    receipt={} if receipt is None else receipt
    receipt.update(events=0,max_bits=0,max_live=0,max_pending=0,roundtrips=0,callback_roundtrips=0,max_transfer_bits=0)
    for row in records:
        op,ident,*args=row
        if op==0:
            columns,*bindings=args;ports,zeros=[],[];cursor=iter(bindings)
            for kind in cursor:
                if kind==1:
                    ports.append(pending.pop(next(cursor)));continue
                base=next(cursor) if kind==2 else None
                size=next(cursor)
                if base is not None:
                    period=next(cursor);cycle,step=divmod(round_no,period)
                    index=group*plan.source_width+base+cycle
                    if cycle<plan.rounds//period and index<plan.width:
                        ports.append(rows[index].select(codec.ns['axes'](plan.n,size,period,step)));continue
                job=machine.zero(rows[0].select(range(size)));ports.append(job);zeros.append(job)
            slot=next(i for i in range(codec.limits.contexts) if i not in services)
            services[slot]=iter(machine.native(ports,columns));live[ident]=slot,zeros
        elif op==1:
            serial,size,selected=args;slot=live[ident][0];job=next(services[slot])
            if len(job.axes)!=size:raise ArithmeticError('The physical native word issued the wrong rank.')
            for k in range(selected,size):
                job,controls,bits=codec.transfer_roundtrip(job,(ident,serial,size,selected,k))
                need(controls==(ident,serial,size,selected,k),'leaf continuation')
                receipt['callback_roundtrips']+=1
                receipt['max_transfer_bits']=max(receipt['max_transfer_bits'],bits)
                machine.leaf(job.select((k,)))
            if selected:pending[serial]=job.select(range(selected))
        else:
            slot,zeros=live.pop(ident);iterator=services[slot]
            if next(iterator,None) is not None:raise ArithmeticError('The word emitted an extra loan.')
            for job in zeros:machine.retire_zero(job)
            services.pop(slot)
        image=codec.pack(rows,live,pending,group,round_no)
        need(image[1]<=codec.state_bound(),'image exceeds written capacity')
        rows,live,pending,group,round_no=codec.unpack(image)
        need({entry[0] for entry in live.values()}==set(services),'native slot binding')
        receipt['events']+=1;receipt['roundtrips']+=1
        receipt['max_bits']=max(receipt['max_bits'],image[1])
        receipt['max_live']=max(receipt['max_live'],len(live))
        receipt['max_pending']=max(receipt['max_pending'],len(pending))
    if live or pending:raise ArithmeticError('The last native owner did not return.')
    need(not services,'unclosed resident native service')
    return receipt
