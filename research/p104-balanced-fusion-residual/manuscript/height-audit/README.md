# Ordinary-only minimum first heights

For the fixed seven-stage e264 price recurrence, geometric ratio 16, debit `11/8`, gap `10^-21` and final booking `κ+5g` at `κ=0.003890115286594461`, the least integer first heights are:

| Trial | Least first H | Relative reduction from `2*10^12` |
| --- | ---: | ---: |
| `143519922218066619/2^65` | 1,920,864,718,790 | 3.9567640605% |
| `287039844436133239/2^66` | 1,479,259,210,417 | 26.03703947915% |

The four exact stage-7 margins are the cap minus the required ordinary booking; a positive value passes the strict inequality.

| Trial | First H | Exact margin | Approximation |
| --- | ---: | --- | ---: |
| 65-bit | 1,920,864,718,789 | `-105317725745311877/8448052374772727525933056000000000000000000000000` | `−1.24665095661×10^-32` |
| 65-bit | 1,920,864,718,790 | `8158050008405753/844805237477712557244416000000000000000000000000` | `+9.65672281195×10^-33` |
| 66-bit | 1,479,259,210,416 | `-9126686979662669/271077117057856109019136000000000000000000000000` | `−3.36682309400×10^-32` |
| 66-bit | 1,479,259,210,417 | `47305501493475931/13011701618785889325940736000000000000000000000000` | `+3.63561222655×10^-33` |

At both successful heights all first six price bookings are strictly above their preceding rate and strictly below their own cap. In each adjacent pair the first six booked ticks, including `b6`, are exactly the same; the eta cap is inactive at stage seven. On that shared plateau the final margin has the form `A−B/h`, with `A,B>0`. Its exact zero is

* 65-bit: `359006208000000000000000000000/186898225829369407`, whose floor is 1,920,864,718,789.
* 66-bit: `718012416000000000000000000000/485386476517284043`, whose floor is 1,479,259,210,416.

To cover all earlier rounding plateaus, note that each `c−(11/8)/(16^i*h)` increases with positive integer `h`. Taking the minimum with eta is monotone, and the stage limit is monotone in its prior booked tick. Python's actual truncation toward zero is monotone on the real line, as is subtracting one grid tick. Induction therefore makes every intermediate booked rate and the seventh cap nondecreasing in `h`. Since the cap at the predecessor integer is too low, every smaller integer fails regardless of any additional earlier-stage failures. The next integer passes all seven price checks.

`height_exact.py` computes the recurrence using only integer numerators, denominators, multiplication and division, performs a 41-step binary search and checks the four exact signs and plateau boundaries. The separate `cross_check.py` implements the literal recurrence with `fractions.Fraction`, and checked 2,352 stage calculations including small heights, both adjacent pairs and seeded samples. Run

```sh
python3 -I -B height_exact.py
python3 -I -B cross_check.py
```

This result concerns only the ordinary price recurrence and its fixed height ratio. It does **not** establish the numerical supplier, source allocation, controller entry, physical stock, all-size bound, or a second complete multiplier. In particular the percentage reduction is a reduction in the first ordinary height, not a measured runtime improvement.
