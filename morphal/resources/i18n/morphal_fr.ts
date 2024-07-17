<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE TS>
<TS version="2.1" language="fr">
<context>
    <name>MorphALGeometryToMedians</name>
    <message>
        <location filename="../../core/geometry_to_medians.py" line="53"/>
        <source>            This algorithm generates a segment layer representing the medians of the geometries            from an input line layer or an input polygon layer.            
These segments are normalised, i.e. their point of origin is always located as far west             as possible, or otherwise as far south as possible.            
It creates a new vector layer with the same content as the input one, but with            additional computed attributes: median orientation, computed from East or from North,            median length and median associated elongation.</source>
        <translation>Cet algorithme génère une couche de segments représentant les médianes à partir d'une couche de lignes ou de polygones en entrée.
Ces segments sont normalisés, i.e. que leur point d'origine est toujours situé le plus à l'ouest possible, ou à défaut le plus au sud possible.
Il génère une nouvelle couche vectorielle avec le même contenu que la couche d'entrée, mais avec des attributs supplémentaires: les orientations des médianes, calculées depuis l'est ou le nord, les longueurs des médianes et les élongations associées aux médianes.</translation>
    </message>
    <message>
        <location filename="../../core/geometry_to_medians.py" line="65"/>
        <source>Layer CRS</source>
        <translation>SCR de la couche</translation>
    </message>
    <message>
        <location filename="../../core/geometry_to_medians.py" line="66"/>
        <source>Project CRS</source>
        <translation>SCR du projet</translation>
    </message>
    <message>
        <location filename="../../core/geometry_to_medians.py" line="67"/>
        <source>Ellipsoidal</source>
        <translation>Ellipsoïdale</translation>
    </message>
    <message>
        <location filename="../../core/geometry_to_medians.py" line="276"/>
        <source>East</source>
        <translation>Est</translation>
    </message>
    <message>
        <location filename="../../core/geometry_to_medians.py" line="274"/>
        <source>North</source>
        <translation>Nord</translation>
    </message>
    <message>
        <location filename="../../core/geometry_to_medians.py" line="75"/>
        <source>Input layer</source>
        <translation>Couche source</translation>
    </message>
    <message>
        <location filename="../../core/geometry_to_medians.py" line="83"/>
        <source>Calculate using</source>
        <translation>Calculer en utilisant</translation>
    </message>
    <message>
        <location filename="../../core/geometry_to_medians.py" line="92"/>
        <source>Orientations calculated from</source>
        <translation>Orientations calculées à partir de la direction</translation>
    </message>
    <message>
        <location filename="../../core/geometry_to_medians.py" line="101"/>
        <source>Medians</source>
        <translation>Médianes</translation>
    </message>
    <message>
        <location filename="../../core/geometry_to_medians.py" line="113"/>
        <source>Geometries to medians</source>
        <translation>Lignes ou polygones vers médianes</translation>
    </message>
    <message>
        <location filename="../../core/geometry_to_medians.py" line="129"/>
        <source>The layer geometry type is different from a line or a polygon</source>
        <translation>Le type géométrique de la couche source est différent d'un type linéaire ou polygonal</translation>
    </message>
    <message>
        <location filename="../../core/geometry_to_medians.py" line="135"/>
        <source>The layer doesn&apos;t contain any feature: no output provided</source>
        <translation>La couche ne contient aucun objet : aucun résultat n'est fourni</translation>
    </message>
    <message>
        <location filename="../../core/geometry_to_medians.py" line="203"/>
        <source>No project is available in this context</source>
        <translation>Aucun projet disponible dans ce contexte</translation>
    </message>
