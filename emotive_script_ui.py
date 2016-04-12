# EmotiveModeler CAD plugin for Rhino, 2016
# Created by Philippa Mothersill as part of her Masters at the MIT Media Lab (2014) - read more here: http://emotivemodeler.media.mit.edu/
# Advised by Mike Bove, Object-Based Media group, and helped by Itamar Belsen, Jane Cutler and Anna Walsh
# Copyright 2016 Massachusetts Institute of Technology

import rhinoscriptsyntax as rs
import Rhino
import Meier_UI_Utility
import random
import json
import config
import emotive_script_ui_helper

# Creates initial UI panel, buttons, slidebars, textboxes, design_history capability, checkboxes, and all their associated listeners. Look at Meier_UI_Utility to understand how this goes to Rhino.
    # draw_emotion_helper method is where you want to go for solving weird UI edge cases when a new drawing is rendered.

# Credit to Mark Meier for UI interface

def Main():
    # Make the UI object
    ui = AllControlExample()
    # Show the dialog from the UI class
    Rhino.UI.Dialogs.ShowSemiModal(ui.form)

# This is just a class to test all the UI controls
class AllControlExample():
    def __init__(self):
        self.object_id = "Bottle"
        self.drawn_emotion = "neutral"
        self.emotion_id = "neutral"
        self.design_history = 0
        self.outpath = str(config.outpath_design_history + str(self.design_history) + ".jpg")
        self.history = []

        # Make a new form (dialog)
        self.form = Meier_UI_Utility.UIForm("EmotiveModeler")
        # Initialize drawable object
        self.drawn = emotive_script_ui_helper.draw_emotion_object(self.object_id, self.emotion_id)
        # Accumulate controls for the form
        self.addControls()
        # Layout the controls on the form
        self.form.layoutControls()
        self.init_enable_disable()

    # Add each control to an accumulated list of controls
    def addControls(self):
        # The controls get added to the panel of the form
        p = self.form.panel

        # dropdown list for object type
        self.objectType_combobox(p)

        # text box and draw buttons for emotion_id
        self.emotion_id_textbox(p)
        # self.add_emotionTextBox(p)

        # groupbox for checkboxes
        self.removeable_emotions_collection(p)

        # checkboxes and sliders for emotion breakdown
        self.modify_emotion_sliders(p)

        # self.suggested_words(p)

        #  design history text and image
        self.addDesignHistory(p)    

        # render/save button
        self.render_save_buttons(p)

    # Disable/enable appropriate fields for initialization
    def init_enable_disable(self):
        for c in self.form.panel.Controls:
            c.Enabled = False
        self.form.panel.Controls.Find("objectType_select", True)[0].Enabled = True
        self.form.panel.Controls.Find("objectType", True)[0].Enabled = True
        self.current_emotion_label = self.form.panel.Controls.Find("current_emotion_id", True)[0]
        object_type_label = self.form.panel.Controls.Find("object_type_label", True)[0]
        object_type_label.Text = "Enter a word to inspire the design of your "+str(self.object_id)+". Separate words with periods."
        object_type_label.Enabled = True

        self.form.panel.Controls.Find("emotion_id_textbox", True)[0].Enabled = True

        create_design_button = self.form.panel.Controls.Find("draw_button", True)[0]
        create_design_button.Enabled = True
        self.form.AcceptButton = create_design_button

        # enable history section
        self.form.panel.Controls.Find("design_history_text", True)[0].Enabled = True
        self.form.panel.Controls.Find("design_history_outpath", True)[0].Enabled = True
        design_history_image = self.form.panel.Controls.Find("history_image", True)[0]
        design_history_image.Enabled = True
        self.form.panel.Controls.Find("undo_button", True)[0].Enabled = False

        self.form.panel.Controls.Find("render_button", True)[0].Enabled = True
        self.form.panel.Controls.Find("save_button", True)[0].Enabled = True
        self.form.panel.Controls.Find("history_button", True)[0].Enabled = True

        self.current_emotion_label.Enabled = True
        self.current_emotion_label.Text = "Current emotion: "+self.drawn_emotion
        self.form.panel.Controls.Find("emotion_id_textbox", True)[0].Focus()

    # ====================== UI objects =====================

    # dropdown list for object type
    def objectType_combobox(self, p):
        p.addLabel("objectType_select", "Select a new object to design: ", None, True)
        # get object names
        # object_data_names = config.object_types
        object_data_names = ["Bottle", "Jewelry", "Totem", "Chair"]
        # object_data_names.insert(0, "Choose an object")
        p.addComboBox("objectType", object_data_names, 0, False, self.objectType_selected)
        p.addLabel("current_emotion_id", "Current emotion: ", None, True)
        p.addSeparator("sep1", 400, True)

    # text box and draw buttons for emotion_id
    def emotion_id_textbox(self, p):
        p.addLabel("object_type_label", "Enter a word to inspire the design of your ", None, True)
        p.addTextBox("emotion_id_textbox", "", 150, False, self.emotion_id_textbox_textEntered)
        p.addButton("draw_button", "Create Design", 100, False, self.draw_button)
        # p.addLabel("", "                                                ", None, False)
        p.addButton("add_emotion_button", "Add Word to Design", 150, True, self.add_emotion_button)
        # p.addLabel("", "", None, True)

    def removeable_emotions_collection(self, p):
        p.addFlowLayoutPanel("removed","Remove words",20,400,True)
        p.addButton("remove_button","Remove words",150,True,self.remove_emotion_button)
        p.addSeparator("sep2", 400, True)

    # checkboxes and sliders for emotion breakdown
    def modify_emotion_sliders(self, p):            #emotion_breakdown(self, p):
        p.addLabel("modify_label", "Modify the number and amount of individual emotions included in the form: ", None, True)
        p.addLabel("", "", None, True)

        primary_emotions = config.primary_emotions[1:]      # remove "neutral"
        emotion_breakdown = self.drawn.get_emotion().get_breakdown()

        for e in primary_emotions:
            p.addLabel("primary_emotion_label_"+e, e, None, False)
            p.addTrackBar("track_bar_"+e, 0, config.max_trackbar_value, 1, 2, 1, emotion_breakdown[e], 150, False, self.trackbar_slider_listener)
            p.addTextBox("track_bar_value_"+e, str(emotion_breakdown[e]), 50, True, self.trackbar_value_listener)

        p.addButton("modify_button","Modify shape",150,True,self.modify_emotion_button)

    # add emotion breakdown text and image of previous design 
    def addDesignHistory(self, p):
        p.addSeparator("sep4", 400, True)

        # p = self.form.panel
        p.addLabel("design_history_text", "Previous design:  ", None, False)
        p.addLabel("design_history_outpath", self.drawn_emotion, None, True)

        p.addLabel("design_history_breakdown", "", None, True)
        p.addLabel("", "", None, False)

        p.addPictureBox("history_image", self.outpath, False)
        p.addLabel("", "", None, True)

        p.addButton("undo_button", "Revert to previous design", 150, False, self.undo_button)
        p.addButton("revert_button", "Revert to original design", 150, True, self.revert_button)

    # render and savebuttons
    def render_save_buttons(self, p):
        p.addSeparator("sep4", 400, True)
        p.addButton("render_button", "Render", 150, False, self.render_button)
        p.addButton("save_button", "Save", 150, False, self.save_button)
        p.addButton("history_button", "Design History", 150, True, self.history_button)


    # ====================== Delegates =====================

    # Called when the objectType buttons are pressed
    def objectType_selected(self, sender, e):
        self.object_selection = sender.SelectedIndex
        self.object_id = sender.SelectedItem
        emotive_script_ui_helper.draw_emotion_object(self.object_id, self.drawn_emotion)
        self.form.panel.Controls.Find("emotion_id_textbox", True)[0].Focus()


    # Called when the text changes in the box (every keypress)
    def emotion_id_textbox_textEntered(self, sender, e):
        self.emotion_id = sender.Text.lower()
        print self.emotion_id

    # Called when the slider is slid along the trackbar; makes text boxes match sliders
    def trackbar_slider_listener(self, sender, e):
        p = self.form.panel
        # Can't figure out how to pass in one 'emotion' value well, so am just updating all of them
        primary_emotions = config.primary_emotions[1:]      # remove "neutral"
        for emotion in primary_emotions:
            new_value = p.Controls.Find("track_bar_"+emotion, True)[0].Value
            p.Controls.Find("track_bar_value_"+emotion, True)[0].Text = str(new_value)

    # Called when the text boxes next to the sliders are modified; makes sliders match text boxes
    def trackbar_value_listener(self, sender, e):
        p = self.form.panel
        # Can't figure out how to pass in one 'emotion' value well, so am just updating all of them
        primary_emotions = config.primary_emotions[1:]      # remove "neutral"
        for emotion in primary_emotions:
            new_value = p.Controls.Find("track_bar_value_"+emotion, True)[0].Text
            if new_value != "" and new_value.isdigit():
                if int(new_value) > config.max_trackbar_value:
                    new_value = config.max_trackbar_value
                p.Controls.Find("track_bar_"+emotion, True)[0].Value = int(new_value)

    # Called when "Modify shape" is pressed; modifies and draws the shape
    # TODO: how is this different from draw_emotion_helper?
    def modify_emotion_button(self, sender, e):
        p = self.form.panel
        # render image
        self.__historyImage(p)
        old_modify_emotion_breakdown = self.drawn.get_emotion().get_breakdown()
        self.history.append((self.drawn_emotion, old_modify_emotion_breakdown))
        p.Controls.Find("design_history_breakdown", True)[0].Text = str(old_modify_emotion_breakdown)

        new_modify_emotion_breakdown = self.drawn.get_emotion().get_breakdown()

        self.drawn_emotion = self.drawn.get_emotion().get_emotion()

        primary_emotions = config.primary_emotions[1:]
        for emotion in primary_emotions:
            new_value = p.Controls.Find("track_bar_"+emotion, True)[0].Value
            new_modify_emotion_breakdown[emotion] = new_value

        # modify user dictionary and draw
        emotive_script_ui_helper.modify_user_dictionary(self.object_id, self.drawn_emotion, new_modify_emotion_breakdown)
        self.drawn = emotive_script_ui_helper.draw_emotion_object(self.object_id, self.drawn_emotion)
        self.history.append((self.drawn_emotion, new_modify_emotion_breakdown))


    # Called when the draw button is pressed
    def draw_button(self, sender, e):
        # draw
        self.draw_emotion_helper()
        # emotion_breakdown = self.drawn.get_emotion().get_breakdown()
        # self.history.append((self.drawn_emotion, emotion_breakdown))

    # Called when the add emotion button is pressed
    def add_emotion_button(self, sender, e):
        # reassign emotion
        self.emotion_id += "."+self.drawn_emotion

        # draw
        self.draw_emotion_helper()
        # emotion_breakdown = self.drawn.get_emotion().get_breakdown()
        # self.history.append((self.drawn_emotion, emotion_breakdown))

    # Called when the remove emotion button is pressed
    def remove_emotion_button(self, sender, e):
        p = self.form.panel

        to_remove = []
        for box in p.Controls.Find("removed", True)[0].Controls:
            if box.Checked:
                to_remove.append(box)

        self.emotion_id = self.drawn_emotion
        for removed_emotion in to_remove:
            # remove all occurrences of emotion
            self.emotion_id = self.emotion_id.replace(removed_emotion.Name,'')

        # clean up string
        if self.emotion_id.startswith("."):
            self.emotion_id = self.emotion_id[1:]
        if self.emotion_id.endswith("."):
            self.emotion_id = self.emotion_id[:-1]

        if self.emotion_id == "":
            self.emotion_id = "neutral"

        # draw
        self.draw_emotion_helper()

    # Used for both "Create Design" and "Add Word to Design"
    def draw_emotion_helper(self, revert=False):
        p = self.form.panel

        if not revert: #update history and render images if undo function has not already done it
            # render image
            self.__historyImage(p)
            old_breakdown = self.drawn.get_emotion().get_breakdown(revert)
            self.drawn = emotive_script_ui_helper.draw_emotion_object(self.object_id, self.emotion_id, revert)
            #TODO: __str__ or __repr__ in Emotion class
            self.history.append((self.drawn_emotion, old_breakdown))
            breakdown = self.drawn.get_emotion().get_breakdown(revert)
            p.Controls.Find("design_history_breakdown", True)[0].Enabled = True
            p.Controls.Find("design_history_breakdown", True)[0].Text = str(old_breakdown)
            self.drawn_emotion = self.drawn.get_emotion().get_emotion()
            self.current_emotion_label.Text = "Current emotion: "+self.drawn_emotion

            # reset toolbar if undo function has not already done it
            p.Controls.Find("modify_label", True)[0].Enabled = True
            for e in config.primary_emotions[1:]:
                p.Controls.Find("primary_emotion_label_"+e, True)[0].Enabled = True
                p.Controls.Find("track_bar_"+e, True)[0].Value = min(10, breakdown[e])
                p.Controls.Find("track_bar_"+e, True)[0].Enabled = True
                p.Controls.Find("track_bar_value_"+e, True)[0].Text = str(min(10, breakdown[e]))
                p.Controls.Find("track_bar_value_"+e, True)[0].Enabled = True

        p.Controls.Find("emotion_id_textbox", True)[0].Text = ""
        p.Controls.Find("emotion_id_textbox", True)[0].Focus()

        self.emotions_contained = self.drawn.get_emotion().get_emotions_contained()

        not_neutral = True if self.drawn_emotion != "neutral" else False
        self.__set_neutral_dependent_buttons(not_neutral)
        self.__add_emotion_checkboxes(self.emotions_contained, not_neutral)

        if len(self.history[:self.design_history]) < 1: #Do not let user click undo button if there are no previous designs to revert to
            p.Controls.Find("undo_button", True)[0].Enabled = False
        else:
            p.Controls.Find("undo_button", True)[0].Enabled = True

    def __add_emotion_checkboxes(self, emotions, not_neutral):
        p = self.form.panel
        # Clear all checkboxes
        flp_ctrls = p.Controls.Find("removed", True)[0]. Controls
        ctrls_list = list(flp_ctrls)
        for ctrl in ctrls_list:
            ctrl.Dispose()
        # Repopulate
        if not_neutral:
            for emotion in emotions:
                c = p.addCheckBox(emotion,emotion,False,False,None)
                flp_ctrls.Add(c)

    def __set_neutral_dependent_buttons(self, not_neutral):
        p = self.form.panel
        p.Controls.Find("add_emotion_button", True)[0].Enabled = not_neutral
        p.Controls.Find("removed", True)[0].Enabled = not_neutral
        p.Controls.Find("remove_button", True)[0].Enabled = not_neutral
        p.Controls.Find("modify_button", True)[0].Enabled = not_neutral

    # Called when the button is pressed
    def __historyImage(self, p):
        self.design_history = self.design_history + 1
        self.outpath = str(config.outpath_design_history + str(self.design_history) + ".jpg")
        # set view and render image to target folder
        rs.CurrentView("Perspective")
        rs.Command("_-Render", False)
        rs.Command("_-SaveRenderWindowAs  \n\"" + self.outpath + "\"\n", False)
        rs.Command("_-CloseRenderWindow", False)
        p.Controls.Find("history_image", True)[0].Load(self.outpath)
        p.Controls.Find("design_history_outpath", True)[0].Text = self.drawn_emotion

    # Called when undo_button clicked
    def undo_button(self, sender, e):
        self.history = self.history[:self.design_history]

        if len(self.history) >= 1:
            self.design_history = self.design_history - 1
            self.drawn_emotion = self.history[self.design_history][0]
            self.current_emotion_label.Text = "Current emotion: "+self.drawn_emotion
            self.drawn = emotive_script_ui_helper.draw_emotion_object(self.object_id, self.drawn_emotion)

            p = self.form.panel
            for e in config.primary_emotions[1:]:
                p.Controls.Find("track_bar_"+e, True)[0].Value = self.history[self.design_history][1][e]

            self.outpath = str(config.outpath_design_history + str(self.design_history) + ".jpg")
            p.Controls.Find("history_image", True)[0].Load(self.outpath)
            p.Controls.Find("design_history_outpath", True)[0].Text = str(self.history[self.design_history-1][0])
            p.Controls.Find("design_history_breakdown", True)[0].Text = str(self.history[self.design_history-1][1])
            self.draw_emotion_helper(True)
        else:
            rs.MessageBox("You don't have a previous design to revert to")

    # Called when revert_button clicked
    def revert_button(self, sender, e):
        self.emotion_id = self.drawn_emotion
        self.draw_emotion_helper(True)

    # Called when render_button clicked
    def render_button(self, sender, e):
        emotive_script_ui_helper.render_emotion_object(self.object_id, self.emotions_contained[0])

    # Called when save_button clicked
    def save_button(self, sender, e):
        emotive_script_ui_helper.save_emotion_object(self.object_id, self.emotions_contained[0])

    # Called when save_button clicked
    def history_button(self, sender, e):
        rs.MessageBox(self.history)
        print self.history


    # def suggested_words(self,p):
    #     emotions = self.drawn.get_emotion().get_emotions_contained()

    #     synonyms = []
    #     syn_list= []

    #     for emotion in emotions:

    #         for i, syn in enumerate(wn.synsets(emotion, pos)):
    #             syns = [n.replace('_', '') for n in syn.lemma_names]
    #             synonyms.append(syns)

    #     syn_list = list(set(sum(synonyms,[])))

    #     # for i in xrange(len(nltk_words)):
    #     #     # p.addCheckBox(str(nltk_words[i]), str(nltk_words[i]), False, False, self.add_emotion_nltk_CheckStateChanged)
    #     #     p.addLabel("nltk_words_label", related_words_label, None, True)

    #     rs.MessageBox(syn_list)
    #     # related_words_label = str("Related words to " + emotion_words + ": " + syn_list)
    #     # p.addLabel("suggested_words_label", related_words_label, None, True)




# Execute it...
if( __name__ == "__main__" ):
    emotive_script_ui_helper = reload(emotive_script_ui_helper)
    Meier_UI_Utility = reload(Meier_UI_Utility)
    Main()
