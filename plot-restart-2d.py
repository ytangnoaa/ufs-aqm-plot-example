#!/usr/bin/env python
# plot variables at restart file's lowest layers 

import netCDF4 as nc
import sys, yaml
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
from datetime import datetime, timedelta
import xarray as xr
import numpy as np
import glob
states_provinces = cfeature.NaturalEarthFeature(
        category='cultural',
        name='admin_1_states_provinces_lines',
        scale='50m',
        facecolor='none')

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
parea=ainput['parea']
figfolder=ainput['figfolder']
modnames=ainput['modnames']
valueint=ainput['valueint']

fgrid=xr.open_dataset(ainput['gridfile'])
im=fgrid['lon'].size
jm=fgrid['lat'].size
geolon=fgrid['geolon']
geolat=fgrid['geolat']
geolonmax=geolon.max()
if geolonmax > 180:
  geolonmax=geolonmax-360.
geolonmin=geolon.min()
if geolonmin > 180:
  geolonmin=geolonmin-360.
geolatmax=geolat.max()
geolatmin=geolat.min()
if ( geolon.max() > 280 ) & (geolon.min() < 180):
 clon=180
 parea[0]=parea[0]-clon
 parea[1]=parea[1]-clon
else:
 clon=0
cproj=ccrs.PlateCarree(central_longitude=clon)

lines=glob.glob(ainput['filelist'])
nlines=len(lines)
stime={}
n=0
for aline in lines:
  itmp=aline.rindex('.fv_tracer')
  tstring1=aline[itmp-15:itmp]
#  print('tstring1=',tstring1)
  stime[n]=datetime.strptime(tstring1,'%Y%m%d.%H%M%S')
  n=n+1
 
ftstart=datetime.strptime(tstart,tfmt)
ftend=datetime.strptime(tend,tfmt)

while ftstart <= ftend:

  for n in range(nlines):
    if ftstart == stime[n] :
      break
  if n >= nlines:
    print('can not find time range in list ',ftstart)
    exit(1)    
  
  ctstring=ftstart.strftime('%Y%m%d%H')
  
  print('process time ',ctstring, stime[n])
  
  ftracer=xr.open_dataset(lines[n])

  if im != ftracer['xaxis_1'].size :
    print('inconsitent fv_tracer xaxis')
    exit(1)
  if jm != ftracer['yaxis_1'].size :
    print('inconsitent fv_tracer yaxis')
    exit(1)
      
# variable loop
  for m in range(len(modnames)):
   cvar=modnames[m]
   myvalues=valueint[m]
   if cvar in ftracer.variables.keys():
     cunits=''
     conv=1.
     if cvar in sp_gas:
       cunits='ppbV'
       conv=1000
     elif cvar in sp_aero:
       cunits='$\mu$g/kg'
   else:
      print('cat not find ',cvar)   

   cint=valueint[m]
   
   ax=plt.axes(projection=cproj)
   ax.set_extent(parea, cproj)
   plt.subplots_adjust(wspace=0.6,hspace=0.4)
   
   plt.pcolormesh(geolon,geolat,ftracer[cvar][0,-1,:,:]*conv,cmap='jet',transform=ccrs.PlateCarree(),norm=colors.BoundaryNorm(boundaries=myvalues,ncolors=256))

   cbar=plt.colorbar(fraction=0.07,orientation='horizontal')
   cbar.set_label('Surface '+cvar+' ('+cunits+')',fontsize=16)
   plt.title(case+' Predicted '+cvar+' at '+ctstring)
   ax.add_feature(cfeature.BORDERS)
   ax.add_feature(cfeature.COASTLINE)
   ax.add_feature(states_provinces, edgecolor='gray')
   if clon != 180:
    plt.tight_layout()
   plt.savefig(figfolder+'/chem_'+cvar+'_'+case+'_'+ctstring+'.png',dpi=300)
   plt.clf()
  
  ftracer.close()

  ftstart=ftstart+timedelta(hours=tstep)
  
