import System.Drawing
import System.Windows.Forms
from System.Drawing import *
from System.Windows.Forms import *

#
# These classes help to create graphical user interfaces 
# by Mark Meier
# Please see my blog post for details at:
# http://mkmra2.blogspot.com/2012/12/creating-graphical-user-interfaces-with.html
#
class UIForm(Form):
    """
    Provides a graphical user interface form (dialog). 
    """
    def __init__(self, title):
        """
        Initializes a new instance of the GUIForm class.
        title: The text for the title bar of the dialog box
        """
        self.Text = title
        self.panel = UIPanel()
        # Start with a teeeeny size. The AutoSize will make it large enough
        self.Width = 10
        self.Height = 10
    
    def layoutControls(self):
        """ 
        Sets up the properties of the form, docks the panel with all the 
        accumulated controls to the form, then asks the panel to layout
        its controls.
        """
        self.AutoSize = True
        self.ShowInTaskbar = True
        self.MaximizeBox = False
        self.MinimizeBox = True
        self.ShowIcon = False
        self.FormBorderStyle = FormBorderStyle.FixedToolWindow
        
        self.SuspendLayout()
        self.panel.layoutControls()
        self.Controls.Add(self.panel)
        
        # Special case any Cancel button so it cancels the dialog (Esc key works)
        ctrlList = self.panel.Controls.Find("Cancel", True)
        if (len(ctrlList) != 0):
            c = ctrlList[0]
            self.CancelButton = c
        self.ResumeLayout(False)

