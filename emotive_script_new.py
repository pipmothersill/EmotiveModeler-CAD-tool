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

# Generate user_emotion_dict object
# TODO: what to do if doesn't exist
user_emotion_dict_file = open(config.user_emotion_dictionary_filename).read()
user_emotion_dict = json.loads(user_emotion_dict_file)

class Drawable_Object():
	def __init__(self, object_id, emotion_id, user_emotion_dict):
		self.object_id = object_id
		self.user_emotion_dict = user_emotion_dict
		self.emotion = self.__get_emotion_object(emotion_id)

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
	def __get_emotion_object(self, emotion_id):
		with open(config.system_emotion_dictionary_filename) as system_emotion_dict_file:		# Word dictionary of default emotion breakdowns
			system_emotion_dict = json.loads(system_emotion_dict_file.read())
		with open(config.primary_emotion_taxonomy_filename) as primary_emotion_taxonomy_file:	# Emotion taxonomy for primary emotions
			primary_emotion_taxonomy = json.loads(primary_emotion_taxonomy_file.read())
		with open(config.primary_scaling_factors_filename) as primary_scaling_factors_file:		# Scaling factors for primary emotions
			primary_scaling_factors = json.loads(primary_scaling_factors_file.read())

		return emotion_class.Emotion(emotion_id, self.user_emotion_dict, system_emotion_dict, primary_emotion_taxonomy, primary_scaling_factors)

	# Resets view
	def __reset_view(self):
		rs.ViewCPlane(None, rs.WorldXYPlane() )
		rs.Command("_Zoom _A _E _Enter")
		rs.Command("_SelAll")
		rs.Command("_Shade _d=r _Enter")
		rs.Command("_SelNone")

	# Clears everything drawn
	def __clear_all(self):
		rs.Command("_SelAll")
		rs.Command("Delete")


# Returns object type from input
def get_obj_type():
	object_id = ""
	while object_id not in config.object_types and object_id not in config.exit_commands:
		object_id = rs.GetString('Enter object type (B=Bottle)')
	if object_id in config.exit_commands:
		return None
	else:
		return config.object_types[object_id]

# Returns emotion type from input
def get_emotion_type(object_id):
	emotion_id = ""
	while emotion_id == "":
		emotion_id = rs.GetString('Enter emotion of ' + object_id + ". Separate emotions with periods.")
	return emotion_id

# Returns next action from input
def get_next_action():
	actions = ["e","a","m","r","s","n"]
	actions.extend(config.exit_commands)
	next_action = ""
	while next_action not in actions:
		next_action = rs.GetString('Enter (e) for new emotion, (a) to add emotion, (m) to modify, (r) to render animation, (s) to save, or (n) for new object:')
	return next_action

# Returns emotions to add from input
def get_added_emotions():
	added_emotion = rs.GetString('Enter emotions to add. Separate emotions with periods.')
	return added_emotion

def get_modified_emotion_breakdown_directly(emotion_object):
	emotion_breakdown = emotion_object.get_breakdown()
	for primary_emotion in emotion_breakdown:
		new_value = int(rs.GetString("'"+str(primary_emotion)+"' is currently set to "+str(emotion_breakdown[primary_emotion])+". Enter (0) or (int) to reset it to that value."))
		# prevent negatives
		if new_value < 0:
			new_value = 0
		emotion_breakdown[primary_emotion] = new_value
	return emotion_breakdown

def get_modified_emotion_breakdown_proportionally(emotion_object):
	emotions_contained = emotion_object.get_emotions_contained()
	emotion_breakdown = emotion_object.get_breakdown()
	for emotion in emotions_contained:
		delta_emotion = int(rs.GetString("For emotion '"+emotion+"', enter an integer value to increase the amount of that emotion by. (To decrease, enter a negative integer.)"))
		emotion_id = drawable.get_emotion().get_emotion_id()
		if emotion_id in config.primary_emotions:
			emotion_breakdown[emotion_id] += delta_emotion
		else:
			# determine how to scale emotion
			e_breakdown_multiplied = {}
			for e in e_breakdown:
				e_breakdown_multiplied[e] = delta_emotion * e_breakdown[e]
			# implement scaling
			for e in emotion_breakdown:
				emotion_breakdown[e] += e_breakdown_multiplied[e]
				# prevent negatives
				if emotion_breakdown[e] < 0:
					emotion_breakdown[e] = 0
	return emotion_breakdown

