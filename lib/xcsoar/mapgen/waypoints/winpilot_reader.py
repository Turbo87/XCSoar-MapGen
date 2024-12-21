# -*- coding: utf-8 -*-
from xcsoar.mapgen.waypoints.waypoint import Waypoint
from xcsoar.mapgen.waypoints.list import WaypointList
import cherrypy

def __parse_altitude(str):
    # cherrypy.log(f'parse_altitude({str})')
    str = str.lower()
    if str.endswith("ft") or str.endswith("f"):
        str = str.rstrip("ft")
        return int(str) * 0.3048
    else:
        str = str.rstrip("m")
        # cherrypy.log(f'parse_altitude:str = {str})')
        float_alt = float(str)
        # cherrypy.log(f'parse_altitude:float_alt = {float_alt})')
        int_alt = int(float_alt)
        # cherrypy.log(f'parse_altitude:int_alt = {int_alt})')

    return int(int_alt)


#Winpilot .DAT file lat/lon formats
# Latitude, Longitude: in one of the following formats (ss=seconds, dd = decimals):
# dd:mm:ss (for example: 36:15:20N)
# dd:mm.d (for example: 36:15.3N)
# dd:mm.dd (for example: 36:15.33N)
# dd:mm.ddd (for example: 36:15.333N)
def __parse_coordinate(str):
    # cherrypy.log(f'winpilot  parse_coordinate({str})')

    str = str.lower()
    negative = str.endswith("s") or str.endswith("w")
    str = str.rstrip("sw") if negative else str.rstrip("ne")

    # cherrypy.log(f'parse_coordinate before str.split: str = {str}')

    strsplit = str.split(":")
    # cherrypy.log(f'parse_coordinate after str.split into {len(strsplit)} elements')
    if len(strsplit) < 2:
        return None

    if len(strsplit) == 2:
        # cherrypy.log(f'parse_coordinate in 2 element block')
        # degrees + minutes / 60
        a = int(strsplit[0]) + float(strsplit[1]) / 60
        # cherrypy.log(f'parse_coordinate in 2 element block: a = {a}')

    if len(strsplit) == 3:
        # cherrypy.log(f'parse_coordinate in 3 element block')
        # degrees + minutes / 60 + seconds / 3600
        a = int(str[0]) + float(str[1]) / 60 + float(str[2]) / 3600
        # cherrypy.log(f'parse_coordinate in 3 element block: a = {a}')

    if negative:
        a *= -1

    # cherrypy.log(f'parse_coordinate just before return with a = {a}')

    return a


def parse_winpilot_waypoints(lines):
    # cherrypy.log('in parse_winpilot_waypoints function:')

    waypoint_list = WaypointList()
    wpnum = 0
    for byteline in lines:
        wpnum += 1
        # cherrypy.log(f'winpilot line {wpnum}: {byteline}')

        line = byteline.decode('ISO-8859-2') #gfp 241210: added 'ISO-8859-2' decoding for correct cherrypy logging display
        line = line.strip()
        if line == "" or line.startswith("*"):
            continue
        # cherrypy.log(f'winpilot line {wpnum}: {line}')

        fields = line.split(",")
        # cherrypy.log(f'winpilot line {wpnum}: fields = {fields}')
        # cherrypy.log(f'winpilot line {wpnum}: line splits into {len(fields)} fields')
        if len(fields) < 6:
            continue



        # fieldnum = 0
        # for field in fields:
        #     cherrypy.log(f'field {fieldnum} = {field}')
        #     fieldnum += 1

        wp = Waypoint()
        wp.lat = __parse_coordinate(fields[1])
        wp.lon = __parse_coordinate(fields[2])
        wp.altitude = __parse_altitude(fields[3])
        wp.name = fields[5].strip()

        # cherrypy.log(f'waypoint {wpnum}: {wp.name}, {wp.lat:.3f}, {wp.lon:.3f}')

        waypoint_list.append(wp)



    return waypoint_list
