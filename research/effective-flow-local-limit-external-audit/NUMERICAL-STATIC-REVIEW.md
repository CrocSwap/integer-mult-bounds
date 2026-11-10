# Static mathematical review of the two finite-H engines

Verdict: **no enclosure-direction or proof-relevant validation defect found** in the two frozen implementations. Their methods independently enclose the six stated finite-law predicates for every alpha in the declared bracket, centered at the actual expectation. This review does not prove the existence/location of the tilt root or execute any numerical program.

Reviewed after both first receipts were sealed: BUILD/primary.py, BUILD/oracle.py, their algorithm notes, CASES/SCHEMA/SOURCE-PINS, both first certificates and RUN records, and BLIND-FIRST-COMPARISON.json. Current source SHA256 values equal the first RUN pins:

- primary: `6b9573fe12318fd816ea31602757195a22a902330d2a96b0d23640e82d41d70a`;
- oracle: `edd04477b6949362ee6200b85b6ea7157bcb83cdd43f625c22733a5b33a8c782`.

Only text reading and metadata hashing were performed. No new or source program, import, compile, checker, numerical experiment or kernel was run. Source numerical-checker code was not read. This note is the sole intentional write for this task.

## Primary logarithm, exponential and rounding

In primary.py:103–111, the atanh series uses z=(p-1)/(p+1) for p=2,3,5. All z lie in [0,1). Eighty iterations sum powers z through z^159; the next stored power is z^161. Every omitted denominator is at least 161, so `2*z^161/[161*(1-z squared)]` bounds the whole positive omitted tail. Lower and upper rounding is therefore in the correct direction. Factoring each required rank into these three primes and adding log intervals preserves the enclosure, with log 1 exactly zero; an unsupported prime is rejected.

The positive exponential series at primary.py:130–143 includes terms 0 through 79. The first omitted term is x^80/80!. All later successive ratios are at most x/81<1 on the checked 0<=x<4 domain. Thus the geometric tail `first_omitted/(1-x/81)` is a valid upper bound. The lower endpoint uses the positive partial sum at the lower argument; the upper endpoint uses partial sum plus tail at the upper argument. Monotonicity justifies those endpoint choices.

The grid functions at lines 94–100 implement exact rational floor and ceiling at scale 10^18 by integer division. Python Fraction denominators are positive; `-floor(-n/d)` is the correct ceiling even for signed inputs. No binary floating conversion or hidden truncation is used.

## Oracle decreasing rectangles and twelve squarings

In oracle.py:119–130, log r is integrated as 1/t over [1,r]. With N=4096, width h=(r-1)/N and decreasing integrand, right rectangles are lower and left rectangles upper. Their exact terms are `(r-1)/(N+k*(r-1))`; the code uses k=1..N below and k=0..N-1 above. Termwise floor/ceiling to scale 10^12 preserves each inequality and hence the sums. The r=1 branch is exactly zero. This direct integration method does not reuse prime logs or the primary atanh calculation.

For 0<=x<M=4096, the elementary log inequalities give `(1+x/M)^M<=exp(x)<=(1-x/M)^(-M)`. The engine checks nonnegative ordered arguments below 4<M. It rounds the lower initial base 1+lower/M down and the upper initial base 1/(1-upper/M) up. Both are nonnegative. Each integer square followed by outward division preserves order because squaring is monotone on nonnegative numbers. Exactly twelve squarings raise the bases to 2^12=M; they are not merely twelve first-order steps. The upper denominator is positive throughout. The x=0 control has exact base one in both directions.

Oracle ceiling_ratio and floor/ceil_scaled use the same exact integer quotient principle at their different grid. No transcendental library or numerical approximation is an acceptance input. This is a genuinely different exponential enclosure from the primary Taylor tail.

## Every alpha, normalization and actual mean

Both alpha endpoints and all rank logs are nonnegative. Therefore, for every alpha inside the bracket, the true alpha*log r lies between the product of the lower endpoints and the product of the upper endpoints. Each subsequent monotone exponential interval encloses r^alpha simultaneously across that bracket. A single midpoint is not substituted.

With weight intervals [l_r,u_r], lower normalizer L=sum(l_r)>0 and upper normalizer U=sum(u_r), both engines use `l_r/U <= p_r <= u_r/L`. The oracle additionally clips the upper endpoint at 1, which is safe for a probability. Using equal normalizer endpoints in the opposite direction would be invalid; neither engine does so. Correlation among alpha, probabilities, weights and logs only widens these boxes and is never assumed away as probabilistic independence.

