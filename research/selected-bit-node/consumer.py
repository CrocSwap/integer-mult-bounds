"""Catalogue-bound common local and native idle consumers of actual leaf traces."""
from controller import Callback
from directory import produce
from layout import Layout
from numeric import Geometry, selected_coefficient
from packet import read_prefix
import packet_engine
from records import Fields
from trace import execute
from words import Unsigned, need


class Consumer:
    def __init__(self,context,indices,program,specifications,parent_size,depth):
        self.context,self.indices,self.program=context,indices,program
        self.specifications,self.parent_size,self.depth=specifications,parent_size,depth
        need(program.code_bits==context.codes.bits,"one full selected source vocabulary")

    def apply(self,source,request_id,common,low,old_directory,old_count,before,gap,suffix,observe=None):
        context,indices=self.context,self.indices
        request=self.specifications.catalogue.requests[request_id]
        need(common==(request.kind!="IDLE"),"common local versus native idle source view")
        spec=self.specifications.bind(request_id,common,low)
        plan=self.specifications.plan(spec.code)
        directory,prefixes=produce(old_directory,self.depth,old_count,spec.code,context)
        raw=Unsigned(indices)
        divisor,one=indices.literal(64),indices.literal(1)
        columns,remainder=raw.divmod(self.parent_size,divisor)
        need(raw.compare(columns,one)==0,"first selected internal width range")
        indices.free_many(divisor,remainder)
        fields,carry=raw.add(self.depth,one);indices.free(one)
        need(not carry,"current field depth margin")
        geometry=Geometry(plan,indices,columns,self.depth,spec.code,self.program)
        layout=Layout(geometry,self.parent_size,context.ring,context.q,before,gap,suffix)
        try:
            directory.rewind();first=read_prefix(directory,fields);directory.rewind()
            prefix=Fields(indices,context.arena,context.codes.bits);prefix.tape=first
            frame=Callback(context.ring,indices,self.program,prefix,self.specifications,spec.code,allow_fallback=True)
            valid=raw.compare(frame.final_size,self.parent_size)==0 and raw.compare(frame.depth,self.depth)==0
            frame.close();first.clear()
            need(valid,"selected node and encoded incoming frame agree")
            def coefficient(prefix,reference):
                values=Fields(indices,context.arena,context.codes.bits);values.tape=prefix
                return selected_coefficient(plan,context.ring,indices,self.program,values,
                                            self.specifications,spec.code,reference)
            return packet_engine.run(source,execute(geometry),layout,directory,prefixes,fields,coefficient,
                                     observe=observe)
        finally:
            layout.close();geometry.close();indices.free_many(columns,fields)
            directory.clear();prefixes.close();old_directory.rewind()


class IncomingWeights:
    """Read the unchanged parent program with exactly its frozen field prefix."""
    def __init__(self,context,indices,program,specifications,parent_size,depth):
        import oracle
        self.context,self.indices,self.program=context,indices,program
        self.specifications,self.parent_size,self.depth=specifications,parent_size,depth
        self.ambient=specifications.bind(0,True,tuple(map(tuple,oracle.eye(64)))).code

    def coefficient(self,prefix,request):
        need(request.kind=="incoming","original parent weight request")
        context,indices=self.context,self.indices
        fields=Fields(indices,context.arena,context.codes.bits);fields.tape=prefix
        frame=Callback(context.ring,indices,self.program,fields,self.specifications,self.ambient,
                       allow_fallback=True,leaf=True)
        try:
            need(frame.raw.compare(frame.final_size,self.parent_size)==0 and
                 frame.raw.compare(frame.depth,self.depth)==0,"frozen-only incoming parent frame")
            value=frame.weight(request.coordinate)
            if request.negative_inverse:
                inverse=context.ring.inverse(value)
                need(inverse is not None,"incoming remainder weight is a unit")
                opposite=context.ring.negate(inverse)
                context.arena.free_many(value,inverse);value=opposite
            frame.close()
            return value
        except ValueError:
            frame.abort()
            raise
