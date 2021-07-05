import re
from numpy.lib.function_base import append
import requests
import numpy as np
from requests.api import get
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from datetime import datetime

iterate = 0

# Print iterations progress
def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    # Print New Line on Complete
    if iteration == total: 
        print()

def getuserID(access_token):
    url = "https://graph.facebook.com/v11.0/me?access_token="+access_token
    req = requests.get(url).json()
    return req["id"]

def indexPage(access_token):
    url = "https://graph.facebook.com/v11.0/me/accounts?fields=name,access_token&access_token="+access_token
    req = requests.get(url).json()
    return req["data"]

def indexPageInbox(id,limit,page_token):
    url = f"https://graph.facebook.com/v11.0/{id}/conversations?fields=id&limit={limit}&access_token={page_token}"
    req = requests.get(url).json()
    return req["data"]

def getChatByID(id,page_id,page_token):
    global iterate
    url = f"https://graph.facebook.com/v11.0/{id}?fields=messages.limit(100){{message,from}}&access_token={page_token}"
    req = requests.get(url).json()
    data = [str(msg["message"]).replace(","," ") for msg in ((req["messages"])["data"])[::-1] if (msg["from"])["id"] != page_id]
    data = list(filter(lambda x: len(x) != 0,data))
    iterate+=1
    printProgressBar(iterate, len(page_inbox), prefix = 'Extracting:', suffix = 'Complete', length = 50)
    return data

# get access_token 
now = datetime.now()
current_time = now.strftime("%d-%m-%Y-%H-%M-%S")
browser = webdriver.Chrome()
browser.get("https://m.facebook.com/composer/ocelot/async_loader/?publisher=feed")
wait = WebDriverWait(browser,60)
wait.until(lambda browser: browser.current_url == "https://m.facebook.com/composer/ocelot/async_loader/?publisher=feed&refsrc=deprecated&_rdr#_=_")
source = browser.page_source
pattern = re.compile(r'EAAAA[0-9a-zA-Z]+')
match = pattern.search(source)
access_token = match.group()
print(access_token)
browser.quit()

pages = indexPage(access_token)
print("Select page you want to collect the inbox data:")
for i in range(len(pages)):
    print(f'{i} - {(pages[i])["name"]}')
select = int(input("Select:"))

page_id = (pages[select])["id"] 
limit = int(input("How many users to retrive?:"))
page_token = (pages[select])["access_token"]
page_inbox = indexPageInbox(page_id,limit,page_token)
printProgressBar(0, len(page_inbox), prefix = 'Extracting:', suffix = 'Complete', length = 50)
chat = sum([x for x in [getChatByID(x["id"],page_id,page_token) for x in page_inbox] if x],[])
np.savetxt(f'./output/{current_time}-inbox_data.csv', chat, delimiter="," , fmt="%s",header='Users Inbox')