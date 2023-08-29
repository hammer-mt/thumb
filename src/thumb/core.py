
import os
import csv
from typing import List, Dict, Union, Optional
from dotenv import load_dotenv

load_dotenv()

import langchain
import gradio

class Thumb:
    
    def __init__(self):
        self.openai_api_key = os.environ.get("OPENAI_API_KEY", None)
        self.langchain_api_key = os.environ.get("LANGCHAIN_API_KEY", None)

    def test(self, 
             prompts: List[str], 
             cases: List[Dict[str, str]], 
             runs: int = 30, 
             models: List[str] = ['gpt-3.5-turbo'], 
             cache: bool = True, 
             references: Optional[List[str]] = None) -> Dict[str, Union[str, List[str]]]:
        
        responses = self._generate_responses(prompts, cases, runs, models)
        
        if cache:
            self._cache_to_csv(responses)
        
        # Check for Langchain API key and trace if available
        if self.langchain_api_key:
            self._trace_to_langchain(responses)
        
        return responses

    def _generate_responses(self, 
                            prompts: List[str], 
                            cases: List[Dict[str, str]], 
                            runs: int, 
                            models: List[str]) -> Dict[str, Union[str, List[str]]]:
        
        all_responses = {}
        
        for prompt in prompts:
            for case in cases:
                for model in models:
                    for _ in range(runs):
                        formatted_prompt = prompt.format(**case)
                        mock_responses = [f"Mock response for: {formatted_prompt}"] * runs
                        all_responses[formatted_prompt] = mock_responses
        
        return all_responses
    
    def _cache_to_csv(self, responses: Dict[str, Union[str, List[str]]]):
        with open('res_cache.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Prompt", "Response"])
            for prompt, response_list in responses.items():
                for response in response_list:
                    writer.writerow([prompt, response])
    
    def evals(labels: Optional[List[str]] = None):
        labels = labels or ["👎", "👍"]
        pass

thumb = Thumb()
