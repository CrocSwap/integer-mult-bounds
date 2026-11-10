// Exact necessary-condition enumeration of dense-y families (R2 dropped), cost <= chain.
// types (lo,hi,Y subset of [lo,hi]); family = multiset of >= L-1 types; sign-consistency prefilter
// identical to the sign prefilter of the base package (signed union-find on uncovered pairs + uncovered-row rule).
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>
#include <time.h>
static double f(double x){return x>0?x*log(x):0;}
typedef struct{double c;int lo,hi;unsigned Y,M;}T;
static T ty[200000];static int nt,L,mx;static double CH,cmin;
static long long nleaf,nok;
static int cur[64];
static unsigned cov[64];
static int cmpT(const void*a,const void*b){double x=((T*)a)->c,y=((T*)b)->c;return x<y?-1:x>y;}
static double fcost(int lo,int hi,unsigned Y){int m=hi-lo+1;double c=f(8*m+1);int r=0;for(int k=lo;k<=hi;k++){if(Y>>k&1){c-=f(8*r);r=0;}else r++;}return c-f(8*r);}
static int par[64],ps[64];
static int find(int x,int*p){int q=0;while(par[x]!=x){q^=ps[x];x=par[x];}*p=q;return x;}
static int ok(void){
 for(int i=0;i<2*L;i++){par[i]=i;ps[i]=0;}
 for(int i=0;i<L;i++)for(int j=0;j<L;j++){
  if(i==j||(cov[i]>>j&1))continue;
  int w=(i>j)?0:1,pa,pb;int ra=find(i,&pa),rb=find(L+j,&pb);
  if(ra==rb){if((pa^pb)!=w)return 0;}else{par[ra]=rb;ps[ra]=pa^pb^w;}
 }
 for(int i=0;i<L;i++)if(!cov[i]){for(int k=0;k<L;k++)if(k!=i&&!(cov[k]>>i&1))return 0;}
 return 1;
}
static void pr(int n,double c){printf("%.6f d=%+.6f n=%d:",c,c-CH,n);for(int k=0;k<n;k++){T*t=&ty[cur[k]];printf(" [%d,%d|",t->lo,t->hi);for(int i=t->lo;i<=t->hi;i++)if(t->Y>>i&1)printf("%d",i);printf("]");}printf("\n");fflush(stdout);}
static void rec(int start,int n,double c){
 if(n>=L-1){nleaf++;if(ok()){nok++;pr(n,c);}}
 if(n>=mx)return;
 for(int i=start;i<nt;i++){
  if(c+ty[i].c>CH+1e-7)break;
  int need=L-2-n;if(need<0)need=0;
  if(c+ty[i].c+need*cmin>CH+1e-7)continue;
  unsigned sv[64];memcpy(sv,cov,sizeof cov);
  for(int r=0;r<L;r++)if(ty[i].Y>>r&1)cov[r]|=ty[i].M;
  cur[n]=i;rec(i,n+1,c+ty[i].c);
  memcpy(cov,sv,sizeof cov);
  if(n==0){fprintf(stderr,"top %d/%d cost %.3f leaves %lld ok %lld t=%ld\n",i,nt,ty[i].c,nleaf,nok,(long)clock()/CLOCKS_PER_SEC);}
 }
}
int main(int argc,char**argv){L=atoi(argv[1]);mx=argc>2?atoi(argv[2]):L+4;
 int g=L/2;CH=0;
 for(int c=0;c<g;c++){CH+=fcost(c,g-1,1u<<c);CH+=fcost(g,g+c,1u<<(g+c));}
 for(int lo=0;lo<L;lo++)for(int hi=lo;hi<L;hi++){int m=hi-lo+1;for(unsigned mk=1;mk<(1u<<m);mk++){unsigned Y=mk<<lo;ty[nt].lo=lo;ty[nt].hi=hi;ty[nt].Y=Y;ty[nt].M=((1u<<m)-1)<<lo;ty[nt].c=fcost(lo,hi,Y);nt++;}}
 qsort(ty,nt,sizeof(T),cmpT);cmin=ty[0].c;
 printf("L=%d chain=%.9f types=%d cmin=%.4f maxfields=%d\n",L,CH,nt,cmin,mx);fflush(stdout);
 rec(0,0,0);
 printf("DONE leaves=%lld signconsistent=%lld\n",nleaf,nok);
}