All log values are nonnegative. Thus sums of probability/log endpoint products enclose the actual mean mu, not the inherited special value log 5. The primary separately bounds the raw second moment and uses `[second_lower-mean_upper squared, second_upper-mean_lower squared]`. Its mean interval is nonnegative, making squaring monotone as required. Dependency between those intervals cannot invalidate the outward subtraction.

The oracle takes a different route. For each atom, `log r-mu` belongs to `[log_lower-mean_upper,log_upper-mean_lower]`. The minimum absolute value is zero if this interval contains zero, otherwise the smaller absolute endpoint; the maximum is the larger absolute endpoint. Summing lower probabilities times lower squared distances and upper probabilities times upper squared distances encloses the variance directly. This requires no raw-moment subtraction or tensor/independence assumption about the enclosing boxes.

Both third absolute-moment upper bounds sum upper probabilities times upper cubed distances. Their support bound is the largest upper distance over positive-count atoms; zero-count controls are excluded from actual support. Those are valid for the entire alpha bracket and every actual mean inside the mean enclosure. H acceptance requires all six exact rational comparisons, including variance lower>=2 and upper<=3. Neither method proves that the actual mean equals log 5 or that the tilt root lies in the supplied bracket.

## Controls and complete-certificate behavior

Both implementations rerun their own arithmetic engine after setting the log-3 count to zero, alpha to [0,0], or the zero-atom count to zero. These are changes to the input law, not edits of a desired flag. The corresponding H predicate must fail. The oracle additionally retains exact zero-probability witnesses and an alpha-zero variance interval with upper<2. The primary requires the actual alpha-zero variance predicate to fail, without pretending to retain that same richer oracle witness. All-zero counts trigger the specific normalizer guard; the oracle catches its dedicated NormalizationError rather than an unrelated exception.

Both also execute parser/rational controls for duplicate keys, floats, nonfinite tokens and Boolean fractions. Rational proof fields are canonical Fraction strings; both reject noncanonical rational spellings and Boolean values as fractions. True Boolean outcomes are required where appropriate. All exceptions and comparisons remain active under optimization; no acceptance relies on assert.

Before arithmetic, both authenticate frozen CASES/SCHEMA/SOURCE-PINS hashes and exactly the eleven required FILES paths: two engine sources, three metadata files and six inert texts. Reading peer code for its hash is not an import. The source texts remain inert. Missing, duplicate or unexpected manifest paths fail.

Both default paths recompute the entire own certificate, including method-specific enclosures and controls, then compare complete canonical JSON to the submitted retained certificate. Primary has an explicit exact-key/type validator; oracle's partial encoding checks are supplemented by whole canonical equality, which rejects changed schema, method, extra/nested fields, controls and Boolean/integer aliases. Neither accepts merely because the six H flags are true. Emit mode writes only after complete recomputation and positive/control gates.

## Retained evidence, distinction and limits

The primary first RUN reports exit 0 at 21:35:22 UTC, about 0.207 seconds and 27,901,952 bytes peak RSS. The oracle reports exit 0 at 21:35:28 UTC, about 0.037 seconds and 28,180,480 bytes. Both record no peer-certificate read and empty stderr. I read those records; I did not reproduce their execution.

The first certificates intentionally differ. Root's comparison records equality of six common provenance/bracket/flag fields, all six H flags true, and overlap of eleven interval pairs (nine probabilities, mean and variance). It does not claim identical method-specific bounds or full-certificate equality across engines. Canonical hashes are primary `b598709235102b67c92f18389b7854a3c8c94baec6ba1cb2411cad20841a8f75` and oracle `81efa6c9c6071686d96391e38d43b58fc2ce4f1be26c99f5fbefc33f485569e5`. Overlap is corroboration, not the enclosure proof; the algorithms' outward directions supply that proof.

No code correction is requested. Subsequent normal/optimized replays, emitted-certificate equality to each own first, external corruption controls, publication integrity and all resulting status updates belong to root's separate evidence. All-n Fourier/smoothing analysis, source tilt-bracket correctness, symbolic onset, kernel/full-flow propagation, native/physical/resource interfaces, multiplication conclusions and selected framework assumptions remain outside this finite-H review.

The nine-atom law, alpha bracket, effective local-limit theorem and predecessors retain alephnan/PR6713 and the credited source authors' attribution. Atanh/Taylor tails, decreasing rectangles, elementary power sandwiches, outward rational rounding and moment boxes are classical. This separate AI-assisted static review is not blind to the submitted code/notes after their seals, human scientific acceptance or proof-kernel certification.
