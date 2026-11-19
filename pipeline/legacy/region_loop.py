# Prototype kept for reference: loops each person separately (used for the first cafe loop).
# Usage: python region_loop.py SRC.mp4 BLEND OUT_video.mp4 regions.json [ids-to-ping-pong]
# regions.json maps a region name to a polygon [[x,y],...] in 1920x1080 pixels. Audio is not handled here.
import subprocess, numpy as np, cv2, sys, json
src=sys.argv[1]; K=int(sys.argv[2]); out=sys.argv[3]
W,H=1920,1080
fr=np.frombuffer(subprocess.run(["ffmpeg","-v","error","-i",src,"-f","rawvideo","-pix_fmt","rgb24","-"],capture_output=True).stdout,np.uint8).reshape(-1,H,W,3)
n=len(fr)
def poly(pts):
    m=np.zeros((H,W),np.float32); cv2.fillPoly(m,[np.array(pts,np.int32)],1.0); return m
regions={k:poly(v) for k,v in json.load(open(sys.argv[4])).items()}
for k in regions: regions[k]=cv2.GaussianBlur(regions[k],(0,0),12)
# low-res gray for search
small=np.stack([cv2.resize(cv2.cvtColor(f,cv2.COLOR_RGB2GRAY),(192,108),interpolation=cv2.INTER_AREA) for f in fr]).astype(np.float32)
sm={k:cv2.resize(v,(192,108))>0.5 for k,v in regions.items()}
bgm=np.ones((108,192),bool)
for v in sm.values(): bgm&=~v
sm["bg"]=bgm
def cost(mask,s,L):
    return np.abs(small[s+L-K-1]-small[s])[mask].mean()
best=None
for L in range(120,n-K+1,4):
    tot=0; ss={}
    for name,m in sm.items():
        c,s=min((cost(m,s,L),s) for s in range(K,n-L+1,2)); ss[name]=(s,round(c,2)); tot+=c
    if best is None or tot<best[0]: best=(tot,L,ss)
tot,L,ss=best
print("loop length",L,"frames =",round(L/24,2),"s; per-region start & seam cost:",ss)
dis=cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM)
gx,gy=np.meshgrid(np.arange(W,dtype=np.float32),np.arange(H,dtype=np.float32))
cache={}
def flows(s):
    if s not in cache:
        A=fr[s+L-K-1]; B=fr[s]
        ga=cv2.cvtColor(A,cv2.COLOR_RGB2GRAY); gb=cv2.cvtColor(B,cv2.COLOR_RGB2GRAY)
        cache[s]=(A,B,dis.calc(ga,gb,None),dis.calc(gb,ga,None))
    return cache[s]
PING=set(sys.argv[5].split(',')) if len(sys.argv)>5 else set()
def pseq(s,t):
    h=L//2; i=t if t<=h else L-t
    return fr[s+i].astype(np.float32)
def seq(s,t):
    k=t-(L-K)
    if k<0: return fr[s+t].astype(np.float32)
    A,B,fab,fba=flows(s); a=(k+1)/(K+1)
    Aw=cv2.remap(A,gx-a*fba[...,0],gy-a*fba[...,1],cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT).astype(np.float32)
    Bw=cv2.remap(B,gx-(1-a)*fab[...,0],gy-(1-a)*fab[...,1],cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT).astype(np.float32)
    w=a*a*(3-2*a)
    return Aw*(1-w)+Bw*w
PS={}
for k in PING:
    h=L//2; PS[k]=max(range(0,n-h),key=lambda s0: sum(np.abs(small[s0+i]-small[s0+i-1])[sm[k]].mean() for i in range(1,h+1)))
print('pingpong starts',PS)
masks={k:v[...,None] for k,v in regions.items()}
total=sum(masks.values()); bgw=np.clip(1-total,0,1)
p=subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r","24","-i","-","-c:v","libx264","-preset","veryfast","-crf","16","-pix_fmt","yuv420p",out],stdin=subprocess.PIPE)
for t in range(L):
    o=seq(ss["bg"][0],t)*bgw
    for k,m in masks.items(): o+=(pseq(PS[k],t) if k in PING else seq(ss[k][0],t))*m
    p.stdin.write(np.clip(o/(bgw+total),0,255).astype(np.uint8).tobytes())
p.stdin.close(); p.wait()
json.dump({"L":L,"starts":{k:v[0] for k,v in ss.items()}},open(out+".json","w"))
