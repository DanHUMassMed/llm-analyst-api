from fastapi.testclient import TestClient
from fastapi import FastAPI
import json
import os
from app.api.v1.internet_search import router

# Create the FastAPI app and include the router
app = FastAPI()
app.include_router(router)

# Initialize the TestClient with the FastAPI app
client = TestClient(app)

    
def test_ddg_search(capfd):
    response = client.post("/ddg-search", json={"query": "dan"})
    assert response.status_code == 200
    json_data = response.json()
    
    # with capfd.disabled():
    #     pretty_json = json.dumps(json_data, indent=4, sort_keys=True)
    #     print(pretty_json)
        
    assert len(json_data) > 1
    

def test_tavily_search(capfd):
    api_key = os.environ["TAVILY_API_KEY"]
    response = client.post("/tavily-search", json={"query": "dan", "api_key":api_key})
    assert response.status_code == 200
    json_data = response.json()
    
    # with capfd.disabled():
    #     pretty_json = json.dumps(json_data, indent=4, sort_keys=True)
    #     print(pretty_json)
        
    assert len(json_data) > 1

