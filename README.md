# EmotiveModeler-CAD-tool

The EmotiveModeler is a plugin for the Rhinoceros CAD tool that allows both novice and expert designers to use only descriptive adjectives and emotions to manipulate the design of some basic objects so that their forms communicate various emotive characters.

#Background
We have an unconscious understanding of the meaning of different physical objects through our extensive interactions with them. Designers consciously understand this language, allowing them to embody meaning in objects through their physical geometries, often using complex CAD tools to develop 3D models of their designs. Despite advances in more accessible design tools, this early part of the design process - where a designer understands what sort of forms will best convey the meaning they want - is still very hard for beginners. The EmotiveModeler integrates this knowledge about our emotive perception of shapes into a CAD tool that allows both novice and expert designers to use only descriptive adjectives and emotions to design objects whose forms communicate the emotive character of the chosen words.

The EmotiveModeler plugin allows you to manipulate the shape of a few very simple pre-installed objects (a bottle, a simple jewelery pendant, a totem, all included in this software version) by typing in any word and setting a range of emotions associated to the word.  Each of these 8 emotions has a range of shape variables associated to it (specified in the "emotion_taxonomy.json" file).  When the word is associated to any of these emotions (or you change the emotion values) the shape can be regenerated to reflect those combined emotive-shape characteristics.

You can read more about the research behind the EmotiveModeler and see it in action here: http://emotivemodeler.media.mit.edu/

#How to Install the EmotiveModeler plugin (Windows)
1. Download these files to your computer and save them to an easy to access location.

2. Open Rhino (2014 versions onwards)

3. Ensure that IronPython is installed on your Rhino version.

4. Modify Save etc file names in "config.py" file: Some of the functions in the EmotiveModeler allow you to save files and animations to your local computer.  You need to modify the file directory name in the "config.py" file to do this however.  Create folders called "Animations", "Saved_models" and "Design_history" and modify the file names on lines 17-19 to reflect the location of your folders, e.g. replace outpath_render = "C:\\Users\\Pip\Documents\\EmotiveModeler\\Animations\\Emotion_" with outpath_render = "C:\\Users\\Your_Name\\Documents\\EmotiveModeler\\Animations\\Emotion_", or whatever the file path is to that folder.  Remember to use double back-slashes between each file level in your file name e.g."...EmotiveModeler\ \Animations..." (with no space) otherwise the system won't be able to find the files needed to run and will show a bug (single-backslashes are shown here due to limitations with the viewer.)

5. Set Rendering settings:  There is a small window in the UI that shows the previous design.  In order to see the image, the Render -> Render properties, and change the Resolution viewport size to a Custom size of 200 x 150 pixels.

6. In the Command Line, type "RunPythonScript" and push "Enter".  This will open up a directory window.  Navigate to your new EmotiveModeler folder and open the file called "emotive_script_ui.py".  This should start the EmotiveModeler plugin.

7. You can create your own button in Rhino to activate this.  Here is a good tutorial for how to set up your own button to activate a script: http://developer.rhino3d.com/guides/rhinoscript/running_scripts_from_macros/ (The "EmotiveModeler Rhino button.png" image included in these files is an example of how you can set up the full UI plugin and the plugin without the UI window to be activated.)

8. If Rhino can't find the folders that are related to the scripts, ensure that Rhino knows where to look for your scripts by adding this search path in the Python script folder.  Open the editor with the command EditPythonScript and go to Tools > Options and enter the path to your folder (e.g. "C:\Users\Your_Name\Documents\EmotiveModeler") in Module Search Paths.

#How to Use the EmotiveModeler (Windows)
When the EmotiveModeler plugin window pops up, a base model of a bottle will appear in the drawing windows.
The EmotiveModeler window is pretty self explanatory but here is a summary of the key features:

1. Select a new object to design: the drop down box will show the few pre-existing simple objects that can be modified.  Select one to change the base object to be modified.
(The volumes and finishing features, e.g. bottle lid shape etc, of these simple base objects can be modified in the "object_features.json" file or in lines 161-184 of the "construction_functions.py" file.)

2. Enter a word to design: type any word here and click "Create Design".  Multiple words can also be entered by separating them with periods (no spaces).  Once a word has been entered, additional words can also be added by clicking the "Add word to design" button.  The words associated to the designed object are listed below this text box - to remove any of them, click the box next to them and then click the "Remove words" button.  If a word is not recognised in the dictionary, a message window will appear asking if you wish to add the word to the dictionary.  If you click "Yes", it will ask you to set the emotions associated to that word using the sliders below the text entry box.

3. Modifying the emotions associated to the words entered: After clicking "Create design", the system will search for any emotions related to the words entered (in the "word_emotion_dictionary_plutchik_edits.json" file in the "working dictionary json" folder) and a new form will be generated in the drawing windows.  Sometimes there are already emotions associated to these words, sometimes there are none.  These emotion levels can be modified if you wish.  Simply drag the sliders to the new values you would like and then click "Modify shape".  A new shape related to that combination of emotions will then be generated. (This new combination of emotions associated to the word(s) entered will be saved in the "user_emotion_dictionary.json" file in the "working dictionary json" folder.)

4. If you would like to save an animation, Rhino model, or the design variables associated to your designs, click on the "Render", "Save" or "Design History" buttons.  These should save the appropriate files to the folders you made.


#Notes:
Due to coding limitations, The EmotiveModeler UI does not fully function in the Mac version of Rhino.  A version with a Command Line based interaction is available by running the "emotive_script_new.py".  Follow the Command Line instructions to manipulate the words and emotions as above.  This can also be used in the Windows version if the GUI is not required or not working.

The EmotiveModeler plugin is a prototype created as part of Masters research at the MIT Media Lab.  We are sharing it to allow other researchers to benefit from this research and play around with it's capabilities.  It is currently not at commercial development standard, and as such may still have some bugs!  We are afraid we can't offer support on this tool but would love to hear of any comments you have while using it.

Third party research and code used to support some of the functionality in the EmotiveModeler is listed below - many thanks to the authors for allowing it to be used for this research:

NRC Word-Emotion Association Lexicon by Saif Mohammad: http://saifmohammad.com/WebPages/NRC-Emotion-Lexicon.htm
(Crowdsourcing a Word-Emotion Association Lexicon, Saif Mohammad and Peter Turney, Computational Intelligence, 29 (3), 436-465, 2013.)

Graphical User Interface Library for Rhino (Windows) by Mark Meier: http://mkmra2.blogspot.com/2012/12/creating-graphical-user-interfaces-with.html

Advised by Mike Bove, Object-Based Media group, and helped by Itamar Belsen, Jane Cutler and Anna Walsh

Copyright 2016 Massachusetts Institute of Technology
