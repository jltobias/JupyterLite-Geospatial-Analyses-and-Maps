
from pathlib import Path
import json, math
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from IPython.display import HTML, display

DATA_CREDITS = {
    'admin_boundaries': 'Synthetic teaching layer; workflow inspired by GADM administrative boundaries. GADM data are not bundled.',
    'osm_roads': 'Synthetic teaching layer; workflow inspired by OpenStreetMap/Geofabrik extracts. OSM data are not bundled.',
    'health_facilities': 'Synthetic teaching layer; workflow inspired by healthsites.io health facility mapping. Healthsites data are not bundled.',
}

def _root():
    cwd=Path.cwd()
    for p in [cwd,*cwd.parents]:
        if (p/'data').exists(): return p
    return cwd

def load_dataset(name):
    return pd.read_csv(_root()/'data'/name)

def load_geojson(name):
    p=_root()/'data'/name
    with open(p, encoding='utf-8') as f: return json.load(f)

def quick_summary(df):
    print(f'Rows: {len(df):,} | Columns: {len(df.columns)}')
    display(df.head())
    nums=df.select_dtypes(include='number')
    if len(nums.columns): display(nums.describe().T[['mean','std','min','max']].round(2))

def haversine(lon1,lat1,lon2,lat2):
    R=6371.0088
    lon1,lat1,lon2,lat2=map(np.radians,[lon1,lat1,lon2,lat2])
    dlon=lon2-lon1; dlat=lat2-lat1
    a=np.sin(dlat/2)**2 + np.cos(lat1)*np.cos(lat2)*np.sin(dlon/2)**2
    return 2*R*np.arcsin(np.sqrt(a))

def _polygon_xy(feature):
    coords=feature['geometry']['coordinates'][0]
    return [p[0] for p in coords], [p[1] for p in coords]

def map_boundaries(title='Administrative boundary map'):
    g=load_geojson('admin_boundaries.geojson')
    fig, ax=plt.subplots(figsize=(8,5.5))
    for f in g['features']:
        xs,ys=_polygon_xy(f)
        ax.fill(xs,ys,alpha=.35,edgecolor='black',linewidth=1)
        cx=sum(xs[:-1])/len(xs[:-1]); cy=sum(ys[:-1])/len(ys[:-1])
        ax.text(cx,cy,f['properties']['id'],ha='center',va='center',fontsize=8)
    ax.set_title(title); ax.set_xlabel('longitude'); ax.set_ylabel('latitude'); ax.grid(True,alpha=.2)
    plt.show()

def map_choropleth(value='rate_per_10k', title='Boundary choropleth'):
    g=load_geojson('admin_boundaries.geojson')
    vals=np.array([f['properties'].get(value,0) for f in g['features']], dtype=float)
    lo,hi=vals.min(), vals.max()
    fig, ax=plt.subplots(figsize=(8,5.5))
    for f,v in zip(g['features'],vals):
        xs,ys=_polygon_xy(f)
        shade=(v-lo)/(hi-lo+1e-9)
        ax.fill(xs,ys,alpha=.55+shade*.35,edgecolor='black',linewidth=1)
        ax.text(sum(xs[:-1])/len(xs[:-1]),sum(ys[:-1])/len(ys[:-1]),str(round(v,1)),ha='center',va='center',fontsize=8)
    ax.set_title(title+' — '+value); ax.set_xlabel('longitude'); ax.set_ylabel('latitude'); ax.grid(True,alpha=.2)
    plt.show()

def map_points(df, lon='lon', lat='lat', color=None, title='Point map', size=45):
    map_boundaries(title='Context boundaries')
    fig, ax=plt.subplots(figsize=(8,5.5))
    g=load_geojson('admin_boundaries.geojson')
    for f in g['features']:
        xs,ys=_polygon_xy(f); ax.fill(xs,ys,alpha=.15,edgecolor='gray',linewidth=.8)
    if color and color in df.columns:
        sc=ax.scatter(df[lon],df[lat],c=df[color],s=size,alpha=.78,edgecolors='black',linewidths=.3)
        fig.colorbar(sc, ax=ax, label=color)
    else:
        ax.scatter(df[lon],df[lat],s=size,alpha=.78,edgecolors='black',linewidths=.3)
    ax.set_title(title); ax.set_xlabel('longitude'); ax.set_ylabel('latitude'); ax.grid(True,alpha=.2)
    plt.show()

