# 八源 28 步问题：投影提升的匹配障碍（部分结果）

## Reviewer summary (English)

**Partial result; the eight-source 28-step question remains open. No new kappa.**
This package proves a general projection obstruction and excludes one particular
seven-source optimal projection. It does not exclude all 28-step words.

For a nonempty projected set `Q`, let `G(Q)` have an edge `{u,v}` exactly when
`u XOR v` has this unique unordered representation in `Q`. For a lift
`P ⊆ Q × F₂` projecting onto `Q`, let `S` be the projected states whose fibers
contain both layers. If `P + P` is the whole ambient space, `S` must cover every
edge of `G(Q)`: otherwise the unique pair has only one layer parity and misses
one of the two lifted differences. Hence
`|P| = |Q| + |S| ≥ |Q| + τ(G(Q)) ≥ |Q| + ν(G(Q))`.
This is a written proof for arbitrary dimension; the finite tests below are
corroboration rather than its justification.

For the 24-step seven-source word `341236425430103051216402`, all 24 prefix
states are distinct and their differences cover `F₂⁷`. An explicit matching of
11 unique-difference edges and a vertex cover of size 11 certify `τ = ν = 11`.
Every universal lift with exactly this projected state set therefore needs at
least 35 distinct states, or at least 36 steps for a closed singleton path.
**The 36-step lower bound is conditional on this fixed projection, not a global
bound on f(8), and attainability at 36 is not asserted.**

The checker also verifies an exact static lift criterion against direct XOR
enumeration on all 65,805 nonempty sets in dimensions 2–4, checks the known
32-step Gray upper construction, and rejects four false controls. In particular,
revisited projections invalidate the tempting general bound that the number of
double-layer states is at most the number of new-coordinate calls.

The exploratory logs are incomplete searches. The 28-step SMT run returned
`unknown` after its timeout, not `unsat`. Normal and optimized standard-library
checks reproduce `OBSTRUCTION-RESULT.json`; commands are in section 6.
The detailed proof, certificates, attribution and limitations follow below.

状态：**原问题尚未解决**。本轮得到一个一般必要条件、一个完整的固定投影排除证明，以及可复现的精确检查。没有证明所有 28 步候选不存在，没有把随机搜索或求解器超时当成排除证据，也没有提高已知的 `28 <= f(8) <= 32`。

Prepared for Nicholas Stone with substantial OpenAI Codex assistance, 2026-10-24, Asia/Shanghai. New text/code: Apache-2.0. No independent human or proof-kernel review, and no historical novelty claim.

## 1. 问题及已知前提

在八维二进制空间中，从零开始，每一步翻转一个坐标，最终返回零。记长度为 L 的单坐标序列为 w，终点前的前缀状态集合为 P。通用性条件为

\[
P+P=\mathbb F_2^8.
\]

