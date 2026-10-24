// Exact integer flow routines retained from PR4867, substantial OpenAI Codex assistance. Apache-2.0.
struct FlowEdge {int to,rev;long long cap,initial;bool forward;};
struct Flow{
 int n;std::vector<std::vector<FlowEdge>> g;std::vector<int> level,it;
 Flow(int n):n(n),g(n),level(n),it(n){}
 void add(int a,int b,long long c){FlowEdge x{b,(int)g[b].size(),c,c,true},y{a,(int)g[a].size(),0,0,false};g[a].push_back(x);g[b].push_back(y);}
 long long dfs(int u,int t,long long f){if(u==t)return f;for(int&i=it[u];i<(int)g[u].size();i++){auto&e=g[u][i];if(e.cap>0&&level[e.to]==level[u]+1){long long z=dfs(e.to,t,std::min(f,e.cap));if(z>0){e.cap-=z;g[e.to][e.rev].cap+=z;return z;}}}return 0;}
 long long maxflow(int s,int t){long long total=0;for(;;){std::fill(level.begin(),level.end(),-1);std::queue<int>q;q.push(s);level[s]=0;while(!q.empty()){int u=q.front();q.pop();for(auto&e:g[u])if(e.cap>0&&level[e.to]<0){level[e.to]=level[u]+1;q.push(e.to);}}if(level[t]<0)break;std::fill(it.begin(),it.end(),0);while(long long z=dfs(s,t,1000000000000000LL))total+=z;}return total;}
 void check(int s,int t,long long value){std::vector<long long>balance(n);for(int u=0;u<n;u++)for(auto&e:g[u])if(e.forward){long long f=e.initial-e.cap;if(f<0||f>e.initial)throw 21;balance[u]-=f;balance[e.to]+=f;}for(int i=0;i<n;i++)if(balance[i]!=(i==s?-value:(i==t?value:0)))throw 22;}
 bool unique_empty(int sink,int k){std::vector<std::vector<int>>rev(n);for(int u=0;u<n;u++)for(auto&e:g[u])if(e.cap>0)rev[e.to].push_back(u);std::vector<int>seen(n);seen[sink]=1;std::queue<int>q;q.push(sink);while(!q.empty()){int u=q.front();q.pop();for(auto v:rev[u])if(!seen[v]){seen[v]=1;q.push(v);}}for(int i=0;i<k;i++)if(!seen[i])return false;return true;}
 std::vector<int> chosen(int s){std::vector<int>seen(n);seen[s]=1;std::queue<int>q;q.push(s);while(!q.empty()){int u=q.front();q.pop();for(auto&e:g[u])if(e.cap>0&&!seen[e.to]){seen[e.to]=1;q.push(e.to);}}return seen;}
};