def map_lines(title='Road/network map'):
    roads=load_geojson('osm_roads.geojson')
    fig, ax=plt.subplots(figsize=(8,5.5))
    for f in load_geojson('admin_boundaries.geojson')['features']:
        xs,ys=_polygon_xy(f); ax.fill(xs,ys,alpha=.12,edgecolor='gray')
    for r in roads['features']:
        xs=[p[0] for p in r['geometry']['coordinates']]; ys=[p[1] for p in r['geometry']['coordinates']]
        ax.plot(xs,ys,linewidth=2 if r['properties']['class']=='primary' else 1,alpha=.8)
    ax.set_title(title); ax.set_xlabel('longitude'); ax.set_ylabel('latitude'); ax.grid(True,alpha=.2)
    plt.show()

def map_grid(df, value='elevation_m', title='Raster-like grid map'):
    xcol='x' if 'x' in df.columns else None
    ycol='y' if 'y' in df.columns else None
    if xcol and ycol:
        arr=df.pivot_table(index='y', columns='x', values=value).sort_index(ascending=False)
        fig, ax=plt.subplots(figsize=(8,5.5)); im=ax.imshow(arr.values, aspect='auto')
        fig.colorbar(im, ax=ax, label=value); ax.set_title(title); ax.set_xlabel('grid x'); ax.set_ylabel('grid y'); plt.show()
    else:
        map_points(df, color=value, title=title)

def interactive_leaflet(df=None, lon='lon', lat='lat', label='id', title='Interactive map'):
    g=json.dumps(load_geojson('admin_boundaries.geojson'))
    if df is None:
        df=load_dataset('health_facilities.csv')
    pts=df[[lon,lat]].copy()
    pts['label']=df[label].astype(str) if label in df.columns else [f'point {i}' for i in range(len(df))]
    records=pts.dropna().head(250).to_dict('records')
    center=[float(pts[lat].mean()), float(pts[lon].mean())]
    map_id='map_'+str(abs(hash(str(records)+title))%100000000)
    html=f"""
    <div style="font-weight:600;margin:4px 0">{title}</div>
    <div id="{map_id}" style="height:420px;border:1px solid #aaa;border-radius:8px"></div>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <script>
    (function(){{
      const map = L.map('{map_id}').setView({center}, 9);
      L.tileLayer('https://tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{maxZoom:19, attribution:'&copy; OpenStreetMap contributors'}}).addTo(map);
      const boundary={g};
      L.geoJSON(boundary, {{style:{{color:'#334155',weight:1,fillOpacity:0.08}}}}).addTo(map);
      const pts={json.dumps(records)};
      pts.forEach(p => L.circleMarker([p['{lat}'], p['{lon}']], {{radius:5, color:'#b91c1c', fillOpacity:0.75}}).bindPopup(String(p.label)).addTo(map));
    }})();
    </script>"""
    display(HTML(html))

def classify_quantiles(s, k=5):
    return pd.qcut(s.rank(method='first'), k, labels=[f'Q{i}' for i in range(1,k+1)])

def nearest_join(left, right, lon='lon', lat='lat'):
    out=[]
    for _,r in left.iterrows():
        d=haversine(r[lon],r[lat],right[lon].to_numpy(),right[lat].to_numpy())
        j=int(np.argmin(d)); rr=right.iloc[j].to_dict()
        out.append({**r.to_dict(), 'nearest_id': rr.get('id', rr.get('site', rr.get('county','target'))), 'distance_km': float(d[j])})
    return pd.DataFrame(out)

def idw(points, value, grid_lon, grid_lat, power=2):
    vals=[]
    for lo,la in zip(grid_lon,grid_lat):
        d=haversine(lo,la,points['lon'].to_numpy(),points['lat'].to_numpy())
        d=np.maximum(d, .001); w=1/(d**power)
        vals.append(float((w*points[value].to_numpy()).sum()/w.sum()))
    return np.array(vals)

def simple_kmeans(df, cols, k=3, n_iter=20):
    X=df[cols].to_numpy(dtype=float); X=(X-X.mean(axis=0))/(X.std(axis=0)+1e-9)
    centers=X[np.linspace(0,len(X)-1,k,dtype=int)].copy()
    for _ in range(n_iter):
        labels=((X[:,None,:]-centers[None,:,:])**2).sum(axis=2).argmin(axis=1)
        for j in range(k):
            if (labels==j).any(): centers[j]=X[labels==j].mean(axis=0)
    return labels

def morans_i(df, value, lon='lon', lat='lat', threshold_km=35):
    x=df[value].to_numpy(dtype=float); z=x-x.mean(); n=len(x); num=0.0; wsum=0.0
    for i in range(n):
        d=haversine(df.iloc[i][lon],df.iloc[i][lat],df[lon].to_numpy(),df[lat].to_numpy())
        w=((d>0)&(d<threshold_km)).astype(float); num+=(w*z[i]*z).sum(); wsum+=w.sum()
    return (n/wsum)*num/(z*z).sum() if wsum else np.nan
