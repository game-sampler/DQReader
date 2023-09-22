import openpyxl, difflib
import pandas as pd
import matplotlib
from collections import Counter
from matplotlib import pyplot as plt

#grabs masterguide from folder - errors and exits if not found
try:
    masterguide = pd.read_excel("MasterGuide.xlsx", sheet_name=0)
except:
    raise FileNotFoundError("No master's guide found or it is not in the same directory as this program. Please download it here: https://docs.google.com/spreadsheets/d/1oAOL4wj39wknnP2iIHIX3jBoVQ6iUERwiVBLu63sBxU/edit#gid=0.")

#drops first row and column
masterguide = masterguide.drop(0)
masterguide = masterguide.drop("Unnamed: 0", axis=1)

#fills in any none values in breed section with "Unbreedable", and fills in those for location with "Unknown"
masterguide.Name.fillna("Unbreedable")
masterguide.Location.fillna("Unknown")

#strips any leading spaces from col names
masterguide.columns = masterguide.columns.str.strip()

#converts all of the stat numbers to integers and converts size 2 to "M" to be game-accurate
for monster_stat in ["HP", "MP", "Atk", "Def", "Agi", "Int"]:
    masterguide[monster_stat] = masterguide[monster_stat].apply(lambda x: int(x))
masterguide["Size"] = masterguide.Size.apply(lambda x: x if x != 2 else "M")

#fixes a spelling error in family and strips spaces
masterguide["Family"] = masterguide["Family"].apply(lambda x: x.strip().replace("Materal", "Material"))


