#!/usr/bin/env python
# plot variables at restart file's lowest layers 

import sys, yaml
import matplotlib.pyplot as plt
import matplotlib.colors as colors
# import cartopy.crs as ccrs
# import cartopy.feature as cfeature
# from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
from datetime import datetime, timedelta
import xarray as xr
import numpy as np
import glob

if len(sys.argv) != 2:
  print('need input yaml')
  sys.exit(1)
with open(sys.argv[1], 'r') as stream:
   try:
     ainput=yaml.safe_load(stream)
   except yaml.YAMLError as exc:
     print(exc)
     
sp_gas=['co','so2','sulf','etha','o3','no2','no',
     'pan','panx','opan','hono','pna','no3','hno3','ntr1','ntr2',
     'intr','n2o5','eth','form','ald2','aldx','par','ole',
     'iole','h2o2','tol','xylmn','isop','ispd','nh3','terp','facd',
     'aacd','pacd','cres','mgly','meoh','etoh','mepx',
     'hcl','ethy','cl2','acet','ket','hocl','fmcl','benzene',
     'open','cron','clno2','gly','glyd','rooh']
sp_aero=['alvpo1i','asvpo1i','asvpo2i','apoci','apncomi',
     'alvpo1j','asvpo1j','asvpo2j','apocj','apncomj','asvpo3j','aivpo1j',
     'alvoo1i','alvoo2i','asvoo1i','asvoo2i',
     'alvoo1j','alvoo2j','asvoo1j','asvoo2j','aiso1j',
     'aiso2j','aiso3j','asqtj','aorgcj','aolgbj','aolgaj',
     'asvoo3j','apcsoj','aglyj','amtno3j','amthydj','aavb1j',
     'aavb2j','aavb3j','aavb4j','amt1j','amt2j','amt3j','amt4j','amt5j','amt6j',
     'aso4i','aso4j','aso4k','anh4i','anh4j','anh4k',
     'ano3i','ano3j','ano3k','anai','anaj','aseacat','acli','aclj',
     'aclk','aeci','aecj','aothri','aothrj','acors','asoil','acaj',
     'akj','afej','aalj','asij','atij','amnj','amgj']
     
tfmt=ainput['tfmt']
tstart=ainput['tstart']
tend=ainput['tend']
tstep=int(ainput['tstep'])
case=ainput['case_name']
figfolder=ainput['figfolder']
modnames=ainput['modnames']
locations=ainput['locations']
ceiling=ainput['ceiling']

## grid and profile locations
fgrid=xr.open_dataset(ainput['gridfile'])
im=fgrid['lon'].size
jm=fgrid['lat'].size
geolon=fgrid['geolon']
geolat=fgrid['geolat']

loc_names=[]
lats=[]
lons=[]
xs=[]
ys=[]
for a, (b, c) in locations.items():
  loc_names.append(a)
  lats.append(b)
  if c < 0:
   c=c+360
  lons.append(c)
# find the nearest grid points
  abs_diff_lat = np.abs(geolat - b)
  abs_diff_lon = np.abs(geolon - c)
  combined_diff = abs_diff_lat + abs_diff_lon
  min_diff_idx = np.unravel_index(np.argmin(combined_diff.values), combined_diff.shape)
  if min_diff_idx[0] > jm or min_diff_idx[1] > im:
    print('location is out of domain, lat,lon,x,y= ', b,c,min_diff_idx[0], min_diff_idx[1])
    sys.exit(1)
  xs.append(min_diff_idx[1])  
  ys.append(min_diff_idx[0])
  
  
## process the tracer and for files
tracer_file=sorted(glob.glob(ainput['filelist']))
nlines=len(tracer_file)
print('tracer_file=',tracer_file)

corefiles=sorted(glob.glob(ainput['corefiles']))
ncores=len(corefiles)
print('corefiles=',corefiles)

if nlines != ncores:
  print('inconsistent tracer file and core file lists ',tracer_file,corefiles)
  sys.exit(1)

