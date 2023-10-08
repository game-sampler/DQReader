import openpyxl, difflib
import pandas as pd
import matplotlib
from collections import Counter
from matplotlib import pyplot as plt
import copy
import tkinter
from tkinter.simpledialog import askstring, askinteger
import tkinter.font as tkinterfont
from tkinter import ttk
import cv2 as cv

#idea - gui app for dqm analytics
#also comparing images to monster images because its funny

#class for converting pandas dataframes to tkinter treeviews
class DFViewer():
    def __init__(self, dataframe, predicate, label, w, h, scrollbar=True, sort_buttons=False):
        #basic setup
        self.root = tkinter.Tk()
        self.root.geometry("%sx%s" % (w, h))
        self.root.title(label)
        self.dataframe = dataframe
        cols = list(dataframe.columns)

        #generates the treeview and slaps it onto the window
        self.table = ttk.Treeview(self.root, selectmode='extended')
        self.table.pack(fill='both')
        self.table['columns'] = cols
        for c in cols:

            #gets a column width by running the given numeric predicate using the column and dataframe
            col_w = predicate(c, self.dataframe)
            self.table.column(c, anchor="w", width=col_w)
            self.table.heading(c, text=c, anchor='w')

        #inserts all values
        for index, row in self.dataframe.iterrows():
            self.table.insert("",0,text=index,values=list(row))
        
        #sets up scrollbar
        if scrollbar:
            scroller = ttk.Scrollbar(self.root, orient ="horizontal", command = self.table.xview)
            scroller.pack(fill='x')
            self.table.config(xscrollcommand=scroller.set)
        
        #sets up buttons to sort the data by each column
        if sort_buttons:
            for attr in self.dataframe.columns:
                button = tkinter.Button(self.root, text="Sort by %s" % attr, command=lambda attr=attr: self.sort_by_col(attr))
                button.pack(side="left", expand=True, fill='x')
    
    #column sort function
    def sort_by_col(self, col):
        self.dataframe = self.dataframe.sort_values(by=[col], ascending=True)
        self.update_from_dataframe()

    #updates the table with new values from the dataframe
    def update_from_dataframe(self):
        for i in self.table.get_children():
            self.table.delete(i)
        for index, row in self.dataframe.iterrows():
            self.table.insert("",0,text=index,values=list(row))

#grabs masterguide from folder - errors and exits if not found
try:
    masterguide = pd.read_excel("MasterGuide.xlsx", sheet_name=0)
except:
    raise FileNotFoundError("No master's guide found or it is not in the same directory as this program. Please download it here: https://docs.google.com/spreadsheets/d/1oAOL4wj39wknnP2iIHIX3jBoVQ6iUERwiVBLu63sBxU/edit#gid=0.")

#drops first row and column
masterguide = masterguide.drop(0)
masterguide = masterguide.drop("Unnamed: 0", axis=1)

#strips any leading spaces from col names
masterguide.columns = masterguide.columns.str.strip()

#fills in any none values in breed section with "Unbreedable", then changes "None" values to that
#fills in location blanks with "Unknown"
masterguide.Location = masterguide.Location.fillna("Unknown")
masterguide.Recipe = masterguide.Recipe.fillna("Unbreedable").apply(lambda x: "Unbreedable" if x == "None" else x)

#converts all of the stat numbers to integers and converts "M" and "G" to integers for ease of analysis
for monster_stat in ["HP", "MP", "Atk", "Def", "Agi", "Int"]:
    masterguide[monster_stat] = masterguide[monster_stat].apply(lambda x: int(x))
masterguide["Size"] = masterguide.Size.apply(lambda x: 2 if x == "M" else (3 if x == "G" else x))

#fixes a spelling error in family and strips spaces
masterguide["Family"] = masterguide["Family"].apply(lambda x: x.strip().replace("Materal", "Material"))

#fills in the blanks for merging traits and skills
masterguide["Merging Trait"] = masterguide["Merging Trait"].fillna("Unknown")
masterguide["Merging Skill"] = masterguide["Merging Skill"].fillna("Unknown")

#name-indexes monsters for ease of use
masterguide.set_index('Name')

#random monster picker
random_monsters = lambda x: masterguide.sample(x)

#basic window width predicate for monster viewing
def basic_predicate(c, tb):
    extragap = 7 if c in ["Atk", "Def", "Agi", "Int", "HP", "MP"] else 0
    return max(max(font.measure(str(i))+extragap, font.measure(c)+4) for i in tb[c])

#now for the funny
monster_window = tkinter.Tk()
monster_window.title("The Great Quest")
monster_window.geometry("500x500")

#code to one-click generate nice little tables for each family using the DFViewer class

def show_monsters(family):
    table = masterguide.groupby("Family").get_group(family) if family != "All Monsters" else masterguide
    win = DFViewer(table, basic_predicate, "%s Family" % family, 1500, 350, sort_buttons=True)
    win.root.mainloop()

#populates main gui with buttons to display tables for each family
buttons = {}
y_offset = 0
for v in ["All Monsters"] + list(set(masterguide["Family"].values)):
    buttons[v] = tkinter.Button(monster_window, text=("%s Family" % v) if v != "All Monsters" else v, command=lambda v=v: show_monsters(v))
    buttons[v].place(x=25, y=50*(y_offset+1))
    y_offset += 1

#custom filters and analytics tbd
custom_filters = tkinter.Button(monster_window, text="Custom Filters", command=lambda: 1)
custom_filters.place(x=350, y=50*y_offset)

#idea - custom filter by the following:
#in breed recipe (e.g. searching zoma returns all monsters that use him in their breed recipe) - some text cleaning required, maybe yoink the code from breeder
#name search
#skill search
#traits search (e.g. searching for "heat up" shows all monsters that have it)
#locational search

analytics = tkinter.Button(monster_window, text="Analytics", command=lambda: 1)
analytics.place(x=350, y=50*(y_offset-1))

#analytics:
#not sure what to do here, maybe the crosstab stuff
#knowing quantities of what (i.e. how many x are y) is a good start
#stat averages perhaps? how many monsters have a specific trait? (inputted by close match with difflib to avoid translation issues to an extent)

#font setup to allow measurement for width setting
font = tkinterfont.Font(family="Consolas", size=10, weight="normal")

#finally, runs program
monster_window.mainloop()