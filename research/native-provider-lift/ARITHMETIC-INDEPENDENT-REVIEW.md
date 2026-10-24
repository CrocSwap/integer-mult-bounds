# Independent review of the new native target

The source reviewed is Cao Yifan's PR #4610 at head 1eb8da6cfb35512c0cc2533413e5ca42f48e13c6, including round-three paid profile

    {1:2201,2:412,3:510,4:127,5:40,8:8}

and unchanged productive census {4:28,7:7,8:47,9:326}. This is a genuinely changed paid invoice relative to the old #4470/#4535 supplier. Its acceptance still requires the exact endpoint/phase/whole-job conditions reviewed separately; a histogram alone cannot establish them.

I read critical_provider_check.py and its frozen majorant engine. The exact interval root certification and the majorant checker both pass on the complete 64,404-paid, 10,928-productive profile with rank surplus 752. The retained witness a=1,b=1,height_base=1024,ell0=650,s=1/20,lambda=1/10,p=2/5,c=133 and upper_exponent=.997067 is applied to the changed profile, not to a stale old root. The bracket is theta in (.9969782241,.9969782242).

For q_C=.0030217755 and N=2^(10^12), the gap 1-theta_hi-q_C is exactly 3/10^10. The source majorant constant obeys log A<20 from (1-theta)log n0 and n0=145*1024^650. The logarithmic overhead is below16 because 133+log N<2^40 and log2<1. Thus total logarithmic overhead is below36. Since log2>2/3, absorption has logarithmic margin greater than

    (3/10^10)*10^12*(2/3)-36 = 164.

No enormous integer N is materialized. The derivative check gap > (2/5)/(133+(2/3)*10^12) ensures continuation for larger ranks. The finite compiler theorem still requires its credited chronological all-column construction and whole-job normalizers; this review does not manufacture them from the root.

I independently recomputed the crossing using a separate 70-digit Decimal exponential/logarithm sum and 180 bisections (provider_review.py), obtaining a saving near .0030217758 in the same bracket. This is corroboration, not the exact interval certificate. The source engine's wrong-root and unfunded-mirror controls reject as intended.

Finally, native_lift.choose('.0030217755','.0030217754') gives positive values for every interface guard and every nine-row excess. NEW-TARGET-PARAMETERS.json records the exact rational choices. In particular q=60435509/20000000000 and delta=1/80241742036, so the full-coordinate group-key exponent is 1-2delta<1, cap xi<epsilon, chirp guard and global gamma guard are strict. The minimum paid-row excess is

    80181306527/1604834840720000000000 > 0.

This establishes the numerical assembly of conditional native κ=.0030217754 from the admitted stronger source provider and the retained analytic caller. It does not assert unconditional mathematical acceptance, a practical algorithm implementation, a new TM frontier or a further paid-profile improvement over the current #4610 round-three head. Prepared for Dugongue with substantial OpenAI Codex assistance; Apache-2.0.
