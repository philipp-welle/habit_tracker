import requests
from datetime import datetime
from tkinter import *
import math
import os

USERNAME = os.environ['ENV_USER']
TOKEN = os.environ['ENV_TOKEN']
GRAPH = os.environ['ENV_GRAPH']

today = datetime.now()
window = Tk()
count = 0
TIMER = None
coding_time = 0
Time = "00:00:00"

pixela_endpoint = "https://pixe.la/v1/users"
user_params = {
    "token": TOKEN,
    "username": USERNAME,
    "agreeTermsOfService": "yes",
    "notMinor": "yes",
}

graph_endpoint = f"{pixela_endpoint}/{USERNAME}/graphs"
graph_config = {
    "id": GRAPH,
    "name": "Coding Graph",
    "unit": "hours",
    "type": "float",
    "color": "ajisai",
}

headers = {
    "X-USER-TOKEN": TOKEN
}

get_endpoint = f"{graph_endpoint}/{GRAPH}/{today.strftime("%Y%m%d")}"

response = requests.get(url=get_endpoint, headers=headers)
todays_coding = response.json()

search_key = True

while search_key:
    if response.status_code == 503:
        response = requests.get(url=get_endpoint, headers=headers)
    else:
        todays_coding = response.json()
        search_key = False

if "quantity" in todays_coding:
    time_list = math.modf(float(todays_coding["quantity"]))
    mins = int(float(time_list[0]) * 100)
    hrs = int(time_list[1])
    if mins < 10:
        mins = f"0{mins}"
    if hrs < 10:
        hrs = f"0{hrs}"
    count = (int(float(time_list[0]) * 100) * 60) + (int(hrs) * 3600)
    coding_time = f"{math.floor(count / 3600)}.{math.floor(count / 60) % 60}"
    Time = f"{hrs}:{mins}:00"
else:
    Time = "00:00:00"


def f_start():
    f_timer()


def f_stop():
    global coding_time, graph_endpoint, count, GRAPH, headers
    window.after_cancel(TIMER)
    mins = int(math.floor(count / 60) % 60)
    if mins < 10:
        mins = f"0{mins}"
    coding_time = f"{math.floor(count / 3600)}.{mins}"
    post_endpoint = f"{graph_endpoint}/{GRAPH}"
    post_config = {
        "date": str(today.strftime('%Y%m%d')),
        "quantity": str(coding_time),
    }
    post_key = True

    if "quantity" in todays_coding:
        post_endpoint = f"{post_endpoint}/{str(today.strftime('%Y%m%d'))}"
        post_config = {
            "quantity": str(coding_time),
        }
        response_put = requests.put(url=post_endpoint, json=post_config, headers=headers)
        while post_key:
            if response_put.status_code == 503:
                response_put = requests.put(url=post_endpoint, json=post_config, headers=headers)
            else:
                post_key = False
    else:
        response_post = requests.post(url=post_endpoint, json=post_config, headers=headers)
        while post_key:
            if response_post.status_code == 503:
                response_post = requests.post(url=post_endpoint, json=post_config, headers=headers)
            else:
                post_key = False



def f_timer():
    global count, TIMER
    count += 1
    hrs = math.floor(count / 3600)
    mins = math.floor(count / 60) % 60
    secs = count % 60
    if secs < 10:
        secs = f"0{secs}"
    if mins < 10:
        mins = f"0{mins}"
    if hrs < 10:
        hrs = f"0{hrs}"
    label_time.config(text=f"{hrs}:{mins}:{secs}")
    TIMER = window.after(1000, f_timer)


label_time = Label(text=Time, font=("Ariel", 24, "bold"))
label_time.grid(row=0, column=0, columnspan=2)
btn_start = Button(text="Start", command=f_start)
btn_start.grid(row=1, column=0)
btn_stop = Button(text="Stop", command=f_stop)
btn_stop.grid(row=1, column=1)

window.mainloop()
