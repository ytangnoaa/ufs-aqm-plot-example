#!/usr/bin/env python
# plot surface 

import sys, yaml
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
from datetime import datetime, timedelta
import xarray as xr
import numpy as np

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

fname=ainput['input_filename']
tfmt=ainput['tfmt']
tstart=ainput['tstart']
tend=ainput['tend']
tstep=int(ainput['tstep'])
parea=ainput['parea']
case=ainput['case_name']
barb_yn=bool(ainput['barb_yn'])
barb_skip=int(ainput['barb_skip'])
figfolder=ainput['figfolder']
modnames=ainput['modnames']
valueint=ainput['valueint']

a=xr.open_mfdataset(fname)
geolon=a.lon.values[0,:,:]
geolat=a.lat.values[0,:,:]

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
# 150E to 320E conversion to 180 centered extent: 150-180=-30  320-180=140

else:
 clon=0
cproj=ccrs.PlateCarree(central_longitude=clon)

ftstart=datetime.strptime(tstart,tfmt)
ftend=datetime.strptime(tend,tfmt)

# obs_title_mapping={'OZONE':'O$_3$','PM2.5':'PM2.5'}

while ftstart <= ftend:

  ctstring=ftstart.strftime('%Y-%m-%dT%H')
       
# variable loop
  for m in range(len(modnames)):
   cvar=modnames[m]
   myvalues=valueint[m]
   if cvar in list(a.keys()):
     cunits=a[cvar].units
     conv=1.
     if 'numerical' in cunits: # AOD
       cunits=''
   else:
      print('cat not find ',cvar)
   
   cint=valueint[m]
  
   ax=plt.axes(projection=cproj)
   ax.set_extent(parea, cproj)
   plt.subplots_adjust(wspace=0.6,hspace=0.4)
   
   plt.pcolormesh(geolon,geolat,a[cvar].loc[ctstring,:,:].values.squeeze()*conv,
    cmap='jet',transform=ccrs.PlateCarree(),norm=colors.BoundaryNorm(boundaries=myvalues,ncolors=256))
   if barb_yn :
     ax.barbs(geolon[::barb_skip,::barb_skip],geolat[::barb_skip,::barb_skip],
      a['ugrd10m'].loc[ctstring,::barb_skip,::barb_skip].values.squeeze(),
      a['vgrd10m'].loc[ctstring,::barb_skip,::barb_skip].values.squeeze(),
      color='k', length=5, transform=ccrs.PlateCarree())

   clabel=cvar.upper()
   cbar=plt.colorbar(fraction=0.07,orientation='horizontal')
   cbar.set_label(clabel+' ('+cunits+')',fontsize=16)
   plt.title(case+' Predicted '+clabel+' at '+ctstring)
   ax.add_feature(cfeature.BORDERS)
   ax.add_feature(cfeature.COASTLINE)
   ax.add_feature(states_provinces, edgecolor='gray')
   if clon != 180:
    plt.tight_layout()
   plt.savefig(figfolder+'/met2d_'+case+'_'+cvar+'_'+ctstring+'.png',dpi=300)
   plt.clf()

  ftstart=ftstart+timedelta(hours=tstep)
