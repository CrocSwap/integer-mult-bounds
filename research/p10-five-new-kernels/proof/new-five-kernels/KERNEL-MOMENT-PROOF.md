# Sufficient moment improvement from the five added kernel entries

This is an ordinary mathematical proof, with exact rational numerical bounds independently checked in native C++. It establishes a strict improvement of the normalized **helper histogram moment**; the delivered bound still requires the bank, prime, fallback, complete source and 47-constraint checks.

Let H be any nonnegative integral histogram with H_3>=6, ranks below100, positive deficitD and massM=Σ rH_r+D>5. Define N_H(a)=Σ rH_r(100/r)^a and F_H(a)=N_H(a)/M. Suppose a in(0,1/1000] satisfies F_H(a)=1. Apply ΔH={1:+7,2:+3,3:-6}; its rank mass is-5, so the new denominator isM-5. Its numerator delta is

    g(a)=7*100^a+6*50^a-18*(100/3)^a.

We have g(0)=-5. For0<=a<=1/1000, the elementary bounds ln100<5, ln50<4, ln(100/3)>7/2 and x^a<101/100 for1<=x<=100 give

    g'(a) < (101/100)*(7*5+6*4)-18*(7/2) = -341/100.

Consequently g(a)<-5-(341/100)a<-5. At the old root, therefore,

    F_new(a)=(M+g(a))/(M-5)<1.

All new child ranks remain below100, so F_new is continuous and strictly increasing and tends to infinity: its unique root is strictly larger than a. This is a **sufficient improvement theorem** for every histogram satisfying the stated hypotheses; it is not merely a numerical derivative observation. It explains why four more paid calls can still improve the exponent: the rank distribution and width change favorably together.

The logarithmic bounds follow from positive Taylor lower bounds e^5>100 (throughdegree6), e^4>50 (throughdegree7), and the rational upper bound for e^(7/2) usingdegree16 plus the geometric tail t_17/(1-(7/2)/18)<100/3. Also e^(1/200)<=200/199<101/100. Every stated rational inequality is checked in `kernel_moment_proof.cpp` without floating point.

At infinitesimal scale, Δφ = -5 ln100-6 ln2+18 ln3 = ln(3^18/(64*100^5))<0. Its exact integer inequality is also checked. Neither this proof nor the one-stage Δφ is a substitute for the literal completed-bank invoice or full-fallback price. No gains are added across independent suppliers.

The five prefix relations themselves pass an independent native C++ replay on the exact PR320 pre-kernel records:4800target columns,5omitted-donor negative controls, no response escaping non-target coordinates, and nonzero rank-one Gram values. The complete new source replay is recorded separately by the delivery lane.
