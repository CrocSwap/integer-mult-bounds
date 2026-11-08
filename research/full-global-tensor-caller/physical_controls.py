"""Encode actual immutable Full events, without inspecting payload values.

Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
"""
from physical_sources import need

END, H_EVENT, D_EVENT = 0, 1, 2
NAMES = ('n','coarse_bits','axis_bits','axes','fractional_bits','data_width',
         'factor_width','cache_width','temporary_width','incoming_bits',
         'incoming_width','radius_bits','position_width','stages','h_count','d_count')


def emit_unsigned(tape,value,width):
    need(type(width) is int and width >= 0 and type(value) is int
         and 0 <= value < 1 << width,'prepared unsigned field')
    if width == 0:
        return
    # One linear byte conversion, then only fixed eight-bit finite arithmetic.
    # Repeatedly shifting the full source integer would cost quadratic work.
    octets = value.to_bytes((width+7)//8,'little')
    for octet in octets[:-1]:
        for bit in range(8):
            tape.append((octet >> bit) & 1)
    for bit in range((width-1)%8+1):
        tape.append((octets[-1] >> bit) & 1)


def emit_signed(tape,value,width):
    need(type(value) is int and -(1 << (width-1)) <= value < 1 << (width-1),
         'prepared signed source coefficient')
    emit_unsigned(tape,value if value >= 0 else (1 << width)+value,width)


class PreparedFull:
    """All online extents are Count tapes; pages come from the actual source."""
    def __init__(self,program,Tape,Count,event_types):
        Hadamard,Diagonal = event_types
        program.validate()
        self.code,self.parameters = Tape(),()
        self.event_count = self.h_count = self.d_count = self.page_components = 0
        self.metadata = dict(n=program.array_bits,coarse_bits=program.coarse_bits,
            axis_bits=program.axis_bits,axes=program.axes,fractional_bits=program.bits,
            data_width=program.data_width,factor_width=program.factor_width,
            cache_width=program.cache_width,temporary_width=program.temporary_width,
            incoming_bits=program.incoming,incoming_width=program.incoming+program.radius_bits+2,
            radius_bits=program.radius_bits,position_width=max(1,(program.array_bits-1).bit_length()),
            stages=program.stages,h_count=program.h_count,d_count=program.diagonal_count)
        try:
            for event in program.events():
                event.validate()
                need(event.step == self.event_count and event.array_bits == self.metadata['n']
                     and event.fractional_bits == self.metadata['fractional_bits']
                     and event.data_width == self.metadata['data_width'],
                     'unchanged complete source event geometry and order')
                if isinstance(event,Hadamard):
                    need(len(event.positions) == self.metadata['axes'],'all source-selected H axes')
                    emit_unsigned(self.code,H_EVENT,2)
                    for position in event.positions:
                        emit_unsigned(self.code,position,self.metadata['position_width'])
                    self.h_count += 1
                else:
                    need(isinstance(event,Diagonal),'actual Full diagonal event')
                    for name in ('coarse_bits','axis_bits','axes','factor_width','cache_width','temporary_width'):
                        need(getattr(event,name) == self.metadata[name],'unchanged source diagonal '+name)
                    emit_unsigned(self.code,D_EVENT,2)
                    for block in event.pages:
                        for page in reversed(block):
                            for gaussian in page:
                                for component in gaussian:
                                    emit_signed(self.code,component,event.factor_width)
                                    self.page_components += 1
                    self.d_count += 1
                self.event_count += 1
            emit_unsigned(self.code,END,2)
            self.code.rewind()
            need((self.event_count,self.h_count,self.d_count) ==
                 (program.stages,program.h_count,program.diagonal_count),'all source events exactly once')
            program.validate()
            self.parameters = tuple(Count.literal(self.metadata[name]) for name in NAMES)
        except BaseException:
            self.close()
            raise

    def run(self,owner,payload):
        return owner.run(payload,self.code,*self.parameters)

    def close(self):
        from session import erase_marker
        for value in self.parameters:
            value.close()
            erase_marker(value.tape)
        self.parameters = ()
        self.code.clear()
        erase_marker(self.code)
