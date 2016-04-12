# EmotiveModeler CAD plugin for Rhino, 2016
# Created by Philippa Mothersill as part of her Masters at the MIT Media Lab (2014) - read more here: http://emotivemodeler.media.mit.edu/
# Advised by Mike Bove, Object-Based Media group, and helped by Itamar Belsen, Jane Cutler and Anna Walsh
# Copyright 2016 Massachusetts Institute of Technology

import math
import json
import rhinoscriptsyntax as rs

# # Return the primary emotion breakdown dictionary for a secondary emotion
# def get_emotion_breakdown(emotion_dict, user_emotion_dict, emotion):
# 	emotion_breakdown = {}
# 	if emotion in user_emotion_dict:
# 		emotion_breakdown = user_emotion_dict[emotion]
# 	elif emotion in emotion_dict:
# 		emotion_breakdown = emotion_dict[emotion]
# 	else:		# multiple adjectives
# 		emotions = emotion.split(".")
# 		for e in emotions:
# 			e_breakdown = get_emotion_breakdown(emotion_dict, user_emotion_dict, e)
# 			for value in e_breakdown:
# 				if value in emotion_breakdown:		# add emotions together
# 					emotion_breakdown[value] = emotion_breakdown[value] + e_breakdown[value]
# 				else:								# add new emotion
# 					emotion_breakdown[value] = e_breakdown[value]
# 	return emotion_breakdown

# # Return a list of primary emotions present in a secondary emotion
# def get_emotions_present(emotion_dict, user_emotion_dict, emotion):
# 	emotion_breakdown = get_emotion_breakdown(emotion_dict, user_emotion_dict, emotion)
# 	primary_emotions_present = []
# 	for primary_emotion in emotion_breakdown:
# 		if emotion_breakdown[primary_emotion] != 0:
# 			primary_emotions_present.append(primary_emotion)
# 	return primary_emotions_present

# # Return the sum of each scaling factor for all the primary emotions present in a secondary emotion
# def get_sum_scaling_factors(emotion_taxonomy_data, scaling_factors_data, primary_emotions_present, user_emotion_dict, emotion):
# 	sums = {}
# 	for weight in scaling_factors_data["neutral"]:
# 		sums[weight] = 0
# 	for primary_emotion in primary_emotions_present:
# 		for weight in sums:
# 			# In the original word_emotion_dictionary, emotions either are present or aren't (0 or 1)
# 			multiplier = 1
# 			if emotion in user_emotion_dict:
# 				multiplier = user_emotion_dict[emotion][primary_emotion]
# 			sums[weight] += scaling_factors_data[primary_emotion][weight] * multiplier
# 	return sums

# # Return the spine equation for a secondary emotion
# def get_spine_equation(emotion_taxonomy_data, scaling_factors_data, primary_emotions_present, sum_spine_weighting, user_emotion_dict, emotion):
# 	spine_equation = {}
# 	if len(primary_emotions_present) == 0:			# set to neutral values
# 		spine_equation = emotion_taxonomy_data["neutral"]["spine_equation"]
# 	else:
# 		primary_emotion_scaling_factors_data = {}
# 		for primary_emotion in primary_emotions_present:
# 			primary_emotion_data = emotion_taxonomy_data[primary_emotion]
# 			emotion_spine_equation = primary_emotion_data["spine_equation"]
# 			primary_emotion_scaling_factors_data[primary_emotion] = scaling_factors_data[primary_emotion]
# 			emotion_spine_equation_weighting = primary_emotion_scaling_factors_data[primary_emotion]["spine_weighting"]
# 			for term in emotion_spine_equation:			# a_term, b_term, h_term, k_term
# 				if term not in spine_equation:
# 					spine_equation[term] = 0
# 				multiplier = 1
# 				if emotion in user_emotion_dict:
# 					multiplier = user_emotion_dict[emotion][primary_emotion]
# 				spine_equation[term] += (emotion_spine_equation[term] * emotion_spine_equation_weighting * multiplier)/sum_spine_weighting
# 	return spine_equation