</context>
<context>
    <name>MorphALGeometryToSegments</name>
    <message>
        <location filename="../../core/morphal_geometry_to_segments.py" line="59"/>
        <source>Input layer</source>
        <translation>Couche source</translation>
    </message>
    <message>
        <location filename="../../core/morphal_geometry_to_segments.py" line="67"/>
        <source>Unicity of created segments</source>
        <translation>Unicité des segments créés</translation>
    </message>
    <message>
        <location filename="../../core/morphal_geometry_to_segments.py" line="75"/>
        <source>Segments</source>
        <translation>Segments</translation>
    </message>
    <message>
        <location filename="../../core/morphal_geometry_to_segments.py" line="103"/>
        <source>The layer geometry type is different from a line or a polygon</source>
        <translation>Le type géométrique de la couche source est différent d'un type linéaire ou polygonal</translation>
    </message>
    <message>
        <location filename="../../core/morphal_geometry_to_segments.py" line="109"/>
        <source>The layer doesn&apos;t contain any feature: no output provided</source>
        <translation>La couche ne contient aucun objet : aucun résultat n'est fourni</translation>
    </message>
    <message>
        <location filename="../../core/morphal_geometry_to_segments.py" line="204"/>
        <source>-Unicity</source>
        <translation>-Unicite</translation>
    </message>
    <message>
        <location filename="../../core/morphal_geometry_to_segments.py" line="47"/>
        <source>            This algorithm generates a segment layer from an input line layer or an input polygon layer.            
These segments are normalised, i.e. their point of origin is always located as far west             as possible, or otherwise as far south as possible.            
Optionally, it is possible to generate unique segments based on geometry.            
The attribute table of the output layer is identical to the one of the input layer.</source>
        <translation>Cet algorithme génère une couche de segments à partir d'une couche de lignes ou de polygones en entrée.
Ces segments sont normalisés, i.e. que leur point d'origine est toujours situé le plus à l'ouest possible, ou à défaut le plus au sud possible.
En option, il est possible de générer des segments uniques d'un point de vue géométrique.
La table d'attributs de la couche de sortie est identique à de la couche d'entrée.</translation>
    </message>
    <message>
        <location filename="../../core/morphal_geometry_to_segments.py" line="87"/>
        <source>Geometries to segments</source>
        <translation type="unfinished">Lignes ou polygones vers segments</translation>
    </message>
</context>
<context>
    <name>MorphALPolygonIndicators</name>
    <message>
        <location filename="../../core/polygon_indicators.py" line="148"/>
        <source>Compute multiple morphological indicators for polygons</source>
        <translation>Calculer de nombreux indicateurs morphologiques pour polygones</translation>
    </message>
    <message>
        <location filename="../../core/polygon_indicators.py" line="73"/>
        <source>Layer CRS</source>
        <translation>SCR de la couche</translation>
    </message>
    <message>
        <location filename="../../core/polygon_indicators.py" line="74"/>
        <source>Project CRS</source>
        <translation>SCR du projet</translation>
    </message>
    <message>
        <location filename="../../core/polygon_indicators.py" line="75"/>
        <source>Ellipsoidal</source>
        <translation>Ellipsoïdale</translation>
    </message>
    <message>
        <location filename="../../core/polygon_indicators.py" line="79"/>
        <source>Input layer</source>
        <translation>Couche source</translation>
    </message>
    <message>
        <location filename="../../core/polygon_indicators.py" line="87"/>
        <source>Calculate using</source>
        <translation>Calculer en utilisant</translation>
    </message>
    <message>
        <location filename="../../core/polygon_indicators.py" line="96"/>
        <source>Perimeter</source>
        <translation>Périmètre</translation>
    </message>
    <message>
        <location filename="../../core/polygon_indicators.py" line="104"/>
        <source>Area</source>
        <translation>Aire</translation>
    </message>
    <message>
        <location filename="../../core/polygon_indicators.py" line="112"/>
        <source>Miller&apos;s compactness index (roundness)</source>
        <translation>Compacité : indice de Miller (rondeur)</translation>
    </message>
    <message>
        <location filename="../../core/polygon_indicators.py" line="120"/>
        <source>Gravelius&apos; compactness index</source>
        <translation>Compacité : indice de Gravelius</translation>
    </message>
    <message>
        <location filename="../../core/polygon_indicators.py" line="128"/>
        <source>Polygonal elongation (based on MBR)</source>
        <translation>Elongation polygonale (basée sur le rectangle minimum englobant)</translation>
    </message>
    <message>
        <location filename="../../core/polygon_indicators.py" line="136"/>
        <source>Morphological indicators</source>
        <translation>Indicateurs morphologiques</translation>
    </message>
    <message>
        <location filename="../../core/polygon_indicators.py" line="230"/>
        <source>No project is available in this context</source>
        <translation>Aucun projet disponible dans ce contexte</translation>
    </message>
