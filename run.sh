rm testout.csv testcon.csv
python areaweight.py \
  --from-layer ~/t/Proj/WinStress/shapefiles/watersheds.shp \
  --from-id uniq_id3 \
  --to-layer ~/t/Proj/GLEI/shapefiles/seg_shed.shp \
  --to-id seg_num \
  --attributes catch_area carea_km area_km3 \
  --contrib testcon.csv

#  --buffer 100
#  --output testout.csv \
