import os, numpy
import pandas as pd
from matplotlib import pyplot as plt
import tkinter
import tkinter.font as tkinterfont
from tkinter import ttk, filedialog
import openpyxl
from openpyxl_image_loader import SheetImageLoader
from PIL import ImageTk, Image
import cv2

#idea - gui app for dqm analytics
#also comparing images to monster images because its funny

#class for converting pandas dataframes to tkinter treeviews
class DFViewer():
    def __init__(self, dataframe, predicate, label, w, h, scrollbar=True, sort_buttons=False):
        #basic setup
        self.root = tkinter.Toplevel()
        self.root.geometry("%sx%s" % (w, h))
        self.root.title(label)
        self.dataframe = dataframe
        cols = list(dataframe.columns)

        #shows search numbers and what have you
        label = tkinter.Label(self.root, text="%d entries found" % len(dataframe))
        label.pack(side="top")

        #generates the treeview and slaps it onto the window
        self.table = ttk.Treeview(self.root, selectmode='extended')
        self.table.pack(fill='both')
        self.table['columns'] = cols
        self.table.bind("<Double-1>", self.OnDoubleClick)
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

    #double click to show a picture of the monster
    def OnDoubleClick(self, event):
        item = self.table.selection()[0]
        row = int(self.table.item(item,"text"))
        global dt
        img = ImageTk.PhotoImage(dt[row-1])
        win = tkinter.Toplevel()
        win.geometry("300x300")
        win.title("%s" % masterguide['Name'].values[row-1])
        label = tkinter.Label(win, image=img)
        label.pack()
        win.mainloop()

