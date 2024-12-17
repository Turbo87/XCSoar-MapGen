# -*- coding: utf-8 -*-
from xcsoar.mapgen.waypoints.waypoint import Waypoint
from xcsoar.mapgen.waypoints.list import WaypointList
import cherrypy



class __CSVLine:
    def __init__(self, line):
        self.__line = line
        self.__index = 0

    def has_next(self):
        return self.__index < len(self.__line)

    def __next__(self):
        if self.__index >= len(self.__line):
            return None

        in_quotes = False

        for i in range(self.__index, len(self.__line)):
            if self.__line[i] == '"':
                in_quotes = not in_quotes

            if self.__line[i] == "," and not in_quotes:
                break

        next = (
            self.__line[self.__index : i + 1].rstrip(",").strip('"').replace('"', '"')
        )
        self.__index = i + 1

        return next

    next = __next__


def __parse_altitude(str):
    str = str.lower()
    if str.endswith("ft") or str.endswith("f"):
        str = str.rstrip("ft")
        return int(float(str) * 0.3048)
    else:
        str = str.rstrip("m")
        if len(str) > 0:
            return int(float(str))
        else:
            return None


def __parse_coordinate(str):
    str = str.lower()
    negative = str.endswith("s") or str.endswith("w")
    is_lon = str.endswith("e") or str.endswith("w")
    str = str.rstrip("sw") if negative else str.rstrip("ne")

    # degrees + minutes / 60
    if is_lon:
        a = int(str[:3]) + float(str[3:]) / 60
    else:
        a = int(str[:2]) + float(str[2:]) / 60

    if negative:
        a *= -1
    return a


def __parse_length(str):
    str = str.lower()
    if str.endswith("m"):
        str = str.rstrip("m")
        return int(float(str))
    else:
        return None


def parse_seeyou_waypoints(lines, bounds=None):
    waypoint_list = WaypointList()
    cherrypy.log('in parse_seeyou_waypoints function:')

    #gfp 241210: modified to wait for header line before processing
    #gfp 241210: added 'ISO-8859-2' decoding for correct cherrypy logging display

    #gfp 241208 added to print out all lines in selected .CUP file
    # wpnum = 0
    # for byteline in lines:
    #     wpnum = wpnum + 1
    #     line = byteline.decode('ISO-8859-2')

    header = 'name,code,country,lat,lon,elev,style,rwdir,rwlen,freq,desc'

    wpnum = 0
    for byteline in lines:
        wpnum = wpnum + 1
        line = byteline.decode('ISO-8859-2') #gfp 241210: added 'ISO-8859-2' decoding for correct cherrypy logging display
        line = line.strip()
        if line == "name,code,country,lat,lon,elev,style,rwdir,rwlen,freq,desc":
            continue

        # cherrypy.log('in for loop: wpnum = %s line = %s' %(wpnum, line))
#        cherrypy.log(f'for loop row {wpnum}: {line}')

        #check for blank lines or comments
        if line == "" or line.startswith("*"):
            continue

        if header in line: 
            cherrypy.log(f'header line found at row {wpnum}: {line}')
            continue #skip to next line (first waypoint line)

        if line == "-----Related Tasks-----":
            cherrypy.log('In -----Related Tasks----: line = %s' % line)
            break

        # cherrypy.log('in for loop before line = __CSVLine(line): wpnum = %s' %wpnum)

        fields = []
        # line = __CSVLine(line)
        CSVline = __CSVLine(line)
        # cherrypy.log(f'row {wpnum}: line = __CSVLine(line) ->> {line}')

        # while line.has_next():
        #     fields.append(next(line))

        while CSVline.has_next():
            fields.append(next(CSVline))


        #display fields for this line
        # cherrypy.log('extracted fields for line = %s' %wpnum)
        # idx = 0
        # for field in fields:
        #     cherrypy.log(f' field[{idx}] = {field}')
        #     idx += 1

   


        if len(fields) < 6:
            continue

        lat = __parse_coordinate(fields[3])
        if bounds and (lat > bounds.top or lat < bounds.bottom):
            continue

        lon = __parse_coordinate(fields[4])
        if bounds and (lon > bounds.right or lon < bounds.left):
            continue

        wp = Waypoint()
        wp.lat = lat
        wp.lon = lon
        wp.altitude = __parse_altitude(fields[5])
        wp.name = fields[0].strip()
        wp.country_code = fields[2].strip()

        # cherrypy.log('waypoint %s: name = %s' %(wpnum, wp.name))


        if len(fields) > 6 and len(fields[6]) > 0:
            wp.cup_type = int(fields[6])

        if len(fields) > 7 and len(fields[7]) > 0:
            wp.runway_dir = int(fields[7])

        if len(fields) > 8 and len(fields[8]) > 0:
            wp.runway_len = __parse_length(fields[8])

        if len(fields) > 9 and len(fields[9]) > 0:
            wp.freq = float(fields[9])

        if len(fields) > 10 and len(fields[10]) > 0:
            wp.comment = fields[10].strip()

        # cherrypy.log(f'waypoint {wpnum}: {wp.name}, {wp.lat:.3f}, {wp.lon:.3f}')

        #gfp print out current 'bounds' params
        # cherrypy.log(f'bounds = {bounds}')
 
        waypoint_list.append(wp)
     

    return waypoint_list
