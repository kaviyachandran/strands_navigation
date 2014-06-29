#!/usr/bin/env python

import sys
import rospy


from geometry_msgs.msg import Pose
from geometry_msgs.msg import Point

from visualization_msgs.msg import *
from interactive_markers.interactive_marker_server import *

from strands_navigation_msgs.msg import TopologicalNode
from topological_navigation.topological_map import *


class vertex_controllers(object):

    def __init__(self, map_name) :
        self.in_feedback=False
        self.topo_map = topological_map(map_name)
        self._vertex_server = InteractiveMarkerServer(map_name+"_zones")
        



    def update_map(self, map_name) :

        self.topo_map = topological_map(map_name)
        self._vertex_server.clear()
        
        for node in self.topo_map.nodes :
            node._get_coords()
            count=0
            for i in node.vertices :
                #print i[0], i[1]
                Vert = Point()
                Vert.z = 0.05
                Vert.x = node.px + i[0]
                Vert.y = node.py + i[1]
                vertname = "%s-%d" %(node.name, count)
                Pos = Pose()
                Pos.position = Vert
                self._vertex_marker(vertname, Pos, vertname)
                count+=1


    def _vertex_marker(self, marker_name, pose, marker_description="vertex marker"):
        # create an interactive marker for our server
        marker = InteractiveMarker()
        marker.header.frame_id = "/map"
        marker.name = marker_name
        marker.description = marker_description

        # the marker in the middle
        box_marker = Marker()
        box_marker.type = Marker.SPHERE
        box_marker.scale.x = 0.25
        box_marker.scale.y = 0.25
        box_marker.scale.z = 0.25
        box_marker.color.r = 0.5
        box_marker.color.g = 0.0
        box_marker.color.b = 0.5
        box_marker.color.a = 0.8

        # create a non-interactive control which contains the box
        box_control = InteractiveMarkerControl()
        box_control.always_visible = True
        #box_control.always_visible = False
        box_control.markers.append( box_marker )
        marker.controls.append( box_control )

        # move x
        control = InteractiveMarkerControl()
        control.orientation.w = 1
        control.orientation.x = 0
        control.orientation.y = 1
        control.orientation.z = 0
        control.always_visible = False
#        control.name = "move_x"
#        control.interaction_mode = InteractiveMarkerControl.MOVE_AXIS
        control.name = "move_plane"
        control.interaction_mode = InteractiveMarkerControl.MOVE_PLANE
        marker.controls.append(control)


        self._vertex_server.insert(marker, self._vertex_feedback)
        self._vertex_server.applyChanges()

        if pose is not None:
            pose.position.z=pose.position.z+0.15
            self._vertex_server.setPose( marker.name, pose )
            self._vertex_server.applyChanges()


    def _vertex_feedback(self, feedback):
        self.in_feedback=True
        vertex_name = feedback.marker_name.rsplit('-', 1)
        node_name = vertex_name[0]
        vertex_index = int(vertex_name[1])
        self.topo_map.update_node_vertex(node_name, vertex_index, feedback.pose)
        self.update_needed=True

        
    def reset_feedback(self) :
        self.in_feedback=False
        
    def reset_update(self) :
        self.update_needed=False

    def clear():
        self._vertex_server.clear()
        self._vertex_server.applyChanges()
