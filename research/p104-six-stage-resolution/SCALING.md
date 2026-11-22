# The cost of approaching the raw crossing

For the fixed complete #8035 binary inventory put t=1-c and let T(t) and
P(t) be its productive and paid rank moments. Let c* be their crossing in
[0.00389,0.00389046]. Define

    alpha = P(t)/T(t), delta = 1-alpha,
    gamma = P(t+z)/(12^z T(t)), lambda = 15^w T(t-w)/T(t),
    F_theta(v) = 1 - alpha^v - theta gamma^v - lambda^v,

with z=593/2048, w=491/1024 and fixed theta=1/64 or 2. An allowed column
cutoff L pays the rounding requirement whenever F_theta(v)>2/L. Both
coefficients have previously established full split-tail tariff proofs.

The directed derivative of T(1-c)-P(1-c) lies strictly between -384104 and
-384101 throughout the stated interval. The directed endpoint signs enclose
c* between 0.003890115286594461129996942 and 0.003890115286594461129996943.
In particular delta is positive and proportional to c*-c from the left.
The same interval calculation gives gamma<0.907227, lambda<0.900011,
and gamma>lambda. At the root gamma* lies between 0.907225472004138239146095
and 0.907225472004138239146096.

With unrestricted finite v and finite L, c* is exactly the supremum of this
moment test on the interval. For c<c* all three ratios are below one, so
some finite v makes F_theta(v)>0 and any L>2/F_theta(v) pays rounding.
For c>=c* the raw term alone is at least one. This is a result about a
specific sufficient pricing test. A growing tensor power also changes
physical storage, individual ranks and the separate numerical supplier
requirements of an algorithm.

There is a sharp scaling law. Extend v to positive real x and let x_theta
be the unique zero of F_theta. The least positive integer v passing with
some finite L is floor(x_theta)+1, since F_theta increases strictly.
Put A=log(1/delta) and a=-log(gamma*), using natural logarithms. Then

    a x_theta = A - log A + log(a theta) + o(1)

as c approaches c* from below. First x_theta tends to infinity: any bounded
x leaves the other two tail terms bounded away from zero while 1-alpha^x
tends to zero. Uniform q<1 bounds gamma and lambda; at x=C A for a sufficiently
large fixed C the tails are O(delta^2), whereas 1-(1-delta)^x>=delta for
x>=1. Hence x_theta=O(A) and x_theta delta tends to zero. Smoothness of
the moments and the nonzero crossing derivative give gamma(c)^x_theta =
(gamma*)^x_theta (1+o(1)). The strict gap lambda*<gamma* makes the
productive tail negligible compared to the split tail. At the unique zero
we therefore have delta x_theta=(1+o(1)) theta exp(-a x_theta). Taking
logarithms gives a x_theta + log x_theta=A+log theta+o(1). First this gives
x_theta~A/a and then the expansion above by substitution.

In particular a is about 0.09736427 and the leading slope is 1/a, about
10.27071. Changing theta from 2 to 1/64 saves log(128)/a, about 49.83
continuous factors in the limit, with a rounding error below one in the
difference of the corresponding integer minima. For each displayed
finite threshold, check_scaling.py proves failure at v-1 and success at v.
For distances 10^-12, 10^-18 and 10^-24 below the lower root endpoint, the
minimal powers are respectively 233, 370, 508 for theta=2 and 210, 338, 469
for theta=1/64. These minimize the positive surplus before imposing a
particular fixed column cutoff. The finite application must pay its own 2/L.
The logarithmic inversion is elementary here and is a special case of
the classical Lambert W expansion (Corless et al., 1996).

## A separate limit from the installed six-stage rule

Write H_i for the stage log-rank, d>0 for its paid debit, b_0=0, and
C_i=c-d/H_i. At each stage the strict condition is
b_i < min(eta,(249 C_i+b_(i-1))/250). Thus b_6<c(1-250^-6).
The pinned selector sets b_i=(floor(S*limit)-1)/S for i<=5, S=10^18.
For a sharper necessary upper bound use u_0=0 and
u_i=(ceil(S*(249c*+u_(i-1))/250)-2)/S for i<=5. Each real installed
limit is strictly below its ideal limiting argument, which proves
b_i<=u_i inductively even if an ideal argument is itself a grid point.
The active interval is below eta. The five limiting tick integers are
3874554825448082, 3890053044749874, 3890115037627081,
3890115285598590, 3890115286590476. Their values are constant over the
entire directed bracket for c*. The resulting sixth-stage upper bound
(249c*+u_5)/250 lies between 0.003890115286594445189476954232 and
0.003890115286594445189476955228. Therefore the grid excludes every
reported kappa above 0.003890115286594445. To achieve that last reporting
tick also requires a separate finite tariff, physical resources and the
signed outer application. Other selectors, stage counts, suppliers and
word models have different upper bounds.
