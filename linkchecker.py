import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import requests
import time

def getfile():
    file = filedialog.askopenfile()
    try:
        pd.read_csv(file)
        print(f'File read of {file} successful.')
        return file
    except:
        messagebox.showwarning(title="Invalid Filetype",message="Error: Please ensure input file is in CSV format.")
        return None

def collecturls(df, column):
    urls = []
    for index, row in df.iterrows():
        url = row[column]
        urls.append(url)
    return urls

def proxyurls():
    #Not sure about the structure of the proxy
    #Have been using dashes and putting proxy in target link (e.g., canadacommons.ca/xxx -> canadacommons-ca.us1.proxy.openathens.net)
    #Ex Libris docs say:
        # OpenAthens Redirector – This option uses the following URL structure:
        #     https://<OpenAthens Redirector URL>?url=<encoded target URL>
        #     The <OpenAthens Redirector URL> portion of the structure is the vendor-provided URL from OpenAthens.
        #     Enter https://go.openathens.net/redirector/<your domain> for the Proxy url parameter.
        #     The ?url= portion of the URL is added by Alma.
        #     The <encoded target URL> is the target URL in its encoded form.
    pass

def checkstatus(urls):
    statuses = []
    for url in urls:
        for i in range(7):
            try:
                status = requests.get(url)
                if status.status_code == 200 or status.status_code == 404:
                    statuses.append([f'\"{url}\"',f'\"{status.reason}\"'])
                    break
                else:
                    print(f'Status returned: {status.reason}. Retrying in {i**2} seconds.')
                    time.sleep(i**2)
                    continue
            except Exception as e:
                statuses.append([f'\"{url}\"',f'\"{e}\"'])
    return statuses

def saveoutput():
    pass

def main():
    #Build GUI for application
    root = tk.Tk()
    root.title("LoP Link Checker")
    root.minsize(500,500)
    root.attributes("-fullscreen",True)
    tk.Label(root, text="Welcome to the Library of Parliament Link Checker. Before continuing, please ensure you have exported a report from Analytics in CSV including a list of URLs to review.").pack(pady="5")
    tk.Label(root, text="STEP 1: Select a file to process:").pack(pady=10)
    file = tk.Button(root, text="Choose a file", command=getfile).pack(pady=10)
    print("File selected: ",file)
    root.update_idletasks()
    tk.Label(root, text="Which column holds the URLs to be tested?").pack(pady=5)
    columnheaders = ttk.Combobox(root, values=[]).pack(pady=10)
    if file:
        print("Found file. Loading column headers to choose.")
        df = pd.read_csv(file)
        print(df)
        headers = list(df.columns.values)
        print(headers)
        columnheaders.configure(values=headers)
        #columnselect = ttk.Combobox(root, values=headers, postcommand=getfile).pack()
        root.update_idletasks()
        column = columnheaders.get()
        print('Column selected: ',column)
    else:
        columnheaders.configure(values=["No File"])
        root.update_idletasks()
    proxyyn = False
    tk.Checkbutton(root, value="Proxy links (OpenAthens)?", variable=proxyyn).pack(pady=5)
    tk.Label(root, text="When ready to process, hit RUN. The process may take some time to complete. For updates, check the terminal.")
    ##Pass df, column, proxyyn to checkstatus
    ##Call collecturls in checkstatus to get list of URLs
    ##If proxyyn is set to True, call proxyurls in collecturls to proxy each URL as it's passed into list
    ##If URLs are proxied, pass back list of lists with [baseurl,proxiedurl] for saving in final output
    tk.Button(root, text="RUN", command=checkstatus()).pack(pady=5)
    ##############################
    root.mainloop()

if __name__ == "__main__":
    main()