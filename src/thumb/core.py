
import os
import random
import csv
import json
from collections import defaultdict
from uuid import uuid4
import ipywidgets as widgets
from IPython.display import display
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
    thumb.generate()
    thumb.evaluate()

    return thumb

def load(tid):
    return ThumbTest(tid)

class ThumbTest:
    
    def __init__(self, tid=None):

        self.data = defaultdict(dict)

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
        for prompt in prompts:
            pid = f"pid-{hash_id(prompt)}"
            if pid not in self.prompts.keys():
                self.prompts[pid] = prompt

    def add_cases(self, cases):
        for case in cases:
            cid = f"cid-{hash_id(json.dumps(case))}"
            if cid not in self.cases.keys():
                # if base still in cases, remove it
                if "base" in self.cases.keys():
                    del self.cases["base"]
                self.cases[cid] = case

    def add_models(self, models):
        for model in models:
            if model not in self.models:
                self.models.append(model)

    def add_runs(self, runs):
        # check if runs is an int
        if not isinstance(runs, int):
            raise TypeError("runs must be an integer")
        # check if runs is greater than 0
        if runs < 1:
            raise ValueError("runs must be greater than 0")

        self.runs += runs

    def generate(self):
        for pid in self.prompts.keys():
            for cid in self.cases.keys():
                for model in self.models: 
                    runs_completed = len(self.data.get(pid, {}).get(cid, {}).get(model, {}).keys())
                    if runs_completed < self.runs:
                        # Process this combination
                        runs = self.runs - runs_completed
                        prompt = self.prompts[pid]
                        
                        test_case = self.cases[cid]
                        
                        responses = get_responses(prompt, test_case, model, runs, self.tid, pid, cid)

                        # Ensure pid is in the dictionary
                        if pid not in self.data:
                            self.data[pid] = {}

                        # Ensure cid is in the dictionary associated with pid
                        if cid not in self.data[pid]:
                            self.data[pid][cid] = {}

                        # If the model is not in the dict, add it
                        if model not in self.data[pid][cid]:
                            self.data[pid][cid][model] = {}
                        
                        # Add the responses to the dictionary
                        for idx, response_content in enumerate(responses):
                            response_dict = {
                                'content': response_content,
                                'feedback': None  # No feedback yet
                            }
                            loc = len(self.data[pid][cid][model].keys()) + idx
                            self.data[pid][cid][model][loc] = response_dict

                        self._save_data()

    def _save_data(self):
        """
        Save responses, prompts, cases, and models to a json file.
        """
        # Create a dictionary to hold the relevant data
        data = {
            'data': self.data,
            'prompts': self.prompts,
            'cases': self.cases,
            'models': self.models,
            'runs': self.runs,
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
        self.data = data.get('data', {})
        self.prompts = data.get('prompts', {})
        self.cases = data.get('cases', {})
        self.models = data.get('models', [])
        self.runs = data.get('runs', 0)

    def _prep_for_eval(self):
        """
        Prepare the responses for evaluation.
        """
        # Create a list to hold the responses
        responses = []
        
        # Loop through the prompts
        for pid in self.data.keys():
            # Loop through the cases
            for cid in self.data[pid].keys():
                # Loop through the models
                for model in self.data[pid][cid].keys():
                    # Loop through the responses
                    for idx, response in self.data[pid][cid][model].items():
                        # if the response has feedback, skip it
                        if response['feedback'] is not None:
                            continue
                        # Create a dictionary to hold the response data
                        response_data = {
                            'pid': pid,
                            'cid': cid,
                            'model': model,
                            'idx': idx,
                            'response': response.content,
                        }
                        
                        # Add the response data to the list of responses
                        responses.append(response_data)
        
        # shuffle the order of the responses
        random.shuffle(responses)

        return responses
    
    def _receive_feedback(self, label, pid, cid, model, idx):
        # convert thumbs up / down to 1 / 0
        value = 1 if label.description == "👍" else 0

        # Update the response based on the provided index
        self.data[pid][cid][model][idx]['feedback'] = value

    def evaluate(self):
        prepped_data = self._prep_for_eval()
        data_len = len(prepped_data)
        labels = ["👎", "👍"]
        label_widgets = [widgets.Button(description=label) for label in labels]

        response_box = widgets.Output()
        progress_bar = widgets.IntProgress(min=0, max=data_len, description="Progress:")

        def on_button_clicked(b):
            with response_box:
                response_box.clear_output()
                pid, cid, model, idx, response_content = update_response()
                self._receive_feedback(b, pid, cid, model, idx)
                progress_bar.value = len(prepped_data)

                # show response content in the output widget
                response_box.value = response_content

        def update_response():
            # get the next response
            response = prepped_data.pop(0)
            pid = response['pid']
            cid = response['cid']
            model = response['model']
            idx = response['idx']
            response_content = response['response']

            return pid, cid, model, idx, response_content

        # add on_click to buttons
        for label_widget in label_widgets:
            label_widget.on_click(on_button_clicked)
        
        label_widget = widgets.HBox(label_widgets)
        output_widget = widgets.Output()
        display(progress_bar, label_widget, output_widget)


