# Next wave: reuse sharper spectral bounds for the unchanged circulant compiler

Status: proposed derivation, not independently reviewed or publication ready.
This file is separate from the frozen first-wave cut/interval package.

## Exact objective

Prove a smaller sufficient external fractional precision for the unchanged
direct-circulant source word by applying Nick Petalas's #4852 ideal completed
downset theorem to the **spectral** root/leading-section bounds. Keep the
source's larger component admission and original allocation unchanged.
Propagate every resulting bound through the original pivoted sixteen-H
lowering, routing, tensor schedule, coefficient cache and bootstrap.

This is an analytic_recovery enabling lemma. It does not price coefficient
preparation, copying, restoration or recursive native services, change their
tariffs, or improve the multiplication exponent. A lower sufficient bit count
alone is not a measured speed or space improvement.

## Inputs and dependency pins

* Canonical base: e54523517d0f03e58352e647c403a5af3e525a57.
* #8093 parent proof and unchanged source word at publication head
  13561dbdf4971a7ae0901d2f43df8de3981e94a5.
* #7849 direct-circulant source head
  3615fd982f2f4dc7172bef6f0dc9a4f77d5ab6dd.
* Nick Petalas #4852 at
  8acf04b4c42fe75894a87a3b2d37ddb68e96a798, retained proof SHA256
  1e59ae73eb142ec3d4579ce98244295b733896afca0fec3693906fc6def26d3f.
* Brian/JoyboyBrian #4977 at
  cd30004ff733d4acac45a47a74fc9b1e76ef35e4 credits the rounded allocation
  substitution. This task does not duplicate that adapter: it keeps the old
  allocation and uses sharper analysis of its overprecise generated word.
* First-wave source-cut/relative-interval proof, pending separate review,
  frozen in ../package/ and ../FROZEN-FILES.json.

## Optimistic complete analytic budget

For one padded root of width t=2^ell>=2 the parent proof gives actual spectral
bounds Lambda=2 and Q=4*t from strict accretivity. Put chi=8*t. The credited
block-solve theorem gives B<=2*sqrt(t)*chi^2<=2^7*t^3. Since the original
component allocator has B_old>=256*t^3, its actual eta still implies
theta_new<=theta_old<=1/4. No narrower number is passed to a component guard.

For each actual shear, ||K||,||L||<=chi. Its exact displacement envelope
satisfies be<=4*t*chi by component/spectral conversion. With rank<=5*t,

```
alpha <= 320*t^4
KG <= 514*t^3
Hgen <= (3200*t^3)*(2318*t^4) < 2^23*t^7.
```

The actual scalar fragments also fit H=2^23*t^7. Hence, provisionally,

```
Kroot_original <= 2*max(1,2,4*t)*B*H <= 2^33*t^11
Soriginal_gate <= 2*B^2*H^2 <= 2^61*t^20
Routed_root_prefix <= 4*Kroot_original*64^40*(2*Soriginal_gate)
                   <= 2^337*t^31
Axis_prefix <= (2*t)^2*(2^337*t^31)^2 = 2^676*t^64.
```

For d axes, L=sum ell_i, retain the paid H-pack allowance and infinity-norm
conversion:

```
E = ceil(257*L/2)+1354*d
A = 20*L+303*d
J = 20000*(d+1)*(max ell_i+2)^6
C = 4*J*(d+1)^2+d+1
P = 4*p+A+2*E+bit_length(C)
  = 4*p+277*L+3011*d+(L mod 2)+bit_length(C).
```

Compare the parent selector's linear part 4*p+1361*L+4746*d+(L mod 2).
At p=72, widths (4,5), the prospective sufficient selector is 8,842 bits
against the parent's 22,068 and the original source's 688,620. This numerical
comparison is provisional until the full source/error proof is reviewed.

## Decisive obligations and stopping rule

1. Verify the credited #4852 block-row/inverse-block-column proof applies to
   the padded root and every source downset; Toeplitz structure is not needed
   for this theorem but the source rank premise remains unchanged.
2. Prove existing eta and scalar margins dominate the smaller **analytic**
   B and spectral Q; never conflate operator envelopes with executable
   component guards. Inspect actual full/generator parameter forwarding.
3. Bound the actual prepared displacement envelope and all local child
   fragments at the existing allocated precision, with stored inverses.
4. Recompute every lowering/cache/data-error/endpoint-bias term. Failure of
   one source-to-bound bridge stops the claimed selector, even if arithmetic
   constants or finite experiments pass.
5. Verify with independent exact formula checks, actual-source allocation
   probes, matrix negative controls and separate mathematical cross-review.

No astronomical source execution is attempted. Preserve first-wave proof
bytes throughout. Finish a source-specific lemma or a precise failed bridge;
do not extend into global storage or kappa claims.
