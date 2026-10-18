"""Concrete selected residual consumer for newly produced common directories."""
from controller import Callback
from numeric import Geometry, selected_coefficient
import packet
from plan import compile_plan
from records import Fields, Tape
from words import Unsigned, need


class SelectedResidual:
    def __init__(self, context, indices, program, specifications, code, parent_size, depth,
                 before, suffix):
        # Only fixed source/low data enters this compilation step.
        import oracle
        spec = specifications[code]
        _request, common, low = context.codes.decode(code)
        need(context.dimension == 64 and common and low == spec.low and
             spec.template.chart == tuple(map(tuple, oracle.eye(64))) and
             program.code_bits == context.codes.bits, "selected common-view residual consumer")
        q = context.q
        prepared = oracle.multiply(low,oracle.reduce_rational(spec.template.preparation,q),q)
        projector = oracle.multiply([row[:spec.template.rank] for row in prepared],
                                    oracle.inverse(prepared,q)[:spec.template.rank],q)
        self.plan = compile_plan(projector,spec.template.rank,q,spec.good)
        self.context,self.indices,self.program = context,indices,program
        self.specifications,self.code = specifications,code
        self.parent_size,self.depth,self.before,self.suffix = parent_size,depth,before,suffix

    def __call__(self, source, directory, prefix_count):
        context, indices = self.context,self.indices
        raw = Unsigned(indices)
        divisor,one = indices.literal(64),indices.literal(1)
        columns,remainder = raw.divmod(self.parent_size,divisor)
        indices.free_many(divisor,remainder)
        field_count,carry = raw.add(self.depth,one)
        indices.free(one)
        need(not carry, "current source field extent")
        geometry = Geometry(self.plan,indices,columns,self.depth,self.code,self.program)
        padded_count = prefix_count.marginal()
        try:
            directory.rewind()
            first = packet.read_prefix(directory,field_count)
            directory.rewind()
            fields = Fields(indices,context.arena,context.codes.bits)
            fields.tape = first
            frame = Callback(context.ring,indices,self.program,fields,self.specifications,self.code,
                             allow_fallback=True)
            valid = raw.compare(frame.final_size,self.parent_size) == 0 and raw.compare(frame.depth,self.depth) == 0
            frame.close()
            first.clear()
            need(valid, "shared trace agrees with the encoded parent frame")
            def coefficient(prefix, request):
                current = Fields(indices,context.arena,context.codes.bits)
                current.tape = prefix
                return selected_coefficient(self.plan,context.ring,indices,self.program,current,
                                            self.specifications,self.code,request)
            return packet.run(source,geometry,self.parent_size,context.ring,context.q,
                              self.before,self.suffix,padded_count,field_count,directory,coefficient)
        finally:
            geometry.close()
            indices.free_many(columns,field_count)
            padded_count.close()
            directory.rewind()


class SelectedCopy511:
    """Bind the authenticated physical interval to its concrete selected callee."""
    def __init__(self, context, indices, program, specifications, common_low,
                 parent_size, depth, before, suffix):
        import oracle
        from binding import selected_episode
        from routes import compile_route, inverse_rational
        from sources import compile_specification
        self.episode = selected_episode(context.q)
        inverse = oracle.reduce_rational(inverse_rational(self.episode.chart),context.q)
        native_low = oracle.multiply(common_low,inverse,context.q)
        self.route = compile_route(native_low,self.episode.chart,context.codes)
        self.code = context.codes.encode(self.episode.request,True,common_low)
        spec = compile_specification(self.code,self.episode.template,common_low)
        need(self.code not in specifications or specifications[self.code] == spec,
             "one frozen/current source-code interpretation")
        vocabulary = dict(specifications)
        vocabulary[self.code] = spec
        self.residual = SelectedResidual(context,indices,program,vocabulary,self.code,
                                         parent_size,depth,before,suffix)
        self.context,self.indices,self.depth = context,indices,depth

    def __call__(self, families, old_directory, old_fields, old_count, fibre):
        from episode import physical
        need(Unsigned(self.indices).compare(old_fields,self.depth) == 0,
             "physical old fields agree with the generated parent depth")
        return physical(families,self.episode,self.route,self.code,self.context,old_directory,
                        old_fields,old_count,fibre,self.residual)
