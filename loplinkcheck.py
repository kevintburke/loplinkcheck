import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import re
import requests
import time
from datetime import datetime

class LinkChecker:
    def __init__(self, root):
        self.root = root
        self.root.title("LoP Link Checker")
        self.df = None
        tk.Label(root, text="Welcome to the Library of Parliament Link Checker. Before continuing, please ensure you have exported a report from Analytics in CSV including a list of URLs to review.").pack(pady=5)
        
        tk.Label(root, text="STEP 1: Select CSV file to process:").pack(pady=10)
        tk.Button(root, text="Select File", command=self.getfile).pack(pady=5)

        tk.Label(root, text="STEP 2: Which column holds the URLs to be checked?").pack(padx=10)
        self.columnbox = tk.Listbox(root, exportselection=0, height=5)
        self.columnbox.pack()

        tk.Label(root, text="Which column holds the record ID to be preserved in the output?").pack(padx=10)
        self.idbox = tk.Listbox(root, exportselection=0, height=5)
        self.idbox.pack()
        
        self.proxyyn = tk.BooleanVar()
        tk.Checkbutton(root, text="Proxy links for testing (OpenAthens ONLY)? NOTE: Proxying is currently likely to return false positives. Use with caution!", variable=self.proxyyn).pack(pady=10)

        tk.Button(root, text="Run Test", command=self.checkurls).pack(pady=10)

        self.prog = tk.Text(root, height=9)
        self.prog.pack(pady=5)

        tk.Label(root, text="WARNING: This process will run in the background and may take some time to complete. To interrupt and cancel it, open the terminal and hit Ctrl+C.").pack(pady=5)

        self.statuses = []

    def getfile(self):
        file = filedialog.askopenfilename()
        try:
            self.df = pd.read_csv(file, encoding='utf-8')
            print("File read successfully")
        except:
            messagebox.showwarning(title="Invalid Filetype",message="Error: Please ensure input file is in CSV format.")
            return None
        for column in list(self.df.columns.values):
            self.columnbox.insert(tk.END, column)
            self.idbox.insert(tk.END, column)
    
    def checkurls(self):
        urls = []
        urlcolumn = self.columnbox.get(self.columnbox.curselection())
        idcolumn = self.idbox.get(self.idbox.curselection())
        for index, row in self.df.iterrows():
            url = [row[idcolumn],str(row[urlcolumn]).lstrip("jkey=")]
            urls.append(url)
        if self.proxyyn.get():
            print("Proxying URLs...")
            for url in urls:
                url[1] = re.sub("http:","https:",url[1]).strip()
                url[1] = re.sub(" ","%20",url[1])
                baseurl = "https://go.openathens.net/redirector/lop.parl.ca?url="
                proxiedurl = baseurl + url[1]
                print(proxiedurl)
                ##This block uses the proxy format base-url-with-dashes.us1. proxy.openathens.net/rest/of/url
                ##The redirect method is preferred, but this block may work if it fails
                # baseurl = re.sub(r'(https:\/\/)([A-Za-z0-9.]+)(.*)$',r'\2',url)
                # baseurl = re.sub(r'\.',r'-',baseurl)
                # baseurl = baseurl + ".us1.proxy.openathens.net"
                # proxiedurl = re.sub(r'(https:\/\/)([A-Za-z0-9.]+)(.*)$',r'\1§\3',url)
                # proxiedurl = re.sub(r'§',baseurl,proxiedurl)
                url.append(proxiedurl)
        else:
            print("Cleaning URLs...")
            for url in urls:
                url[1] = re.sub("http:","https:",url[1]).strip()
                url[1] = re.sub(" ","%20",url[1])
                print(url[1])
                url.append(url[1])
        self.statuses = self.checkstatus(urls)
        print(type(self.statuses))
        outputdf = pd.DataFrame(self.statuses, columns=["Identifier","URL","Clean/Proxied URL","HTTP Response"])
        messagebox.showinfo(title="Process Complete",message="Process complete. Please save output")
        today = datetime.now().strftime('%d%m%Y')
        output = filedialog.asksaveasfilename(title="Save Output",defaultextension=".csv",filetypes=[("CSV","*.csv"),("All Files","*.*")])
        if not output.lower().endswith(".csv"):
            output += ".csv"
        outputdf.to_csv(output, index=False, columns=["Identifier","URL","Clean/Proxied URL","HTTP Response"])
        messagebox.showinfo(title="Output Saved",message=f'Output saved as {output}.')

    ##Replace statuses with urls list of lists, appending status code to each list as passed
    def checkstatus(self, urls):
        count = 1
        for url in urls:
            print("Checking URL: ",url[2])
            for i in range(7):
                status = None
                self.prog.insert(tk.END, f'Checking URL {count} of {len(urls)}...\n')
                self.prog.update_idletasks()
                try:
                    status = requests.get(url[2])
                    if status.status_code in [200, 404]:
                        url.append(f'{status.status_code}: {status.reason}')
                        self.prog.update_idletasks()
                        break
                    else:
                        print(f'Status returned: {status.reason}. Retrying in {2**i} seconds.')
                        self.prog.insert(tk.END, f'Error. Resting and checking link again in {2**i} seconds...\n')
                        self.prog.update_idletasks()
                        time.sleep(2**i)
                        continue
                except Exception as e:
                    url.append(e)
                    self.prog.update_idletasks()
                    break
            if status != None and (status.status_code not in [200, 404]):
                url.append(f'{status.status_code}: {status.reason}')
            self.prog.delete(1.0, tk.END)
            self.prog.update_idletasks()
            count += 1
        return urls

def main():
    root = tk.Tk()
    app = LinkChecker(root)
    root.mainloop()

if __name__ == "__main__":
    main()