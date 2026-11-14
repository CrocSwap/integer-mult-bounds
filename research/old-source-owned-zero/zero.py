"""Literal OLD23 context/source to a complete typed owned zero HOME.

Apache-2.0; prepared for @CubeJerry with OpenAI assistance. Runtime control
uses only fixed R/W/M/J/H instructions. All Python integer work is offline.
"""
from pathlib import Path
from hashlib import sha256
import importlib.util
import sys

HERE = Path(__file__).resolve().parent
sys.dont_write_bytecode = True
raw = (HERE/'inputs/codec-guide.py').read_bytes()
if sha256(raw).hexdigest() != '119b69594a2a33550eec9b6e083db8f496c3fb3d9c1214b6703d687a0a662eba':
    raise ValueError('frozen codec guide drift')
spec = importlib.util.spec_from_file_location('old_zero_codec_guide', HERE/'inputs/codec-guide.py')
C = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = C
exec(compile(raw, str(HERE/'inputs/codec-guide.py'), 'exec'), C.__dict__)
BLANK, LEFT, DELIMITER, END = C.BLANK, C.LEFT, 4, 5
NAMES, PORT = C.NAMES, C.PORT
HOME = 'PACK'
# Fixed instruction-label substitution to the actual retained OLD machine:
# ZERO=0, ONE=1, LEFT=2, SEP=3, END=4, BASE=5, BLANK=6.
# This is not a runtime rewrite of any public cell or coded delimiter010.
HARDWARE_SYMBOL = {0: 0, 1: 1, BLANK: 6, LEFT: 2, DELIMITER: 3, END: 4}

def hardware_code(program):
    out = []
    for instruction in program:
        if instruction[0] == 'R':
            out.append(('R', instruction[1], {HARDWARE_SYMBOL[s]: q for s, q in instruction[2].items()}))
        elif instruction[0] == 'W':
            out.append(('W', instruction[1], HARDWARE_SYMBOL[instruction[2]]))
        else:
            out.append(instruction)
    return tuple(out)

class Builder(C.Builder):
    def w(self, tape, value):
        # A too-short inactive home rejects before touching its right marker.
        # A fresh body is blank; an existing inactive body is binary.
        if tape == HOME and value in (0, 1):
            ready = self.fresh('home-cell')
            self.r(HOME, {0: ready, 1: ready, BLANK: ready})
            self.label(ready)
        super().w(tape, value)

    def home_origin(self):
        """At END, return to the permanent HOME LEFT marker, not body cell1."""
        self.m(HOME, -1)
        self.expect(HOME, DELIMITER)
        self.m(HOME, -1)
        loop, step, done = self.fresh(), self.fresh(), self.fresh()
        self.label(loop)
        self.r(HOME, {0: step, 1: step, LEFT: done})
        self.label(step)
        self.m(HOME, -1)
        self.j(loop)
        self.label(done)

    def close_home(self):
        fresh, present, done = self.fresh(), self.fresh(), self.fresh()
        self.r(HOME, {BLANK: fresh, DELIMITER: present})
        self.label(fresh)
        self.w(HOME, DELIMITER)
        self.m(HOME, 1)
        self.expect(HOME, BLANK)
        self.w(HOME, END)
        self.j(done)
        self.label(present)
        self.m(HOME, 1)
        self.expect(HOME, END)
        self.label(done)
        self.home_origin()

    def validate_and_zero(self):
        outer, record, finish = self.fresh(), self.fresh(), self.fresh()
        comps, component, next_record = self.fresh(), self.fresh(), self.fresh()
        self.label(outer)
        self.r('N', {1: record, BLANK: finish})
        self.label(record)
        self.label(comps)
        self.r('R2', {1: component, BLANK: next_record})
        self.label(component)
        bits, take, delimiter = self.fresh(), self.fresh(), self.fresh()
        bit, wrong, decoded = self.fresh(), self.fresh(), self.fresh()
        self.label(bits)
        self.r('W', {1: take, BLANK: delimiter})
        self.label(take)
        self.codeword(bit, bit, wrong)
        self.label(bit)
        self.w(HOME, 0)
        self.m(HOME, 1)
        self.m('W', 1)
        self.j(bits)
        self.label(wrong)
        self.halt('REJECT')
        self.label(delimiter)
        self.codeword(wrong, wrong, decoded)
        self.label(decoded)
        self.rewind('W')
        self.m('R2', 1)
        self.j(comps)
        self.label(next_record)
        self.rewind('R2')
        self.m('N', 1)
        self.j(outer)
        self.label(finish)
        self.expect('OLD', BLANK)
        self.rewind('OLD')
        self.rewind('N')

