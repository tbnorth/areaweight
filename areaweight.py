"""
areaweight.py - GDAL (OGR) based area weighting of attributes
between polygon layers, see make_parser() for usage.

Terry Brown, Terry_N_Brown@yahoo.com, Thu Sep 17 13:49:05 2015
"""

import argparse
import csv
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
    
    from_attr = {}

    for out_n, to_feature in enumerate(to_layer):
        to_id = to_feature.GetField(opt.to_id)
        to_geom = to_feature.GetGeometryRef().Clone()
        if opt.transform and opt.transform_before_buffer:
            to_geom.Transform(opt.transform)
        if opt.buffer:
            to_geom = to_geom.Buffer(opt.buffer)
        if opt.transform and not opt.transform_before_buffer:
            to_geom.Transform(opt.transform)
        from_layer.SetSpatialFilter(to_geom)
        from_layer.ResetReading()
        total_area = 0
        intersecting = set()
        for n, from_feature in enumerate(from_layer):
            from_geom = from_feature.GetGeometryRef()
            intersection = to_geom.Intersection(from_geom)
            intersect_area = intersection and intersection.GetArea()
            # SetSpatialFilter() can return non-intersecting polys (BBox hits)
            if not intersect_area:
                continue
            from_id = from_feature.GetField(opt.from_id)
            intersecting.add(from_id)
            if opt.total_area:
                if from_id not in from_attr:
                    from_attr[from_id] = from_geom.GetArea()
            else:
                # always update when using actual intersect area
                from_attr[from_id] = intersect_area
            total_area += from_attr[from_id]
            for attr in opt.attributes:
                if (from_id, attr) not in from_attr:
                    if opt.from_table:
                        from_attr[(from_id, attr)] = float(opt.from_table[from_id][opt.c2f[attr]])
                    else:
                        from_attr[(from_id, attr)] = float(from_feature.GetField(attr))
        total_attr = {attr:0 for attr in opt.attributes}
        for from_id in intersecting:
            from_area = from_attr[from_id]
            prop = from_attr[from_id] / total_area
            contrib = [to_id, from_id, total_area, from_area, prop]
            for attr in opt.attributes:
                share = prop * from_attr[(from_id, attr)]
                total_attr[attr] += share
                contrib.append(from_attr[(from_id, attr)])
                contrib.append(share)
            if opt.contrib:
                opt.contrib.writerow(contrib)
        out = [to_id, len(intersecting), total_area]
        for attr in opt.attributes:
            out.append(total_attr[attr])
        opt.output.writerow(out)
        if opt.progress:
            print("%d: %s %s" % (out_n+1, opt.to_id, to_id))
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
     parser.add_argument("--buffer", type=float,
         help="Distance to buffer to-layer polys before intersection"
     )
     parser.add_argument("--transform-before-buffer", action='store_true', default=False,
         help="Transform to-layer to from-layer *before* buffering, not after"
     )
     parser.add_argument("--total-area", action='store_true', default=False,
         help="Use total area of from-layer features, not intersecting area"
     )
     parser.add_argument("--from-table",
         help="Path to table data source if attributes are not in from-layer"
     )
     parser.add_argument("--from-table-id",
         help="Name of ID field in from-table, values should match from-id values"
     )
     parser.add_argument("--output",
         help="Path to output file (csv), must not exist already"
     )
     parser.add_argument("--contrib",
         help="Path to optional file (csv), to receive contribution information, "
         "must not exist already"
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
    ans = osr.CoordinateTransformation(to, from_)
    return ans
def main():

    opt = make_parser().parse_args()
    
    # open CSV output file
    if opt.output:
        if os.path.exists(opt.output):
            raise AreaWeightException("Output file '%s' already exists" % opt.output)
        opt.output = csv.writer(open(opt.output, 'w'))
        opt.progress = True
    else:
        opt.output = csv.writer(sys.stdout)
        opt.progress = False
    heads = [opt.to_id, 'aw_n', 'aw_a']
    for attrib in opt.attributes:
        heads.extend([attrib])
    opt.output.writerow(heads)
        
    # optionally open CSV contribution info. file
    if opt.contrib:
        if os.path.exists(opt.contrib):
            raise AreaWeightException("Contrib file '%s' already exists" % opt.contrib)
        opt.contrib = csv.writer(open(opt.contrib, 'w'))
        heads = [opt.to_id, opt.from_id, 'total_area', 'from_area', 'prop']
        for attrib in opt.attributes:
            heads.extend([attrib, 'aw_'+attrib])
        opt.contrib.writerow(heads)
    
    if opt.from_table:
        # FIXME, assume CSV for now, should switch to OGR datasource
        logging.info("Reading attributes from '%s'" % opt.from_table)
        reader = csv.reader(open(opt.from_table))
        opt.c2f = {i:n for n, i in enumerate(next(reader))}
        opt.from_table = {}
        for row in reader:
            opt.from_table[row[opt.c2f[opt.from_table_id]]] = row

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
        logging.debug(from_layer.GetSpatialRef())
        logging.debug(to_layer.GetSpatialRef())

    area_weight(opt, from_layer, to_layer)
if __name__ == '__main__':
    main()
