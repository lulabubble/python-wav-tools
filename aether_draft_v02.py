import numpy as np,wave,os
S=44100;N=lambda d:int(S*d)
def L(n,d=0.001,s=10,r=28,b=8/3):
 x,y,z=0.1,0,0;dt=d;spm=max(1,int(1/(S*dt)));np_=n*spm
 lx,ly,lz=np.zeros(np_),np.zeros(np_),np.zeros(np_)
 for i in range(np_):
  lx[i],ly[i],lz[i]=x,y,z;dx,dy,dz=s*(y-x),x*(r-z)-y,x*y-b*z
  x,y,z=x+dx*dt,y+dy*dt,z+dz*dt
 return lx[::spm][:n],ly[::spm][:n],lz[::spm][:n]
def W(r):
 H=np.array([[1,1,1,1,1,1,1,1],[1,-1,1,-1,1,-1,1,-1],[1,1,-1,-1,1,1,-1,-1],[1,-1,-1,1,1,-1,-1,1],[1,1,1,1,-1,-1,-1,-1],[1,-1,1,-1,-1,1,-1,1],[1,1,-1,-1,-1,-1,1,1],[1,-1,-1,1,-1,1,1,-1]])
 return(H[r%8]+1)//2
def F(s,f1,f2,f3):
 def f(sig,fc,bw):
  r,c=np.exp(-np.pi*bw/S),np.cos(2*np.pi*fc/S);y1,y2,o=0.,0.,np.zeros_like(sig)
  for i in range(len(sig)):y0=(1-r)*sig[i]+2*r*c*y1-r*r*y2;o[i],y2,y1=y0,y1,y0
  return o
 return f(f(f(s,f1,90),f2,130),f3,200)
def V(dur,f0,fm,asp=0):
 n=N(dur);t=np.arange(n)/S;f=f0*(1+0.06*np.sin(2*np.pi*fm*t))
 ph=np.cumsum(2*np.pi*f/S)
 return(np.sin(ph)+0.4*np.sin(2*ph)+0.15*np.sin(3*ph))*(1+asp*np.random.randn(n))
def E(sig,a=0.02,r=0.03):
 n=len(sig);w=np.ones(n);at,rt=int(S*a),int(S*r)
 if at:w[:at]=np.linspace(0,1,at)**2
 if rt and n-rt>at:w[-rt:]=np.linspace(1,0,rt)**2
 return sig*w
def D(sig,dlys,decs):
 o=sig.copy()
 for d,dec in zip(dlys,decs):
  if d<len(sig):o[d:]+=sig[:-d]*dec
 return o
def M(L,R):
 s=np.column_stack((L,R));s-=np.mean(s,0)
 pk=np.max(np.abs(s))
 if pk:s/=pk/0.92
 return np.tanh(s*1.2)*0.95
def Wf(path,L,R):
 p=path if os.path.isdir("/storage/emulated/0/Download")else f"/mnt/agents/output/{os.path.basename(path)}"
 try:os.makedirs(os.path.dirname(p),exist_ok=True)
 except PermissionError:pass
 with wave.open(p,'wb')as w:
  w.setnchannels(2);w.setsampwidth(2);w.setframerate(S)
  a=(M(L,R)*32767).astype(np.int16);w.writeframes(a.tobytes())
 print(f"Saved:{p}")
