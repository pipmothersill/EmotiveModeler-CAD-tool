# EmotiveModeler CAD plugin for Rhino, 2016
# Created by Philippa Mothersill as part of her Masters at the MIT Media Lab (2014) - read more here: http://emotivemodeler.media.mit.edu/
# Advised by Mike Bove, Object-Based Media group, and helped by Itamar Belsen, Jane Cutler and Anna Walsh
# Copyright 2016 Massachusetts Institute of Technology

import math
import json
import config
import rhinoscriptsyntax as rs
import emotive_script_ui_helper

# Bulk of the emotion processing: uses dictionaries and user input to get all the shape's emotive properties (spine equation, aspect ratios, color, weight of 'primary' emotions)
class Emotion():

	# emotion: string value of this emotion
	# user_emotion_dict: emotion breakdowns specified by the user
	# system_emotion_dict: emotion breakdowns calculated by the system
	# primary_emotion_taxonomy: geometric representations for primary emotions
	# primary_scaling_factors: weights for combining primary emotions
	def __init__(self, emotion, user_emotion_dict, system_emotion_dict, primary_emotion_taxonomy, primary_scaling_factors, revert=False):
		self.user_emotion_dict = user_emotion_dict
		self.system_emotion_dict = system_emotion_dict
		self.primary_emotion_taxonomy = primary_emotion_taxonomy
		self.primary_scaling_factors = primary_scaling_factors

		# sort and alphabetize emotions in emotion
		self.emotions_contained = emotion.split(".")
		self.emotions_contained.sort()
		self.emotions_contained[:] = [e for e in self.emotions_contained if self.__is_emotion_valid(e)]
		if len(self.emotions_contained) == 0:
			self.emotion = "neutral"
		else:
			self.emotion = ".".join(self.emotions_contained)

		self.revert = revert
		self.primary_emotions_present = self.__get_emotions_present()
		self.sum_scaling_factors = self.__get_sum_scaling_factors()

	# Return string representation of emotion
	def get_emotion(self):
		return self.emotion

	# Return list of emotions contained (separated by '.')
	def get_emotions_contained(self):
		return self.emotions_contained

	# Return the primary emotion breakdown dictionary for a primary, secondary, or tertiary emotion.
	def get_breakdown(self, revert=False):
		self.revert = revert
		return self.__get_breakdown_helper(self.emotion, self.revert)

	# Return a dictionary of properties for a secondary emotion
	def get_properties(self):
		emotion_properties = {}
		if self.__is_primary_emotion():
			emotion_properties = self.primary_emotion_taxonomy[self.emotion]
		else:
			emotion_properties["spine_equation"] = self.__get_spine_equation()
			emotion_properties["global_vertical_AR"] = self.__get_value_number_property("global_vertical_AR")
			emotion_properties["global_horizontal_AR"] = self.__get_value_number_property("global_horizontal_AR")
			emotion_properties["vertical_AR"] = self.__get_vertical_AR()
			emotion_properties["horizontal_AR"] = self.__get_horizontal_AR()
			emotion_properties["vertical_wrapping"] = self.__get_value_number_property("vertical_wrapping")
			emotion_properties["color"] = self.__get_render_rgb()
			emotion_properties["spikiness"] = self.__get_spikiness()
		return emotion_properties

	def __is_emotion_valid(self, e):
		if e in self.system_emotion_dict:
			return True
		else:
			if e:
				user_response = rs.MessageBox("Word '"+e+"' not found. Would you like to add '"+e+"' to the dictionary?", 4 | 0)
				if user_response == 6: #user says 'yes'
					rs.MessageBox("'"+e+"' added to dictionary. Neutral object created to reflect '"+e+"'; add its emotive components using sliders.")
					neutral_emotion_breakdown = {"sadness": 0, "trust": 0, "anger": 0, "surprise": 0, "joy": 0, "fear": 0, "anticipation": 0, "disgust": 0}
					emotive_script_ui_helper.modify_user_dictionary(None, e, neutral_emotion_breakdown)
					emotive_script_ui_helper.add_to_system_dictionary(e, neutral_emotion_breakdown)
					return True
			return False

	# Return True if emotion is primary emotion and False otherwise
	def __is_primary_emotion(self):
		if self.emotion in config.primary_emotions:
			return True
		else:
			return False

	# Return the primary emotion breakdown dictionary for a primary, secondary, or tertiary emotion.
	def __get_breakdown_helper(self, emotion, revert=False):
		emotion_breakdown = {}
		if emotion in config.primary_emotions:				# primary emotion
			for p_emotion in config.primary_emotions:
				if p_emotion == emotion:
					emotion_breakdown[p_emotion] = 1
				else:
					emotion_breakdown[p_emotion] = 0
		else:												# secondary emotion
			# check if already in user dictionary if we are not reverting to previous shape
			if emotion in self.user_emotion_dict and not revert:
				emotion_breakdown = self.user_emotion_dict[emotion]
			# if we are reverting to previous shape or the emotion is not in the user dict
			elif (emotion in self.user_emotion_dict and revert) or (emotion not in self.user_emotion_dict):
				# check if emotion is one secondary adjective
				if emotion in self.system_emotion_dict:
					emotion_breakdown = self.system_emotion_dict[emotion]
				# check if emotion is multiple secondary emotions (tertiary)
				else:
					for e in self.emotions_contained:
						e_breakdown = self.__get_breakdown_helper(e)
						for value in e_breakdown:
							if value in emotion_breakdown:		# add emotions together
								emotion_breakdown[value] = emotion_breakdown[value] + e_breakdown[value]
							else:								# add new emotion
								emotion_breakdown[value] = e_breakdown[value]
		return emotion_breakdown

	# Return a list of primary emotions present in a secondary emotion
	def __get_emotions_present(self):
		emotion_breakdown = self.get_breakdown(self.revert)
		primary_emotions_present = []
		for primary_emotion in emotion_breakdown:
			if emotion_breakdown[primary_emotion] != 0:
				primary_emotions_present.append(primary_emotion)
		return primary_emotions_present

	# Return a dictionary of the sum of each scaling factors for all the primary emotions present in a secondary emotion
	def __get_sum_scaling_factors(self):
		sums = {}
		for weight in self.primary_scaling_factors["neutral"]:
			sums[weight] = 0
		for primary_emotion in self.primary_emotions_present:
			for weight in sums:
				# In the original word_emotion_dictionary, emotions either are present or aren't (0 or 1)
				multiplier = 1
				# Otherwise, look up what the user has set it to be
				if self.emotion in self.user_emotion_dict:
					multiplier = self.user_emotion_dict[self.emotion][primary_emotion]
				sums[weight] += self.primary_scaling_factors[primary_emotion][weight] * multiplier
		return sums

	# Return the spine equation for a secondary emotion
	def __get_spine_equation(self):
		spine_equation = {}
		if len(self.primary_emotions_present) == 0:			# set to neutral values
			spine_equation = self.primary_emotion_taxonomy["neutral"]["spine_equation"]
		else:
			for primary_emotion in self.primary_emotions_present:
				emotion_spine_equation = self.primary_emotion_taxonomy[primary_emotion]["spine_equation"]
				emotion_spine_equation_weighting = self.primary_scaling_factors[primary_emotion]["spine_weighting"]
				for term in emotion_spine_equation:			# a_term, b_term, h_term, k_term
					if term not in spine_equation:
						spine_equation[term] = 0
					multiplier = 1
					if self.emotion in self.user_emotion_dict:
						multiplier = self.user_emotion_dict[self.emotion][primary_emotion]
					spine_equation[term] += (emotion_spine_equation[term] * emotion_spine_equation_weighting * multiplier)/self.sum_scaling_factors["spine_weighting"]
		return spine_equation

	# Return 'spikiness' (min 0; max 1) for the construction_function. Spikiness does not have a scaling factor because it's equally important for all of the emotions
	# For now, it is not based on the 'magnitude' of each emotion represented, only which emotions are represented.
	def __get_spikiness(self):
		spiky_list = [self.primary_emotion_taxonomy[emotion]["spikiness"] for emotion in self.primary_emotions_present]
		spikiness = sum(spiky_list)/float(len(spiky_list)) if len(spiky_list) > 0 else 0
		return min(spikiness, 1)

	# Return the value for a weighted combination of primary emotions for a secondary emotion property in the form of a number (int or float)
	## used for global_vertical_AR, global_horizontal_AR, vertical_wrapping
	def __get_value_number_property(self, property_name):
		number_property = 0
		if len(self.primary_emotions_present) == 0:			# set to neutral values
			number_property = self.primary_emotion_taxonomy["neutral"][property_name]
		else:
			for primary_emotion in self.primary_emotions_present:
				emotion_number_property = self.primary_emotion_taxonomy[primary_emotion][property_name]
				emotion_number_property_weighting = self.primary_scaling_factors[primary_emotion][property_name+"_weighting"]
				multiplier = 1
				if self.emotion in self.user_emotion_dict:
					multiplier = self.user_emotion_dict[self.emotion][primary_emotion]
				number_property += (emotion_number_property * emotion_number_property_weighting * multiplier)/self.sum_scaling_factors[property_name+"_weighting"]
		return number_property

	# Return the vertical_AR dict for a weighted combination of primary emotions
	def __get_vertical_AR(self):
		vertical_AR = {}
		if len(self.primary_emotions_present) == 0:			# set to neutral values
			vertical_AR = self.primary_emotion_taxonomy["neutral"]["vertical_AR"]
		else:
			levels = {}
			levels_present = {}
			sums = {}
			primary_emotion_scaling_factors_data = {}
			emotion_vertical_AR = {}
			# record which vertical_AR levels (1, 2, 3, etc) are present in the union of the vertical_AR dicts of primary_emotions_present
			# also keep a cumulative sum for doing a weighted sum later
			for primary_emotion in self.primary_emotions_present:
				primary_emotion_data = self.primary_emotion_taxonomy[primary_emotion]
				primary_emotion_scaling_factors_data[primary_emotion] = (self.primary_scaling_factors[primary_emotion])
				emotion_vertical_AR[primary_emotion] = primary_emotion_data["vertical_AR"]
				for level in emotion_vertical_AR[primary_emotion]:				# 1, 2, 3, etc.
					if level not in levels:
						levels[level] = []
						sums[level] = 0
						levels_present[level] = 0
					levels[level].append(primary_emotion)
					multiplier = 1
					if self.emotion in self.user_emotion_dict:
						multiplier = self.user_emotion_dict[self.emotion][primary_emotion]
					sums[level] += primary_emotion_scaling_factors_data[primary_emotion]["vertical_AR_weighting"] * multiplier
					# check to see how many emotions present at each level
					if emotion_vertical_AR[primary_emotion][level] == None:
						level_present = 0
					elif emotion_vertical_AR[primary_emotion][level] != None:
						level_present = 1
					levels_present[level] += level_present
			# get the weighted sum per level
			for level in levels:
				vertical_AR[level] = 0
				for primary_emotion in levels[level]:
					primary_emotion_data = self.primary_emotion_taxonomy[primary_emotion]
					if primary_emotion_data["vertical_AR"][level] != None:
						multiplier = 1
						if self.emotion in self.user_emotion_dict:
							multiplier = self.user_emotion_dict[self.emotion][primary_emotion]
						# scaling factors for diff nos. of emotions present at every level
						# if combo of emotions, i.e. levels_present>1, need weighted scaling factors,
						# if only one emotion present, i.e. levels_present<=1, scaling factor weighting needs to be 1 in total (i.e. sum of weightings/sum of weightings)
						if levels_present[level] > 1:
						 	scaling_factor = primary_emotion_scaling_factors_data[primary_emotion]["vertical_AR_weighting"]
						else:
						 	scaling_factor = sums[level]
					 	# scaling_factor = primary_emotion_scaling_factors_data[primary_emotion]["vertical_AR_weighting"]
						vertical_AR[level] += (primary_emotion_data["vertical_AR"][level] * scaling_factor * multiplier)/sums[level]
						# set to null if it is 0 (all numbers are positive so there cannot be a valid 0)
				if vertical_AR[level] == 0:
					vertical_AR[level] = None
		return vertical_AR

	# Return the horizontal_AR dict for a weighted combination of primary emotions
	def __get_horizontal_AR(self):
		horizontal_AR = {}
		if len(self.primary_emotions_present) == 0:			# set to neutral values
			horizontal_AR = self.primary_emotion_taxonomy["neutral"]["horizontal_AR"]
		else:
			levels = {}
			levels_present = {}
			sums = {}
			primary_emotion_scaling_factors_data = {}
			emotion_horizontal_AR = {}
			# record which horizontal_AR levels (1, 2, 3, etc) are present in the union of the horizontal_AR dicts of primary_emotions_present
			# also keep a dict of cumulative sums for doing weighted sums later
			for primary_emotion in self.primary_emotions_present:
				primary_emotion_data = self.primary_emotion_taxonomy[primary_emotion]
				primary_emotion_scaling_factors_data[primary_emotion] = self.primary_scaling_factors[primary_emotion]
				emotion_horizontal_AR[primary_emotion] = primary_emotion_data["horizontal_AR"]
				for level in emotion_horizontal_AR[primary_emotion]:				# 1, 2, 3, etc.
					if level not in levels:
						levels[level] = []
						sums[level] = {}
						for term in emotion_horizontal_AR[primary_emotion][level]:		# level_horizontal_AR_x, level_horizontal_AR_y, points_in_curve, horizontal_smoothness
							sums[level][term+"_weighting"] = 0
					levels[level].append(primary_emotion)
					for term in sums[level]:
						multiplier = 1
						if self.emotion in self.user_emotion_dict:
							multiplier = self.user_emotion_dict[self.emotion][primary_emotion]
						sums[level][term] += primary_emotion_scaling_factors_data[primary_emotion][term] * multiplier
			for level in levels:
				horizontal_AR[level] = {"level_horizontal_AR_x":0,"level_horizontal_AR_y":0,"points_in_curve":0,"horizontal_smoothness":0}
				for primary_emotion in levels[level]:
					primary_emotion_data = self.primary_emotion_taxonomy[primary_emotion]
					for term in horizontal_AR[level]:
						multiplier = 1
						if self.emotion in self.user_emotion_dict:
							multiplier = self.user_emotion_dict[self.emotion][primary_emotion]
						# scaling factors for diff nos. of emotions present at every level
						# if combo of emotions, i.e. length of levels array at each level >1, need weighted scaling factors,
						# if only one emotion present, i.e. length of levels array at each level <=1, scaling factor weighting needs to be 1 in total (i.e. sum of weightings/sum of weightings)
						if len(levels[level]) > 1:
						 	scaling_factor = primary_emotion_scaling_factors_data[primary_emotion][term+"_weighting"]
						else:
						 	scaling_factor = sums[level][term+"_weighting"]
					 	scaling_factor = primary_emotion_scaling_factors_data[primary_emotion][term+"_weighting"]
						horizontal_AR[level][term] += (primary_emotion_data["horizontal_AR"][level][term] * scaling_factor * multiplier)/sums[level][term+"_weighting"]
				horizontal_AR[level]["points_in_curve"] = int(round(horizontal_AR[level]["points_in_curve"]))
				horizontal_AR[level]["horizontal_smoothness"] = int(round(horizontal_AR[level]["horizontal_smoothness"]))
		return horizontal_AR

	# Return rgb colour value for combination of primary emotions
	def __get_render_rgb(self):
		render_rgb = {}
		if len(self.primary_emotions_present) == 0:			# set to neutral values
			render_rgb = self.primary_emotion_taxonomy["neutral"]["color"]
		else:
			for primary_emotion in self.primary_emotions_present:
				emotion_render_rgb = self.primary_emotion_taxonomy[primary_emotion]["color"]
				emotion_render_rgb_weighting = self.primary_scaling_factors[primary_emotion]["color_weighting"]
				for term in emotion_render_rgb:			# r, g, b
					if term not in render_rgb:
						render_rgb[term] = 0
					multiplier = 1
					if self.emotion in self.user_emotion_dict:
						multiplier = self.user_emotion_dict[self.emotion][primary_emotion]
					render_rgb[term] += (emotion_render_rgb[term] * emotion_render_rgb_weighting * multiplier)/self.sum_scaling_factors["color_weighting"]
		return render_rgb


