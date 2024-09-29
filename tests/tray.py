#!/usr/bin/python
import os
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('AyatanaAppIndicator3', '0.1')
from gi.repository import Gtk as gtk, AyatanaAppIndicator3 as appindicator

def main():
    indicator = appindicator.Indicator.new(
        'customtray',
        'semi-starred-symbolic',
        appindicator.IndicatorCategory.APPLICATION_STATUS
    )
    indicator.set_status(appindicator.IndicatorStatus.ACTIVE)
    indicator.set_menu(build_menu())

def build_menu():
    menu = gtk.Menu()

    command_one = gtk.MenuItem(label='My Notes')
    command_one.connect('activate', note)
    menu.append(command_one)

    exittray = gtk.MenuItem(label='Exit Tray')
    exittray.connect('activate', quit)
    menu.append(exittray)

    menu.show_all()
    return menu

def note(_):
    os.system('gedit ~/Documents/notes.txt')

def quit(_):
    gtk.main_quit()

if __name__ == "__main__":
    main()
    gtk.main()
