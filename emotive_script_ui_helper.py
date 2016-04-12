# EmotiveModeler CAD plugin for Rhino, 2016
# Created by Philippa Mothersill as part of her Masters at the MIT Media Lab (2014) - read more here: http://emotivemodeler.media.mit.edu/
# Advised by Mike Bove, Object-Based Media group, and helped by Itamar Belsen, Jane Cutler and Anna Walsh
# Copyright 2016 Massachusetts Institute of Technology

import rhinoscriptsyntax as rs
import math
import json
import construction_functions
import config
import emotion_class
import os

# This class takes all tasks related to drawing objects in the main Rhino UI window from emotive_script_ui. These include: modifying user dictionary, adding to system dictionary, drawing emotion object, rendering emotion object, and saving emotion object

# Generate dictionary objects
user_emotion_dict_file = open(config.user_emotion_dictionary_filename).read()
user_emotion_dict = json.loads(user_emotion_dict_file)
system_emotion_dict_file = open(config.system_emotion_dictionary_filename).read()
system_emotion_dict = json.loads(system_emotion_dict_file)

class Drawable_Object():
	def __init__(self, object_id, emotion_id, user_emotion_dict, revert=False):
		self.object_id = object_id
		self.user_emotion_dict = user_emotion_dict
		self.system_emotion_dict = system_emotion_dict #might take too long
		self.emotion = self.__get_emotion_object(emotion_id, revert)

	# Draws Drawable_Object based on its form.
	def draw(self):
		self.__get_shape()
		self.__clear_all()
		# reset_view()
		self.__get_shape()
		self.__reset_view()

	def get_emotion(self):
		return self.emotion

	# Returns shape of constructed object
	def __get_shape(self):
		obj = construction_functions.ObjectConstruction(self.object_id, self.emotion)
		(spine_curve, end_plane) = obj.create_form()
		return (spine_curve, end_plane)

	# Returns Emotion object based on string representation of emotion.
	def __get_emotion_object(self, emotion_id, revert):
		with open(config.primary_emotion_taxonomy_filename) as primary_emotion_taxonomy_file:	# Emotion taxonomy for primary emotions
			primary_emotion_taxonomy = json.loads(primary_emotion_taxonomy_file.read())
		with open(config.primary_scaling_factors_filename) as primary_scaling_factors_file:		# Scaling factors for primary emotions
			primary_scaling_factors = json.loads(primary_scaling_factors_file.read())

		return emotion_class.Emotion(emotion_id, self.user_emotion_dict, self.system_emotion_dict, primary_emotion_taxonomy, primary_scaling_factors, revert)

	# Resets view
	def __reset_view(self):
		rs.ViewCPlane(None, rs.WorldXYPlane() )
		rs.Command("_Zoom _A _E _Enter")
		rs.Command("_SelAll")
		rs.Command("_Shade _d=r _Enter")
		rs.Command("_SelNone")
		# execute colour change in here??

	# Clears everything drawn
	def __clear_all(self):
		rs.Command("_SelAll")
		rs.Command("Delete")

# def get_modified_emotion_breakdown_proportionally(emotion_object):
# 	emotions_contained = emotion_object.get_emotions_contained()
# 	emotion_breakdown = emotion_object.get_breakdown()
# 	for emotion in emotions_contained:
# 		delta_emotion = int(rs.GetString("For emotion '"+emotion+"', enter an integer value to increase the amount of that emotion by. (To decrease, enter a negative integer.)"))
# 		emotion_id = drawable.get_emotion().get_emotion_id()
# 		if emotion_id in config.primary_emotions:
# 			emotion_breakdown[emotion_id] += delta_emotion
# 		else:
# 			# determine how to scale emotion
# 			e_breakdown_multiplied = {}
# 			for e in e_breakdown:
# 				e_breakdown_multiplied[e] = delta_emotion * e_breakdown[e]
# 			# implement scaling
# 			for e in emotion_breakdown:
# 				emotion_breakdown[e] += e_breakdown_multiplied[e]
# 				# prevent negatives
# 				if emotion_breakdown[e] < 0:
# 					emotion_breakdown[e] = 0
# 	return emotion_breakdown


