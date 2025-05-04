# ufs-aqm-plot-example

This repository includes python-based plotting examples for UFS-AQM output files
https://ufs-srweather-app.readthedocs.io/en/release-public-v2.2.0/BuildingRunningTesting/AQM.html


These outputs include  
aqm.t12z.chem_sfc.nc     # hourly surface chemical concentration with ozone, PM2.5 etc
aqm.t12z.phy.f???.nc     # hourly surface/2-D meteorological variables and AOD
*.fv_tracer.res.tile1.nc # 3-D restart files for chemical species in certain time interval, e.g. 6 hours. Its datetime can be found in its filename, gaseous species is in ppmV and aerosols are unit ug/kg
*.fv_core.res.tile1.nc   # 3-D restart files for meteorological variables

To make plots, edit the yaml file, and run

plot-met2d.py met2d-20240707T12.yaml
plot-spatial-surface.py spatial-surf-20240707T12.yaml
plot-restart-2d.py restart2d-20250407T06.yaml
plot-restart-profile.py restart-profile-20250407T12.yaml
