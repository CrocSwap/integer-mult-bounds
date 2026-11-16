// impl B: own E8 (Bourbaki, from SECOND/s2.c construction), HT=i => h = fundamental weight w_i, Off = roots with alpha_i coeff != 0.
// cover test: slot-assignment DFS (each leftover point goes to a slot whose affine rank stays <= dim-1). usage: b i dims [stop]
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef unsigned long long u64; typedef struct{u64 a,b;} M2;
static int adjm[8][8],R[240][8],nR,pos[120][8],lab[120];
static int ip(int*c,int*d){int s=0;for(int i=0;i<8;i++)s+=2*c[i]*d[i];for(int i=0;i<8;i++)for(int j=0;j<8;j++)if(adjm[i][j])s-=c[i]*d[j];return s;}
static int popc(M2 m){return __builtin_popcountll(m.a)+__builtin_popcountll(m.b);}
static int cmp(const void*x,const void*y){const M2*p=x,*q=y;return p->a<q->a?-1:p->a>q->a?1:p->b<q->b?-1:p->b>q->b?1:0;}
static int nd,dims[8],ns,sl[128];
// slot state: basis of differences from slot's anchor
typedef struct{int cnt,anchor,b[8],r;} Slot;
static int reduce(Slot*s,int x){for(int t=7;t>=0&&x;t--)if((x>>t&1)&&s->b[t])x^=s->b[t];return x;}
static int asg[128];
static int dfs(int i,Slot*S,int nused){
  if(i==ns)return 1;
  int seen_empty=0;
  for(int k=0;k<nd;k++){Slot c=S[k];
    if(c.cnt==0){if(seen_empty)continue;seen_empty=1;c.cnt=1;c.anchor=sl[i];Slot T[8];memcpy(T,S,sizeof(Slot)*nd);T[k]=c;asg[i]=k;if(dfs(i+1,T,nused))return 1;continue;}
    int x=(sl[i]^c.anchor)&255;int y=reduce(&c,x);
    if(y){ if(c.r>=dims[k]-1)continue; int t=7;while(!(y>>t&1))t--; c.b[t]=y;c.r++; }
    c.cnt++;Slot T[8];memcpy(T,S,sizeof(Slot)*nd);T[k]=c;asg[i]=k;if(dfs(i+1,T,nused))return 1;}
  return 0;}
static int coverable(){Slot S[8];memset(S,0,sizeof S);return dfs(0,S,0);}
int main(int argc,char**argv){int HT=atoi(argv[1]);char*ds=argv[2];int stop=argc>3;
 int cap=0;nd=0;for(char*t=strtok(ds,",");t;t=strtok(0,",")){dims[nd]=atoi(t);cap+=1<<(dims[nd]-1);nd++;}
 int lmax=getenv("LEFTMAX")?atoi(getenv("LEFTMAX")):999;
 int E[7][2]={{0,2},{2,3},{3,4},{4,5},{5,6},{6,7},{1,3}};for(int i=0;i<7;i++){adjm[E[i][0]][E[i][1]]=adjm[E[i][1]][E[i][0]]=1;}
 for(int i=0;i<8;i++){memset(R[i],0,32);R[i][i]=1;}nR=8;
 for(int k=0;k<nR;k++)for(int i=0;i<8;i++){int al[8]={0};al[i]=1;int c=ip(R[k],al);int w[8];for(int j=0;j<8;j++)w[j]=R[k][j]-c*al[j];
  int f=0;for(int q=0;q<nR&&!f;q++)if(!memcmp(R[q],w,32))f=1;if(!f)memcpy(R[nR++],w,32);}
 int np=0;for(int k=0;k<nR;k++){int ok=1;for(int j=0;j<8;j++)if(R[k][j]<0)ok=0;if(ok){memcpy(pos[np],R[k],32);np++;}}
 if(nR!=240||np!=120)return 1;
 for(int t=0;t<120;t++){int l=256;for(int j=0;j<8;j++)l|=(pos[t][j]&1)<<j;lab[t]=l;}
 M2 off={0,0};for(int t=0;t<120;t++)if(pos[t][HT-1]!=0){if(t<64)off.a|=1ULL<<t;else off.b|=1ULL<<(t-64);}
 M2*all=malloc(sizeof(M2)*130000);int na=0;
 for(int f=1;f<512;f++)for(int g=f+1;g<512;g++){M2 m={0,0};for(int t=0;t<120;t++)if(!__builtin_parity(f&lab[t])&&!__builtin_parity(g&lab[t])){if(t<64)m.a|=1ULL<<t;else m.b|=1ULL<<(t-64);}all[na++]=m;}
 qsort(all,na,sizeof(M2),cmp);M2*mk=malloc(sizeof(M2)*130000);int nm=0;for(int i=0;i<na;i++)if(i==0||cmp(&all[i],&all[i-1]))mk[nm++]=all[i];
 int k=0;for(int i=0;i<nm;i++){int dom=0;for(int j=0;j<nm&&!dom;j++)if(j!=i&&(mk[i].a&~mk[j].a)==0&&(mk[i].b&~mk[j].b)==0)dom=1;if(!dom)mk[k++]=mk[i];}nm=k;
 fprintf(stderr,"HT=%d |Off|=%d maximal masks %d cap %d\n",HT,popc(off),nm,cap);
 long long npair=0,ncov=0;int minl=999;
 for(int i=0;i<nm;i++){M2 r={off.a&~mk[i].a,off.b&~mk[i].b};for(int j=i;j<nm;j++){M2 q={r.a&~mk[j].a,r.b&~mk[j].b};int c=popc(q);if(c<minl)minl=c;if(c>cap||c>lmax)continue;npair++;
   ns=0;for(int t=0;t<120;t++)if((t<64?q.a>>t:q.b>>(t-64))&1)sl[ns++]=lab[t];
   if(coverable()){ncov++;if(ncov<=1){printf("COVER i=%d j=%d left=%d lines:",i,j,c);for(int t=0;t<120;t++)if((t<64?q.a>>t:q.b>>(t-64))&1)printf(" %d",t);printf("\n labels/slot:");for(int z=0;z<ns;z++)printf(" %d:%d",sl[z],asg[z]);printf("\n");fflush(stdout);}if(stop)goto done;}}}
 done:printf("B HT=%d dims=%s cap=%d: pairs leftover<=cap %lld, coverable %lld, min leftover %d (masks %d)\n",HT,argv[2],cap,npair,ncov,minl,nm);}
