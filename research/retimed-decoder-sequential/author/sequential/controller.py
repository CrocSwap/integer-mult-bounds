"""Literal sequential table replacement for the scoped decoder interface."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from codec import Reader,Writer
from source_loader import need
from tapes import Meter,Tape,Table,bit_image,byte_image


class Controller:
    def __init__(self,codec):
        self.codec=codec;self.m=Meter(codec.limits.field_bits)
        self.callback_count=0;self.slot_candidates=0;self.state_peak=0
        self.tables=tuple(Table(self.m) for _ in range(3));self.calendar=Tape(self.m);self.calendar_ready=False
        self.decode_calls=0;self.row_records_written=0;self.calendar_copies=0
        self.request=Tape(self.m);self.reply=Tape(self.m)
        self.input_rows=Tape(self.m);self.rows_ready=False
    def job_bits(self,job):
        self.m.word(2**32*(self.codec.limits.n+1)**4)
        out=Writer();self.codec.put_job(out,job);return bit_image(out.finish())
    def job(self,bits):
        self.m.word(2**32*(self.codec.limits.n+1)**4)
        r=Reader(*byte_image(bits));job=self.codec.get_job(r);r.finish();return job
    def live_bits(self,slot,zeros):
        out=Writer();w=self.m.width;out.put(slot,w);out.put(len(zeros),w)
        for job in zeros:self.codec.put_job(out,job)
        bits=bit_image(out.finish());self.m.word(2**32*(self.codec.limits.n+1)**4*(len(zeros)+1));return bits
    def live_value(self,bits):
        r=Reader(*byte_image(bits));slot=r.get(self.m.width);count=r.get(self.m.width)
        zeros=[self.codec.get_job(r) for _ in range(count)];r.finish()
        self.m.word(2**32*(self.codec.limits.n+1)**4*(count+1));return slot,zeros
    def event_reader(self,records):
        # The supplied immutable event sequence is materialized once. Its
        # producer (Plan.events and setup) is outside this interface.
        tape=self.calendar
        if not self.calendar_ready:
            image=self.codec.pack_records(records);tape.put_bits(bit_image(image));self.calendar_ready=True;self.calendar_copies+=1
        tape.at(0);count=tape.get_u()
        for _ in range(count):
            op=tape.get_u();ident=tape.get_u();row=[op,ident]
            if op==0:
                row.append(tape.get_u())
                for _ in range(self.codec.limits.targets):
                    kind=tape.get_u();row.append(kind)
                    for _ in range(3 if kind==2 else 1):row.append(tape.get_u())
            elif op==1:
                for _ in range(3):row.append(tape.get_u())
            else:need(op==2,'event opcode')
            yield tuple(row)
        tape.at(0)
    def close_calendar(self):
        self.calendar.clear();self.calendar_ready=False
    def ensure_rows(self,rows):
        if not self.rows_ready:
            self.input_rows.put_u(len(rows))
            for job in rows:
                bits=self.job_bits(job);self.input_rows.put_u(len(bits));self.input_rows.put_bits(bits)
            self.rows_ready=True
    def row_reader(self):
        self.input_rows.at(0);count=self.input_rows.get_u()
        for i in range(count):yield i,self.input_rows.get_bits(self.input_rows.get_u())
        self.input_rows.at(0)
    def retire_rows(self):
        self.input_rows.clear();self.rows_ready=False
    def free_slot(self,live):
        # Intentionally slow. No random-access occupied-set is available.
        for candidate in range(self.codec.limits.contexts):
            self.slot_candidates+=1;used=False
            for _,payload in live.walk():
                self.m.word();slot,_=self.live_value(payload)
                if slot==candidate:used=True
            if not used:return candidate
        raise ValueError('no native service slot')
    def call(self,opcode,action,*args,slot=None):
        # Explicit request/reply metadata transfer. The resident callback body
        # starts only after its complete request has been written.
        self.callback_count+=1;self.m.word();self.request.clear();self.reply.clear()
        need(opcode in range(5),'callback opcode');self.request.put_u(opcode)
        self.request.put_u(len(args));self.request.put_u(0 if slot is None else slot)
        for value in args:
            if hasattr(value,'owner') and hasattr(value,'axes'):
                bits=self.job_bits(value);self.request.put_u(1);self.request.put_u(len(bits));self.request.put_bits(bits)
            elif isinstance(value,list):
                self.request.put_u(2);self.request.put_u(len(value))
                for job in value:
                    bits=self.job_bits(job);self.request.put_u(len(bits));self.request.put_bits(bits)
            elif isinstance(value,int):self.request.put_u(3);self.request.put_u(value)
            elif value is None:self.request.put_u(4)
            else:
                need(slot is not None,'opaque body requires explicit bounded slot')
                self.request.put_u(5);self.request.put_u(slot)
        self.request.at(0);need(self.request.get_u()==opcode,'callback opcode roundtrip')
        argc=self.request.get_u();request_slot=self.request.get_u();decoded=[]
        for i in range(argc):
            kind=self.request.get_u()
            if kind==1:decoded.append(self.job(self.request.get_bits(self.request.get_u())))
            elif kind==2:
                count=self.request.get_u();items=[]
                for _ in range(count):items.append(self.job(self.request.get_bits(self.request.get_u())))
                decoded.append(items)
            elif kind==3:decoded.append(self.request.get_u())
            elif kind==4:decoded.append(None)
            else:
                need(kind==5 and self.request.get_u()==request_slot==slot,'service slot request')
                # Resolving the resident body is the explicitly excluded service
                # dispatch, not a free decoder table lookup.
                decoded.append(args[i])
        result=action(*decoded)
        if hasattr(result,'owner') and hasattr(result,'axes'):
            bits=self.job_bits(result);self.reply.put_u(1);self.reply.put_u(len(bits));self.reply.put_bits(bits)
        else:self.reply.put_u(0 if result is None else 2)
        self.reply.at(0);kind=self.reply.get_u()
        if kind==1:result=self.job(self.reply.get_bits(self.reply.get_u()))
        else:need(kind in (0,2),'service reply tag')
        self.request.clear();self.reply.clear();return result
    def run(self,plan,rows,machine,records):
        need(len(rows)==plan.width,'productive row count')
        # A new nonoverlapping caller handoff replaces the prior returned input
        # image. This activation's input image survives until its return.
        self.retire_rows()
        for group in range((plan.width+plan.source_width-1)//plan.source_width):
            for round_no in range(plan.rounds):
                self.m.word(16);self.decode(plan,rows,round_no,group,machine,records)
        self.close_calendar();return self.receipt()
    def decode(self,plan,rows,round_no,group,machine,records):
        self.decode_calls+=1;self.row_records_written+=len(rows)
        row_table,live,pending=self.tables
        self.ensure_rows(rows)
        row_table.reset(self.row_reader(),count=len(rows))
        live.reset();pending.reset()
        # The sole dictionary is the explicitly excluded resident service body
        # environment, not the decoder's rows/live/pending representation.
        services={}
        for row in self.event_reader(records):
            self.m.word(20);op,ident,*args=row
            if op==0:
                columns,*bindings=args;ports,zeros=[],[];cursor=iter(bindings)
                for kind in cursor:
                    self.m.word(12)
                    if kind==1:
                        ports.append(self.job(pending.pop(next(cursor))));continue
                    base=next(cursor) if kind==2 else None;size=next(cursor)
                    if base is not None:
                        period=next(cursor);cycle,step=divmod(round_no,period)
                        index=group*plan.source_width+base+cycle
                        if cycle<plan.rounds//period and index<plan.width:
                            source=self.job(row_table.get(index))
                            ports.append(source.select(self.codec.ns['axes'](plan.n,size,period,step)));continue
                    exemplar=self.job(row_table.get(0)).select(range(size))
                    job=self.call(0,machine.zero,exemplar);ports.append(job);zeros.append(job)
                slot=self.free_slot(live)
                services[slot]=iter(self.call(1,machine.native,ports,columns,slot=slot))
                live.rewrite(ident,self.live_bits(slot,zeros))
            elif op==1:
                serial,size,selected=args;slot,_=self.live_value(live.get(ident))
                job=self.call(2,next,services[slot],slot=slot);need(len(job.axes)==size,'paid size')
                # Full paid-job continuation has a charged explicit image.
                full=self.job_bits(job)
                for k in range(selected,size):
                    self.m.word(4);restored=self.job(full)
                    self.call(3,machine.leaf,restored.select((k,)))
                if selected:pending.rewrite(serial,self.job_bits(job.select(range(selected))))
            else:
                slot,zeros=self.live_value(live.pop(ident))
                need(self.call(2,next,services[slot],None,slot=slot) is None,'extra paid loan')
                for job in zeros:self.call(4,machine.retire_zero,job)
                del services[slot]
            self.state_peak=max(self.state_peak,sum(t.historical_bits() for t in self.tables))
        need(live.empty() and pending.empty() and not services,'complete decoder return')
        for table in (row_table,live,pending):table.close()
        return self.receipt()
    def receipt(self):
        return dict(tape_cell_actions=self.m.cells,bounded_register_charges=self.m.registers,
                    lowered_bit_step_upper=self.m.total_upper(),table_sweeps=self.m.sweeps,decode_calls=self.decode_calls,
                    row_records_written=self.row_records_written,calendar_copies=self.calendar_copies,
                    free_slot_candidates=self.slot_candidates,callback_calls=self.callback_count,
                    historical_table_bits=self.state_peak,
                    historical_event_bits=self.calendar.peak,historical_input_row_bits=self.input_rows.peak,
                    historical_callback_bits=self.request.peak+self.reply.peak,
                    scope='Sequential table cell actions plus a separately proved conservative register/adapter upper bound; callback bodies excluded.')