# Modifies the user dictionary and writes it to file
def modify_user_dictionary(object_id, emotion_id, emotion_breakdown):
	# update entry for emotion_id in user_emotion_dict
	user_emotion_dict[emotion_id] = emotion_breakdown
	# update emotions that contain this emotion
	emotions_contained = emotion_id.split(".")
	for key in user_emotion_dict:
		key_emotions = key.split(".")
		# check to see if all emotions in emotion_id are contained in key
		contains_all_so_far = True
		for e in emotions_contained:
			if e not in key_emotions:
				contains_all_so_far = False
				break
		# if so, updates user_emotion_dict_data
		if contains_all_so_far and key != emotion_id:
			# remove from dictionary and put back correctly
			user_emotion_dict.pop(key)
			if object_id:
				drawable = Drawable_Object(object_id, key, user_emotion_dict)
			key_breakdown = drawable.get_emotion().get_breakdown()
			user_emotion_dict[key] = key_breakdown
	# write user_emotion_dict data to file
	with open(config.user_emotion_dictionary_filename, 'w') as outfile:
		json.dump(user_emotion_dict, outfile)

def add_to_system_dictionary(emotion_id, emotion_breakdown):
	system_emotion_dict[emotion_id] = emotion_breakdown
	with open(config.system_emotion_dictionary_filename, 'w') as outfile:
		json.dump(system_emotion_dict, outfile)

# Draws Drawable_Object with type and emotion
def draw_emotion_object(object_id, emotion_id, revert=False):
	drawable = Drawable_Object(object_id, emotion_id, user_emotion_dict, revert)
	drawable.draw()
	return drawable

# Renders object
def render_emotion_object(object_id, emotion_id):
	outpath = config.outpath_render + object_id+"_"+emotion_id
	if not os.path.exists(outpath):
		os.makedirs(outpath)
	# set render view to perspective view
	rs.CurrentView("Perspective")
	# set animation turntable properties
	rs.Command("-SetTurntableAnimation 30 Clockwise png RenderFull Perspective " + emotion_id + " -Enter")
	# record animation to target folder
	rs.Command("-RecordAnimation  _TargetFolder " + outpath + " -Enter")

# Saves object
def save_emotion_object(object_id, emotion_id):
	outpath = config.outpath_save + object_id+"_"+emotion_id
	rs.Command("-Save  " + outpath + " -Enter")
	rs.MessageBox("Saved!")

def exit_script():
	rs.Exit()

# def switch_on_new_emotion(object_id, emotion_id=None):
# 	if not emotion_id:
# 		emotion_id = get_emotion_type(object_id)
# 		drawable = draw_emotion_object(object_id, emotion_id)

# 	if next_action == "m":								# modify emotion
# 		drawable = draw_emotion_object(object_id, emotion_id)
# 		emotion_object = drawable.get_emotion()
# 		direct_or_proportional = get_modify_directly_or_proportionally(emotion_object, emotion_id)
# 		emotion_breakdown = {}
# 		if direct_or_proportional == "c":
# 			emotion_breakdown = get_modified_emotion_breakdown_directly(emotion_object)
# 		elif direct_or_proportional == "p":		# no other options
# 			emotion_breakdown = get_modified_emotion_breakdown_proportionally(emotion_object)
# 		modify_user_dictionary(object_id, emotion_id, emotion_breakdown)
# 		draw_emotion_object(object_id, emotion_id)
# 		switch_on_new_emotion(object_id, emotion_id)

# Fixes data reload problem in Rhino
construction_functions = reload(construction_functions)
emotion_class = reload(emotion_class)
config = reload(config)