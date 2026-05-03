import os
import json
import logging
import re
from datetime import datetime
from google import genai
from google.genai import types
from duckduckgo_search import DDGS
from config import Config
from scraper.scraper import get_scraper

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class dynamic_verifier:
    def __init__(self):
        self.api_key = Config.GEMINI_API_KEY
        self.primary_model = Config.PRIMARY_MODEL
        self.fallback_model = Config.FALLBACK_MODEL
        self.scraper = get_scraper()
        
        if self.api_key:
            self.client = genai.Client(api_key=self.api_key)
        else:
            self.client = None
            logger.warning("Gemini API Key not found. Dynamic verification will be limited.")

    def _call_gemini(self, prompt, json_mode=False):
        if not self.client:
            return None
        
        models_to_try = [self.primary_model, self.fallback_model]
        import time

        for m_idx, model in enumerate(models_to_try):
            for attempt in range(Config.MAX_RETRIES):
                try:
                    config = None
                    if json_mode:
                        config = types.GenerateContentConfig(response_mime_type="application/json")
                    
                    logger.info(f"Calling {model} (Attempt {attempt + 1})...")
                    response = self.client.models.generate_content(
                        model=model,
                        contents=prompt,
                        config=config
                    )
                    return response.text.strip()
                except Exception as e:
                    error_msg = str(e).upper()
                    # Check for transient errors: 503 (Unavailable), 429 (Quota), etc.
                    is_transient = any(code in error_msg for code in ["503", "UNAVAILABLE", "429", "RESOURCE_EXHAUSTED", "SERVICE_UNAVAILABLE"])
                    
                    if is_transient and attempt < Config.MAX_RETRIES - 1:
                        wait_time = (2 ** attempt) + 1
                        logger.warning(f"Transient error with {model}. Retrying in {wait_time}s...")
                        time.sleep(wait_time)
                        continue
                    
                    # If we reach here, it's either not transient or we've exhausted retries for THIS model
                    logger.error(f"Error with {model}: {error_msg}")
                    break # Exit the attempt loop to try next model (if any)

        return "ERROR: The AI model is currently overloaded. Please try again in a moment."

    def extract_claims(self, text):
        """
        Extracts core verifiable claims from the input text.
        """
        prompt = f"""
        Analyze the following text and extract the 2-3 most important verifiable claims.
        For each claim, create a concise, searchable query for a fact-checking search.
        
        TEXT: {text[:2000]}
        
        Output in JSON format:
        {{
            "claims": [
                {{"original": "claim text", "query": "search query"}},
                ...
            ]
        }}
        """
        res = self._call_gemini(prompt, json_mode=True)
        if res:
            try:
                return json.loads(res).get('claims', [])
            except:
                pass
        
        # Fallback simple query
        return [{"original": text[:100], "query": text[:100]}]

    def search_and_verify(self, text_or_url):
        """
        Main entry point for verification.
        """
        input_text = text_or_url
        source_url = None
        
        # If input is a URL, scrape it first
        if text_or_url.startswith(('http://', 'https://')):
            source_url = text_or_url
            scrape_res = self.scraper.scrape_article(text_or_url)
            if scrape_res.get('error'):
                return {"error": f"Scraping error: {scrape_res['error']}"}
            input_text = scrape_res['text']

        # 1. Extract Claims
        claims = self.extract_claims(input_text)
        
        # 2. Search Web for each claim
        all_sources = []
        search_results = []
        
        with DDGS() as ddgs:
            for claim in claims[:2]:
                query = claim['query']
                try:
                    logger.info(f"Searching for: {query}")
                    # Try with 'y' timelimit for very recent results
                    results = ddgs.text(query, max_results=3, timelimit='y')
                    
                    # Fallback if 'y' (year) returned nothing, try without timelimit
                    if not results:
                        results = ddgs.text(query, max_results=3)

                    if results:
                        for r in results:
                            search_results.append({
                                'title': r.get('title', 'No Title'),
                                'link': r.get('href', r.get('link', '')),
                                'snippet': r.get('body', r.get('snippet', ''))
                            })
                except Exception as e:
                    logger.error(f"Search error for '{query}': {e}")

        # 3. Scrape top sources for deeper verification (optional, but requested for 'live verification')
        # To keep it lightweight and fast, we'll mostly rely on snippets but scrape the top 1 link if available
        if search_results:
            top_links = [r['link'] for r in search_results[:2]]
            scraped_data = self.scraper.scrape_multiple(top_links)
            for i, data in enumerate(scraped_data):
                if not data.get('error'):
                    search_results[i]['full_text'] = data['text'][:2000] # Limit context

        # 4. Final Verification via Gemini
        context_str = ""
        for i, r in enumerate(search_results):
            context_str += f"SOURCE {i+1}: {r['title']}\nURL: {r['link']}\nCONTENT: {r.get('full_text', r['snippet'])}\n\n"
        


        prompt = f"""
        You are an expert Fact-Checker. Compare the INPUT TEXT against the provided SEARCH SOURCES.
        
        INPUT TEXT:
        {input_text[:3000]}
        
        CURRENT DATE: {datetime.now().strftime('%B %d, %Y (%A)')}
        
        SEARCH SOURCES:
        {context_str if context_str else "NO LIVE SOURCES FOUND (The search engine returned no results for this claim yet)."}
        
        Task:
        1. Determine if the input text is REAL, FAKE, or MISLEADING.
        2. Provide a confidence score (0-100).
        3. Explain why (citing source inconsistencies).
        4. CRITICAL: If SEARCH SOURCES are empty, do NOT default to FAKE. Most likely, the event is too recent for search engines to index. 
           In this case, mark as "MISLEADING" or "REAL" if plausible, with a lower confidence, and explain that "Live data is still propagating".
        5. Identify 5-8 "suspicious" or "key" words for highlighting.
        
        Output strictly in JSON:
        {{
            "prediction": "REAL | FAKE | MISLEADING",
            "confidence": <int>,
            "explanation": "...",
            "sources": [...],
            "highlighted_keywords": [...]
        }}
        """
        
        res = self._call_gemini(prompt, json_mode=True)
        if not res:
            return {"error": "AI Verification failed to respond."}
            
        if isinstance(res, str) and res.startswith("ERROR:"):
            return {"error": res.replace("ERROR: ", "")}

        try:
            final_result = json.loads(res)
            # Add some original metadata
            final_result['original_text'] = input_text
            final_result['source_url'] = source_url
            
            # Cap confidence as per industry standards (e.g. 95%) or user request
            if final_result['confidence'] > 95:
                final_result['confidence'] = 95
                
            return final_result
        except Exception as e:
            return {"error": f"Failed to parse AI response: {str(e)}"}

# Singleton
verifier_instance = dynamic_verifier()

def get_verifier():
    return verifier_instance
