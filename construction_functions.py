# EmotiveModeler CAD plugin for Rhino, 2016
# Created by Philippa Mothersill as part of her Masters at the MIT Media Lab (2014) - read more here: http://emotivemodeler.media.mit.edu/
# Advised by Mike Bove, Object-Based Media group, and helped by Itamar Belsen, Jane Cutler and Anna Walsh
# Copyright 2016 Massachusetts Institute of Technology

import rhinoscriptsyntax as rs
import math
import json
import config
import emotion_class
import random

# Creates Rhino objects

# Fixing data reload problem
emotion_class = reload(emotion_class)

class ObjectConstruction:

	# object_id: string representation of object type
	# emotion_object: instance of the Emotion class
	def __init__(self, object_id, emotion_object):
		with open(config.object_features_filename) as object_file:								# Contains object properties
			object_data = json.loads(object_file.read())

		self.object_id = object_id

		# Initialize object
		self.object_properties = object_data["object_name"][self.object_id]
		self.emotion = emotion_object
		self.emotion_properties = self.emotion.get_properties()

		self.x_points = []
		self.dimensions = self.__calculate_geometry()

	def create_form(self):
		render_color = self.__set_render_color()
		spine_curve = self.__generate_spine()
		end_plane = self.__generate_form_levels(spine_curve)
		return (spine_curve, end_plane)

	def __set_render_color(self):
		r = self.emotion_properties["color"]["r"]
		g = self.emotion_properties["color"]["g"]
		b = self.emotion_properties["color"]["b"]
		rs.LayerColor("Default", (r, g, b))

	def __calculate_geometry(self):
		global_volume = self.object_properties["global_volume"]
		global_width = self.object_properties["global_width"]
		# Average aspect ratios
		vertical_AR = self.emotion_properties["global_vertical_AR"]
		horizontal_AR = self.emotion_properties["global_horizontal_AR"]

		# Calculations
		global_height = global_width/vertical_AR
		global_depth = global_width/horizontal_AR
		actual_width = global_width/math.pow(((global_width*global_height*global_depth)/(global_volume)), 1.0/3)
		actual_height = actual_width/vertical_AR
		actual_depth = actual_width/horizontal_AR

		dimensions = {}
		dimensions["actual_width"] = actual_width
		dimensions["actual_height"] = actual_height
		dimensions["actual_depth"] = actual_depth
		dimensions["vertical_AR"] = vertical_AR

		return dimensions

	def __generate_spine(self):
		a_term = (self.emotion_properties["spine_equation"]["a_term"]*self.dimensions["actual_height"])
		b_term = (self.emotion_properties["spine_equation"]["b_term"]*self.dimensions["actual_height"])
		if b_term == 0:
			b_term = 1
		h_term = (self.emotion_properties["spine_equation"]["h_term"]*self.dimensions["actual_height"])
		k_term = (self.emotion_properties["spine_equation"]["k_term"]*self.dimensions["actual_height"])

		spine_points_list = []

		for loft_index in xrange(self.object_properties["number_of_lofts"]):
				y = 0
				z = loft_index * (self.dimensions["actual_height"] / self.object_properties["number_of_lofts"])
				x = h_term + math.sqrt(abs(math.pow(a_term,2.0) * (1 - ((math.pow(z-k_term,2.0))/math.pow(b_term,2.0))))) #equation of circle
				self.x_points.append(x)
				spine_points_list.append(rs.AddPoint([x, y, z]))
		spine_curve = rs.AddCurve(spine_points_list, 1)

		return spine_curve

	def __generate_form_levels(self, spine_curve):
		crvdomain = rs.CurveDomain(spine_curve)
		printedState = ""
		crosssection_planes = []
		crosssection_plane_nums = []
		crosssections = []
		t_step = (crvdomain[1] - crvdomain[0]) / (self.object_properties["number_of_lofts"]-1)
		t = crvdomain[0]
		for t in rs.frange(crvdomain[0], crvdomain[1], t_step):
			if(self.emotion_properties["vertical_AR"][str(int(t+1))] != None):		
				crvcurvature = rs.CurveCurvature(spine_curve, t)
				crosssectionplane = None
				if not crvcurvature:
					crvPoint = rs.EvaluateCurve(spine_curve, t)
					crvTangent = rs.CurveTangent(spine_curve, t)
					crvPerp = (0,0,1)
					crvNormal = rs.VectorCrossProduct(crvTangent, crvPerp)
					printedState = printedState + str(crvNormal)
					crosssectionplane = rs.PlaneFromNormal(crvPoint, crvTangent)
					if(t==0):
						crosssectionplane = rs.PlaneFromNormal([0,0,0], [0,0,1])
				else:
					crvPoint = crvcurvature[0]
					crvTangent = crvcurvature[1]
					crvPerp = rs.VectorUnitize(crvcurvature[4])
					crvNormal = rs.VectorCrossProduct(crvTangent, crvPerp)
					printedState = printedState + str(crvNormal)
					crosssectionplane = rs.PlaneFromNormal(crvPoint, crvTangent, crvNormal)
				if crosssectionplane:
					crosssection_planes.append(crosssectionplane)
					crosssection_plane_nums.append(str(int(t+1)))
		if len(crosssection_plane_nums) > 0:
			last_element = crosssection_plane_nums.pop(len(crosssection_plane_nums)-1)
			crosssection_plane_nums.insert(0, last_element)
		for index in xrange(len(crosssection_plane_nums)):
			crosssections.append(self.__generate_individual_levels(crosssection_planes[index], crosssection_plane_nums[index]))
		if not crosssections: return
		crosssections.append(crosssections.pop(0))
		rs.AddLoftSrf(crosssections,closed=False,loft_type=int(round(self.emotion_properties["vertical_wrapping"])))
				
		return crosssection_planes[0]
	
	def __generate_individual_levels(self, crosssectionplane, loft_height):
		cplane = rs.ViewCPlane( None, crosssectionplane)
		level_points = []
		spikiness = self.emotion_properties["spikiness"] # max spikiness = 1
		scaling_factor_aid = 0.2*spikiness
		#draws profile curves on each spine level
		for i in xrange(self.emotion_properties["horizontal_AR"][loft_height]["points_in_curve"]):
			scaling_factor = 1 - scaling_factor_aid if i%2 == 0 else 1 #ranges from a difference in 0.8 and 1 (no difference)
			angle = 2 * math.pi * i / self.emotion_properties["horizontal_AR"][loft_height]["points_in_curve"]
			x_point = scaling_factor*self.dimensions["actual_height"] * self.dimensions["vertical_AR"] * self.emotion_properties["vertical_AR"][loft_height] * self.emotion_properties["horizontal_AR"][loft_height]["level_horizontal_AR_x"] * math.cos(angle) / 2
			y_point = scaling_factor*self.dimensions["actual_height"] * self.dimensions["vertical_AR"] * self.emotion_properties["vertical_AR"][loft_height] * self.emotion_properties["horizontal_AR"][loft_height]["level_horizontal_AR_y"] * math.sin(angle) / 2
			z_point = 0
			point = rs.XformCPlaneToWorld([x_point, y_point, z_point], cplane)
			level_points.append(rs.AddPoint(point))

		connecting_point = level_points[0]
		level_points.append(rs.AddPoint(connecting_point))

		level_curve = rs.AddCurve(level_points,self.emotion_properties["horizontal_AR"][str(loft_height)]["horizontal_smoothness"])

		#twists curve start point 180deg if it is below the spine_x point (to make sure loft doesn't twist)
		crvStart = rs.CurveStartPoint(level_curve)
		if crvStart[0] <= self.x_points[int(loft_height)-1]:
			crvDomain = rs.CurveDomain(level_curve)
			rs.CurveSeam(level_curve, (crvDomain[0] + crvDomain[1]) / 2)

		# add planar surface to top and bottom of bottle
		if loft_height =="5" or loft_height=="1":
			rs.AddPlanarSrf(level_curve)

		# hide curves and points on level profiles
		rs.HideObjects(level_curve)
		rs.HideObjects(level_points)

		# object finishing features 
		if (self.object_id == "Bottle"):
			if loft_height == "5":
				rs.AddCylinder(cplane,14.5,7.4,cap=True)

		if (self.object_id == "Chair"):
			if loft_height == "5":
				rs.AddCylinder(cplane,14.5,7.4,cap=True)

		if (self.object_id == "Jewelry"):
			if loft_height == "5":
				major_radius = 5.0
				minor_radius = major_radius - 1.5
				# rotated_cplane = rs.RotatePlane(cplane, 45.0, cplane.XAxis)
				direction = rs.AddPoint((0,0,1))
				rs.AddTorus(cplane.Origin, major_radius, minor_radius, direction)

		if (self.object_id == "Totem"):
			if loft_height == "1":
				base_width = 80
				base_length = 60
				base_depth = -10
				base_points = [(-base_width/2,-base_length/2,0),(base_width/2,-base_length/2,0),(base_width/2,base_length/2,0),(-base_width/2,base_length/2,0),(-base_width/2,-base_length/2,base_depth),(base_width/2,-base_length/2,base_depth),(base_width/2,base_length/2,base_depth),(-base_width/2,base_length/2,base_depth)]
				rs.AddBox(base_points)

		
		return level_curve