</context>
<context>
    <name>MorphALPolygonPerimeterArea</name>
    <message>
        <location filename="../../core/morphal_polygon_perimeter_area.py" line="88"/>
        <source>Add polygon perimeters and areas</source>
        <translation>Ajouter périmètres et aires à une couche vectorielle polygonale</translation>
    </message>
    <message>
        <location filename="../../core/morphal_polygon_perimeter_area.py" line="55"/>
        <source>Layer CRS</source>
        <translation>SCR de la couche</translation>
    </message>
    <message>
        <location filename="../../core/morphal_polygon_perimeter_area.py" line="56"/>
        <source>Project CRS</source>
        <translation>SCR du projet</translation>
    </message>
    <message>
        <location filename="../../core/morphal_polygon_perimeter_area.py" line="57"/>
        <source>Ellipsoidal</source>
        <translation>Ellipsoïdale</translation>
    </message>
    <message>
        <location filename="../../core/morphal_polygon_perimeter_area.py" line="61"/>
        <source>Input layer</source>
        <translation>Couche source</translation>
    </message>
    <message>
        <location filename="../../core/morphal_polygon_perimeter_area.py" line="69"/>
        <source>Calculate using</source>
        <translation>Calculer en utilisant</translation>
    </message>
    <message>
        <location filename="../../core/morphal_polygon_perimeter_area.py" line="78"/>
        <source>Layer with added perimeters and areas</source>
        <translation>Couche avec périmètres et aires ajoutés</translation>
    </message>
    <message>
        <location filename="../../core/morphal_polygon_perimeter_area.py" line="143"/>
        <source>No project is available in this context</source>
        <translation>Aucun projet disponible dans ce contexte</translation>
    </message>
    <message>
        <location filename="../../core/morphal_polygon_perimeter_area.py" line="46"/>
        <source>            This algorithm computes polygon perimeters and areas in a vector layer.            
It creates a new vector layer with the same content as the input one, but with            additional computed attributes : perimeter and area.</source>
        <translation>Cet algorithme calcule les périmètres et les aires des entités d'une couche vectorielle dont le type géométrique associé est polygonal. 
Il génère une nouvelle couche vectorielle avec le même contenu que la couche d'entrée, mais avec des attributs supplémentaires : périmètre et aire.</translation>
    </message>
    <message>
        <location filename="../../core/morphal_polygon_perimeter_area.py" line="105"/>
        <source>The layer doesn&apos;t contain any feature: no output provided</source>
        <translation>La couche ne contient aucun objet : aucun résultat n'est fourni</translation>
    </message>
