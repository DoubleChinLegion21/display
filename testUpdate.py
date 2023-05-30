import requests

url = 'http://192.168.86.26:5000' 
myobj = {"time": 1000, "name": "bobb", "history":{}}

x = requests.post(url, json=myobj)

print(x.text)