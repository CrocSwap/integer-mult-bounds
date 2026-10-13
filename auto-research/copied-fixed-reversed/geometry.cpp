// Complete exact finite-field witness for PR34 data prefixes with L25=I+J.
// Nonzero residues certify nonzero rational minors; this is not CRT rank recovery.
#include <cstdint>
#include <iostream>
#include <vector>
using namespace std;
constexpr int q=1000003,a=23,b=25,d=a+b-1;
int mul(int x,int y){return int(int64_t(x)*y%q);}
int power(int x,int n){int z=1;for(;n;n>>=1,x=mul(x,x))if(n&1)z=mul(z,x);return z;}
int main(){
 for(int i=2;i*i<=q;++i)if(q%i==0)return 10;
 vector<int> R,C,piv;
 for(int i=0;i<a;i++)R.push_back(i),C.push_back(i);
 R.push_back(a-1);C.push_back(0);
 for(int i=0;i<a;i++)R.push_back(i),C.push_back(i);
 piv.push_back(2*a);
 for(int i=1;i<a-1;i++)piv.push_back(i+a+1);
 for(int i=a-1;i<a+5;i++)piv.push_back(2*a-i);
 for(int i=a+5;i<2*a-1;i++)piv.push_back(i-a-3);
 piv.push_back(1);piv.push_back(0);
 int xs[a],sum=0;for(int i=1;i<=a;i++)sum+=i*i;
 for(int i=0;i<a;i++)xs[i]=mul(sum,power((i+1)*(i+1),q-2));
 int count=0;int64_t checked=0,zeros=0;
 cout<<"{\"prime\":"<<q<<",\"records\":[\n";
 for(int u=0;u<b;u++)for(int v=u+1;v<b;v++)for(int w=v+1;w<b;w++){
  int ys[b],M[d][d];bool available[d];
  for(int i=0;i<b;i++)ys[i]=(i==u||i==v||i==w)?mul(3*(b+1),power(2*(3*(b+1)-10),q-2)):q-mul(b+1,power(5,q-2));
  for(int i=0;i<d;i++){available[i]=true;for(int j=0;j<d;j++){
   int z=q-1;if(R[i]==C[j])z+=xs[R[i]];if(i%b==(a*b-d+j)%b)z+=ys[i%b];M[i][j]=z%q;
  }}
  int determinant=1;
  for(int i=0;i<d;i++){
   int c=piv[i],value=M[i][c];if(!available[c]||!value){cerr<<"zero pivot "<<u<<","<<v<<","<<w<<" row "<<i<<"\n";return 1;}
   for(int j=c+1;j<d;j++)if(available[j]){if(M[i][j]){cerr<<"ordered zero failed\n";return 2;}zeros++;}
   determinant=mul(determinant,value);checked++;available[c]=false;
   int inv=power(value,q-2);
   for(int r=i+1;r<d;r++)if(M[r][c]){
    int ratio=mul(M[r][c],inv);
    for(int j=0;j<d;j++)if(available[j]&&M[i][j]){int z=M[r][j]-mul(ratio,M[i][j]);M[r][j]=z<0?z+q:z;}
    M[r][c]=0;
   }
  }
  if(count++)cout<<",\n";cout<<"["<<u<<","<<v<<","<<w<<","<<determinant<<"]";
 }
 cout<<"\n],\"triple_count\":"<<count<<",\"nonzero_pivots\":"<<checked<<",\"ordered_zero_checks\":"<<zeros<<"}\n";
 return count==b*(b-1)*(b-2)/6?0:3;
}
