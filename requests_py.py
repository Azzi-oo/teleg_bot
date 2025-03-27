import requests

url = "https://catfact.ninja/fact"

response = requests.get(url)

if response.status_code == 200:
    data = response.json()
    print(data["fact"])
else:
    print(f"Error: {response.status_code}")
