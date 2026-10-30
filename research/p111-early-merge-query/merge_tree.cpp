#include <iostream>
#include <vector>
#include <array>
#include <limits>
using namespace std;
int main(){int n;if(!(cin>>n)||n>20)return 1;vector<array<int,9>> leaf(n);vector<int> lr(n);for(int i=0;i<n;i++){int k;cin>>k;lr[i]=k;for(int j=0;j<k;j++)cin>>leaf[i][j];}
int N=1<<n;vector<array<int,9>> bas(N);vector<int> rk(N),dp(N,1000000),split(N);dp[0]=0;
for(int s=1;s<N;s++){int bit=__builtin_ctz((unsigned)s),prev=s&(s-1);bas[s]=bas[prev];for(int a=0;a<lr[bit];a++){int x=leaf[bit][a];for(int j=8;j>=0;j--)if(x>>j&1){if(bas[s][j])x^=bas[s][j];else{bas[s][j]=x;break;}}}for(int x:bas[s])rk[s]+=x!=0;
if(!prev){dp[s]=0;continue;}int low=s&-s;for(int a=(s-1)&s;a;a=(a-1)&s){if(!(a&low))continue;int b=s^a;if(!b)continue;int c=dp[a]+dp[b]+rk[s];if(c<dp[s]){dp[s]=c;split[s]=a;}}}
cout<<"{\"leaves\":"<<n<<",\"union_rank\":"<<rk[N-1]<<",\"internal_rank_sum\":"<<dp[N-1]<<",\"tree\":[";vector<int> todo{N-1};bool first=true;while(!todo.empty()){int s=todo.back();todo.pop_back();if(!(s&(s-1)))continue;int a=split[s],b=s^a;if(!first)cout<<",";first=false;cout<<"["<<s<<","<<a<<","<<b<<","<<rk[s]<<"]";todo.push_back(b);todo.push_back(a);}cout<<"]}";
}