# # Return the value for a weighted combination of primary emotions for a secondary emotion property in the form of a number (int or float)
# ## used for global_vertical_AR, global_horizontal_AR, vertical_wrapping
# def get_value_number_property(property_name, emotion_taxonomy_data, scaling_factors_data, primary_emotions_present, sum_weighting, user_emotion_dict, emotion):
# 	number_property = 0
# 	if len(primary_emotions_present) == 0:			# set to neutral values
# 		number_property = emotion_taxonomy_data["neutral"][property_name]
# 	else:
# 		primary_emotion_scaling_factors_data = {}
# 		for primary_emotion in primary_emotions_present:
# 			primary_emotion_data = emotion_taxonomy_data[primary_emotion]
# 			primary_emotion_scaling_factors_data[primary_emotion] = scaling_factors_data[primary_emotion]
# 			emotion_number_property = primary_emotion_data[property_name]
# 			emotion_number_property_weighting = primary_emotion_scaling_factors_data[primary_emotion][property_name+"_weighting"]
# 			multiplier = 1
# 			if emotion in user_emotion_dict:
# 				multiplier = user_emotion_dict[emotion][primary_emotion]
# 			number_property += (emotion_number_property * emotion_number_property_weighting * multiplier)/sum_weighting
# 	return number_property

# # Return the vertical_AR dict for a weighted combination of primary emotions
# def get_vertical_AR(emotion_taxonomy_data, scaling_factors_data, primary_emotions_present, user_emotion_dict, emotion):
# 	vertical_AR = {}
# 	if len(primary_emotions_present) == 0:			# set to neutral values
# 		vertical_AR = emotion_taxonomy_data["neutral"]["vertical_AR"]
# 	else:
# 		levels = {}
# 		levels_present = {}
# 		sums = {}
# 		primary_emotion_scaling_factors_data = {}
# 		emotion_vertical_AR = {}
# 		# record which vertical_AR levels (1, 2, 3, etc) are present in the union of the vertical_AR dicts of primary_emotions_present
# 		# also keep a cumulative sum for doing a weighted sum later
# 		for primary_emotion in primary_emotions_present:
# 			primary_emotion_data = emotion_taxonomy_data[primary_emotion]
# 			primary_emotion_scaling_factors_data[primary_emotion] = (scaling_factors_data[primary_emotion])
# 			emotion_vertical_AR[primary_emotion] = primary_emotion_data["vertical_AR"]
# 			for level in emotion_vertical_AR[primary_emotion]:				# 1, 2, 3, etc.
# 				if level not in levels:
# 					levels[level] = []
# 					sums[level] = 0
# 					levels_present[level] = 0
# 				levels[level].append(primary_emotion)
# 				multiplier = 1
# 				if emotion in user_emotion_dict:
# 					multiplier = user_emotion_dict[emotion][primary_emotion]
# 				sums[level] += primary_emotion_scaling_factors_data[primary_emotion]["vertical_AR_weighting"] * multiplier
# 				# check to see how many emotions present at each level
# 				if emotion_vertical_AR[primary_emotion][level] == None:
# 					level_present = 0
# 				if emotion_vertical_AR[primary_emotion][level] != None:
# 					level_present = 1
# 				levels_present[level] += level_present
# 		# get the weighted sum per level
# 		for level in levels:
# 			vertical_AR[level] = 0
# 			for primary_emotion in levels[level]:
# 				primary_emotion_data = emotion_taxonomy_data[primary_emotion]
# 				if primary_emotion_data["vertical_AR"][level] != None:
# 					multiplier = 1
# 					if emotion in user_emotion_dict:
# 						multiplier = user_emotion_dict[emotion][primary_emotion]
# 					# scaling factors for diff nos. of emotions present at every level
# 					# if combo of emotions, i.e. levels_present>1, need weighted scaling factors,
# 					# if only one emotion present, i.e. levels_present<=1, scaling factor weighting needs to be 1 in total (i.e. sum of weightings/sum of weightings)
# 					if levels_present[level] > 1:
# 					 	scaling_factor = primary_emotion_scaling_factors_data[primary_emotion]["vertical_AR_weighting"]
# 					else:
# 					 	scaling_factor = sums[level]
# 				 	# scaling_factor = primary_emotion_scaling_factors_data[primary_emotion]["vertical_AR_weighting"]
# 					vertical_AR[level] += (primary_emotion_data["vertical_AR"][level] * scaling_factor * multiplier)/sums[level]
# 					# set to null if it is 0 (all numbers are positive so there cannot be a valid 0)
# 			if vertical_AR[level] == 0:
# 				vertical_AR[level] = None
# 	return vertical_AR

