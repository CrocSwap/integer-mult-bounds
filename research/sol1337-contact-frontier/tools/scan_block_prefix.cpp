// Apache-2.0; substantial OpenAI Codex assistance. Immutable coherent-group cut.
#define main retained_discovery_main
#include "../vendor/dynamic_neighbors.cpp"
#undef main
#include <queue>
#include <iomanip>
#include <map>
struct FlowEdge {int to,rev;long long cap,initial;bool forward;};
struct Flow{
 int n;std::vector<std::vector<FlowEdge>> g;std::vector<int> level,it;
 Flow(int n):n(n),g(n),level(n),it(n){}
 void add(int a,int b,long long c){FlowEdge x{b,(int)g[b].size(),c,c,true},y{a,(int)g[a].size(),0,0,false};g[a].push_back(x);g[b].push_back(y);}
 long long dfs(int u,int t,long long f){if(u==t)return f;for(int&i=it[u];i<(int)g[u].size();i++){auto&e=g[u][i];if(e.cap>0&&level[e.to]==level[u]+1){long long z=dfs(e.to,t,std::min(f,e.cap));if(z>0){e.cap-=z;g[e.to][e.rev].cap+=z;return z;}}}return 0;}
 long long maxflow(int s,int t){long long total=0;for(;;){std::fill(level.begin(),level.end(),-1);std::queue<int>q;q.push(s);level[s]=0;while(!q.empty()){int u=q.front();q.pop();for(auto&e:g[u])if(e.cap>0&&level[e.to]<0){level[e.to]=level[u]+1;q.push(e.to);}}if(level[t]<0)break;std::fill(it.begin(),it.end(),0);while(long long z=dfs(s,t,1000000))total+=z;}return total;}
 void check(int s,int t,long long value){std::vector<long long>balance(n);for(int u=0;u<n;u++)for(auto&e:g[u])if(e.forward){long long f=e.initial-e.cap;if(f<0||f>e.initial)throw 21;balance[u]-=f;balance[e.to]+=f;}for(int i=0;i<n;i++)if(balance[i]!=(i==s?-value:(i==t?value:0)))throw 22;}
 bool unique_empty(int sink,int k){std::vector<std::vector<int>>rev(n);for(int u=0;u<n;u++)for(auto&e:g[u])if(e.cap>0)rev[e.to].push_back(u);std::vector<int>seen(n);seen[sink]=1;std::queue<int>q;q.push(sink);while(!q.empty()){int u=q.front();q.pop();for(auto v:rev[u])if(!seen[v]){seen[v]=1;q.push(v);}}for(int i=0;i<k;i++)if(!seen[i])return false;return true;}
 std::vector<int> chosen(int s){std::vector<int>seen(n);seen[s]=1;std::queue<int>q;q.push(s);while(!q.empty()){int u=q.front();q.pop();for(auto&e:g[u])if(e.cap>0&&!seen[e.to]){seen[e.to]=1;q.push(e.to);}}return seen;}
};
int main(int argc,char**argv){if(argc!=3)return 2;std::ifstream in(argv[1]);int n,f,m,e;in>>n>>f>>m>>e;std::vector<int> frame(n),fixed(n);for(int i=0;i<n;i++)in>>frame[i]>>fixed[i];std::vector<V> fs(f,V(9)),maps(m,V(18));for(auto&b:fs)for(auto&x:b)in>>x;for(auto&b:maps)for(auto&x:b)in>>x;std::vector<Edge>edges(e);for(auto&t:edges)in>>t.a>>t.b>>t.r>>t.sign>>t.map;if(!in)return 3;
 std::map<int,V>groups;for(int i=0;i<n;i++)if(!fixed[i])groups[frame[i]].push_back(i);
int cases=0,negative=0;long long best=0;V bestchosen;unsigned bestaxis=0;
 std::ofstream out(argv[2]);out<<std::setprecision(17)<<"{\"scope\":\"all1022 coherent alternatives for176variableempty-chart contacts andall9 concaveprefix tariffs; exact integerbinarycut\",\"cases\":[";bool first=true;
 for(auto&[fr,group]:groups)if(group.size()>1){std::vector<int> index(n,-1);for(unsigned j=0;j<group.size();j++)index[group[j]]=j;
 for(auto axis:canonical_transvection_axes(fs[fr]))for(int prefix=1;prefix<=9;prefix++){V changed=fs[fr];turn(changed,axis);int k=group.size(),source=k,sink=k+1;Flow flow(k+2);std::vector<long long> unary(k);std::vector<std::array<int,10>> rank_unary(k);
 for(const auto&t:edges){int a=index[t.a],b=index[t.b];if(a<0&&b<0)continue;if(a>=0&&b>=0){if(t.map||t.r)throw 4;flow.add(a,b,1);flow.add(b,a,1);}else{int node=a>=0?a:b;V both=map(maps[t.map],a>=0?changed:fs[frame[t.a]]);const V& right=b>=0?changed:fs[frame[t.b]];both.insert(both.end(),right.begin(),right.end());int r=(int)basis(both).size()-9;unary[node]+=std::min(r,prefix)-std::min(t.r,prefix);rank_unary[node][r]++;rank_unary[node][t.r]--;}}
 long long offset=0;for(int i=0;i<k;i++){if(unary[i]<0){flow.add(source,i,-unary[i]);offset+=unary[i];}else flow.add(i,sink,unary[i]);}
 long long maximum=flow.maxflow(source,sink);flow.check(source,sink,maximum);long long value=maximum+offset;auto chosen=flow.chosen(source);long long cut=0;for(int u=0;u<flow.n;u++)if(chosen[u])for(auto&e:flow.g[u])if(e.forward&&!chosen[e.to])cut+=e.initial;if(cut!=maximum)throw 23;bool unique=flow.unique_empty(sink,k);V selection;for(int i=0;i<k;i++)if(chosen[i])selection.push_back(group[i]);cases++;if(value< -0){negative++;if(value<best){best=value;bestchosen=selection;bestaxis=axis;}}
 if(!first)out<<',';first=false;out<<"["<<fr<<","<<axis<<","<<prefix<<","<<value<<","<<selection.size()<<","<<int(unique)<<"]";
 }}out<<"],\"negative\":"<<negative<<",\"best_integer_delta\":"<<best<<",\"best_axis\":"<<bestaxis<<",\"best_selection\":[";for(unsigned i=0;i<bestchosen.size();i++)out<<(i?",":"")<<bestchosen[i];out<<"]}\n";std::cout<<"cases="<<cases<<" negative="<<negative<<" best="<<best<<" size="<<bestchosen.size()<<"\n";}
