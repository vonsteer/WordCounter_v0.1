import tkinter as tk
import csv
import re
import requests
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from pandas import pandas as pd
from tkinter import filedialog, Button, END
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

titles = ''
contents = []
l= []
regex = re.compile('<title>(.*?)</title>', re.IGNORECASE|re.DOTALL) #regex is faster, chose this above bs4 or any other parser for that reason

class FirstFrame(tk.Frame):
    def __init__(self, master=None, **kwargs):
        tk.Frame.__init__(self, master, **kwargs)
        self.pack()
        master.title('WordCounter v0.1')
        master.geometry("300x200")
        lbl = tk.Label(self, text='Please select a file:')
        lbl.pack()
        self.e = tk.Entry(self,width=50)
        self.e.pack()
        self.e.focus()
        browse_button = Button(self, text='Browse', command=self.open_csv)
        browse_button.pack()
        cbutton = Button(self, text='Continue', command=self.Continue)
        cbutton.pack()
    def read_csv(self, filename):
        with open(filename,'rt') as f:
            global count
            data = csv.reader(f)
            for row  in data:
                links = row[0]
                contents.append(links)
    def open_csv(self, event=None):
        self.e.delete(0, END)
        filename = filedialog.askopenfilename()
        self.e.insert(0, filename)
    def Continue(self, event=None):
        self.read_csv(self.e.get())
        self.destroy() #destroy current window and open next
        self.app= SecondFrame(self.master)


class SecondFrame(tk.Frame):
    def __init__(self, master=None, **kwargs):
        tk.Frame.__init__(self, master, **kwargs)
        self.pack()
        master.title('WordCounter v0.1')
        master.geometry("1000x600")
        self.request(contents)
        self.filter_it(titles)
        df_words = pd.DataFrame(l, columns=['Word'])
        plt.style.use('seaborn')
        figure = plt.Figure(figsize=(10,5), dpi=100)
        ax = figure.add_subplot(111)
        canvas = FigureCanvasTkAgg(figure, self)
        canvas.get_tk_widget().pack(side = tk.BOTTOM, fill = tk.BOTH, expand = True)
        df = df_words['Word'].value_counts(ascending=False)[:10].rename_axis('Word').reset_index(name='Counts')
        graph = df.plot.barh(x='Word', y='Counts', rot=0, color='#f23d3d', ax=ax)
        ax.set_xlabel("Word Count", weight='bold')
        ax.set_ylabel("Word", weight='bold')
        ax.set_title("Wordcounter", weight='bold')
        graph.invert_yaxis()
        plt.tight_layout()
        self.text1 = tk.Text(self, height=20, width=50)
        self.scroll = tk.Scrollbar(self, command=self.text1.yview)
        self.text1.configure(yscrollcommand=self.scroll.set)
        self.text1.insert(tk.END, titles, 'color')
        self.text1.pack(side=tk.LEFT, fill = tk.BOTH, expand = True)
        self.scroll.pack(side=tk.LEFT, fill=tk.Y)
    def request(self, contents):
        global titles
        for urls in contents:   
            if ".amazon." in urls:
                headers = {
                'authority': 'www.amazon.de',
                'pragma': 'no-cache',
                'cache-control': 'no-cache',
                'upgrade-insecure-requests': '1',
                'user-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:79.0) Gecko/20100101 Firefox/79.0',
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'accept-Encoding': 'gzip, deflate, br',
                'sec-fetch-site': 'none',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-dest': 'document',
                'accept-language': 'en-GB,en;q=0.5'}
            else:
                headers = {
                'user-agent': 'Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36',}    
            url = requests.get(urls, headers=headers)
            result = regex.search(url.text)
            try:
                fr = re.sub(r'\:.*|-.*|\|.*','', (result[1]))  
                titles += (" ")+ fr + "\n"
            except(TypeError):
                fr = "Extractation Failed"
                titles += (" ")+ fr + "\n"
    def filter_it(self, titles):
        global l
        #filtered = re.sub(r'[^A-Za-z0-9 ]+', ' ',titles)
        newStopWords = ['Extractation Failed','mercado', 'libre','amazonde','amazon', 'amazonca', 'en', 'amazonde', 'amazonfr', 'amazoncom', 'amazoncouk', 'mercadolibre', 'ebay', 'ebaycom' ]
        stopwords = nltk.corpus.stopwords.words('english')
        stopwords.extend(newStopWords)
        word_tokens = word_tokenize(titles.lower()) 
        l = [w for w in word_tokens if not w in stopwords] 
    

if __name__=="__main__":
    root = tk.Tk()
    app=FirstFrame(root)
    app.mainloop()
