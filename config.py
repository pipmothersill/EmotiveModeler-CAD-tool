# EmotiveModeler CAD plugin for Rhino, 2016
# Created by Philippa Mothersill as part of her Masters at the MIT Media Lab (2014) - read more here: http://emotivemodeler.media.mit.edu/
# Advised by Mike Bove, Object-Based Media group, and helped by Itamar Belsen, Jane Cutler and Anna Walsh
# Copyright 2016 Massachusetts Institute of Technology

object_features_filename = "object_features.json"
system_emotion_dictionary_filename = "working dictionary json/word_emotion_dictionary_plutchik_edits.json"
primary_emotion_taxonomy_filename = "emotion_taxonomy.json"
primary_scaling_factors_filename = "emotion_taxonomy_scaling_factors.json"
user_emotion_dictionary_filename = "working dictionary json/user_emotion_dictionary.json"

primary_emotions = ["neutral","anger","anticipation","disgust","fear","joy","sadness","surprise","trust"]

exit_commands = ["exit","quit","q"]

object_types = { "B":"Bottle",
				 "J":"Jewelry",
				 "T":"Totem",
				 "C":"Chair"
				 }
# change these file directories to those of your own folders called "Animations", "Saved_models" and "Design_history"
outpath_render = "C:\\Users\\Pip\\Documents\\EmotiveModeler\\Animations\\Emotion_"
outpath_save = "C:\\Users\\Pip\\Documents\\EmotiveModeler\\Saved_models\\Emotion_"
outpath_design_history = "C:\\Users\\Pip\\Documents\\EmotiveModeler\\Design_history\\History_"


max_trackbar_value = 10