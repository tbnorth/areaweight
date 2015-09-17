"""
areaweight.py - GDAL (OGR) based area weighting of attributes
between polygon layers, see make_parser() for usage.

Terry Brown, Terry_N_Brown@yahoo.com, Thu Sep 17 13:49:05 2015
"""

import argparse
import logging; logging.basicConfig(level=logging.INFO, format='%(message)s')
import os
import sys

from osgeo import ogr
from osgeo import osr
class AreaWeightException(Exception):
    """Local exception class"""
    pass
 
def area_weight(opt, from_layer, to_layer):
    """area_weight - perform area weighting

    :param argparse Namespace opt: options
    :param OGR Layer from_layer: layer with attributes
    :param OGR Layer to_layer: layer needing attributes
    """

    for to_feature in to_layer:
        print to_feature.GetFID()
def make_parser():
     
     parser = argparse.ArgumentParser(
         description="""GDAL (OGR) based area weighting of attributes
         between polygon layers""",
         formatter_class=argparse.ArgumentDefaultsHelpFormatter
     )
     
     parser.add_argument("--from-layer", required=True,
         help="Path to layer with attributes to area weight"
     )
     parser.add_argument("--to-layer", required=True,
         help="Path to layer for which attributes will be weighted. "
         "This layer is not altered, only used as a source of polygons."
     )
     parser.add_argument("--from-id", required=True,
         help="Name of ID field in from-layer"
     )
     parser.add_argument("--to-id", required=True,
         help="Name of ID field in to-layer"
     )
     parser.add_argument("--attributes", required=True, nargs='+',
         help="Attribute field names, in from-layer or from-table, to area weight"
     )
     parser.add_argument("--from-table",
         help="Path to table data source if attributes are not in from-layer"
     )
     parser.add_argument("--from-table-d",
         help="Name of ID field in from-table, values should match from-id values"
     )
     parser.add_argument("--output",
         help="Path to output file (csv), must not exist already."
     )
     parser.add_argument("--contrib",
         help="Path to optional file (csv), to receive contribution information, "
         "must not exist already."
     )

     return parser

def make_transform(from_, to):
    """make_transform - make a , return None
    if layers in same projection already

    :param OGR layer from_: layer in SR to transform from
    :param OGR layer to: layer in SR to transform to
    :return: osr.CoordinateTransformation or None
    """

    to = to.GetSpatialRef()
    from_ = from_.GetSpatialRef()
    if from_ == to:
        return None
    ans = osr.CoordinateTransformation(from_, to)
    return ans
def main():

    opt = make_parser().parse_args()
    
    # open CSV output file
    if opt.output:
        if os.path.exists(opt.output):
            raise AreaWeightException("Output file '%s' already exists" % opt.output)
        opt.output = open(opt.output, 'w')
    else:
        opt.output = sys.stdout
        
    # optionally open CSV contribution info. file
    if opt.contrib:
        if os.path.exists(opt.contrib):
            raise AreaWeightException("Contrib file '%s' already exists" % opt.contrib)
        opt.contrib = open(opt.contrib, 'w')

    # open geometries
    from_ds = ogr.Open(opt.from_layer)
    from_layer = from_ds.GetLayer()
    to_ds = ogr.Open(opt.to_layer)
    to_layer = to_ds.GetLayer()
    # handle transformations
    opt.transform = make_transform(from_layer, to_layer)
    if opt.transform is None:
        logging.info("Layers in same projection")
    else:
        logging.info("Re-projecting to-layer to from-layer")

    area_weight(opt, from_layer, to_layer)
    
if __name__ == '__main__':
    main()
