# -*- coding: utf-8 -*-
from xcsoar.mapgen.waypoints.seeyou_reader import parse_seeyou_waypoints
from xcsoar.mapgen.waypoints.winpilot_reader import parse_winpilot_waypoints
import cherrypy

#cherrypy.log(data.decode('utf-8'))

def parse_waypoint_file(filename, file=None):
    # cherrypy.log('in parse_waypoint_file: filename = %s' % filename)
    lines = 0 #gfp added so 'lines' object stays in scope
    if not file:
        cherrypy.log('in parse_waypoint_file: if not file block with filename = %s' % filename)

    else:
   #     # #241207 gfp bugfix: parser fcns need 'lines' (list of lines) vs 'file'
        lines = file.readlines()

        # cherrypy.log('in parse_waypoint_file: %s lines read from %s' %(lines.count, filename))
        cherrypy.log('in parse_waypoint_file: %s lines read from %s' %(len(lines), filename))
        # wpnum = 0
        # for line in lines:
        #     wpnum+=1
        #     decoded_line = line.decode('ISO-8859-2')
        #     cherrypy.log('line%s: %s' % (wpnum, decoded_line))

    if filename.lower().endswith(".xcw") or filename.lower().endswith(".dat"):
        return parse_winpilot_waypoints(lines)
    elif filename.lower().endswith(".cup"):
        # cherrypy.log('in parse_waypoint_file filename.lower().endswith(".cup"): filename = %s' % filename)
        return parse_seeyou_waypoints(lines)#241207 gfp bugfix:
    else:
        # cherrypy.log('in parse_waypoint_file ELSE block: filename = %s' % filename)

        raise RuntimeError(
            "Waypoint file {} has an unsupported format.".format(filename)
        )
