#!/usr/bin/env bash
# Rerun the eight span facts of SPANFACTS.md from the shipped sources (provenance/src), compare with the shipped logs (provenance/logs).
#   usage: bash provenance/replay_spanfacts.sh        PYTHON=... (needs numpy)   JOBS=4 (parallel processes, default 4)   CC=cc
#          LOGDIR=dir   (per-fact replay logs and replay_summary.txt; default a fresh temporary directory; the shipped copy is provenance/logs/REPLAY)
# Every job is niced (10), runs under timeout 1200 s (a chunk is far below that: 3 s to 8 min), at most JOBS at a time.
# What is rerun (first implementation: the sources the facts were established with; second implementation where one exists):
#   1  (6,6)+1 <= 3      s66 mode 1 (C) and indep.py mode 1, 6 chunks (independent Python)
#   2  (6,6)+2 <= 4      s6x (= s6y), 4 rep-chunks
#   3  (6,6,3) s0 <= 4   s6x 6 6 4 lim 80, 8 rep-chunks, then the exact third-flat refinement on the 3 reps with relaxed span 8 (= s6r)
#   4  (7,4) s0 <= 4     s6x, 4 rep-chunks
#   5  (7,5) s0 <= 4     s6x, 2 rep-chunks; plus the |Off|<=88 extension pass (s3x NEWLO=80 PASS1=1, 24 chunks)
#   6  (6,6,4) s0 <= 5   s3f (|Off|<=80, target 8, 24 chunks) and s3y (|Off|<=88, target 6, 48 chunks: pass; target 5: the crack) and s3x pass 1
#   7  (6,5,4)+1 <= 4    s3f target 8, 24 chunks
#   8  (6,4,4)+1 <= 4    s3f target 8, 24 chunks
#   facts 6-8 are rerun a second time with the independent checker s3z (same chunks, same arguments) and compared.
set -uo pipefail
HERE=$(cd "$(dirname "$0")" && pwd); SRC="$HERE/src"; LOGS="$HERE/logs"; PY="${PYTHON:-python3}"; CC="${CC:-cc}"; JOBS="${JOBS:-4}"
LOGDIR="${LOGDIR:-${TMPDIR:-/tmp}/replay_logs.$$}"
export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 OPENBLAS_NUM_THREADS=1
"$PY" -c "import numpy" 2>/dev/null || { echo "FAIL python needs numpy (PYTHON=...)"; exit 1; }
command -v "$CC" >/dev/null || { echo "FAIL needs a C compiler"; exit 1; }
W=$(mktemp -d "${TMPDIR:-/tmp}/replay.XXXXXX"); mkdir -p "$W/work" "$W/out" "$W/gen77" "$W/gen80" "$W/gen88" "$LOGDIR"; T0=$SECONDS
echo "== build and direction data (work dir $W)"
for p in s66 s6x s3f s3x s3y s3z; do "$CC" -O2 -o "$W/work/$p" "$SRC/$p.c" 2>"$W/cc_$p.log" || { echo "FAIL compile $p.c"; cat "$W/cc_$p.log"; exit 1; }; done
OUT="$W/gen77" "$PY" -B "$SRC/gen.py" 77 > "$W/gen77.log" 2>&1 &
OUT="$W/gen80" "$PY" -B "$SRC/gen.py" 80 > "$W/gen80.log" 2>&1 &
OUT="$W/gen88" "$PY" -B "$SRC/gen88.py" 88 > "$W/gen88.log" 2>&1 &
wait
cp "$W/gen77/data.txt" "$W/gen80/data80.txt" "$W/gen88/data88.txt" "$W/gen80/gens.txt" "$W/work/"
bad=0
cmp -s "$W/gen80/gens.txt" "$HERE/data/gens.txt" || { echo "FAIL generated gens.txt differs from data/gens.txt"; bad=1; }
gzip -dc "$HERE/data/data88.txt.gz" | cmp -s - "$W/work/data88.txt" || { echo "FAIL generated data88.txt differs from data/data88.txt.gz"; bad=1; }
cmp -s <(head -n 114 "$W/work/data80.txt") <(head -n 114 "$W/work/data88.txt") || { echo "FAIL data80/data88 headers differ"; bad=1; }
[ $bad = 0 ] && echo "PASS direction lists regenerated (gen.py 77/80, gen88.py 88): data.txt, data80.txt, data88.txt, gens.txt; data88.txt and gens.txt equal the shipped copies"
# ---- job list: one line per job:  NAME<TAB>command (run in $W/work)
J="$W/jobs.lst"; : > "$J"
job() { printf '%s\t%s\n' "$1" "$2" >> "$J"; }
reps() { local k=$1 n=$2 s="" i; for ((i=k;i<159;i+=n)); do s="$s,$i"; done; echo "${s#,}"; }
reps51() { local k=$1 n=$2 s="" i; for ((i=k;i<51;i+=n)); do s="$s,$i"; done; echo "${s#,}"; }
job f1_s66_m1 "./s66 1"
for c in 0 1 2 3 4 5; do job f1_indep_m1_c$c "$PY -B $SRC/indep.py 1 $c 6"; done
for k in 0 1 2 3; do job f2_y662_$k "./s6x data80.txt 6 6 2 78 $(reps $k 4)"; done
for k in 0 1 2 3 4 5 6 7; do job f3_y664_$k "./s6x data80.txt 6 6 4 80 $(reps $k 8)"; done
job f3_r664 "./s6x data80.txt 6 6 4 80 67,68,82 8"
for k in 0 1 2 3; do job f4_y740_$k "./s6x data80.txt 7 4 0 80 $(reps51 $k 4)"; done
for k in 0 1; do job f5_y750_$k "./s6x data80.txt 7 5 0 80 $(reps51 $k 2)"; done
for r in $(seq 0 23); do
  job f5_p1y750_$r "NEWLO=80 PASS1=1 ./s3x data88.txt 7 5 0 0 88 8 24 $r"
  job f6_p1a664_$r "NEWLO=80 PASS1=1 ./s3x data88.txt 6 6 4 0 88 8 24 $r"
  job f6_s3f_a664s0_$r "./s3f data80.txt 6 6 4 0 80 8 24 $r"
  job f7_s3f_b654s1_$r "./s3f data80.txt 6 5 4 1 80 8 24 $r"
  job f8_s3f_b644s1_$r "./s3f data80.txt 6 4 4 1 80 8 24 $r"
  job z6_s3z_a664s0_$r "./s3z data80.txt 6 6 4 0 80 8 24 $r"
  job z7_s3z_b654s1_$r "./s3z data80.txt 6 5 4 1 80 8 24 $r"
  job z8_s3z_b644s1_$r "./s3z data80.txt 6 4 4 1 80 8 24 $r"