def compile_zero():
    b = Builder()
    b.label('ENTER')
    b.expect(HOME, LEFT)
    b.m(HOME, 1)
    kept = {'outer': 'OUTER', 'rows': 'ROWS', 'row_bits': 'ROWCLAIM',
            'within_bits': 'A', 'record_bits': 'REC', 'f': 'F', 'K': 'K',
            'rho': 'RHO', 'active_start': 'U', 'cutoff': 'CUTOFF'}
    for name in C.SCHEMA:
        b.parse(kept.get(name))
    b.expect('CONTEXT', BLANK)
    b.rewind('CONTEXT')
    for tape in ('OUTER', 'ROWS', 'ROWCLAIM', 'REC', 'F', 'K'):
        b.positive(tape)
    b.w('ONECOUNT', 1)
    b.scale('F', 9, 'G')
    b.multiply('G', 'K', 'GK')
    b.sum('U', 'GK', 'END')
    b.less('END', 'A')
    b.less('RHO', 'K', True)
    b.infer_width()
    b.sum('W', 'ONECOUNT', 'TMP2')
    b.scale('TMP2', 6, 'DEN')
    b.clear('TMP2')
    b.quotient('REC', 'DEN', 'R')
    b.scale('R', 2, 'R2')
    b.copy_reset('REC', 'ROWEXPECTED')
    b.rewind('ROWEXPECTED')
    b.repeat_shift('ROWEXPECTED', 'A')
    b.equal('ROWEXPECTED', 'ROWCLAIM')
    b.multiply('OUTER', 'ROWS', 'CROWS')
    b.copy_reset('CROWS', 'N')
    b.rewind('N')
    b.repeat_shift('N', 'A')
    b.copy_reset('CROWS', 'BASEP')
    b.rewind('BASEP')
    b.repeat_shift('BASEP', 'U')
    b.sub('A', 'U', 'TMP2')
    b.sub('TMP2', 'G', 'EXP')
    b.clear('TMP2')
    b.w('S', 1)
    b.repeat_shift('S', 'EXP')
    b.clear('EXP')
    for tape in ('F', 'R', 'BASEP', 'S', 'W'):
        b.gamma(tape)
    b.gamma_binary('CUTOFF')
    b.rewind('GAMMA')
    b.copy('GAMMA', HOME, erase=True)
    b.rewind('GAMMA')
    b.label('ZERO_DATA')
    b.validate_and_zero()
    b.label('ZERO_FINISHED')
    b.close_home()
    for tape in C.NAMES[3:]:
        b.clear(tape)
    b.halt('LIVE_HOME')
    # Complete retirement keeps the same physical owner and markers.
    b.label('CLEAR')
    b.expect(HOME, LEFT)
    b.m(HOME, 1)
    loop, step, end = b.fresh(), b.fresh(), b.fresh()
    b.label(loop)
    b.r(HOME, {0: step, 1: step, DELIMITER: end})
    b.label(step)
    b.w(HOME, 0)
    b.m(HOME, 1)
    b.j(loop)
    b.label(end)
    b.m(HOME, 1)
    b.expect(HOME, END)
    b.home_origin()
    b.halt('RETIRED_HOME')
    return b.finish()