class UIPanel(FlowLayoutPanel):
    """
    A graphical user interface panel. This panel is normally docked in a Form. 
    This class manages the adding of controls to the panel, and the storage 
    and tab index building for the panel's controls.
    Controls are "flowed" onto the form, left to right, top to bottom.
    Each control determines if it begins on a new line by passing True
    to its breakFlowAfter parameter. If the form is wide enough, a value
    of False will cause the control to be positioned on the same line. 
    """
    def __init__(self):
        """
        Initializes a new instance of the GUIPanel class.
        """
        self.controls = [] # The list of controls the panel accumulates as code adds them
        self.tabIndex = 0 # Each control added uses this tabIndex and then increments it
        
        # Properties of the FlowLayoutPanel
        self.AutoSize = True
        self.AutoScroll = True 
        self.FlowDirection = FlowDirection.LeftToRight
        self.WrapContents = True
    
    def addSeparator(self, name, width, breakFlowAfter):
        """
        Adds a separator (horizontal bar) to the panel. This is normally
            simply an organization aide. 
        Parameters:
            name: The name for the control. You may pass "" if you don't need to
                reference the control by name. 
            width: The horizontal size in pixels for the control.
            breakFlowAfter: Pass True to have the next control on a new line. 
                False to have the next control on the same line if there is room.
        Returns:
            The control which was added.
        """
        c = GroupBox()
        c.Size = System.Drawing.Size(width, 8) # 8 makes it a horizontal bar
        c.Margin = System.Windows.Forms.Padding(3, 6, 3, 10) # 5 is to align with other controls vertically
        c.TabStop = False
        self.SetFlowBreak(c, breakFlowAfter)
        self.controls.append(c)
        return c
    
    def addLabel(self, name, text, color, breakFlowAfter):
        """
        Adds a Label control.
        Parameters:
            name: The name for the control. 
                This can be "" if you don't need to reference the control by name.
            text: The text that the label displays.
            color: A list of color values (RGB) for the text. 
                Example: (0, 0, 255) would be Blue.
                Pass None to get black label text. 
            breakFlowAfter: Pass True to have the next control on a new line. 
                False to have the next control on the same line if there is room.
        Returns:
            The control which was added.
        """
        c = Label()
        c.Name = name
        c.Text = text
        if (color != None):
            clr = System.Drawing.Color.FromArgb(color[0], color[1], color[2])
            c.ForeColor = clr
        c.AutoSize = True
        c.Margin = System.Windows.Forms.Padding(3, 5, 3, 0) # 5 is to align with other controls vertically
        self.SetFlowBreak(c, breakFlowAfter)
        self.controls.append(c)
        return c
    
    def addLinkLabel(self, name, text, URL, breakFlowAfter, delegate):
        """
        Adds a LinkLabel control. This provides a hyperlink which normally
            launches the default browser with that link. You may override
            that and provide your own event handler if you like. 
        Parameters:
            name: The name for the control. You may pass "" if you don't need to
                reference the control by name. 
            text: The display text for the link. 
            URL: The link. Example: "http://python.rhino3d.com/forums/". Your
                code can retrieve this URL from the Tag property of the control. 
            breakFlowAfter: Pass True to have the next control on a new line. 
                False to have the next control on the same line if there is room.
            delegate: The event handler when the LinkClicked event is raised. 
                Pass None if you want to launch the default browser with the URL.
        Returns:
            The control which was added.
        """
        c = LinkLabel()
        c.Tag = URL # Stuff the URL here so the event handler can get it :)
        c.Text = text
        c.AutoSize = True
        c.TabStop = False
        c.Margin = System.Windows.Forms.Padding(3, 5, 3, 0) # 5 is to align with other controls vertically
        self.SetFlowBreak(c, breakFlowAfter)
        if (delegate != None):
            c.LinkClicked += delegate
        else:
            c.LinkClicked += self.linkLabel_LinkClicked
        self.controls.append(c)
        return c
        
    def linkLabel_LinkClicked(self, sender, e):
        """
        The default event handler for the addLinkLabel method (see above). 
        """
        try:
            # Open the default browser with a URL:
            System.Diagnostics.Process.Start(sender.Tag)
            sender.LinkVisited = true;
        except:
            pass
    
    def addPictureBox(self, name, filename, breakFlowAfter):
        """
        Adds a PictureBox control. The size is automatically determined by 
            the image file passed.
            The following image types are supported: BMP, GIF, JPEG, PNG, TIFF.
            Note: In some cases the Winforms layout code seems to add too much
                vertical space around a PictureBox. One solution is to add an empty
                label before the control and set its breakFlowAfter property
                to False. Like this:
                    addLabel("", "", None, False)
                    addPictureBox("picbox1", "./SamplePicture.jpg", True)

        Parameters:
            name: The name for the control. You may pass "" if you don't need to
                reference the control by name. 
            filename: The filename for the image to display.
                Examples: "c:/MyPicture.bmp" or "./Resources/Diagram.jpg"
            breakFlowAfter: Pass True to have the next control on a new line. 
                False to have the next control on the same line if there is room.
        Returns:
            The control which was added.
        """
        c = PictureBox()
        c.Name = name
        try:
            image = Image.FromFile(filename)
            c.Image = image
            c.Height = image.Height
            c.Width = image.Width
            self.SetFlowBreak(c, breakFlowAfter)
            self.controls.append(c)
            return c
        except:
            print "Error: Could not load image "+filename
            return None
        
    def addTextBox(self, name, text, width, breakFlowAfter, delegate):
        """
        Adds a TextBox control. 
        Parameters:
            name: The name for the control. You may pass "" if you don't need to
                reference the control by name. 
            text: The default text for the box.
            width: The horizontal size in pixels for the control.
            breakFlowAfter: Pass True to have the next control on a new line. 
                False to have the next control on the same line if there is room.
            delegate: The event handler when the TextChanged event is raised. 
                Pass None if you don't need to handle the event. 
        Returns:
            The control which was added.
        """
        c = TextBox()
        c.Name = name
        c.Text = text
        c.Size = System.Drawing.Size(width, 23)
        c.TabIndex = self.tabIndex; self.tabIndex += 1
        if (delegate != None):
            c.TextChanged += delegate
        self.SetFlowBreak(c, breakFlowAfter)
        self.controls.append(c)
        return c
    
    def addReadonlyText(self, name, text, width, breakFlowAfter):
        """
        Adds a ReadOnly Text field control. The text appears in a box
            and is disabled so the user knows they can't type into it. 
        Parameters:
            name: The name for the control. You may pass "" if you don't need to
                reference the control by name. 
            text: The text for the box.
            width: The horizontal size in pixels for the control.
            breakFlowAfter: Pass True to have the next control on a new line. 
                False to have the next control on the same line if there is room.
        Returns:
            The control which was added.
        """
        c = Label()
        c.Name = name
        c.Text = text
        c.TabStop = False
        c.AutoEllipsis = True
        c.BorderStyle = System.Windows.Forms.BorderStyle.Fixed3D
        c.Size = System.Drawing.Size(width, 23)
        c.Enabled = False
        c.Margin = System.Windows.Forms.Padding(3, 3, 3, 3)
        c.Padding = System.Windows.Forms.Padding(3, 3, 3, 3) 
        self.SetFlowBreak(c, breakFlowAfter)
        self.controls.append(c)
        return c
    
    def addCheckBox(self, name, text, checked, breakFlowAfter, delegate):
        """
        Adds a CheckBox control to the panel.
        Parameters:
            name: The name for the control. You may pass "" if you don't need to
                reference the control by name. 
            text: The label for the control. 
            checked: Pass True to initiall set the box to checked; otherwise False.
            breakFlowAfter: Pass True to have the next control on a new line. 
                False to have the next control on the same line if there is room.
            delegate: The event handler when the CheckStateChanged event is raised. 
                Pass None if you don't need to handle the event. 
        Returns:
            The control which was added.
        """
        c = CheckBox()
        c.Name = name
        c.Text = text
        c.AutoSize = True
        c.Checked = checked
        c.TabIndex = self.tabIndex; self.tabIndex += 1
        if (delegate != None):
            c.CheckStateChanged += delegate
        self.SetFlowBreak(c, breakFlowAfter)
        self.controls.append(c)
        return c

    def addFlowLayoutPanel(self, name, text, height, width, breakFlowAfter):
        c = FlowLayoutPanel()
        c.Name = name
        c.Text = text
        c.Height = height
        c.Width = width
        self.SetFlowBreak(c, breakFlowAfter)
        self.controls.append(c)
        return c
    
    def addButton(self, name, text, width, breakFlowAfter, delegate):
        """
        Adds a push button control to the form. 
            Note: Buttons with text "OK" and "Cancel" are treated as special
            cases and the appropriate flags are set so they function like
            normal Windows OK and Cancel buttons (dismissing the Form). 
        Parameters:
            name: The name for the control. You may pass "" if you don't need to
                reference the control by name. 
            text: The text for the button. 
            width: The horizontal size in pixels for the control.
            breakFlowAfter: Pass True to have the next control on a new line. 
                False to have the next control on the same line if there is room.
            delegate: The event handler when the Click event is raised. 
                Pass None if you don't need to handle the event. 
        Returns:
            The control which was added.
        """
        c = Button()
        c.AutoSizeMode = AutoSizeMode.GrowAndShrink
        c.AutoEllipsis = False
        c.Name = name
        c.Text = text
        c.TabIndex = self.tabIndex; self.tabIndex += 1
        if (delegate != None):
            c.Click += delegate
        if (width != None):
            c.Width = width
        else:
            c.AutoSize = True
        # Special case the OK and Cancel buttons so they work as expected
        if (text == "OK"):
            c.DialogResult = DialogResult.OK
        elif (text == "Cancel"):
            c.DialogResult = DialogResult.Cancel
        self.SetFlowBreak(c, breakFlowAfter)
        self.controls.append(c)
        return c
    
    def addComboBox(self, name, items, initialIndex, breakFlowAfter, delegate):
        """
        Adds a multiple selection drop-down list control to the panel. 
        Note: This control currently takes up too much vertical space on the form.
            There seems to be a layout bug in the Winforms auto-size code. 
        Parameters:
            name: The name for the control. You may pass "" if you don't need to
                reference the control by name. 
            items: A list of strings, one for each choice from the box. 
            initialIndex: The zero based index of which item is initially selected. 
            breakFlowAfter: Pass True to have the next control on a new line. 
                False to have the next control on the same line if there is room.
            delegate: The event handler when the SelectedIndexChanged event is raised. 
                Pass None if you don't need to handle the event. 
        Returns:
            The control which was added.
        """
        c = ComboBox()
        c.Name = name
        for item in items:
            c.Items.Add(item)
        c.DropDownStyle = ComboBoxStyle.DropDownList # So you can't type into it
        c.SelectedIndex = initialIndex
        c.TabIndex = self.tabIndex; self.tabIndex += 1
        if (delegate != None):
            c.SelectedIndexChanged += delegate
        self.SetFlowBreak(c, breakFlowAfter)
        self.controls.append(c)
        return c
    
    def addNumericUpDown(self, name, lowerLimit, upperLimit, increment, \
        decimalPlaces, initValue, width, breakFlowAfter, delegate):
        """
        Adds a NumericUpDown control. This provides a type in area
            to enter the number and arrows to increment/decrement the number.
        Parameters:
            name: The name for the control. You may pass "" if you don't need to
                reference the control by name. 
            lowerLimit: The lowest value allowed. Lesser values are ignored and 
                this limit is used instead.
            upperLimit: The highest value allowed. Larger values are ignored and 
                this limit is used instead.
            increment: The amount the number is incresed or decreased with 
                each click of the arrows. 
            decimalPlaces: The number of digits to display. 
                Pass 0 to display integers.
            initValue: The initial (default) value to display. 
            width: The horizontal size in pixels for the control.
            breakFlowAfter: Pass True to have the next control on a new line. 
                False to have the next control on the same line if there is room.
            delegate: The event handler when the ValueChanged event is raised. 
                Pass None if you don't need to handle the event. 
        Returns:
            The control which was added.
        """
        c = NumericUpDown()
        c.BeginInit()
        c.Name = name
        c.TabIndex = self.tabIndex; self.tabIndex += 1
        if (delegate != None):
            c.ValueChanged += delegate
        c.Minimum = lowerLimit
        c.Maximum = upperLimit
        c.Increment = increment
        c.DecimalPlaces = decimalPlaces
        c.Value = initValue
        if (width != None):
            c.Width = width
        self.SetFlowBreak(c, breakFlowAfter)
        self.controls.append(c)
        c.EndInit()
        return c
    
    def addTrackBar(self, name, lowerLimit, upperLimit, smallChange, largeChange, tickFrequency, initValue, width, breakFlowAfter, delegate):
        """
        Adds a track bar (slider) control
        Parameters:
            name: The name for the control. You may pass "" if you don't need to
                reference the control by name. 
            lowerLimit: The lowest value allowed. Lesser values are ignored and 
                this limit is used instead.
            upperLimit: The highest value allowed. Larger values are ignored and 
                this limit is used instead.
            smallChange: Sets how many positions to move if the keyboard arrows 
                are used to move the slider.
            largeChange: Sets how many positions to move if the bar is clicked on 
                either side of the slider.
            initValue: The initial (default) value to display. 
            width: The horizontal size in pixels for the control.
            breakFlowAfter: Pass True to have the next control on a new line. 
                False to have the next control on the same line if there is room.
            delegate: The event handler when the ValueChanged event is raised. 
                Pass None if you don't need to handle the event. 
        Returns:
            The control which was added.
        """
        c = TrackBar()
        c.BeginInit()
        c.Name = name
        c.TabIndex = self.tabIndex; self.tabIndex += 1
        if (width != None):
            c.Width = width
        if (delegate != None):
            c.ValueChanged += delegate
        c.Minimum = lowerLimit
        c.Maximum = upperLimit
        c.SmallChange = smallChange
        c.LargeChange = largeChange
        if (tickFrequency != None):
            c.TickFrequency = tickFrequency
        c.Value = initValue
        self.SetFlowBreak(c, breakFlowAfter)
        self.controls.append(c)
        c.EndInit()
        return c
    
    def layoutControls(self):
        """
        Add all the accumulated controls to the panel. Call this method 
        after you have used the "addXYZ..." methods to add your 
        controls to the panel.
        """
        self.SuspendLayout()
        self.AutoSize = True
        self.AutoSizeMode = AutoSizeMode.GrowAndShrink
        for c in self.controls:
            self.Controls.Add(c)
        self.ResumeLayout(False)

if( __name__ == "__main__" ):
    print "No Syntax Errors"