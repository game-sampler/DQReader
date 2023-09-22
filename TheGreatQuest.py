import openpyxl, difflib
import pandas as pd
import matplotlib
from collections import Counter
from matplotlib import pyplot as plt
import copy
import tkinter
from tkinter.simpledialog import askstring, askinteger
from tkinter import ttk
import cv2 as cv

#idea - gui app for dqm analytics
#also comparing images to monster images because its funny

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

#random monster picker
random_monsters = lambda x: masterguide.sample(x)

#test, prints a crosstab of merging skills by family
#family_health = pd.crosstab(masterguide['Family'], masterguide['Merging Skill'])
#family_health.plot.bar(legend=True, title="Merging Skills by Family")
#plt.show()

#now for the funny
monster_window = tkinter.Tk()
monster_window.title("The Great Quest")
monster_window.geometry("500x500")

#code to one-click generate nice little tables for each family

def show_monsters(family):
    fammed = masterguide.groupby("Family")
    fammed = fammed.get_group(family)
    newroot = tkinter.Tk()
    newroot.title('%s Family' % family)
    cols = list(masterguide.columns)

    review = ttk.Treeview(newroot)
    review.pack()
    review['columns'] = cols
    for c in cols:
        review.column(c, anchor="w")
        review.heading(c, text=c, anchor='w')

    for index, row in fammed.iterrows():
        review.insert("",0,text=index,values=list(row))

    verscrlbar = ttk.Scrollbar(newroot, orient ="horizontal", command = review.xview)
    verscrlbar.pack(side ='bottom', fill ='x')
    newroot.mainloop()

#populates main gui with buttons to display tables for each family

buttons = {}
y_offset = 0
for v in list(set(masterguide["Family"].values)):
    buttons[v] = tkinter.Button(monster_window, text="%s Family" % v, command=lambda v=v: show_monsters(v))
    buttons[v].place(x=25, y=50*(y_offset+1))
    y_offset += 1

custom_filters = tkinter.Button(monster_window, text="Custom Filters", command=show_analytics_window)
custom_filters.place(x=350, y=50*y_offset)

custom_filters = tkinter.Button(monster_window, text="Analytics", command=superfilter)
custom_filters.place(x=350, y=50*(y_offset-1))

monster_window.mainloop()