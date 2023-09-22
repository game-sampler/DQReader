import openpyxl, difflib
import pandas as pd
import matplotlib
from collections import Counter
from matplotlib import pyplot as plt

import tkinter
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
family_health = pd.crosstab(masterguide['Family'], masterguide['Merging Skill'])
family_health.plot.bar(legend=True, title="Merging Skills by Family")
plt.show()

#now for the funny