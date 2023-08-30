
import os
import csv
import json
from collections import defaultdict
from uuid import uuid4
from dotenv import load_dotenv

load_dotenv()

from .llm import get_responses
from .utils import hash_id

def test(prompts, cases=None, runs=10, models=["gpt-3.5-turbo"]):
    thumb = ThumbTest()
    thumb.add_prompts(prompts)
    thumb.add_cases(cases)
    thumb.add_models(models)
    thumb.add_runs(runs)

    return thumb

def load(tid):
    return ThumbTest(tid)

class ThumbTest:
    
    def __init__(self, tid=None, cache=True):
        self.cache = cache
        self.langchain_api_key = os.environ.get("LANGCHAIN_API_KEY", None)

        self.responses = defaultdict(dict)

        self.prompts = {}
        self.cases = {"base": None}
        self.models = []
        self.runs = 0

        if tid:
            self.tid = tid
            self._load_data()
            print(f"ThumbTest loaded with tid: {self.tid}")
        else:
            self.tid = uuid4().hex[0:8]
            print(f"ThumbTest initialized with tid: {self.tid}")

        

    def add_prompts(self, prompts):
        updated_prompts = []
        for prompt in prompts:
            pid = f"pid-{hash_id(prompt)}"
            if pid not in self.prompts.keys():
                self.prompts[pid] = prompt
                updated_prompts.append(pid)
        
        if len(updated_prompts) > 0:
            self._generate()

    def add_cases(self, cases):
        updated_cases = []
        for case in cases:
            cid = f"cid-{hash_id(json.dumps(case))}"
            if cid not in self.cases.keys():
                # if base still in cases, remove it
                if "base" in self.cases.keys():
                    del self.cases["base"]
                self.cases[cid] = case
                updated_cases.append(cid)
        
        if len(updated_cases) > 0:
            self._generate()

    def add_models(self, models):
        updated_models = []
        for model in models:
            if model not in self.models:
                self.models.append(model)
                updated_models.append(model)
        
        if len(updated_models) > 0:
            self._generate()

    def add_runs(self, runs):
        # check if runs is an int
        if not isinstance(runs, int):
            raise TypeError("runs must be an integer")
        # check if runs is greater than 0
        if runs < 1:
            raise ValueError("runs must be greater than 0")

        self.runs += runs
        self._generate()

    def _generate(self):
        for pid in self.prompts.keys():
            for cid in self.cases.keys():
                for model in self.models:
                    runs_completed = self.responses.get(pid, {}).get(cid, {}).get(model, 0)
                    if runs_completed < self.runs:
                        # Process this combination
                        runs = self.runs - runs_completed
                        prompt = self.prompts[pid]
                        
                        case = self.cases[cid]
                        # tracing enabled if langchain api key is set
                        tracing = self.langchain_api_key is not None
                        
                        responses = get_responses(prompt, case, model, runs, self.tid, pid, cid, tracing)

                        # Ensure pid is in the dictionary
                        if pid not in self.responses:
                            self.responses[pid] = {}

                        # Ensure cid is in the dictionary associated with pid
                        if cid not in self.responses[pid]:
                            self.responses[pid][cid] = {}

                        # If the model is not in the dict, add it
                        if model not in self.responses[pid][cid]:
                            self.responses[pid][cid][model] = responses
                        else:
                            self.responses[pid][cid][model] += responses

                        if self.cache:
                            self._save_data()

    def _save_data(self):
        """
        Save responses, prompts, cases, and models to a json file.
        """
        # Create a dictionary to hold the relevant data
        data = {
            'responses': self.responses,
            'prompts': self.prompts,
            'cases': self.cases,
            'models': self.models
        }
        
        # Convert the dictionary to JSON
        data_json = json.dumps(data, indent=4)
        
        # Define the directory and file path
        dir_path = "thumb/data"
        file_path = os.path.join(dir_path, f"{self.tid}.json")
        
        try:
            # Check if directory exists, if not create it
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
            
            # Write the JSON to the file
            with open(file_path, 'w') as file:
                file.write(data_json)
                print(f"Data saved to {file_path}")
        except Exception as e:
            print(f"Caching failed due to: {e}")


    def _load_data(self):
        """
        Load responses, prompts, cases, and models from a json file.
        """
        # Define the path for the JSON file using the tid value
        file_path = os.path.join("thumb/data", f"{self.tid}.json")
        
        # Check if the file exists
        if not os.path.exists(file_path):
            print(f"No data found for tid: {self.tid}")
            return
        
        # Read the JSON from the file
        with open(file_path, 'r') as file:
            data = json.load(file)
        
        # Update the instance variables with the loaded data
        self.responses = data.get('responses', {})
        self.prompts = data.get('prompts', {})
        self.cases = data.get('cases', {})
        self.models = data.get('models', [])

        print(data)
    
    def evals(labels=None):
        labels = labels or ["👎", "👍"]
        return labels


