import json, math, os
G = os.path.dirname(os.path.abspath(__file__))
def utm_inv(E, N, zone=42):
    a=6378137.0; f=1/298.257223563; k0=0.9996; e2=f*(2-f); ep2=e2/(1-e2)
    x=E-500000.0; y=N; M=y/k0; mu=M/(a*(1-e2/4-3*e2**2/64-5*e2**3/256))
    e1=(1-math.sqrt(1-e2))/(1+math.sqrt(1-e2))
    p1=mu+(3*e1/2-27*e1**3/32)*math.sin(2*mu)+(21*e1**2/16-55*e1**4/32)*math.sin(4*mu)+(151*e1**3/96)*math.sin(6*mu)
    N1=a/math.sqrt(1-e2*math.sin(p1)**2); T1=math.tan(p1)**2; C1=ep2*math.cos(p1)**2; R1=a*(1-e2)/(1-e2*math.sin(p1)**2)**1.5; D=x/(N1*k0)
    lat=p1-(N1*math.tan(p1)/R1)*(D**2/2-(5+3*T1+10*C1-4*C1**2-9*ep2)*D**4/24+(61+90*T1+298*C1+45*T1**2-252*ep2-3*C1**2)*D**6/720)
    lon=(D-(1+2*T1+C1)*D**3/6+(5-2*C1+28*T1-3*C1**2+8*ep2+24*T1**2)*D**5/120)/math.cos(p1)
    return math.degrees(lon)+(zone-1)*6-180+3, math.degrees(lat)
def hc_to_ll(x, y, tr, sy=1):
    E=(x-tr['jsonmarginX'])/tr['jsonres']/tr['scale']+tr['xoffset']
    N=tr['yoffset']-(-y+tr['jsonmarginY'])/tr['jsonres']/tr['scale']
    return utm_inv(E, N)
def provinces(sy=1):
    d=json.load(open(os.path.join(G,'pk-all.geo.json'))); tr=d['hc-transform']['default']; out={}
    for f in d['features']:
        g=f['geometry']; polys=g['coordinates'] if g['type']=='MultiPolygon' else [g['coordinates']]
        out.setdefault(f['properties']['name'],[]).extend([[hc_to_ll(x,y,tr,sy) for x,y in poly[0]] for poly in polys])
    return out
def topo_countries(names):
    d=json.load(open(os.path.join(G,'world50.json'))); sc=d['transform']['scale']; tl=d['transform']['translate']
    arcs=[]
    for arc in d['arcs']:
        x=y=0; pts=[]
        for dx,dy in arc: x+=dx; y+=dy; pts.append((x*sc[0]+tl[0], y*sc[1]+tl[1]))
        arcs.append(pts)
    def ring(r):
        pts=[]
        for i in r:
            a=arcs[i] if i>=0 else arcs[~i][::-1]
            pts.extend(a if not pts else a[1:])
        return pts
    out={}
    for g in d['objects']['countries']['geometries']:
        n=g['properties'].get('name')
        if n not in names: continue
        polys=g['arcs'] if g['type']=='MultiPolygon' else [g['arcs']]
        out[n]=[ring(p[0]) for p in polys]
    return out
if __name__=='__main__':
    for sy in (1,-1):
        p=provinces(sy); xs=[pt for poly in p['Sind'] for pt in poly]
        print(sy, min(x for x,_ in xs),max(x for x,_ in xs),min(y for _,y in xs),max(y for _,y in xs))
    c=topo_countries({'Pakistan','Afghanistan'}); print({k:len(v) for k,v in c.items()})