这里加法就是 XOR。源码与贡献背景见 [PR5234](https://github.com/CrocSwap/integer-mult-bounds/pull/5234) 和 [PR3058](https://github.com/CrocSwap/integer-mult-bounds/pull/3058)。本轮以 canonical main `1a3ced60b2f7a46bc70280a04f2eeb8ca027c700` 为来源；对应 README 路径为 `research/eight-source-singleton-floor/README.md` 和 `research/connector-covering-code/README.md`。

conorholds 的 PR3058 证明 f(7)=24；本轮引用这一结果，没有重新运行其中排除较短序列的完整计算证明，也不将其视为所有最优 24 步序列的分类。Nick Petalas 的 PR5234 通过逐坐标删除推出 L>=28，并证明 28 步候选的次数只能是 `(4,4,4,4,4,4,2,2)`，允许重新编号。这些是前序结果，不是本轮贡献。Ross Richardson/PR943 的模型、Douglas Colkitt/PR1185 的 Gray 构造及原有贡献者保留署名。

因此，28 步候选删去任一出现四次的坐标后，都会得到一个通用的七源 24 步序列。但其不同前缀状态数不一定是 24，不能未经证明就假定投影是简单环。

## 2. 一般匹配障碍：完整证明

设 Q 是 \(\mathbb F_2^n\) 的一个非空子集。对每个非零差值 d，记其无序表示集合

\[
R_d=\{\{u,v\}\subseteq Q:u\ne v,\ u+v=d\}.
\]

定义图 G(Q)：顶点是 Q；若 \(R_{u+v}=\{\{u,v\}\}\)，就在 u、v 之间连边。也就是说，边的差值在 Q 中只有这一种无序表示。

考虑任意投影恰好等于 Q 的提升 \(P\subseteq Q\times\mathbb F_2\)。定义双层状态集合

\[
S=\{q\in Q:(q,0)\in P\text{ 且 }(q,1)\in P\}.
\]

**引理。** 如果 \(P+P=\mathbb F_2^{n+1}\)，则 S 是 G(Q) 的顶点覆盖。因而

\[
|P|=|Q|+|S|\ \ge\ |Q|+\tau(G(Q))\ \ge\ |Q|+\nu(G(Q)),
\]

其中 τ 是最小顶点覆盖大小，ν 是最大匹配大小。无需假定 G(Q) 是二分图。

**证明。** 取 G(Q) 的任意一条边 {u,v}，令 d=u+v。由于其无序表示唯一，P 中产生差值 `(d,0)` 或 `(d,1)` 的点对，其投影只能是 u、v。若 u、v 均不属于 S，那么它们各只有一个提升，设为 `(u,a)`、`(v,b)`，因此只能产生 `(d,a+b)`，缺少另一个提升差值。这与通用性矛盾，所以至少一个端点属于 S。每条边均如此，S 必须是顶点覆盖。每个 q 的非空纤维有一个或两个点，故 `|P|=|Q|+|S|`。匹配的边两两不共顶点，每条边都需要一个覆盖顶点，故任何匹配大小都是 |S| 的下界。证毕。

**对本题的后果。** 假定存在一个 28 步解。对六个出现四次的坐标 j，分别删除 j，得到投影集合 Q_j；每一个都必须满足

\[
|Q_j|+\nu(G(Q_j))\le 28.
\]

例如，若某个 Q_j 有 24 个不同状态，而且可以给出五条互不相交的唯一差值边，那么该候选立即被排除。对于只有 23 个不同状态的投影，需要六条这样的边；对于 22 个状态，需要七条。只找到一个违反条件的坐标就足够。

这个条件只是必要条件。尚未证明所有七源 24 步投影都违反它，更没有证明存在满足它的实际 28 步闭合路径。

## 3. 一个完整排除的七维最优投影

本轮计算得到以下七源序列：

```text
341236425430103051216402
```

其长度为 24，坐标 0--4 各出现四次，5、6 各出现两次，终态为零。它有 24 个不同前缀状态，差集覆盖全部 128 个七位掩码。引用 f(7)=24，可以称它为七源最优序列。

按访问顺序，其状态为

```text
0, 8, 24, 26, 30, 22, 86, 70, 66, 98, 114, 122,
123, 121, 120, 112, 113, 81, 83, 87, 85, 21, 5, 4
```

下表是 11 条互不相交的唯一差值边。数字是二进制状态的十进制编码，不是序列位置。

| u | v | u XOR v |
|---:|---:|---:|
|22|24|14|
|86|30|72|
|122|70|60|
|123|0|123|
|121|66|59|
|83|113|34|
|87|98|53|
|85|8|93|
|21|81|68|
|5|26|31|
|4|114|118|

逐一枚举 Q 的全部 276 个无序点对，可以检查这些差值各自只有表中所列的一种表示，且 22 个端点互不相同。因此 ν>=11。

另外，集合 `{24,26,66,81,83,85,86,87,70,114,123}` 覆盖 G(Q) 的全部边。因此 τ=ν=11；这里两个方向都有显式证书，不依赖通用顶点覆盖求解器。

由引理，任何具有这个**固定投影集合**的八维通用状态集，都至少需要 `24+11=35` 个不同状态。长度 L 的闭合路径至多有 L 个不同前缀状态，而闭合单坐标路径的长度为偶数，因此

\[
L\ge36.
\]

特别地，在上述七源序列中任意插入四次新坐标调用，都不可能得到八源 28 步解。这里的 36 是固定投影条件下的下界，不是 f(8) 的下界，也没有宣称 36 可达。

## 4. 精确的静态提升判据

匹配条件还可补充为一个精确的集合层面判据。对每个不在 S 中的 q，令 c(q) 为其唯一提升的最后一位。

P 通用当且仅当：

1. S 非空，从而能产生纯新坐标差值 `(0,1)`；
2. 对每个非零 d，以下至少一项成立：R_d 中有一对触及 S；或者所有表示都不触及 S，但这些表示的 `c(u) XOR c(v)` 同时取到 0 和 1。

理由是逐个检查 `(d,0)` 与 `(d,1)`：触及双层状态的一对自动产生两种；否则只能由单层端点的颜色奇偶决定。零差值 `(0,0)` 自动存在。

这是对固定提升集合 P 的充要条件，不是长度为 28 的路径可实现性条件。即使颜色分配满足它，仍须证明状态能按所需单坐标次数和闭合顺序访问。

## 5. 必须保留的重复状态边界

不能一般地说“双层状态数不超过新坐标调用次数”。反例是三维闭合序列

```text
2010120101
```

新坐标 2 只调用两次，但删除它后的投影重复遍历二维方块；四个投影状态全部在两层出现，故 |S|=4。它实际上访问全部八个三维状态。

始终成立的是 `|S|=|P|-|Q|<=L-|Q|`。只有投影具有 24 个不同状态且 L=28 时，才能推出 |S|<=4。验证程序专门拒绝错误的通用上界。

## 6. 验证与搜索结果

必要条件的普遍性来自第 2 节证明。有限计算的用途是核对证书、判据实现以及失败边界。

```sh
python3 -I -W error -B research/eight-source-lift-obstruction/verify_obstruction.py
python3 -I -O -W error -B research/eight-source-lift-obstruction/verify_obstruction.py
```

标准库即可。本轮 CPython 3.12.14 普通/优化执行输出一致，记录在 `OBSTRUCTION-RESULT.json`：

- 检查七源序列、全部 276 对状态、11 边匹配及 11 顶点覆盖证书。
- 枚举提升后维数为 2、3、4 的全部 65,805 个非空状态子集；其中 41,439 个通用。静态提升判据与直接差集枚举完全一致，所有通用实例都满足唯一差值边覆盖条件。
- 复核已知的 32 步 Gray 上界构造。
- 使用单独的连续区间 XOR 枚举，交叉核对一个 28 步搜索样本的差集；它只覆盖 246 个掩码，明确不是解。
- 四个错误控制全部被拒绝，包括非唯一差值、重复匹配端点、无效端点以及错误的双层状态上界。

`experiments/` 保存探索代码和日志，均不作为完整排除证书：

- 28 步交换退火约 8,985 万次候选评估，最好覆盖 246/256；评估不保证互异。
- 对 4,965 个采样得到的七源通用序列枚举四次新调用插入方式，评估 87,135,750 个提升，最好覆盖 242/256。七源父序列并未穷尽，也未去重，不能排除全部 28 步解。
- 完整 28 步 SMT 模型在 180 秒后返回 `unknown`，原因为超时，不能记为 UNSAT。使用 Z3 5.3.1，仅探索脚本需要此依赖；把 z3-solver 安装到脚本旁的 `deps/` 即可复跑。
- 附加的四种 30 步次数形状的启发式探测，以及对覆盖 255/256 的两个样本的局部改进，均未找到通用序列。这也不排除 30 步解。

探索程序用固定随机种子、墙钟停止条件，所以不同机器的评估数量和最佳结果可能不同。数学证书和标准库验证程序不依赖这些随机结果。未运行全域穷举、独立求解器 UNSAT 证书检查、完整七源最优解分类或形式化证明。

## 7. Open next questions / 精确剩余任务与接续方式

目前仍只有已知界 `28 <= f(8) <= 32`。下一步要回答的是：是否存在一个可实现的七源 24 步投影，其唯一差值图允许足够小的顶点覆盖，并且四次新坐标切换能满足第 4 节的所有颜色条件？

完整排除可以走两条路线：证明所有实际七源 24 步投影必有 `|Q|+τ(G(Q))>28`；或者保留满足这一必要条件的投影，再对四次切换位置作完整、带证书的剩余搜索。前一命题尚未建立，也可能过强；不能将它作为已证剪枝。匹配筛选失败只表示未排除，不表示存在合法提升。

**Open next question:** Can all realizable seven-source 24-step projections be
excluded by the matching/cover bound, or can any surviving projection support a
28-step lift? This decides the next obstruction needed to settle the 28-step
case. A feasible first step is to enumerate canonical seven-source parents,
retain the full projected state sets (including repeated visits), and certify
matching witnesses before exhaustively checking insertion positions. The blocker
is the missing complete parent enumeration or a uniform theorem replacing it.
Static color feasibility alone does not establish chronological path feasibility.

This submission is an isolated partial research result. The earlier projection
recurrence PR5416 concerns a different question. No selected result, frozen
predecessor, shared checker or production code is changed.
