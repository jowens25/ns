
#import requests
#from bs4 import BeautifulSoup as bs
from datetime import datetime, timezone
import numpy as np
import sys

def calculate_last_50_jitter(delays):
    delays = delays[-50:]
    return np.sum(np.abs(np.diff(delays)))/(len(delays)-1)

def file_name_to_time(name):
    timestamp_seconds = float(name.split("_")[0])
    return  datetime.fromtimestamp(timestamp_seconds, timezone.utc)

def get_latest_data(references :list[str]):

    ts = {}

    for r in references:

        ts[r["href"]] = r["href"].split("_")[0]

    return max(ts, key=ts.get)


def get_files_to_view():
    host = "http://10.1.10.96:8000"
    try:
        #rsp = requests.get(host, timeout=0.1)
        #soup = bs(rsp.content, "html.parser")
        #references = soup.find_all("a", href=True)
        #print(references)
        #return references
        return
    except Exception as e:
        print(e)
        raise



def get_data_by_name(name :str):
    host = "http://10.1.10.96:8000"

    try:
        rsp = requests.get(host+"/"+name)
    except Exception as e:
        print(e)
        sys.exit()
        


    lines = rsp.content.decode('utf-8').splitlines()

    ts = []
    delays = []
    for i, line in enumerate(lines):
        if i != 0:
            values = line.split(",")
            ts.append(float(values[0]))
            delays.append(float(values[1]))

    return file_name_to_time(name), ts, delays

def get_network_delay_data_locally():

    host = "http://10.1.10.96:8000"

    try:
        rsp = requests.get(host)
    except Exception as e:
        print(e)
        sys.exit()

    #rsp = requests.get(host)
    soup = bs(rsp.content, "html.parser")

    references = soup.find_all("a", href=True) #["href"]
    file_name = get_latest_data(references)
    rsp = requests.get(host+"/"+file_name)

    lines = rsp.content.decode('utf-8').splitlines()

    ts = []
    delays = []
    for i, line in enumerate(lines):
        if i != 0:
            values = line.split(",")
            ts.append(float(values[0]))
            delays.append(float(values[1]))

    return file_name_to_time(file_name), ts, delays

