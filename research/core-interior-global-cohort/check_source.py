"""Actual source endpoints, original geometry and complete emitted controls.

Finite independent oracles support PROOF.md; they do not implement physical
payload arithmetic. Prepared for @CubeJerry with OpenAI Codex assistance.
"""
from fractions import Fraction as Q
from hashlib import sha256
from itertools import permutations
import json
from pathlib import Path
import sys
from types import ModuleType
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parent))
from cohort_sources import HERE,VENDOR,authenticate,opened,need
from core_layout import Layout,address
from core_roots import Partition,CoreRoot
from core_caller import prepare
from oracles import check_complete


def reject(action,label):
    try:
        action()
    except (ValueError,RuntimeError,TypeError):
        return label
    raise ValueError('accepted negative control: '+label)


def logical_matrix(r,plan,size):
    """Independent row updates on the complete basis, without source apply()."""
    C=r.exact.C
    matrix=[[C(int(i==j)) for j in range(size)] for i in range(size)]
    for layer in plan:
        occupied=set()
        for ids,gate in layer:
            need(not occupied.intersection(ids),'independent disjoint matching')
            occupied.update(ids)
            old=[matrix[i][:] for i in ids]
            for i,row in zip(ids,gate):
                matrix[i]=[sum((a*x[j] for a,x in zip(row,old)),C()) for j in range(size)]
    return matrix


def reference_matrix(r,root,inverse):
    n=root.partition.size
    C=r.exact.C
    matrix=[[C(int(i==j)) for j in range(n)] for i in range(n)]
    children=root.partition.inverses if inverse else root.partition.matrices
    for ids,child in zip(root.partition.indices,children):
        for i,row in zip(ids,child):
            for j,z in zip(ids,row):
                matrix[i][j]=z
    return matrix


def frobenius_squared(a,b):
    return sum(((x-y).norm2() for ra,rb in zip(a,b) for x,y in zip(ra,rb)),Q(0))


def layout_checks():
    count=0
    for selected in permutations(range(3),2):
        layout=Layout((3,4,3),selected,2)
        image=[]
        for old in range(1<<layout.n):
            new=address(old,layout.gather)
            image.append(new)
            need(address(new,layout.inverse)==old,'independent original address round trip')
            for packed_bit,axis in enumerate(selected):
                digit=(old>>layout.starts[axis])&3
                need(((new>>(2*packed_bit))&3)==digit,'actual selected digit order')
            coarse=new>>(2*len(selected))
            base=layout.original_base(coarse)
            for axis in range(3):
                mask=(1<<layout.lengths[axis])-1
                value=(old>>layout.starts[axis])&mask
                start=(base>>layout.starts[axis])&mask
                need(start==(value&~3 if axis in selected else value),
                     'complete original spectator and high coordinate')
            count+=1
        need(sorted(image)==list(range(1<<layout.n)),'complete field bijection')
    controls=[reject(lambda:Layout([3,4],(1,),2),'mutable lengths'),
              reject(lambda:Layout((3,4),[1],2),'mutable selected axes'),
              reject(lambda:Layout((3,4),(1,1),2),'duplicate selected axis'),
              reject(lambda:Layout((3,4),(0,),4),'local side exceeds original axis')]
    shifted=Layout((1,6),(1,),5)
    need(address(1,shifted.gather)!=1,'shifted original group distinguishes identity gather')
    return dict(addresses=count,selected_orders=6,controls=controls)


class HashTape:
    """Streaming test sink for all encoded bits, not a physical data owner."""
    def __init__(self):
        self.digest=sha256(); self.buffer=bytearray(); self.length=0
    def append(self,value):
        need(value in (0,1),'encoded source bit')
        self.buffer.append(value); self.length+=1
        if len(self.buffer)==65536:
            self.digest.update(self.buffer); self.buffer.clear()
    def rewind(self):
        self.digest.update(self.buffer); self.buffer.clear()
    def hexdigest(self):
        self.rewind(); return self.digest.hexdigest()


class LiteralCount:
    @staticmethod
    def literal(value):
        return value


