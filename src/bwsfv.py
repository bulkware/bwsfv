#!/usr/bin/env python3

""" An application to verify file consistency with .sfv files. """

# Python imports
import argparse  # Parser for command-line options, arguments and sub-commands
import binascii  # Convert between binary and ASCII
import os  # Miscellaneous operating system interfaces
import sys  # System-specific parameters and functions
import threading  # Thread-based parallelism

# GTK imports
import gi
gi.require_version("Gdk", "3.0")
gi.require_version("Gtk", "3.0")
from gi.repository import Gdk  # GIMP Drawing Kit
from gi.repository import GdkPixbuf  # GIMP Drawing Kit
from gi.repository import GLib  # Low-level core library
from gi.repository import Gtk  # GIMP ToolKit
from gi.repository import Pango  # Text layout engine

# Declare variables
application_version = "0.6.0"
script_path = os.path.realpath(__file__)
script_dir = os.path.dirname(script_path)
css_path = os.path.join(script_dir, "default.css")
icon_path = os.path.join(script_dir, "icon_128x128.png")

# Main window
class bwsfv(Gtk.Window):

    def __init__(self):

        # Declare application variables
        self.liststore = Gtk.ListStore(str, str, str, str, str)
        self.config = {
            "window_height": 600,
            "window_width": 800
        }  # Application default configurations

        # Set window defaults
        Gtk.Window.__init__(self, title="bwsfv")
        self.set_icon_from_file(icon_path)
        self.set_default_size(
            self.config.get("window_width"),
            self.config.get("window_height")
        )
        self.set_position(Gtk.WindowPosition.CENTER_ALWAYS)

        # Check stylesheet and load it
        if os.path.isfile(css_path):
            screen = Gdk.Screen.get_default()
            css_provider = Gtk.CssProvider()
            css_provider.load_from_path(css_path)
            context = Gtk.StyleContext()
            context.add_provider_for_screen(
                screen,
                css_provider,
                Gtk.STYLE_PROVIDER_PRIORITY_USER
            )

        # MenuBar
        # ToDo: Replace this classic menu using the new style menu.
        menubar = Gtk.MenuBar()

        filemenu = Gtk.Menu()
        fileselection = Gtk.MenuItem(label="File")
        fileselection.set_submenu(filemenu)

        openselection = Gtk.ImageMenuItem.new_from_stock("gtk-open")
        openselection.set_label("Open file...")
        openselection.connect("activate", self.dialog_open_file)
        filemenu.append(openselection)

        separator = Gtk.SeparatorMenuItem()
        filemenu.append(separator)

        exitselection = Gtk.ImageMenuItem.new_from_stock("gtk-quit", None)
        exitselection.set_label("Exit")
        exitselection.connect("activate", Gtk.main_quit)
        filemenu.append(exitselection)

        menubar.append(fileselection)

        # ToolBar
        toolbar = Gtk.Toolbar()

        toolbutton = Gtk.ToolButton(stock_id=Gtk.STOCK_OPEN)
        toolbutton.set_label("Open file...")
        toolbutton.set_tooltip_text("Open file...")
        toolbutton.connect("clicked", self.dialog_open_file)
        toolbar.add(toolbutton)

        toolbutton = Gtk.ToolButton(stock_id=Gtk.STOCK_APPLY)
        toolbutton.set_label("Check files")
        toolbutton.set_tooltip_text("Check files")
        toolbutton.connect("clicked", self.check_files)
        toolbar.add(toolbutton)

        separatortoolitem = Gtk.SeparatorToolItem()
        toolbar.add(separatortoolitem)

        toolbutton = Gtk.ToolButton(stock_id=Gtk.STOCK_NEW)
        toolbutton.set_label("New file")
        toolbutton.set_tooltip_text("New file")
        toolbutton.connect("clicked", self.new_file)
        toolbar.add(toolbutton)

        toolbutton = Gtk.ToolButton(stock_id=Gtk.STOCK_ADD)
        toolbutton.set_label("Add file(s)...")
        toolbutton.set_tooltip_text("Add file(s)...")
        toolbutton.connect("clicked", self.add_files)
        toolbar.add(toolbutton)

        toolbutton = Gtk.ToolButton(stock_id=Gtk.STOCK_SAVE)
        toolbutton.set_label("Save file...")
        toolbutton.set_tooltip_text("Save file...")
        toolbutton.connect("clicked", self.save_file)
        toolbar.add(toolbutton)

        toolbutton = Gtk.ToolButton(stock_id=Gtk.STOCK_SAVE_AS)
        toolbutton.set_label("Save file as...")
        toolbutton.set_tooltip_text("Save file as...")
        toolbutton.connect("clicked", self.save_file_as)
        toolbar.add(toolbutton)

        separatortoolitem = Gtk.SeparatorToolItem()
        toolbar.add(separatortoolitem)

        toolbutton = Gtk.ToolButton(stock_id=Gtk.STOCK_ABOUT)
        toolbutton.set_label("About application...")
        toolbutton.set_tooltip_text("About application...")
        toolbutton.connect("clicked", self.about_application)
        toolbar.add(toolbutton)

        toolbutton = Gtk.ToolButton(stock_id=Gtk.STOCK_QUIT)
        toolbutton.set_label("Quit")
        toolbutton.set_tooltip_text("Quit")
        toolbutton.connect("clicked", self.quit_application)
        toolbar.add(toolbutton)

        # Treeview
        # The first column in the ListStore is file path(s), but we won't show
        # it since the method to hide columns using "set_visible" didn't work!
        treeview = Gtk.TreeView(model=self.liststore)
        treeview.set_hexpand(True)
        treeview.set_vexpand(True)

        # File name(s)
        renderer_text = Gtk.CellRendererText()
        column_text = Gtk.TreeViewColumn("File name", renderer_text, text=1)
        treeview.append_column(column_text)

        # Extension(s)
        renderer_text = Gtk.CellRendererText()
        column_text = Gtk.TreeViewColumn("Extension", renderer_text, text=2)
        treeview.append_column(column_text)

        # Hashsum(s)
        renderer_text = Gtk.CellRendererText()
        column_text = Gtk.TreeViewColumn("Hashsum", renderer_text, text=3)
        treeview.append_column(column_text)

        # Verify icon(s)
        renderer_pixbuf = Gtk.CellRendererPixbuf()
        column_pixbuf = Gtk.TreeViewColumn(
            "Verify",
            renderer_pixbuf,
            icon_name=4
        )
        treeview.append_column(column_pixbuf)

        # Wrap TreeView into a ScrolledWindow
        scrolled = Gtk.ScrolledWindow()
        scrolled.add(treeview)

        # Progress bar
        self.progressbar = Gtk.ProgressBar(show_text=True)

        # Create a box for the widgets
        box = Gtk.Box(orientation="vertical")
        box.pack_start(menubar, 0, 0, 0)
        box.pack_start(toolbar, 0, 0, 0)
        box.pack_start(scrolled, 1, 1, 0)
        box.pack_start(self.progressbar, 0, 0, 0)

        # Add the box to the window
        self.add(box)

    # New file
    def new_file(self, widget):
        self.liststore.clear()
        self.progressbar.new()
        return True

    # Open file dialog
    def dialog_open_file(self, widget):

        # Declare variables
        checkfile = None

        # Initialize file open dialog
        dialog = Gtk.FileChooserDialog(
            title="Please choose a file",
            parent=self,
            action=Gtk.FileChooserAction.OPEN
        )

        # Define file open dialog buttons
        dialog.add_buttons(
            Gtk.STOCK_CANCEL,
            Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN,
            Gtk.ResponseType.OK,
        )

        # Set file open dialog filters
        filter_text = Gtk.FileFilter()
        filter_text.set_name(".sfv files")
        filter_text.add_mime_type("text/plain")
        dialog.add_filter(filter_text)

        # Show dialog and retrieve possible selection(s)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            checkfile = dialog.get_filename()
        elif response == Gtk.ResponseType.CANCEL:
            pass

        dialog.destroy()

        # Check file selection
        if not checkfile:
            return True

        # Check file extension
        extension = os.path.splitext(checkfile)[1][1:].lower()
        if extension != "sfv":

            # Show error dialog for unsupported file extension
            dialog = Gtk.MessageDialog(
                transient_for=self,
                flags=0,
                message_type=Gtk.MessageType.ERROR,
                buttons=Gtk.ButtonsType.OK,
                text="File selection",
            )

            dialog.format_secondary_text(
                f"Unsupported file extension: {extension}"
            )

            dialog.run()
            dialog.destroy()

            return True

        # Read .sfv file
        dirname = os.path.dirname(checkfile)
        with open(checkfile, "r") as f:
            for line in f:
                line = line.strip()

                # Retrieve file information
                filename = line[0:-9]
                extension = os.path.splitext(filename)[1][1:].lower()
                hashsum = line[-8:]

                self.liststore.append([
                    os.path.join(dirname, filename),
                    filename,
                    extension,
                    hashsum,
                    "system-search"
                ])

    # Save file
    def save_file(self, widget):
        print("Save file")
        return True

    # Save file as...
    def save_file_as(self, widget):
        print("Save file as...")
        return True

    # Add files...
    def add_files(self, widget):

        # Declare variables
        filelist = []

        # Initialize file open dialog
        dialog = Gtk.FileChooserDialog(
            title="Please choose file(s)",
            parent=self,
            action=Gtk.FileChooserAction.OPEN
        )

        # Define file open dialog buttons
        dialog.add_buttons(
            Gtk.STOCK_CANCEL,
            Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN,
            Gtk.ResponseType.OK,
        )

        # Set file open dialog settings
        dialog.set_select_multiple(True)

        # Show dialog and retrieve possible selection(s)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            filelist = dialog.get_filenames()
        elif response == Gtk.ResponseType.CANCEL:
            pass

        dialog.destroy()

        # Check filelist for items
        if not filelist:
            return True

        # Loop filelist and append items to ListStore
        for item in filelist:

            # Retrieve file information
            basename = os.path.basename(item)
            extension = os.path.splitext(item)[1][1:]

            self.liststore.append([
                item,
                basename,
                extension,
                "",
                "system-search"
            ])

        # Check added files
        self.check_files(widget)
        return True

    # About application
    def about_application(self, widget):
        about = Gtk.AboutDialog(transient_for=self)
        about.set_program_name("bwsfv")
        about.set_version(application_version)
        about.set_copyright("Copyright (c) 2021+ Antti-Pekka Meronen.")
        about.set_comments("An application to verify file consistency with .sfv files.")
        about.set_website("https://github.com/bulkware/bwsfv")
        about.set_logo(GdkPixbuf.Pixbuf.new_from_file(icon_path))
        about.run()
        about.destroy()
        return True

    # Quit application
    def quit_application(self, widget):
        Gtk.main_quit()
        return True

    # A method to update ProgressBar
    def update_progessbar(self, progress):

        # Calculate percentage from progress
        if progress < 1.0:
            percent = round(100 * progress, 2)
        else:
            percent = 100

        # Update ProgressBar
        self.progressbar.pulse()
        self.progressbar.set_fraction(progress)
        self.progressbar.set_text(f"{percent}%")
        return True

    # A method to verify file consistency
    def check_files(self, widget):

        # Run file verification in it's own thread
        thread = threading.Thread(target=self.verify_files)
        thread.daemon = True
        thread.start()
        return True

    # A method to verify file consistency
    def verify_files(self):

        fraction = float(1.0 / len(self.liststore))
        progress = float(0.0)

        # Loop files from the ListStore
        for i, item in enumerate(self.liststore):

            # Check file integrity and append progress
            buf = open(item[0], "rb").read()
            buf = (binascii.crc32(buf) & 0xffffffff)
            crc32 = "%08X".lower() % buf

            progress += fraction

            # If there is a hash sum present, compare hash sums
            if item[3]:
                # Change icon depending on results
                if crc32 == item[3]:
                    self.liststore[i][4] = "emblem-default"
                else:
                    self.liststore[i][4] = "emblem-important"

            # Otherwise only apply the retrieved hash sum
            else:
                self.liststore[i][3] = crc32
                self.liststore[i][4] = "emblem-default"

            # Update ProgressBar
            GLib.idle_add(self.update_progessbar, progress)

        # Update ProgressBar to show completion
        GLib.idle_add(self.update_progessbar, 1.0)
        return True


# Initialize and run application
def main():
    win = bwsfv()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()


# Only run as a standalone application
if __name__ == "__main__":
    main()
