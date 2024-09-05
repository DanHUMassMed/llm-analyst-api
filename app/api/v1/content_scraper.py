"""
This module provides various scraping functions to extract content from different types of web links.
It includes specialized scrapers for arXiv links, PDF files, and generic web pages. 
The main function `scrape_urls` determines the appropriate 
scraper based on the URL and aggregates the content into a list of strings.
"""

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional, List

import importlib
import os
import re
import uuid
from concurrent.futures.thread import ThreadPoolExecutor

import requests
from langchain_community.document_loaders.html_bs import BSHTMLLoader
from langchain_community.document_loaders.pdf import PyMuPDFLoader
from langchain_community.document_loaders.web_base import WebBaseLoader
from langchain_community.retrievers.arxiv import ArxivRetriever
from langchain_community.retrievers.wikipedia import WikipediaRetriever

router = APIRouter()

class ScrapeRequest(BaseModel):
    url: str
 
@router.post("/pdf-scraper")
def pdf_scraper(request: ScrapeRequest):
    content = ""
    try:
        loader = PyMuPDFLoader(request.url)
        docs = loader.load()
        content = ""
        for doc in docs:
            content += doc.page_content
    except Exception as e:
        # TODO handle exception
        print("Error! : " + str(e))
    
    return content

@router.post("/arxiv-scraper")
def arxiv_scraper(request: ScrapeRequest):
    content = ""
    try:
        article_code = request.url.split("/")[-1]
        data_type = request.url.split("/")[-2]
        if data_type == "abs":
            # Get the Abstract content
            retriever = ArxivRetriever(load_max_docs=2, doc_content_chars_max=None)
            docs = retriever.invoke(article_code)
            content = docs[0].page_content
        elif data_type == "pdf":
            content = pdf_scraper(request)
        else: # assume HTML
            content = web_scraper(request)
    except Exception as e:
        # TODO handle exception
        print("Error! : " + str(e))
    
    return content

@router.post("/wikipedia-scraper")
def wikipedia_scraper(request: ScrapeRequest):
    content = ""
    try:
        article_code = request.url.split("/")[-1]
        data_type = request.url.split("/")[-2]
        if data_type == "wiki":
            retriever = WikipediaRetriever()
            docs = retriever.invoke(article_code.replace("_", " "))
            content = ""
            for doc in docs:
                content += doc.page_content
    except Exception as e:
        # TODO handle exception
        print("Error! : " + str(e))
    
    return content

    
@router.post("/web-scraper")
def web_scraper(request: ScrapeRequest):
    content = ""
    try:
        loader = WebBaseLoader(request.url)
        loader.requests_kwargs = {"verify": False}
        docs = loader.load()
        content = ""
        for doc in docs:
            content += doc.page_content

        pattern = r"\s{3,}"
        # \s matches any whitespace character (spaces, tabs, newlines, etc.).
	    # {3,} specifies that the pattern is looking for three or more consecutive whitespace characters.
        content = re.sub(pattern, "  ", content)

    except Exception as e:
        print("Error! : " + str(e))
        
    return content
        
        
# ========================================================================================

class ScrapeUrlsRequest(BaseModel):
    urls: List[str]


@router.post("/scrape-urls")
def scrape_urls(request: ScrapeUrlsRequest):
    """
    Given a list of URLs
    1. Determine an appropriate scraper based on URL content
    2. For each URL Scrape the website and aggregate the content into a list of strings
        one for each site
    """

    def extract_data_from_link(link):
        if link.endswith(".pdf"):
            scraper_nm = "pdf_scraper"
        elif "arxiv.org" in link:
            scraper_nm = "arxiv_scraper"
        elif "wikipedia.org" in link:
            scraper_nm = "wikipedia_scraper"
        else:
            scraper_nm = "web_scraper"

        content = ""
        try:
            module_nm = "app.api.v1.content_scraper"
            module = importlib.import_module(module_nm)
            scrape_content = getattr(module, scraper_nm)
            content = scrape_content(ScrapeRequest(url=link))

            if len(content) < 100:
                return {"url": link, "raw_content": None}
            return {"url": link, "raw_content": content}
        except Exception:
            return {"url": link, "raw_content": None}

    content_list = []
    try:
        with ThreadPoolExecutor(max_workers=20) as executor:
            contents = executor.map(extract_data_from_link, request.urls)
            
        content_list = [
            content for content in contents if content["raw_content"] is not None
        ]

    except Exception as e:
        print(f"Error in scrape_urls: {e}")
    return content_list

