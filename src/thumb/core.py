
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
        else:
            self.tid = uuid4().hex[0:8]

        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_PROJECT"] = f"ThumbTest: {self.tid}"
        os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"

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
                        for idx, response in enumerate(responses):
                            response["feedback"] = None
                            loc = len(self.data[pid][cid][model].keys()) + idx
                            self.data[pid][cid][model][loc] = response

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
                            'content': response["content"],
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

    def stats(self):
        # Create a list to hold the scores by prompt
        scores = {}
        
        # Loop through the prompts
        for pid in self.data.keys():
            # Add the prompt to the dictionary
            prompt = self.prompts[pid]
            scores[pid] = {
                'prompt': prompt,
                'feedback': [],
                'tokens': [],
            }
            # Loop through the cases
            for cid in self.data[pid].keys():
                # Loop through the models
                for model in self.data[pid][cid].keys():
                    # Loop through the responses
                    for idx, response in self.data[pid][cid][model].items():

                        # Add the feedback to the list of scores
                        scores[pid]['feedback'].append(response['feedback'])

                        # Add the tokens to the total
                        scores[pid]['tokens'].append(response['tokens']) 
        
        # Calculate the average score
        for pid in scores.keys():
            scores[pid]['avg_score'] = sum(scores[pid]['feedback']) / len(scores[pid]['feedback'])
            scores[pid]['avg_tokens'] = sum(scores[pid]['tokens']) / len(scores[pid]['tokens'])
        
        return scores

    def evaluate(self):
        prepped_data = self._prep_for_eval()
        data_len = len(prepped_data)
        labels = ["👎", "👍"]
        label_widgets = [widgets.Button(description=label) for label in labels]

        test_id = widgets.Label(value=f"ThumbTest: {self.tid}")
        response_box = widgets.HTML()
        progress_bar = widgets.IntProgress(min=0, max=data_len, description="Progress:")

        def update_response():
            nonlocal prepped_data
            if not prepped_data:
                scores = self.stats()
                stats = "".join([f"<p>'{score['prompt']}' <ul><li>Avg. Score: {score['avg_score']}</li><li>Avg. Tokens: {score['avg_tokens']}</li></ul></p>" for score in scores.values()])
                response_box.value = f"Evaluation complete! 🎉<br><b>Results</b>: <br>{stats}"
                progress_bar.value = data_len
                # cache the feedback
                self._save_data()
                return
            
            next_response = prepped_data[0]["content"]
            progress_value = data_len - len(prepped_data)

            response_box.value = next_response
            progress_bar.value = progress_value

        def on_button_clicked(b):
            nonlocal prepped_data
            if not prepped_data:
                return

            response = prepped_data.pop(0)
            pid = response['pid']
            cid = response['cid']
            model = response['model']
            idx = response['idx']

            self._receive_feedback(b, pid, cid, model, idx)
            update_response()

        # add on_click to buttons
        for label_widget in label_widgets:
            label_widget.on_click(on_button_clicked)

        label_widget = widgets.HBox(label_widgets)
        update_response()
        display(response_box, label_widget, progress_bar, test_id)
        


