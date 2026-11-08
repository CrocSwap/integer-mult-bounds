"""A concrete direct rounded C backend for the normalized-H request.

Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
Calls JoyboyBrian's unchanged #5485 integer Gaussian butterfly implementation.
This is an O(N)-work service for one selected bit, not an accelerated supplier.
"""
from fractions import Fraction as Q
from adapter import ceil_log2
from sources import need


class RoundedGaussian:
    def __init__(self, rounded, diagnostics=False):
        self.rounded = rounded
        self.diagnostics = diagnostics
        self.stats = dict(calls=0,butterflies=0,rounding_events=0,peak_numerator=0,
                          normalization_additions=0,phase_negations=0,lift_shifts=0,
                          padded_pair_slots=0,packing_component_writes=0,
                          maximum_internal_grid=0,maximum_word_width=0)

    def apply(self,state,request,E):
        request.validate()
        need(len(state) == request.size,'requested native field length')
        # Each coordinate defect is <=2^(-P-1); N*2^-P safely bounds
        # its Euclidean whole-field norm, including all parallel blocks.
        P = max(request.incoming_bits,request.error_bits+ceil_log2(request.size))
        width = P+4
        need(Q(request.size,1 << P) <= request.sigma,'funded whole-field C defect')
        self.stats['calls'] += 1
        self.stats['maximum_internal_grid'] = max(self.stats['maximum_internal_grid'],P)
        self.stats['maximum_word_width'] = max(self.stats['maximum_word_width'],width)
        step = 1 << request.bit
        pairs = []

        def run():
            data = [(0,0)]*8
            for k,(i,j) in enumerate(pairs):
                a,b = state[i],state[j]
                if self.diagnostics:
                    need(a.norm2() <= 1 and b.norm2() <= 1,'native unit-disk input')
                ints=[]
                for part in (a.re,a.im,b.re,b.im):
                    value=part*(1 << P)
                    need(value.denominator == 1,'native common-grid input lift')
                    ints.append(value.numerator)
                data[2*k] = (ints[0],ints[1])
                data[2*k+1] = (-ints[3],ints[2])  # S=diag(1,i), input
            trace={}
            self.rounded.call(data,1,0,width,trace=trace)
            for k,(i,j) in enumerate(pairs):
                for address,z in ((i,data[2*k]),(j,(-data[2*k+1][1],data[2*k+1][0]))):
                    a,b=z
                    # Exact multiplication by (1-i)/2 after output S.
                    re=self.rounded.checkword(a+b,width)
                    im=self.rounded.checkword(b-a,width)
                    state[address]=E.C(Q(re,1 << (P+1)),Q(im,1 << (P+1)))
            for key in ('butterflies','rounding_events'):
                self.stats[key] += trace[key]
            self.stats['peak_numerator'] = max(self.stats['peak_numerator'],trace['peak_numerator'])
            self.stats['normalization_additions'] += 4*len(pairs)
            self.stats['phase_negations'] += 2*len(pairs)
            self.stats['lift_shifts'] += 4*len(pairs)
            self.stats['padded_pair_slots'] += 4-len(pairs)
            # Clear only this owned packing buffer after the field return.
            for k in range(8):
                data[k]=(0,0)
            self.stats['packing_component_writes'] += 32  # 16 init + 16 clear

        for block in range(0,len(state),2*step):
            for low in range(step):
                pairs.append((block+low,block+low+step))
                if len(pairs)==4:
                    run();pairs.clear()
        if pairs:
            run()
        return state