# Returns 'c' if object is to be modified directly and 'p' if it is to be modified proportionally
def get_modify_directly_or_proportionally(emotion_object, emotion_id):
	emotions_contained = emotion_object.get_emotions_contained()
	if len(emotions_contained) > 1:
		actions = ["p","c"]
		next_action = ""
		while next_action not in actions:
			next_action = rs.GetString(emotion_id+" is an emotion that combines emotions. Enter (p) to modify the proportions of emotions, or (c) to continue modifying directly.")
	else:
		next_action = "c"
	return next_action

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
			drawable = Drawable_Object(object_id, key, user_emotion_dict)
			key_breakdown = drawable.get_emotion().get_breakdown()
			user_emotion_dict[key] = key_breakdown
	# write user_emotion_dict data to file
	with open(config.user_emotion_dictionary_filename, 'w') as outfile:
		json.dump(user_emotion_dict, outfile)

# Draws Drawable_Object with type and emotion
def draw_emotion_object(object_id, emotion_id):
	drawable = Drawable_Object(object_id, emotion_id, user_emotion_dict)
	drawable.draw()
	return drawable

def exit_script():
	rs.Exit()

def switch_on_new_emotion(object_id, emotion_id=None):
	if not emotion_id:
		emotion_id = get_emotion_type(object_id)
		drawable = draw_emotion_object(object_id, emotion_id)
	# Perform next action: either new emotion, add, modify, render, save, or new object
	next_action = get_next_action()
	
	if next_action == "e":									# new emotion
		switch_on_new_emotion(object_id)
	
	elif next_action == "a":								# add emotion
		added_emotion = get_added_emotions()
		emotion_id += "."+added_emotion
		draw_emotion_object(object_id, emotion_id)
		switch_on_new_emotion(object_id, emotion_id)
	
	elif next_action == "m":								# modify emotion
		drawable = draw_emotion_object(object_id, emotion_id)
		emotion_object = drawable.get_emotion()
		direct_or_proportional = get_modify_directly_or_proportionally(emotion_object, emotion_id)
		emotion_breakdown = {}
		if direct_or_proportional == "c":
			emotion_breakdown = get_modified_emotion_breakdown_directly(emotion_object)
		elif direct_or_proportional == "p":		# no other options
			emotion_breakdown = get_modified_emotion_breakdown_proportionally(emotion_object)
		modify_user_dictionary(object_id, emotion_id, emotion_breakdown)
		draw_emotion_object(object_id, emotion_id)
		switch_on_new_emotion(object_id, emotion_id)
	
	elif next_action == "r":								# render
		outpath = config.outpath_render + emotion_id
		if not os.path.exists(outpath):
			os.makedirs(outpath)
		# set render view to perspective view
		rs.CurrentView("Perspective")
		# set animation turntable properties
		rs.Command("-SetTurntableAnimation 30 Clockwise png RenderFull Perspective " + emotion_id + " -Enter")
		# record animation to target folder
		rs.Command("-RecordAnimation  _TargetFolder " + outpath + " -Enter")
		switch_on_new_emotion(object_id, emotion_id)
	
	elif next_action == "s":								# save
		outpath = config.outpath_save + emotion_id
		rs.Command("-Save  " + outpath + " -Enter")
		switch_on_new_emotion(object_id, emotion_id)
	
	elif next_action == "n":								# new object
		switch_on_new_object()

	elif next_action in config.exit_commands:
		exit_script()

def switch_on_new_object():
	# Initialize and draw new object in neutral shape
	object_id = get_obj_type()
	if object_id != None:
		draw_emotion_object(object_id, "neutral")
		# Draw object based on input emotion
		switch_on_new_emotion(object_id)
	else:
		exit_script()


if __name__ == "__main__":
	# Fixes data reload problem in Rhino
	construction_functions = reload(construction_functions)
	emotion_class = reload(emotion_class)
	config = reload(config)
	# clear_all()
	# reset_view()
	rs.Command("_SelAll")
	rs.Command("Delete")
	rs.ViewCPlane(None, rs.WorldXYPlane() )
	rs.Command("_Zoom _A _E _Enter")
	rs.Command("_SelAll")
	rs.Command("_Shade _d=r _Enter")
	rs.Command("_SelNone")

	next_action = ""

	while next_action != "n" and next_action not in config.exit_commands:
		next_action = rs.GetString('Enter (n) for new object')
		if next_action == "n":
			switch_on_new_object()
		else:
			exit_script()



