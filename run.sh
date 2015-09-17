rm testout.csv testcon.csv
python areaweight.py \
  --from-layer ~/t/Proj/WinStress/shapefiles/watersheds.shp \
  --from-id uniq_id3 \
  --to-layer ~/t/Proj/GLEI/shapefiles/seg_shed.shp \
  --to-id seg_num \
  --attributes edmrbsnm pcag sumrel \
  --output testout.csv \
  --contrib testcon.csv