# # Return the horizontal_AR dict for a weighted combination of primary emotions
# def get_horizontal_AR(emotion_taxonomy_data, scaling_factors_data, primary_emotions_present, user_emotion_dict, emotion):
# 	horizontal_AR = {}
# 	if len(primary_emotions_present) == 0:			# set to neutral values
# 		horizontal_AR = emotion_taxonomy_data["neutral"]["horizontal_AR"]
# 	else:
# 		levels = {}
# 		levels_present = {}
# 		sums = {}
# 		primary_emotion_scaling_factors_data = {}
# 		emotion_horizontal_AR = {}
# 		# record which horizontal_AR levels (1, 2, 3, etc) are present in the union of the horizontal_AR dicts of primary_emotions_present
# 		# also keep a dict of cumulative sums for doing weighted sums later
# 		for primary_emotion in primary_emotions_present:
# 			primary_emotion_data = emotion_taxonomy_data[primary_emotion]
# 			primary_emotion_scaling_factors_data[primary_emotion] = scaling_factors_data[primary_emotion]
# 			emotion_horizontal_AR[primary_emotion] = primary_emotion_data["horizontal_AR"]
# 			for level in emotion_horizontal_AR[primary_emotion]:				# 1, 2, 3, etc.
# 				if level not in levels:
# 					levels[level] = []
# 					sums[level] = {}
# 					for term in emotion_horizontal_AR[primary_emotion][level]:		# level_horizontal_AR_x, level_horizontal_AR_y, points_in_curve, horizontal_smoothness
# 						sums[level][term+"_weighting"] = 0
# 				levels[level].append(primary_emotion)
# 				for term in sums[level]:
# 					multiplier = 1
# 					if emotion in user_emotion_dict:
# 						multiplier = user_emotion_dict[emotion][primary_emotion]
# 					sums[level][term] += primary_emotion_scaling_factors_data[primary_emotion][term] * multiplier
# 		for level in levels:
# 			horizontal_AR[level] = {"level_horizontal_AR_x":0,"level_horizontal_AR_y":0,"points_in_curve":0,"horizontal_smoothness":0}
# 			for primary_emotion in levels[level]:
# 				primary_emotion_data = emotion_taxonomy_data[primary_emotion]
# 				for term in horizontal_AR[level]:
# 					multiplier = 1
# 					if emotion in user_emotion_dict:
# 						multiplier = user_emotion_dict[emotion][primary_emotion]
# 					# scaling factors for diff nos. of emotions present at every level
# 					# if combo of emotions, i.e. length of levels array at each level >1, need weighted scaling factors,
# 					# if only one emotion present, i.e. length of levels array at each level <=1, scaling factor weighting needs to be 1 in total (i.e. sum of weightings/sum of weightings)
# 					if len(levels[level]) > 1:
# 					 	scaling_factor = primary_emotion_scaling_factors_data[primary_emotion][term+"_weighting"]
# 					else:
# 					 	scaling_factor = sums[level][term+"_weighting"]
# 				 	scaling_factor = primary_emotion_scaling_factors_data[primary_emotion][term+"_weighting"]
# 					horizontal_AR[level][term] += (primary_emotion_data["horizontal_AR"][level][term] * scaling_factor * multiplier)/sums[level][term+"_weighting"]
# 			horizontal_AR[level]["points_in_curve"] = int(round(horizontal_AR[level]["points_in_curve"]))
# 			horizontal_AR[level]["horizontal_smoothness"] = int(round(horizontal_AR[level]["horizontal_smoothness"]))
# 	return horizontal_AR

