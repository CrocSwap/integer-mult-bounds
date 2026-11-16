// impl A: for each W(E8)-orbit rep A of 7-flat masks and every 7-flat B: qualifying candidates h (root / A2-plane generic / E6A1 dir)
// with F2-rank(labels(Off(h) \ (A|B))) <= 7; report max Q-rank of span of qualifying vectors (A2 plane contributes 2 vectors).
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef unsigned __int128 u128; typedef long long ll;
int lab[120];
static u128 M[44000]; int nm,nr,nc; int rep[64]; u128 OFF[5000]; int nv[5000]; ll V[5000][2][8];
int pc(u128 x){return __builtin_popcountll((unsigned long long)x)+__builtin_popcountll((unsigned long long)(x>>64));}
int rk(u128 x){int b[9],nb=0; for(int t=0;t<120;t++) if((x>>t)&1){int v=lab[t]; for(int i=0;i<nb;i++){int w=v^b[i]; if(w<v)v=w;} if(v){if(nb==8) return 9; b[nb++]=v; for(int i=nb-1;i>0&&b[i]>b[i-1];i--){int s=b[i];b[i]=b[i-1];b[i-1]=s;}}} return nb;}
ll gcdl(ll a,ll b){if(a<0)a=-a;if(b<0)b=-b;while(b){ll t=a%b;a=b;b=t;}return a;}
ll Bs[8][8]; int piv[8]; int nb;
int addv(ll*v0){ll v[8]; memcpy(v,v0,sizeof v);
 for(int i=0;i<nb;i++){int p=piv[i]; if(v[p]){ll a=Bs[i][p],c=v[p]; ll g=0; for(int k=0;k<8;k++){v[k]=a*v[k]-c*Bs[i][k]; g=gcdl(g,v[k]);} if(g>1) for(int k=0;k<8;k++) v[k]/=g;}}
 int p=-1; for(int k=0;k<8;k++) if(v[k]){p=k;break;} if(p<0) return 0; memcpy(Bs[nb],v,sizeof v); piv[nb++]=p; return 1;}
void hexin(FILE*f,u128*x){char s[64]; fscanf(f,"%s",s); u128 r=0; for(char*c=s;*c;c++){int d=(*c<='9')?*c-'0':*c-'a'+10; r=r*16+d;} *x=r;}
int main(int argc,char**argv){
 FILE*f=fopen("ka.in","r"); fscanf(f,"%d %d %d",&nm,&nr,&nc); for(int i=0;i<nm;i++) hexin(f,&M[i]); for(int i=0;i<nr;i++) fscanf(f,"%d",&rep[i]);
 for(int i=0;i<nc;i++){hexin(f,&OFF[i]); fscanf(f,"%d",&nv[i]); for(int j=0;j<nv[i];j++) for(int k=0;k<8;k++) fscanf(f,"%lld",&V[i][j][k]);}
 FILE*g=fopen("lab.in","r"); for(int t=0;t<120;t++) fscanf(g,"%d",&lab[t]);
 long hist[10]={0}; static u128 Ucov[64];
 for(int r=0;r<nr;r++){u128 A=M[rep[r]]; int best=0; long cnt7=0,cnt8=0, nq=0; int bestB=-1;
  for(int b=0;b<nm;b++){u128 U=A|M[b]; nb=0; int nqb=0;
   for(int c=0;c<nc;c++){u128 L=OFF[c]&~U; if(pc(L)>36) continue; if(rk(L)>7) continue; nqb++; for(int j=0;j<nv[c];j++) addv(V[c][j]);}
   hist[nb]++; nq+=nqb; if(nb>best){best=nb;bestB=b;} if(nb>=7){cnt7++; u128 X=A|M[b]; printf("   B=%d |B|=%d same=%d |A&B|=%d span=%d nq=%d\n",b,pc(M[b]),b==rep[r],pc(A&M[b]),nb,nqb); Ucov[r]|=M[b];} if(nb>=8)cnt8++;}
  Ucov[r]|=A; printf("rep %d |A|=%d: |A u N7(A)|=%d max span %d (B=%d)  #B span>=7: %ld  >=8: %ld  total qualifying incidences %ld\n",rep[r],pc(A),pc(Ucov[r]),best,bestB,cnt7,cnt8,nq); fflush(stdout);}
 printf("span histogram over (rep,B):"); for(int i=0;i<10;i++) printf(" %d:%ld",i,hist[i]); printf("\n");
}
