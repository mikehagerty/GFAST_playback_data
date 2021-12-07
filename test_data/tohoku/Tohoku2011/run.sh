#!/bin/tcsh

set DIR = "/opt/earthworm/earthworm_svn/bin"
foreach f (CI*)
  echo $f
  ${DIR}/ms2tank -n 1 $f >! $f.tank
end
cat *.tank >! all_tanks
${DIR}/remux_tbuf all_tanks tohoku.tnk