</context>
<context>
    <name>MorphALRectangularCharacterisation</name>
    <message>
        <location filename="../../core/morphal_rectangular_characterisation.py" line="272"/>
        <source>Rectangular characterisation</source>
        <translation>Caractérisation rectangulaire</translation>
    </message>
    <message>
        <location filename="../../core/morphal_rectangular_characterisation.py" line="90"/>
        <source>Layer CRS</source>
        <translation>SCR de la couche</translation>
    </message>
    <message>
        <location filename="../../core/morphal_rectangular_characterisation.py" line="91"/>
        <source>Project CRS</source>
        <translation>SCR du projet</translation>
    </message>
    <message>
        <location filename="../../core/morphal_rectangular_characterisation.py" line="92"/>
        <source>Ellipsoidal</source>
        <translation>Ellipsoïdale</translation>
    </message>
    <message>
        <location filename="../../core/morphal_rectangular_characterisation.py" line="96"/>
        <source>Input layer</source>
        <translation>Couche source</translation>
    </message>
    <message>
        <location filename="../../core/morphal_rectangular_characterisation.py" line="104"/>
        <source>Calculate using</source>
        <translation>Calculer en utilisant</translation>
    </message>
    <message>
        <location filename="../../core/morphal_rectangular_characterisation.py" line="114"/>
        <source>Detection of rectangular shapes - Level 1</source>
        <translation>Détecter les formes rectangulaires - Niveau 1</translation>
    </message>
    <message>
        <location filename="../../core/morphal_rectangular_characterisation.py" line="122"/>
        <source>Surface distance with convex hull (level 1)</source>
        <translation>Distance surfacique à l'enveloppe convexe (niveau 1)</translation>
    </message>
    <message>
        <location filename="../../core/morphal_rectangular_characterisation.py" line="133"/>
        <source>Surface distance with MBR (level 1)</source>
        <translation>Distance surfacique au rectangle englobant minimum (niveau 1)</translation>
    </message>
    <message>
        <location filename="../../core/morphal_rectangular_characterisation.py" line="144"/>
        <source>Rectangles - level 1</source>
        <translation>Couche de rectangle de niveau 1</translation>
    </message>
    <message>
        <location filename="../../core/morphal_rectangular_characterisation.py" line="155"/>
        <source>Detection of rectangular shapes - Level 2</source>
        <translation>Détecter les formes rectangulaires - Niveau 2</translation>
    </message>
    <message>
        <location filename="../../core/morphal_rectangular_characterisation.py" line="163"/>
        <source>Surface distance with convex hull (level 2)</source>
        <translation>Distance surfacique à l'enveloppe convexe (niveau 2)</translation>
    </message>
    <message>
        <location filename="../../core/morphal_rectangular_characterisation.py" line="174"/>
        <source>Surface distance with MBR (level 2)</source>
        <translation>Distance surfacique au rectangle englobant minimum (niveau 2)</translation>
    </message>
    <message>
        <location filename="../../core/morphal_rectangular_characterisation.py" line="185"/>
        <source>Rectangles - level 2</source>
        <translation>Couche de rectangle de niveau 2</translation>
    </message>
    <message>
        <location filename="../../core/morphal_rectangular_characterisation.py" line="196"/>
        <source>Detection of rectangular shapes - Level 3</source>
        <translation>Détecter les formes rectangulaires - Niveau 3</translation>
    </message>
    <message>
        <location filename="../../core/morphal_rectangular_characterisation.py" line="204"/>
        <source>Surface distance with convex hull (level 3)</source>
        <translation>Distance surfacique à l'enveloppe convexe (niveau 3)</translation>
    </message>
    <message>
        <location filename="../../core/morphal_rectangular_characterisation.py" line="215"/>
        <source>Surface distance with MBR (level 3)</source>
        <translation>Distance surfacique au rectangle englobant minimum (niveau 3)</translation>
    </message>
    <message>
        <location filename="../../core/morphal_rectangular_characterisation.py" line="226"/>
        <source>Rectangles - level 3</source>
        <translation>Couche de rectangle de niveau 3</translation>
    </message>
    <message>
        <location filename="../../core/morphal_rectangular_characterisation.py" line="237"/>
        <source>All rectangular indicators</source>
        <translation>Couche de sortie avec l'ensemble des indicateurs de rectangularité</translation>
    </message>
    <message>
        <location filename="../../core/morphal_rectangular_characterisation.py" line="257"/>
        <source>Roundness threshold</source>
        <translation>Seuil de détection de formes circulaires</translation>
    </message>
    <message>
        <location filename="../../core/morphal_rectangular_characterisation.py" line="305"/>
        <source>The input layer doesn&apos;t contain any feature: no output provided</source>
        <translation>La couche ne contient aucun objet : aucun résultat n'est fourni</translation>
    </message>
</context>
<context>
    <name>MorphALSegmentOrientation</name>
    <message>
        <location filename="../../core/morphal_segment_orientation.py" line="59"/>
        <source>Compute the orientations of a layer of segments</source>
        <translation type="obsolete">Cet algorithme calcule les orientations d'une couche vectorielle dont les entités sont des segments. 
