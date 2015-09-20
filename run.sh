rm testout.csv testcon.csv
python areaweight.py \
  --from-layer ~/t/Proj/WinStress/shapefiles/watersheds.shp \
  --from-id UNIQ_ID3 \
  --to-layer /home/tbrown/t/Proj/GLRI/GLEI2/shapefiles/glri_site.shp \
  --to-id site \
  --attributes ed_mxr_all_norm \
  --output testout.csv \
  --contrib testcon.csv \
  --from-table ws_stress.csv \
  --from-table-id UNIQ_ID3 \
  --buffer 100 \
  --transform-before-buffer \
  --total-area

#  --buffer 100
#  --output testout.csv \