done
for r in $(seq 0 47); do
  job f6_s3y_t6_$r "./s3y data88.txt 6 6 4 0 88 6 48 $r"
  job z6_s3z_t6_$r "./s3z data88.txt 6 6 4 0 88 6 48 $r"
done
job f6_s3y_t5_34 "EXITCRACK=1 ./s3y data88.txt 6 6 4 0 88 5 48 34"
job z6_s3z_t5_34 "EXITCRACK=1 ./s3z data88.txt 6 6 4 0 88 5 48 34"
# long jobs first (indep, s6x, s66), then the many small chunks
sort -s -k1,1 "$J" | awk -F'\t' '{p=($1 ~ /^f1_indep|^f3_y664|^f4_y740|^f1_s66/)?0:1; print p"\t"$0}' | sort -s -n -k1,1 | cut -f2- > "$W/jobs.sorted"
cat > "$W/run1.sh" <<'EOS'
#!/usr/bin/env bash
# run1.sh WORKDIR OUTDIR NAME TIMEOUT PY CMD...   (CMD is one string run via eval, with PY set)
W=$1; O=$2; n=$3; T=$4; PY=$5; cmd=$6; cd "$W" || exit 1; export PY
TIMEFORMAT='%U %S'
{ time timeout "$T" nice -n 10 bash -c "$cmd" > "$O/$n.out" 2> "$O/$n.err"; echo $? > "$O/$n.rc"; } 2> "$O/$n.cpu"
EOS
chmod +x "$W/run1.sh"
echo "== running $(wc -l < "$J") jobs, $JOBS at a time"
while IFS=$'\t' read -r n c; do printf '%s\0' "$n"; printf '%s\0' "$c"; done < "$W/jobs.sorted" |
  xargs -0 -n 2 -P "$JOBS" bash -c '"$0"/run1.sh "$0"/work "$0"/out "$1" 1200 "'"$PY"'" "$2"' "$W" 
WALL=$((SECONDS - T0))
echo "== compare"
"$PY" -B "$HERE/replay_compare.py" "$W/out" "$LOGS" "$LOGDIR" "$WALL" | tee "$W/summary.txt"
cp "$W/summary.txt" "$LOGDIR/replay_summary.txt"
grep -q '^FAIL' "$W/summary.txt" || [ $bad != 0 ] && { echo "REPLAY FAIL (work dir $W)"; exit 1; }
echo "REPLAY PASS (wall ${WALL}s)"; rm -rf "$W"