# # Return a dictionary of properties for a secondary emotion
# def get_properties_for_emotion(emotion_taxonomy_data, scaling_factors_data, emotion_dict, user_emotion_dict, emotion):
# 	emotion_properties = {}

# 	primary_emotions_present = get_emotions_present(emotion_dict, user_emotion_dict, emotion)
# 	sum_scaling_factors = get_sum_scaling_factors(emotion_taxonomy_data, scaling_factors_data, primary_emotions_present, user_emotion_dict, emotion)		# sums are never 0

# 	# get individual values
# 	spine_equation = get_spine_equation(emotion_taxonomy_data, scaling_factors_data, primary_emotions_present, sum_scaling_factors["spine_weighting"], user_emotion_dict, emotion)
# 	global_vertical_AR = get_value_number_property("global_vertical_AR", emotion_taxonomy_data, scaling_factors_data, primary_emotions_present, sum_scaling_factors["global_vertical_AR_weighting"], user_emotion_dict, emotion)
# 	global_horizontal_AR = get_value_number_property("global_horizontal_AR", emotion_taxonomy_data, scaling_factors_data, primary_emotions_present, sum_scaling_factors["global_horizontal_AR_weighting"], user_emotion_dict, emotion)
# 	vertical_wrapping = get_value_number_property("vertical_wrapping", emotion_taxonomy_data, scaling_factors_data, primary_emotions_present, sum_scaling_factors["vertical_wrapping_weighting"], user_emotion_dict, emotion)
# 	vertical_AR = get_vertical_AR(emotion_taxonomy_data, scaling_factors_data, primary_emotions_present, user_emotion_dict, emotion)
# 	horizontal_AR = get_horizontal_AR(emotion_taxonomy_data, scaling_factors_data, primary_emotions_present, user_emotion_dict, emotion)

# 	# insert into dictionary
# 	emotion_properties["spine_equation"] = spine_equation
# 	emotion_properties["global_vertical_AR"] = global_vertical_AR
# 	emotion_properties["global_horizontal_AR"] = global_horizontal_AR
# 	emotion_properties["vertical_AR"] = vertical_AR
# 	emotion_properties["horizontal_AR"] = horizontal_AR
# 	emotion_properties["vertical_wrapping"] = vertical_wrapping

# 	rs.MessageBox(emotion_properties)

# 	return emotion_properties

# Return a dictionary of properties for all secondary emotions in dictionary emotion_dict
def get_all_secondary_emotion_properties(emotion_dict):
	emotion_taxonomy_file = open('emotion_taxonomy.json').read()
	emotion_taxonomy_data = json.loads(emotion_taxonomy_file)
	scaling_factors_file = open('emotion_taxonomy_scaling_factors.json').read()
	scaling_factors_data = json.loads(scaling_factors_file)

	secondary_emotion_properties = {}
	for emotion in emotion_dict:
		secondary_emotion_properties[emotion] = get_properties_for_emotion(emotion_taxonomy_data, scaling_factors_data, emotion_dict, emotion)
	return secondary_emotion_properties

# Write the properties of all the secondary emotions in file named word_dictionary_name to file named outfile_name
def write_results_to_file(word_dictionary_name, outfile_name):
	emotion_dict_file = open(word_dictionary_name).read()
	emotion_dict_data = json.loads(emotion_dict_file)
	secondary_emotion_properties = get_all_secondary_emotion_properties(emotion_dict_data)
	with open(outfile_name, 'w') as outfile:
		json.dump(secondary_emotion_properties, outfile)

# # Iterate through word_emotion_dictionary.json and write results to secondary_emotion_properties.json
# write_results_to_file('working dictionary json/word_emotion_dictionary_full.json', 'working dictionary json/secondary_emotion_properties.json')