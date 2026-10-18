// kgap: min F2 cost for T-block decoder. input: T v ; v lines of 2T ints (p then q).
// usage: kgap ex [slack] | kgap sa restarts steps seed [maxtemp]
// output: "best <cost> f <f> n <nmin>" then for ex: all minimisers as bitstrings over free list; for sa: best B bits.
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <math.h>
typedef uint64_t u64;
int T,v,f; long long P[16][64],Q[16][64];
u64 Rm[16],Am[16]; int ft[4096],fs[4096];
u64 row[64]; int rk[16];
static inline int blockrank(int j){u64 basis[64];memset(basis,0,sizeof basis);int r=0;
 u64 m=Rm[j];while(m){int t=__builtin_ctzll(m);m&=m-1;u64 x=row[t]&Am[j];
  while(x){int b=__builtin_ctzll(x);if(basis[b])x^=basis[b];else{basis[b]=x;r++;break;}}}
 return r;}
static inline int cost(){int c=0;for(int j=0;j<T;j++){rk[j]=blockrank(j);c+=rk[j];}return c;}
u64 rng_s=88172645463325252ULL;
static inline u64 rnd(){rng_s^=rng_s<<13;rng_s^=rng_s>>7;rng_s^=rng_s<<17;return rng_s;}
static inline double urand(){return (rnd()>>11)*(1.0/9007199254740992.0);}
int *fblocks[4096]; int nfb[4096];
int main(int argc,char**argv){
 if(scanf("%d %d",&T,&v)!=2)return 1;
 for(int t=0;t<v;t++){for(int j=0;j<T;j++)scanf("%lld",&P[j][t]);for(int j=0;j<T;j++)scanf("%lld",&Q[j][t]);}
 for(int j=0;j<T;j++){Rm[j]=Am[j]=0;for(int t=0;t<v;t++){if(P[j][t])Rm[j]|=1ULL<<t;if(Q[j][t])Am[j]|=1ULL<<t;}}
 f=0;
 for(int t=0;t<v;t++)for(int s=0;s<v;s++){if(t==s)continue;long long d=0;for(int j=0;j<T;j++)d+=P[j][t]*Q[j][s];
  if(d)continue; int ok=0;for(int j=0;j<T;j++)if((Rm[j]>>t&1)&&(Am[j]>>s&1))ok=1; if(ok){ft[f]=t;fs[f]=s;f++;}}
 for(int t=0;t<v;t++){long long d=0;for(int j=0;j<T;j++)d+=P[j][t]*Q[j][t];if(!d){printf("ERR diag zero %d\n",t);return 2;}}
 // print free list
 printf("free %d\n",f);for(int i=0;i<f;i++)printf("%d,%d ",ft[i],fs[i]);printf("\n");
 for(int t=0;t<v;t++)row[t]=1ULL<<t;
 if(argc>1&&!strcmp(argv[1],"ex")){
  int slack=argc>2?atoi(argv[2]):0; if(f>40){printf("too many free %d\n",f);return 3;}
  u64 N=1ULL<<f,g=0;int best=1000;size_t cap=1<<20,nm=0;u64*ms=malloc(8*cap);int*cs=malloc(4*cap);size_t total=0;
  for(u64 i=0;i<N;i++){
   if(i){int b=__builtin_ctzll(i);g^=1ULL<<b;row[ft[b]]^=1ULL<<fs[b];}
   int c=cost();
   if(c<best){best=c;size_t m=0;for(size_t k=0;k<nm;k++)if(cs[k]<=best+slack){ms[m]=ms[k];cs[m]=cs[k];m++;}nm=m;}
   if(c<=best+slack&&nm<cap){ms[nm]=g;cs[nm]=c;nm++;}
  }
  printf("best %d f %d n %zu\n",best,f,nm);
  size_t lim=nm<2000?nm:2000;for(size_t k=0;k<lim;k++)printf("%d %llu\n",cs[k],(unsigned long long)ms[k]);
  return 0;}
 // SA
 int restarts=atoi(argv[2]);long steps=atol(argv[3]);rng_s^=(u64)atoll(argv[4])*0x9E3779B97F4A7C15ULL;for(int i=0;i<10;i++)rnd();
 double T0=argc>5?atof(argv[5]):1.0;
 int gbest=1000;u64 gb[64];memset(gb,0,sizeof gb);
 for(int r=0;r<restarts;r++){
  for(int t=0;t<v;t++)row[t]=1ULL<<t;
  // random init density
  int on[4096];double dens=urand()*0.6;for(int i=0;i<f;i++){on[i]=urand()<dens;if(on[i])row[ft[i]]^=1ULL<<fs[i];}
  int c=cost();int bst=c;
  for(long st=0;st<steps;st++){
   double temp=T0*(1.0-(double)st/steps)+0.05;
   int i=rnd()%f;row[ft[i]]^=1ULL<<fs[i];
   int c2=cost();
   if(c2<=c||urand()<exp((c-c2)/temp)){c=c2;on[i]^=1;
     if(c<bst){bst=c;} if(c<gbest){gbest=c;memcpy(gb,row,sizeof(u64)*v);} }
   else row[ft[i]]^=1ULL<<fs[i];
  }
 }
 printf("best %d f %d\n",gbest,f);
 for(int t=0;t<v;t++)printf("%llu ",(unsigned long long)gb[t]);printf("\n");
 return 0;}