Il génère une nouvelle couche vectorielle avec le même contenu que la couche d'entrée, mais avec des attributs supplémentaires dans sa table d'attributs : orientation, calculée depuis l'est ou le nord, et en option, une classifation à partir de ces orientations à partir d'un seuil de classificiation à définir.</translation>
    </message>
    <message>
        <location filename="../../core/morphal_segment_orientation.py" line="76"/>
        <source>Degree</source>
        <translation>Degré</translation>
    </message>
    <message>
        <location filename="../../core/morphal_segment_orientation.py" line="77"/>
        <source>Radian</source>
        <translation>Radian</translation>
    </message>
    <message>
        <location filename="../../core/morphal_segment_orientation.py" line="78"/>
        <source>Grade</source>
        <translation>Grade</translation>
    </message>
    <message>
        <location filename="../../core/morphal_segment_orientation.py" line="81"/>
        <source>[0 ; Pi[</source>
        <translation>[0 ; Pi[</translation>
    </message>
    <message>
        <location filename="../../core/morphal_segment_orientation.py" line="82"/>
        <source>[0 ; Pi/2[</source>
        <translation>[0 ; Pi/2[</translation>
    </message>
    <message>
        <location filename="../../core/morphal_segment_orientation.py" line="68"/>
        <source>Layer CRS</source>
        <translation>SCR de la couche</translation>
    </message>
    <message>
        <location filename="../../core/morphal_segment_orientation.py" line="69"/>
        <source>Project CRS</source>
        <translation>SCR du projet</translation>
    </message>
    <message>
        <location filename="../../core/morphal_segment_orientation.py" line="70"/>
        <source>Ellipsoidal</source>
        <translation>Ellipsoïdale</translation>
    </message>
    <message>
        <location filename="../../core/morphal_segment_orientation.py" line="87"/>
        <source>Input layer</source>
        <translation>Couche source</translation>
    </message>
    <message>
        <location filename="../../core/morphal_segment_orientation.py" line="113"/>
        <source>Unit</source>
        <translation>Unité</translation>
    </message>
    <message>
        <location filename="../../core/morphal_segment_orientation.py" line="122"/>
        <source>Interval</source>
        <translation>Intervalle</translation>
    </message>
    <message>
        <location filename="../../core/morphal_segment_orientation.py" line="95"/>
        <source>Calculate using</source>
        <translation>Calculer en utilisant</translation>
    </message>
    <message>
        <location filename="../../core/morphal_segment_orientation.py" line="131"/>
        <source>Round orientations to 3 decimals</source>
        <translation>Arrondir les orientations à 3 décimales</translation>
    </message>
    <message>
        <location filename="../../core/morphal_segment_orientation.py" line="139"/>
        <source>Compute a classification</source>
        <translation>Calculer une classification</translation>
    </message>
    <message>
        <location filename="../../core/morphal_segment_orientation.py" line="147"/>
        <source>Step of the classification</source>
        <translation>Pas de la classification</translation>
    </message>
    <message>
        <location filename="../../core/morphal_segment_orientation.py" line="204"/>
        <source>The layer doesn&apos;t contain any feature: no output provided</source>
        <translation>La couche ne contient aucun objet : aucun résultat n'est fourni</translation>
    </message>
    <message>
        <location filename="../../core/morphal_segment_orientation.py" line="286"/>
        <source>No project is available in this context</source>
        <translation>Aucun projet disponible dans ce contexte</translation>
    </message>
    <message>
        <location filename="../../core/morphal_segment_orientation.py" line="175"/>
        <source>Segments with orientations</source>
        <translation>Segments avec orientations</translation>
    </message>
    <message>
        <location filename="../../core/morphal_segment_orientation.py" line="187"/>
        <source>Compute segments orientations</source>
        <translation>Calculer les orientations d'une couche de segments</translation>
    </message>
    <message>
        <location filename="../../core/morphal_segment_orientation.py" line="342"/>
        <source>East</source>
        <translation>Est</translation>
    </message>
    <message>
        <location filename="../../core/morphal_segment_orientation.py" line="340"/>
        <source>North</source>
        <translation>Nord</translation>
    </message>
    <message>
        <location filename="../../core/morphal_segment_orientation.py" line="104"/>
        <source>Orientations calculated from</source>
        <translation>Orientations calculées à partir de la direction</translation>
    </message>
    <message>
        <location filename="../../core/morphal_segment_orientation.py" line="59"/>
        <source>            This algorithm computes the orientations of a layer of segments.            
It generates a new vector layer with the same content as the input one, but with            additional attributes: orientation, computed from East or from North, and if specified,            a classification based on the computed orientations and a classification step to specify.</source>
        <translation>Cet algorithme calcule les orientations d'une couche vectorielle dont les entités sont des segments. 
Il génère une nouvelle couche vectorielle avec le même contenu que la couche d'entrée, mais avec des attributs supplémentaires: orientation, calculée depuis l'est ou le nord, et en option, une classification à partir de ces orientations à partir d'un seuil de classificiation à définir.</translation>
    </message>
</context>
<context>
    <name>PTM4QgisProvider</name>
    <message>
        <location filename="../../ptm4qgis_provider.py" line="78"/>
        <source>PTM-MorphAL</source>
        <translation>PTM-MorphAL</translation>
    </message>
</context>
</TS>
