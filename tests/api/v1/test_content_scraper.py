from fastapi.testclient import TestClient
from fastapi import FastAPI
import json
import os
from app.api.v1.content_scraper import router

# Create the FastAPI app and include the router
app = FastAPI()
app.include_router(router)

# Initialize the TestClient with the FastAPI app
client = TestClient(app)

URLS = ["https://resources.corwin.com/sites/default/files/handout_14.1.pdf",
        "https://arxiv.org/abs/2409.02056",
        "https://arxiv.org/pdf/2409.02056",
        "https://en.wikipedia.org/wiki/George_W._Bush",
        "https://smallbizsurvival.com/2024/08/young-americans-returning-to-rural-for-more-than-just-holiday-dinners.html"]
    
# def test_pdf_scraper(capfd):
#     response = client.post("/pdf-scraper", json={"url": URLS[0]})
#     assert response.status_code == 200
#     response_text = response.text
    
#     # with capfd.disabled():
#     #     print(response_text)
        
#     assert len(response_text) > 1
    
# def test_arxiv_scraper_abs(capfd):
#     response = client.post("/arxiv-scraper", json={"url": URLS[1]})
#     assert response.status_code == 200
#     response_text = response.text
    
#     # with capfd.disabled():
#     #     print(response_text)
        
#     assert len(response_text) > 1


# def test_arxiv_scraper_pdf(capfd):
#     response = client.post("/arxiv-scraper", json={"url": URLS[2]})
#     assert response.status_code == 200
#     response_text = response.text
    
#     # with capfd.disabled():
#     #     print(response_text)
        
#     assert len(response_text) > 1

# def test_wikipedia_scraper(capfd):
#     response = client.post("/wikipedia-scraper", json={"url": URLS[3]})
#     assert response.status_code == 200
#     response_text = response.text
    
#     with capfd.disabled():
#         print(response_text)
        
#     with open("log_wikipedia_scraper.txt", "w") as file:
#         file.write(response_text)
        
#     assert len(response_text) > 1

# def test_web_scraper(capfd):
#     response = client.post("/web-scraper", json={"url": URLS[3]})
#     assert response.status_code == 200
#     response_text = response.text
    
#     with capfd.disabled():
#         print(response_text)
    
#     with open("log_web_scraper.txt", "w") as file:
#         file.write(response_text)
    
#     assert len(response_text) > 1

def test_scraper_urls(capfd):
    response = client.post("/scrape-urls", json={"urls": URLS})
    assert response.status_code == 200
    json_data = response.json()
    
    pretty_json = json.dumps(json_data, indent=4, sort_keys=True)
   
    with open("log_output.csv", "w") as file:
        file.write(pretty_json)
    
    assert len(json_data) > 1
