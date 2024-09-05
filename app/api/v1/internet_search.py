"""
This module provides various search functions to interact with different search engines and aggregates
the results. 

The concepts originate here:
https://github.com/assafelovic/gpt-researcher


Functions:
    ddg_search(query, max_results=7): Searches using DuckDuckGo.
    tavily_search(query, max_results=7): Searches using Tavily search engine.
    serper_search(query, max_results=7): Searches using Serper API.               [NOT IMPLEMENTED]
    serp_api_search(query, max_results=7): Searches using SerpAPI.                [NOT IMPLEMENTED]
    google_search(query, max_results=7): Searches using Google Custom Search API. [NOT IMPLEMENTED]
    bing_search(query, max_results=7): Searches using Bing Search API.            [NOT IMPLEMENTED]
"""
import os
import json
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional
import requests
from duckduckgo_search import DDGS
from tavily import TavilyClient

router = APIRouter()

class SearchRequest(BaseModel):
    query: str
    max_results: Optional[int] = 7
    api_key: Optional[str] = None

@router.post("/ddg-search")
async def ddg_search(request: SearchRequest):
    """DuckDuckGo is a free private search engine.
    As of May 2024 DuckDuckGo is Free with no search limits
    https://duckduckgo.com/
    
    NOTE: The results have been very good and I have been 
    using this as the default for much of the work
    """
    ddg = DDGS()
    
    search_response = []
    try:
        search_response = ddg.text(
                request.query,
                region = "wt-wt",   # Worldwide Search [us, uk, etc.]
                safesearch = "off", # No safe search filtering [off, moderate, strict]
                timelimit = "y",    # Results from past year [d,w,m,y,a]
                max_results = request.max_results,
            )
    except Exception as e:  # Fallback in case overload on Tavily Search API
        print(f"ddgs_search Error: {e}")

    return search_response

@router.post("/tavily-search")
async def tavily_search(request: SearchRequest):
    """Tavily is a search engine built specifically for AI agents (LLMs).
    As of May 2024 Tavily has Free tier allows 1,000 Free searches per month
    https://tavily.com/
    """
    try:
        client = TavilyClient(request.api_key)
       
        # Search the query
        results = client.search(request.query, search_depth="advanced", max_results=request.max_results)
       
        # Return the results
        search_response = [
            {"href": obj["url"], "body": obj["content"]}
            for obj in results.get("results", [])
        ]
    except Exception as e:  # Fallback in case overload on Tavily Search API
        print(f"tavily_search Error: {e}")
        search_response = await ddg_search(SearchRequest(query=request.query, max_results=request.max_results))

    search_response = [
        obj for obj in search_response if "youtube.com" not in obj["href"]
    ]
    return search_response

