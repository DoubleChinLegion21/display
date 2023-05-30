import requests

url = 'http://192.168.86.26:5000' 
myobj = {"time": 111, "name": "blake", "history" : {"amilia":1231, "asdf":1233, "asdfaee": 222}}

x = requests.post(url, json=myobj)

print(x.text)