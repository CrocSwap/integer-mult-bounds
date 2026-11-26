# Child mass and induction for a native call

## The sharper child sum

Use the [numerical child-volume theorem](child-volume.md), including all three finite repair transforms, their retained row volumes, true padding and all full-volume reserve calls. At an adaptive node write $s=\log_2 m\ge2^{17}$, $l=\log_2(s+2)$, $U=\lceil s\rceil$, $v=\lceil\log_2(U+2)\rceil$. Let $d$ be the largest dyadic with $d^3v\le U$. If $\Lambda$ denotes the total volume of the issued native children divided by the true incoming volume, equation (4) of that theorem gives
$$
 q=\log_2(\Lambda/\sqrt m)\le 33+3s/d+d^2(l+3).
 \tag{3}
$$
The same $d$ occurs in both terms. Put $z=d(l/s)^{1/3}$. Then $z^3\le1+1/s$ and $z^3>l/(8v)$. Since $U+2\le s+3\le\sqrt{2}(s+2)$, one has $v\le l+3/2$ and $l/v\ge34/37>(31/32)^3$. Thus $31/64\le z\le33/32$. Furthermore $\Phi(s)\ge4096$ and $l\ge17$. The function $3/z+(20/17)z^2$ is decreasing throughout this interval, since $2(20/17)(33/32)^3<3$. Dividing (3) by $\Phi(s)$ gives the uniform bound
$$
 \frac{q}{\Phi(s)}
 \le \frac{33}{4096}+\frac{3}{31/64}+\frac{20}{17}(31/64)^2
 =\frac{13{,}982{,}555}{2{,}158{,}592}<\frac{13}{2}.
 \tag{4}
$$
This rounds the same scheduled child volume more tightly. No geometric incidence or reserve is deleted.

For the fixed root degree and the induction through all widths see [the native node](node-root-parameter.md) and [the piecewise density bound](address-native-staircase.md).