stime={}
n=0
for aline,aline2 in zip(tracer_file,corefiles):
#  print('restartfile, corefile ',aline,aline2)
  itmp=aline.rindex('.fv_tracer')
  tstring1=aline[itmp-15:itmp]
  itmp2=aline2.rindex('.fv_core')
  tstring2=aline2[itmp2-15:itmp2]
  if tstring1 != tstring2 :
    print('inconsistent file time tag ',aline, aline2)
    sys.exit(1)
#  print('tstring1=',tstring1)
  stime[n]=datetime.strptime(tstring1,'%Y%m%d.%H%M%S')
  n=n+1
 
ftstart=datetime.strptime(tstart,tfmt)
ftend=datetime.strptime(tend,tfmt)

plt.figure(figsize=(7,12))

while ftstart <= ftend:

  for n in range(nlines):
    if ftstart == stime[n] :
      break
  if n >= nlines:
    print('can not find time range in list ',ftstart)
    sys.exit(1)    
  
  ctstring=ftstart.strftime('%Y%m%d%H')
  
  print('process time ',ctstring, stime[n])
  
  ftracer=xr.open_dataset(tracer_file[n])

  if im != ftracer['xaxis_1'].size :
    print('inconsitent fv_tracer xaxis')
    exit(1)
  if jm != ftracer['yaxis_1'].size :
    print('inconsitent fv_tracer yaxis')
    exit(1)
  
  fcore=xr.open_dataset(corefiles[n])

  if im != fcore['xaxis_1'].size :
    print('inconsitent fv_core xaxis')
    exit(1)
  if jm != fcore['yaxis_2'].size :
    print('inconsitent fv_core yaxis')
    exit(1)
      
# variable loop
  for m in range(len(modnames)):
   cvar=modnames[m]
   if cvar in ftracer.variables.keys():
     cunits=''
     conv=1.
     if cvar in sp_gas:
       cunits='ppbV'
       conv=1000
     elif cvar in sp_aero:
       cunits='$\mu$g/m$^3$' # '$\mu$g/kg' 
   else:
      print('cat not find ',cvar)   

# locations loop
   top_index=[]
   for nloc in range(len(locations)):
     dz=-fcore['DZ'][0,::-1,ys[nloc],xs[nloc]] # inverse the dz to bottom-up
     altitude_interfaces=dz.cumsum()+fcore['phis'][0,ys[nloc],xs[nloc]]/9.8
     altitude_center=altitude_interfaces-dz/2
     itop=np.abs(altitude_center.values-ceiling).argmin()
     top_index.append(itop)
     
     dp=fcore['delp'][0,:,ys[nloc],xs[nloc]] # top-down
     p_interfaces=dp.cumsum()+20 # top pressure is 20 Pa
     p_center=(p_interfaces-dp/2)[::-1] # bottom-up
     
     dens=p_center/(287.058*fcore['T'][0,::-1,ys[nloc],xs[nloc]]) # air density in kg/m3
     if cvar in sp_aero:
       conv=dens
     try:
      plt.plot(ftracer[cvar][0,::-1,ys[nloc],xs[nloc]].values*conv,altitude_center,label=loc_names[nloc])
     except:
      print(cvar,ftracer[cvar].shape,(ftracer[cvar][0,:,ys[nloc],xs[nloc]].values).shape,altitude_center.shape)
      sys.exit(1)
      
#   print('max of top_index=',max(top_index))
   plt.ylim(0,ceiling)
   plt.xlim(0,(ftracer[cvar][0,-max(top_index):-1,ys[:],xs[:]]*conv).max())
   plt.xlabel('Predicted '+cvar+' ('+cunits+')',fontsize=16)
   plt.ylabel('Altitude Above Sea Level (m)')
   plt.legend()
   plt.title(case+' Predicted '+cvar+' at '+ctstring)
   plt.tight_layout()
   plt.savefig(figfolder+'/profile_'+cvar+'_'+case+'_'+ctstring+'.png',dpi=300)
   plt.clf()
  
  ftracer.close()
  fcore.close()
  ftstart=ftstart+timedelta(hours=tstep)
  
