// AUDIT-SC exact covering enumerator (independent of SC-A c/mcov.c, menum.c).
// usage: cov lo hi k Lmax forced out.txt     (target mask over 112 P112 lines, lo=lines 0..63, hi=64..111, hex)
// Enumerates all k-tuples of inclusion-maximal 6-flat sets (restricted to target), records every leftover L with
// |L|<=Lmax and (|L|<=6 or labelrank(L)<=5) and forced line not in L. Writes distinct leftovers + stats.
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
typedef struct {uint64_t lo,hi;} M;
static int pc(M a){return __builtin_popcountll(a.lo)+__builtin_popcountll(a.hi);}
static int lab[112];
static int rnk(M a){int b[9];int n=0;for(int i=0;i<112;i++){int in=i<64?(a.lo>>i)&1:(a.hi>>(i-64))&1;if(!in)continue;int x=lab[i];for(int j=0;j<n;j++){int y=b[j];if((x^y)<x)x^=y;}if(x){b[n++]=x;}}return n;}
static int cmpm(const void*a,const void*b){const M*x=a,*y=b;int px=pc(*x),py=pc(*y);if(px!=py)return py-px;if(x->hi!=y->hi)return x->hi<y->hi?-1:1;if(x->lo!=y->lo)return x->lo<y->lo?-1:1;return 0;}
static M*S;static int ns,K,LMAX,NEED,FORCED;static M T;static int tsz;
// hash set of leftovers
#define HS (1<<24)
static M*H;static char*Hu;static long nh=0;static int minleft=999;static long nleaf=0;
static void add(M l){uint64_t h=(l.lo*0x9E3779B97F4A7C15ULL)^(l.hi*0xC2B2AE3D27D4EB4FULL);size_t i=(h>>20)&(HS-1);while(Hu[i]){if(H[i].lo==l.lo&&H[i].hi==l.hi)return;i=(i+1)&(HS-1);}Hu[i]=1;H[i]=l;nh++;if(nh>HS/2){fprintf(stderr,"hash full\n");exit(2);}}
static void dfs(int t,int start,M cov){
  int c=pc(cov);
  if(t==K){M l={T.lo&~cov.lo,T.hi&~cov.hi};int s=tsz-c;nleaf++;if(s<minleft)minleft=s;
     if(s<=LMAX){ if(FORCED>=0){int in=FORCED<64?(l.lo>>FORCED)&1:(l.hi>>(FORCED-64))&1; if(in)return;}
        if(s<=6||rnk(l)<=5)add(l);} return;}
  for(int i=start;i<ns;i++){
    if(c+(K-t)*pc(S[i])<NEED)break;
    M n={cov.lo|S[i].lo,cov.hi|S[i].hi};
    dfs(t+1,i,n);
  }
  // also allow 'empty' remaining sets (fewer than K sets): equivalent to repeating a set; handled since i>=start allows repeats
}
int main(int argc,char**argv){
  T.lo=strtoull(argv[1],0,16);T.hi=strtoull(argv[2],0,16);K=atoi(argv[3]);LMAX=atoi(argv[4]);FORCED=atoi(argv[5]);
  tsz=pc(T);NEED=tsz-LMAX;
  FILE*f=fopen("labels112.bin","rb");fread(lab,4,112,f);fclose(f);
  f=fopen("flats6.bin","rb");fseek(f,0,SEEK_END);long n=ftell(f)/16;fseek(f,0,SEEK_SET);M*A=malloc(n*16);fread(A,16,n,f);fclose(f);
  for(long i=0;i<n;i++){A[i].lo&=T.lo;A[i].hi&=T.hi;}
  qsort(A,n,16,cmpm);
  // unique
  long u=0;for(long i=0;i<n;i++){if(pc(A[i])==0)continue;if(u&&A[u-1].lo==A[i].lo&&A[u-1].hi==A[i].hi)continue;A[u++]=A[i];}
  // maximal filter
  S=malloc(u*16);ns=0;
  for(long i=0;i<u;i++){int dom=0;for(int j=0;j<ns;j++){if(pc(S[j])<=pc(A[i]))break;if((A[i].lo&~S[j].lo)==0&&(A[i].hi&~S[j].hi)==0){dom=1;break;}}if(!dom)S[ns++]=A[i];}
  int hist[21]={0};for(int i=0;i<ns;i++)hist[pc(S[i])]++;
  fprintf(stderr,"target %d lines, distinct sets %ld, maximal %d, sizes:",tsz,u,ns);for(int s=20;s>0;s--)if(hist[s])fprintf(stderr," %d:%d",s,hist[s]);fprintf(stderr,"\n");
  H=calloc(HS,16);Hu=calloc(HS,1);
  M z={0,0};dfs(0,0,z);
  FILE*o=fopen(argv[6],"w");fprintf(o,"# target %d maximal %d leaves %ld minleft(within bound) %d distinct_leftovers %ld\n",tsz,ns,nleaf,minleft,nh);
  for(size_t i=0;i<HS;i++)if(Hu[i])fprintf(o,"%016llx %016llx\n",(unsigned long long)H[i].lo,(unsigned long long)H[i].hi);
  fclose(o);fprintf(stderr,"leaves %ld minleft %d distinct %ld\n",nleaf,minleft,nh);return 0;}
