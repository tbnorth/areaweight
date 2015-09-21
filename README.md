# Area Weighting

Transfer attribute values from a layer of GIS polygon features for which
the attribute values are known to an overlapping but different layer of
polygon features based on area of overlap.

See [areaweight.pdf](./areaweight.pdf) for an overview.

    Usage:
    
    usage: areaweight.py [-h] --from-layer FROM_LAYER --to-layer TO_LAYER
                         --from-id FROM_ID --to-id TO_ID --attributes ATTRIBUTES
                         [ATTRIBUTES ...] [--buffer BUFFER]
                         [--transform-before-buffer] [--total-area]
                         [--from-table FROM_TABLE] [--from-table-id FROM_TABLE_ID]
                         [--output OUTPUT] [--contrib CONTRIB]

    GDAL (OGR) based area weighting of attributes between polygon layers
    
    optional arguments:
      -h, --help            show this help message and exit
      --from-layer FROM_LAYER
                            Path to layer with attributes to area weight (default:
                            None)
      --to-layer TO_LAYER   Path to layer for which attributes will be weighted.
                            This layer is not altered, only used as a source of
                            polygons. (default: None)
      --from-id FROM_ID     Name of ID field in from-layer (default: None)
      --to-id TO_ID         Name of ID field in to-layer (default: None)
      --attributes ATTRIBUTES [ATTRIBUTES ...]
                            Attribute field names, in from-layer or from-table, to
                            area weight (default: None)
      --buffer BUFFER       Distance to buffer to-layer polys before intersection
                            (default: None)
      --transform-before-buffer
                            Transform to-layer to from-layer *before* buffering,
                            not after (default: False)
      --total-area          Use total area of from-layer features, not
                            intersecting area (default: False)
      --from-table FROM_TABLE
                            Path to table data source if attributes are not in
                            from-layer (default: None)
      --from-table-id FROM_TABLE_ID
                            Name of ID field in from-table, values should match
                            from-id values (default: None)
      --output OUTPUT       Path to output file (csv), must not exist already
                            (default: None)
      --contrib CONTRIB     Path to optional file (csv), to receive contribution
                            information, must not exist already (default: None)