def encoded_controls(program,event_types):
    """Run unchanged real serializer and compare a separate octet/bit oracle."""
    module=ModuleType('_a4_control_source')
    fake=ModuleType('physical_sources'); fake.need=need
    previous=sys.modules.get('physical_sources')
    sys.modules['physical_sources']=fake
    try:
        exec(compile((VENDOR/'physical_controls.py').read_bytes(),
                     '<authenticated complete physical serializer>','exec'),module.__dict__)
        encoded=module.PreparedFull(program,HashTape,LiteralCount,event_types)
    finally:
        if previous is None:sys.modules.pop('physical_sources',None)
        else:sys.modules['physical_sources']=previous
    independent=sha256(); bits=0
    def emit(value,width):
        nonlocal bits
        value %= 1<<width
        data=bytes(int(c) for c in format(value,'0'+str(width)+'b')[::-1])
        independent.update(data); bits+=len(data)
    for event in program.events():
        if isinstance(event,event_types[0]):
            emit(1,2)
            for pos in event.positions:emit(pos,encoded.metadata['position_width'])
        else:
            emit(2,2)
            for c in range(program.labels):
                for axis in range(program.axes-1,-1,-1):
                    for digit in range(program.size):
                        for part in (0,1):emit(event.pages[c][axis][digit][part],program.factor_width)
    emit(0,2)
    expected=2*(program.stages+1)+program.h_count*program.axes*encoded.metadata['position_width']
    expected+=2*program.diagonal_count*program.labels*program.axes*program.size*program.factor_width
    need(bits==expected==encoded.code.length,'exact complete source control bill')
    need(independent.hexdigest()==encoded.code.hexdigest(),'all authentic source encoded bits and order')
    return dict(bits=bits,sha256=independent.hexdigest(),events=encoded.event_count,
                h=encoded.h_count,d=encoded.d_count,components=encoded.page_components,
                physical_execution=False)


def fraction_record(value):
    return dict(numerator_bits=value.numerator.bit_length(),
                denominator_bits=value.denominator.bit_length(),
                hex_sha256=sha256((hex(value.numerator)+'/'+hex(value.denominator)).encode()).hexdigest())


def raw_vector(r,stages,values,all_one=False):
    state=list(values)
    for kind,value in stages:
        if kind=='H':
            stride=1<<value
            for base in range(0,len(state),2*stride):
                for j in range(stride):
                    a,b=state[base+j],state[base+j+stride]
                    state[base+j],state[base+j+stride]=a+b,a-b
        else:
            state=[z*(1 if all_one else c) for z,c in zip(state,value)]
    return state