if __name__ == "__main__":
    #grabs masterguide from folder - errors and exits if not found
    guide_path = os.path.dirname(os.path.realpath(__file__)) + "\\MasterGuide.xlsx"
    
    #image loading code
    masterguide = pd.read_excel(guide_path, sheet_name=0)
    img = openpyxl.load_workbook(guide_path)
    act = img['Monsters ']
    dt = []
    for a in act.iter_rows(min_col=1, max_col=1):
        loc = a[0].coordinate
        image_loader = SheetImageLoader(act)
        if image_loader.image_in(loc):
            image = image_loader.get(loc)
            image.resize((300, 300))
            dt.append(image)
        else:
            print("image fail at cell %s, substituting slime image" % loc)
            if len(dt):
                dt.append(dt[0])
    dt = dt[:722]
    comp_imgs = [cv2.cvtColor(numpy.array(i), cv2.COLOR_RGB2BGR) for i in dt]

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
    monster_window.title("DQReader")
    monster_window.geometry("500x300")

    #code to one-click generate nice little tables for each family using the DFViewer class

    def show_monsters(family):
        table = masterguide.groupby("Family").get_group(family) if family != "All Monsters" else masterguide
        win = DFViewer(table, basic_predicate, family, 1500, 350, sort_buttons=True)
        win.root.mainloop()

    #populates main gui with buttons to display tables for each family
    buttons = {}
    y_offset = 0
    for v in ["All Monsters"] + list(set(masterguide["Family"].values)):
        buttons[v] = tkinter.Button(monster_window, text=("%s Family" % v) if v != "All Monsters" else v, command=lambda v=v: show_monsters(v))
        buttons[v].place(x=25, y=25*(y_offset+1))
        y_offset += 1

    #custom filters and analytics tbd
    def filter_window():
        window = tkinter.Toplevel()
        window.geometry("300x300")
        window.title("Custom Filters")
        textbox = tkinter.Entry(window)
        textbox.place(x=100, y=0)
        def run_filter(arg):
            term = textbox.get()
            filtered = masterguide.copy()
            if term == "":
                tkinter.messagebox.showerror('Error', 'No search term.')
                return
            else:
                if arg == "Trait Search":
                    filtered = filtered[filtered['Traits'].str.contains(term, case=False)]
                if arg == "Name Search":
                    filtered = filtered[filtered['Name'].str.contains(term, case=False)]
                if arg == "Skill Search":
                    filtered = filtered[filtered['Skill'].str.contains(term, case=False)]
                if arg == "Location Search":
                    filtered = filtered[filtered['Location'].str.contains(term, case=False)]
                if arg == "Breed Search":
                    filtered = filtered[filtered['Recipe'].str.contains(term, case=False)]
            if len(filtered) == 0:
                tkinter.messagebox.showinfo('', 'No results found!')
            else:
                filterview = DFViewer(filtered, basic_predicate, "Search Results", 1500, 350, sort_buttons=True)
                filterview.root.mainloop()
        buttons = {}
        y_offset = 0
        for v in ["Trait Search", "Name Search", "Skill Search", "Location Search", "Breed Search"]:
            buttons[v] = tkinter.Button(window, text=v, command=lambda arg=v: run_filter(arg))
            buttons[v].place(x=25, y=50*(y_offset+1))
            y_offset += 1
        window.mainloop()

    custom_filters = tkinter.Button(monster_window, text="Custom Filters", command=filter_window)
    custom_filters.place(x=350, y=75)

    def analytics_window():
        window = tkinter.Toplevel()
        window.geometry("300x300")
        window.title("Analytics Options")
        #generic histogram function
        def histogram(cols, bins, xl, yl):
            plt.hist([masterguide[x] for x in cols], bins, histtype='bar', label=cols)
            plt.legend(loc='upper right')
            plt.xlabel(xl)
            plt.ylabel(yl)
            plt.show()
        stat_histo = tkinter.Button(window, text="View Stat Histogram", command=lambda: histogram(['Atk', 'Def', 'Agi', 'Int', 'HP', 'MP'], 200, 'Stat Value', 'Number of Monsters'))
        size_histo = tkinter.Button(window, text="View Size Histogram", command=lambda: histogram(['Size'], 4, 'Monster Size', 'Number of Monsters'))
        T = tkinter.Text(window, height = 8, width = 52)
        l = tkinter.Label(window, text = "Stat Averages")
        l.config(font =("Courier", 14))
        l.pack()
        T.pack()
        for s in ['Atk', 'Def', 'Agi', 'Int', 'HP', 'MP']:
            T.insert(tkinter.END, '%s Average: %f\n' % (s, masterguide[s].mean()))
        stat_histo.pack()
        size_histo.pack()
        T.config(state = tkinter.DISABLED)
        window.mainloop()

    analytics = tkinter.Button(monster_window, text="Analytics", command=analytics_window)
    analytics.place(x=350, y=50)
    #analytics:
    #not sure what to do here, maybe the crosstab stuff
    #knowing quantities of what (i.e. how many x are y) is a good start
    #stat averages perhaps? how many monsters have a specific trait? (errors should be ironed out at this point)


    #comparison method for image searching
    def compare_histograms(image1, image2):
        hist1 = cv2.calcHist([image1], [0], None, [256], [0, 256])
        hist2 = cv2.calcHist([image2], [0], None, [256], [0, 256])

        similarity_score = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)
        return similarity_score

    def imsearch_window():
        window = tkinter.Toplevel()
        window.geometry("300x300")
        window.title("Image Search")
        l = tkinter.Label(window, text="Display how many results?")
        l.pack()
        textbox = tkinter.Entry(window)
        textbox.pack()
        def monsearch():
            term = textbox.get()
            if term == "":
                term = 750
            term = int(term)
            #prep target image for opencv
            file_path = filedialog.askopenfilename()
            if file_path:
                im = Image.open(file_path)
                im = cv2.cvtColor(numpy.array(im), cv2.COLOR_RGB2BGR)
                scores = [(compare_histograms(i, im)) for i in comp_imgs]
                cln = masterguide.copy()
                cln['Similarity Score'] = scores
                cln = cln.nlargest(term, ['Similarity Score'])
                cln = cln.sort_values(by=['Similarity Score'], ascending=True)
                m = DFViewer(cln, basic_predicate, "Search Results", 1500, 350, sort_buttons=True)
                m.root.mainloop()
        button = tkinter.Button(window, text="Open File", command=monsearch)
        button.pack()

        window.mainloop()

    imsearch = tkinter.Button(monster_window, text="Image Search", command=imsearch_window)
    imsearch.place(x=350, y=25)

    #font setup to allow measurement for width setting
    font = tkinterfont.Font(family="Consolas", size=10, weight="normal")

    #finally, runs program
    monster_window.mainloop()
