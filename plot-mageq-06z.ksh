#!/bin/ksh -x
source ~/.bashrc
export PATH=/opt/cray/pe/python/3.9.4.2/bin:$PATH

today=${1:-`$HOME/bin/ndate|cut -c1-8`}
endday=${2:-$today}
cyc='06'

SORC=/lfs/h2/emc/physics/noscrub/Youhua.Tang/ufs-aqm-plot-example

p_restart_2d=1
p_restart_profile=1
p_met2d=1
do_sftp=1

while [ $today -le $endday ]; do
  t1=$($HOME/bin/ndate +6 $today$cyc)
  t2=$($HOME/bin/ndate +66 $today$cyc)

  t1m=$($HOME/bin/ndate +1 $today$cyc)
  t2m=$($HOME/bin/ndate +72 $today$cyc)

  HOLDIN=/lfs/h1/ops/prod/com/aqm/v7.0/aqm.$today/$cyc
  WORKING=$HOME/ptmp/plot-2d-chem.$today$cyc

  if [ ! -e $WORKING/figures ]; then
   mkdir -p $WORKING/figures
  fi
  cd $WORKING
if [ $p_restart_2d -eq 1 ]; then
  cat > restart2d-wd-$today$cyc.yaml <<EOF1
  filelist: "$HOLDIN/RESTART/*.fv_tracer.res.tile1.nc"
  metfiles: "$HOLDIN/RESTART/*.fv_srf_wnd.res.tile1.nc"
  gridfile: /lfs/h1/ops/prod/packages/aqm.v7.0.11/fix/fix_lam/C793_oro_data.tile7.halo0.nc
  tstart: '${t1:0:8}T${t1:8:2}'
  tend: '${t2:0:8}T${t2:8:2}'
  tfmt: '%Y%m%dT%H'
  tstep: 6
  case_name: 'NAQFC'
  parea: [ 273, 292, 34, 45 ]
  barb_yn : True
  barb_skip : 10
  figfolder: figures
  modnames: ['co','etha','aecj','o3','nox']
  valueint: [ [ 90, 100, 120, 150, 180, 210, 250, 300, 400, 800], 
              [ 0.4, 0.6, 1, 1.5, 2, 3, 5, 10, 20, 50],
              [0.1,0.2,0.3,0.5,1,2,3,5,7,10,20],
              [20,30,40,45,50,55,60,70,80,100,120],
              [0.1,0.2,0.5,1,1.5,2,3,6,10,15,20]]
EOF1
  python $SORC/plot-restart-2d-wd.py restart2d-wd-$today$cyc.yaml 
fi

if [ $p_restart_profile -eq 1 ]; then
  cat > restart-profile-$today$cyc.yaml <<EOF2
  filelist: "$HOLDIN/RESTART/*.fv_tracer.res.tile1.nc"
  corefiles: "$HOLDIN/RESTART/*.fv_core.res.tile1.nc"
  gridfile: /lfs/h1/ops/prod/packages/aqm.v7.0.11/fix/fix_lam/C793_oro_data.tile7.halo0.nc
  tstart: '${t1:0:8}T${t1:8:2}'
  tend: '${t2:0:8}T${t2:8:2}'
  tfmt: '%Y%m%dT%H'
  tstep: 6
  case_name: 'NAQFC'
  ceiling: 5000
  figfolder: figures
  modnames: ['o3','nox','co','etha','aecj']
  locations:
    New_York_City: [40.7128, -74.0060]
    Washington_DC: [38.9072, -77.0369]
    HRG_Airport: [39.7054, -77.7310]
    Baltimore: [39.2905, -76.6104]
    SW_Marcellus: [39.7241, -80.5212]
    Lancaster_PA: [40.0403, -76.3042]
EOF2
  python $SORC/plot-restart-profile.py restart-profile-$today$cyc.yaml 
fi

if [ $p_met2d -eq 1 ]; then
  cat > met2d-$today$cyc.yaml <<EOF3
  input_filename: "$HOLDIN/aqm.t${cyc}z.phy.f*.nc"
  tstart: '${t1m:0:8}T${t1m:8:2}' 
  tend: '${t2m:0:8}T${t2m:8:2}'
  tfmt: '%Y%m%dT%H'
  tstep: 3
  case_name: 'NAQFC'
  parea: [ 273, 292, 34, 45 ]
  barb_yn : True
  barb_skip : 10
  figfolder: figures
  modnames: ['tmp2m','hpbl','aod']
  valueint: [ [260,270,280,285,290,295,300,305,310,315,320],
            [ 30, 50, 100, 200, 300, 400, 500, 700, 1000, 1500,2000, 3000, 5000],
            [0.1,0.2,0.3,0.5,0.7,1,1.5,2,3,4,5]]
EOF3
  python $SORC/plot-met2d.py met2d-$today$cyc.yaml
fi

if [ $do_sftp -eq 1 ]; then
$HOME/bin/sshpass -p '1qaz@WSX3edc4rfv' sftp wx20yt@rzdm<<EOF4
cd /home/ftp/emc/mmb/aq/MAGEQ-NAQFC-plots
mkdir $today$cyc
cd $today$cyc
lcd figures
put *.png
quit
EOF4
fi

  today=$($HOME/bin/ndate +24 $today$cyc|cut -c1-8)
done
