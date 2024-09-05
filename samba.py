import requests
import json
import sys

def samba_process_data(model, system, query):
    url = 'https://fast-api.snova.ai/v1/chat/completions'

    req_json = {"messages": [
        {"role": "system", "content": system},
        {"role": "user", "content": query}
    ],
    "stop": ["<|eot_id|>"],
    "model": model,
    "stream": True, "stream_options": {"include_usage": True}
    }
    
    apikey = ""
    with open("apikey", "r") as f:
        apikey = f.read().splitlines()[0]
    x = requests.post(url, json = req_json, headers={'Authorization': "Basic "+  str(apikey)})    

    full_resp = ""
    for line in x.text.splitlines():
        if "data" in line:
            try:
                jsn_txt = line[line.find("data:")+6:]
                resp = json.loads(jsn_txt)
                chunk = resp["choices"][0]["delta"]["content"]

                full_resp += chunk
            except:
                pass
    return full_resp


if __name__ == "__main__":
    querry = sys.argv[1]
    print(samba_process_data("llama3-8b", "You are a friendly assistant.", querry))

