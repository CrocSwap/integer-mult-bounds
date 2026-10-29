// impl A: reads KILL-A8 dat_h*.txt (gen.py E8, lattice-basis labels). usage: a dat dims(e.g. 4,4,4,3) maxpairs
// pair scan over unordered (La,Lb) of maximal 7-flats; leftover S=Off\(La|Lb); cover S by flats of given dims (flat = dim-d subspace of F2^9 = affine (d-1)-flat of labels)
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef unsigned long long u64; typedef unsigned __int128 u128;
static int lab[120]; static u128 *mk; static int nm; static u128 off;
static int nd, dims[8], cap;
static int pc(u128 x){return __builtin_popcountll((u64)x)+__builtin_popcountll((u64)(x>>64));}
// S points
static int ns, sl[128];
static int rk(int*v,int n){int b[9]={0},r=0;for(int i=0;i<n;i++){int x=v[i];for(int k=8;k>=0&&x;k--)if(x>>k&1){if(b[k])x^=b[k];else{b[k]=x;r++;x=0;}}}return r;}
// all maximal cover-masks (over S bits) of flats of affine dim k containing point p
static int cmpu(const void*x,const void*y){u64 a=*(u64*)x,b=*(u64*)y;return a<b?-1:a>b;}
static u64 res[60000];
static int flats(int p,int k,u64*out,int maxo){
  int idx[64],m=0; for(int i=0;i<ns;i++) if(i!=p) idx[m++]=i;
  int nr=0,kk=k<m?k:m,c[8];
  for(int i=0;i<kk;i++)c[i]=i;
  while(1){
    int b[8]={0};
    for(int i=0;i<kk;i++){int x=(sl[idx[c[i]]]^sl[p])&255;for(int t=7;t>=0&&x;t--)if(x>>t&1){if(b[t])x^=b[t];else{b[t]=x;x=0;}}}
    u64 mm=0;for(int j=0;j<ns;j++){int x=(sl[j]^sl[p])&255;for(int t=7;t>=0&&x;t--)if((x>>t&1)&&b[t])x^=b[t];if(!x)mm|=1ULL<<j;}
    if(nr<60000)res[nr++]=mm; else {fprintf(stderr,"overflow\n");exit(3);}
    if(kk==0)break;
    int i=kk-1; while(i>=0&&c[i]==m-kk+i)i--; if(i<0)break; c[i]++; for(int j=i+1;j<kk;j++)c[j]=c[j-1]+1;
  }
  qsort(res,nr,8,cmpu); int no=0;
  for(int q=0;q<nr;q++) if(q==0||res[q]!=res[q-1]) res[no++]=res[q];
  nr=no; no=0;
  for(int q=0;q<nr;q++){int dom=0;for(int w=0;w<nr&&!dom;w++) if(w!=q&&(res[q]&~res[w])==0)dom=1; if(!dom&&no<maxo)out[no++]=res[q];}
  return no;
}
static u64 sol[8]; static int best[10];
static void compbest(void){static u64 tmp[4096];for(int d=2;d<=5;d++){best[d]=0;for(int p=0;p<ns;p++){int n=flats(p,d-1,tmp,4096);for(int q=0;q<n;q++){int c=__builtin_popcountll(tmp[q]);if(c>best[d])best[d]=c;}}}}
static int cover(u64 rem,int lvl,int usedmask){
  if(!rem) return 1; if(lvl>=nd) return 0;
  int p=__builtin_ctzll(rem);
  {int rc=0;for(int L=0;L<nd;L++)if(!(usedmask>>L&1))rc+=1<<(dims[L]-1); if(__builtin_popcountll(rem)>rc)return 0;}
  for(int L=0;L<nd;L++){ if(usedmask>>L&1)continue; {int dup=0;for(int M=0;M<L;M++)if(!(usedmask>>M&1)&&dims[M]==dims[L])dup=1; if(dup)continue;}
    static u64 buf[8][4096];
    int nn=flats(p,dims[L]-1,buf[lvl],4096);
    for(int q=0;q<nn;q++){sol[lvl]=buf[lvl][q];{int rc=0;for(int M=0;M<nd;M++)if(!((usedmask|1<<L)>>M&1))rc+=best[dims[M]];if(__builtin_popcountll(rem&~buf[lvl][q])>rc)continue;}if(cover(rem&~buf[lvl][q],lvl+1,usedmask|1<<L))return 1;}
  }
  return 0;
}
int main(int argc,char**argv){
  FILE*f=fopen(argv[1],"r"); int P; fscanf(f,"%d %d",&P,&nm); for(int i=0;i<120;i++)fscanf(f,"%d",&lab[i]);
  unsigned long long a,b; fscanf(f,"%llu %llu",&a,&b); off=((u128)b<<64)|a; mk=malloc(16*nm);
  for(int i=0;i<nm;i++){fscanf(f,"%llu %llu",&a,&b);mk[i]=((u128)b<<64)|a;}
  char*s=argv[2]; nd=0; cap=0; for(char*t=strtok(s,",");t;t=strtok(0,",")){dims[nd]=atoi(t);cap+=1<<(dims[nd]-1);nd++;}
  if(getenv("LABS")){ns=0;for(char*t=strtok(getenv("LABS"),",");t;t=strtok(0,","))sl[ns++]=atoi(t);compbest();printf("direct test ns=%d cover=%d\n",ns,cover((1ULL<<ns)-1,0,0));return 0;}
  int maxprint=argc>3?atoi(argv[3]):1;
  fprintf(stderr,"|Off|=%d masks %d cap %d\n",pc(off),nm,cap);
  int lmax=getenv("LEFTMAX")?atoi(getenv("LEFTMAX")):999; long long npair=0,ncov=0; int minl=999; int printed=0;
  for(int i=0;i<nm;i++){u128 r=off&~mk[i]; if(pc(r)-0>cap+64)continue; for(int j=i;j<nm;j++){u128 q=r&~mk[j]; int c=pc(q); if(c<minl)minl=c; if(c>cap||c>lmax)continue; npair++;
    ns=0; for(int t=0;t<120;t++) if((q>>t)&1) sl[ns++]=lab[t];
    // dims descending already assumed
    compbest();
    if(cover(ns==64?~0ULL:((1ULL<<ns)-1),0,0)){ncov++; if(printed<maxprint){printed++;printf("COVER La=%d Lb=%d left=%d lines:",i,j,c);for(int t=0;t<120;t++)if((q>>t)&1)printf(" %d",t);printf("\n  flats:");for(int l=0;l<nd;l++)printf(" %llx",sol[l]);printf("\n");fflush(stdout);} if(argc>4&&ncov>=maxprint)goto done;}}}
  done:
  printf("%s dims=%s cap=%d: pairs with leftover<=cap %lld, coverable %lld, min leftover %d\n",argv[1],argv[2],cap,npair,ncov,minl);
}
