import requests

def main():

    resp = requests.get("http://api.ipstack.com/134.201.250.155?access_key=b098163670077c784be931441c9a96d8")
    result = resp.json()
    city = result["city"]
    print("Target is located in: %s" % city)

main()