def main():
    raw=authenticate()
    controls=[]
    for path in ('research/rational-unitary-fft/core.py','research/rational-unitary-fft/raw_gaussian.py',
                 'research/rational-unitary-fft/gaussian_reference.py',
                 'research/rational-fft-fixed-h/dense.py','research/full-downset-allocation/allocation.py'):
        controls.append(reject(lambda p=path:authenticate({p:raw[p]+b'\n'}),'changed source '+path))
    alias='_retained_gaussian_intervals_'+sha256(raw['research/certified-gaussian-recovery/intervals.py']).hexdigest()
    need(alias not in sys.modules,'fresh alias control')
    sys.modules[alias]=ModuleType(alias)
    try:
        def forged():
            with opened():pass
        controls.append(reject(forged,'preloaded false interval module'))
    finally:sys.modules.pop(alias,None)
    geometry=layout_checks()
    with opened() as r:
        broad=r.reference.Reference(r.raw,127,1,1,1,5,128)
        windows=[]; betas=set(); positions=set()
        for first in (0,32,64,96):
            root=CoreRoot(Partition(r,broad,'broad',first,32,2),12)
            positions.add(root.partition.indices)
            betas.update((x.beta>0)-(x.beta<0) for x in root.children)
            errors=[]; matrices=[]
            for inverse,plan in ((False,root.plan),(True,root.inverse_plan)):
                actual=logical_matrix(r,plan,32)
                matrices.append(actual)
                target=reference_matrix(r,root,inverse)
                error=frobenius_squared(actual,target)
                need(error<=root.defects[inverse]**2,'independent complete source endpoint bound')
                for i in root.partition.boundary:
                    need(all(actual[i][j]==r.exact.C(int(i==j)) and
                             actual[j][i]==r.exact.C(int(i==j)) for j in range(32)),
                         'exact reference complement identity')
                errors.append(fraction_record(error))
            need(matrices[1]!=[[z.conjugate() for z in row] for row in zip(*matrices[0])],
                 'stored inverse distinguished from adjoint')
            if first==0:
                target=reference_matrix(r,root,False)
                for name,broken in (('missing B gauge',root.plan[1:]),
                                    ('missing A gauge',root.plan[:-1])):
                    need(frobenius_squared(logical_matrix(r,broken,32),target)>root.defects[0]**2,
                         'discriminating actual source '+name)
                    controls.append(name)
                moved=[[(tuple(i+1 for i in ids),gate) for ids,gate in layer] for layer in root.plan]
                need(frobenius_squared(logical_matrix(r,moved,32),target)>root.defects[0]**2,
                     'original support mutation exceeds proved error')
                controls.append('changed original interior support')
                adjoint=[[z.conjugate() for z in row] for row in zip(*matrices[0])]
                need(frobenius_squared(adjoint,reference_matrix(r,root,True))>root.defects[1]**2,
                     'adjoint is not the admitted stored inverse')
                controls.append('adjoint substituted for inverse')
                controls.append(reject(lambda:r.source.full.admission(r.exact.Mat(target)),
                                       'whole union falsely admitted as Toeplitz'))
                gate=r.exact.Mat([[1,2],[3,4]])
                controls.append(reject(lambda:r.dense.NativeProgram(r.source,32,
                    [[((0,1),gate)]],10,10,1,1),'unsupported invertible two-wire gate'))
                saved=root.partition.boundary
                root.partition.boundary=saved[:-1]
                controls.append(reject(root.validate,'changed derived boundary record'))
                root.partition.boundary=saved
                child=root.children[0]
                saved=child.gauge_bound;child.gauge_bound+=1
                controls.append(reject(root.validate,'changed raw gauge allowance'))
                child.gauge_bound=saved;root.validate()
            windows.append(dict(first=first,indices=root.partition.indices,
                                source_starts=[x.start for x in root.children],
                                beta=[str(x.beta) for x in root.children],
                                forward_inverse_error_squared=errors))
        need(len(positions)>1 and {-1,1}<=betas,'post-hole positions and both phase signs')
        narrow=r.reference.Reference(r.raw,63,1,3,1,1,160)
        empty=CoreRoot(Partition(r,narrow,'narrow',0,8,2),8)
        need(not empty.children and empty.plan==[[]] and empty.prefix==1
             and empty.defects==(0,0),'actual empty complete-core identity')
        empty_program=empty.lower(False)
        need(empty_program.logical_layers==1 and len(empty_program.raw_stages)==53,
             'empty core pays actual complete compiler idle word')
        vector=[r.exact.C(j-3,2*j-1) for j in range(8)]
        need(raw_vector(r,empty_program.raw_stages,vector)==vector,'actual complete idle endpoint')
        need(raw_vector(r,empty_program.raw_stages,vector,True)!=vector,
             'all-one diagonal word is not identity padding')
        controls.append('fake all-one idle word')
        controls.append(reject(lambda:Partition(r,narrow,'narrow',1,32,2),'unaligned complete core'))
        controls.append(reject(lambda:Partition(r,narrow,'narrow',0,31,2),'ragged complete core'))
        controls.append(reject(lambda:Partition(r,narrow,'narrow',0,32,2,1),'too narrow physical band'))
        low=r.reference.Reference(r.raw,63,1,3,1,1,8)
        controls.append(reject(lambda:CoreRoot(Partition(r,low,'narrow',0,32,2),160),
                               'unfunded source reference at strengthened target'))
        layout=Layout((1,6),(1,),5)
        prior_limit=sys.get_int_max_str_digits()
        original_partition=Partition._partition
        serialization_entries=[]
        def guarded_partition(self):
            need(sys.get_int_max_str_digits()==0,'whole source preparation serialized')
            serialization_entries.append(1)
            return original_partition(self)
        try:
            sys.set_int_max_str_digits(640)
            with patch.object(Partition,'_partition',guarded_partition):
                program=prepare(r,layout,[narrow],['narrow'],[2],
                    [[False],[True],[False],[True]],target=6,radius_bits=5,incoming=1)
            need(serialization_entries and sys.get_int_max_str_digits()==640,
                 'complete successful preparation restores prior decimal limit')
            controls.append(reject(lambda:prepare(r,layout,[narrow],['narrow'],[2],
                [[False],[True],[False],[True]],target=0),'invalid target through serialization scope'))
            need(sys.get_int_max_str_digits()==640,'failed preparation restores decimal limit')
        finally:
            sys.set_int_max_str_digits(prior_limit)
        values=[((7*j)%5-2,(11*j)%7-3) for j in range(program.records)]
        output,counts,roundings,error=check_complete(program,values)
        types=(r.global_compiler.Hadamard,r.global_compiler.Diagonal)
        encoded=encoded_controls(program,types)
        saved=program.bits;program.bits-=1
        controls.append(reject(program.validate,'changed common global grid'))
        program.bits=saved;program.validate()
        saved=program.roots[0][0].partition.first;program.roots[0][0].partition.first=32
        controls.append(reject(program.validate,'changed complete coarse label source'))
        program.roots[0][0].partition.first=saved;program.validate()
        endpoint=dict(records=program.records,layout=layout.record(),stages=program.stages,
            depths=program.depths,grid=program.bits,width=program.data_width,counts=counts,
            nonzero_roundings=roundings,error_squared=fraction_record(error),controls=encoded,
            serialized_partition_entries=len(serialization_entries),
            output_sha256=sha256(json.dumps(output,separators=(',',':')).encode()).hexdigest())
    print(json.dumps(dict(status='PASS_ACTUAL_CORE_SOURCE',geometry=geometry,
        broad_windows=windows,empty_identity_stages=53,complete_endpoint=endpoint,
        negative_controls=controls),sort_keys=True))


if __name__=='__main__':main()
