
import os
import random
import csv
import json
from collections import defaultdict
from uuid import uuid4
import ipywidgets as widgets
from IPython.display import display, clear_output
import asyncio
import nest_asyncio

import pandas as pd
import datetime

from .llm import get_responses, async_get_responses, call, acall
from .utils import hash_id
from .ape import build_candidate_prompt, build_case_prompt, build_rating_prompt

DIR_PATH = "thumb-tests/.cache"

# solves a problem with event loop in asyncio in jupyter notebooks
nest_asyncio.apply()

def test(prompts, cases=None, runs=10, models=["gpt-3.5-turbo"], task_description=None, async_generate=True, show_cases=False, verbose=False):
    if not task_description:
        task_description = prompts[0]
    thumb = ThumbTest(task_description, show_cases=show_cases, verbose=verbose)
    thumb.add_prompts(prompts)


    thumb.add_cases(cases)
    thumb.add_models(models)
    thumb.add_runs(runs)
    if async_generate:
        asyncio.run(thumb.async_generate())
    else:
        thumb.generate()

    thumb.evaluate()

    return thumb

def load(tid):
    # check if the tid is a file path
    if os.path.exists(tid):
        return ThumbTest(file_path=tid)
    else:
        return ThumbTest(tid)

class ThumbTest:
    
    def __init__(self, tid=None, file_path=None, task_description=None, show_cases=False, verbose=False):

        self.verbose = verbose

        self.data = defaultdict(dict)

        self.prompts = {}
        self.cases = {"base-case": None}
        self.models = []
        self.runs = 0

        self.criteria = []
        self.task_description = task_description

        if tid:
            # get just the tid from the file path if its a filepath
            if "/" in tid:
                tid = tid.split("/")[-1].split(".")[0]
            elif "." in tid:
                tid = tid.split(".")[0]   
            
            self.tid = tid
            self._load_data()
            if self.verbose: print(f"Loaded ThumbTest: {self.tid}")
        elif file_path:
            self.tid = file_path.split("/")[-1].split(".")[0]
            self._load_data(file_path)
            if self.verbose: print(f"Loaded ThumbTest: {self.tid}")
        else:
            self.tid = uuid4().hex[0:8]
            if self.verbose: print(f"Created ThumbTest: {self.tid}")

        if os.environ.get("LANGCHAIN_API_KEY", None):
            os.environ["LANGCHAIN_TRACING_V2"] = "true"
            os.environ["LANGCHAIN_PROJECT"] = f"ThumbTest: {self.tid}"
            os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"

        self.show_cases = show_cases

    def __str__(self):
        combinations = len(self.prompts) * len(self.cases) * len(self.models) * self.runs
        if "base-case" in self.cases.keys():
            return f"ThumbTest: {self.tid}\n\nPrompts: {len(self.prompts)}\nCases: {len(self.cases) - 1}\nModels: {len(self.models)}\nRuns: {self.runs}\n\n{len(self.prompts)} x {len(self.cases) - 1} x {len(self.models)} x {self.runs} = {combinations}"
        return f"ThumbTest: {self.tid}\n\nPrompts: {len(self.prompts)}\nCases: {len(self.cases)}\nModels: {len(self.models)}\nRuns: {self.runs}\n\n{len(self.prompts)} x {len(self.cases)} x {len(self.models)} x {self.runs} = {combinations}"
    
    def add_prompts(self, prompts):
        for prompt in prompts:
            # if the prompt is a string, convert it to a list
            if isinstance(prompt, str):
                prompt = [prompt]
            
            msg_string = "\n".join(prompt)
            pid = f"{hash_id(msg_string)}"
            if pid not in self.prompts.keys():
                self.prompts[pid] = prompt
                if self.verbose: print(f"Added prompt: {pid}: {prompt}")

    def add_cases(self, cases):
        if cases is not None:
            for case in cases:
                cid = f"{hash_id(json.dumps(case))}"
                if cid not in self.cases.keys():
                    # if base still in cases, remove it
                    if "base-case" in self.cases.keys():
                        del self.cases["base-case"]
                    self.cases[cid] = case
                    if self.verbose: print(f"Added case: {cid}: {case}")

    def add_models(self, models):
        for model in models:
            if model not in self.models:
                self.models.append(model)
                if self.verbose: print(f"Added model: {model}")

    def add_runs(self, runs):
        # check if runs is an int
        if not isinstance(runs, int):
            raise TypeError("runs must be an integer")
        # check if runs is greater than 0
        if runs < 1:
            raise ValueError("runs must be greater than 0")

        self.runs += runs
        if self.verbose: print(f"Added {runs} runs. Total runs: {self.runs}")

    def add_criteria(self, criteria):
        if isinstance(criteria, str):
            criteria = [criteria]
        self.criteria += criteria
        self.criteria = list(set(self.criteria))
        if self.verbose: print(f"Added criteria: {criteria}")

    def remove_criteria(self, criteria):
        if isinstance(criteria, str):
            criteria = [criteria]
        for criterion in criteria:
            if criterion in self.criteria:
                self.criteria.remove(criterion)
        if self.verbose: print(f"Removed criteria: {criteria}")

    def set_task_description(self, task_description):
        self.task_description = task_description
        if self.verbose: print(f"Set task description: {task_description}")

    def generate(self):
        combinations = len(self.prompts) * len(self.cases) * len(self.models) * self.runs
        if self.verbose: print(f"{len(self.prompts)} prompts x {len(self.cases)} cases x {len(self.models)} x runs {self.runs} = {combinations} calls to the OpenAI API")

        for pid in self.prompts.keys():
            for cid in self.cases.keys():
                for model in self.models: 
                    runs_completed = len(self.data.get(pid, {}).get(cid, {}).get(model, {}).keys())
                    if runs_completed < self.runs:
                        # Process this combination
                        runs = self.runs - runs_completed
                        prompt = self.prompts[pid]
                        
                        test_case = self.cases[cid]
                        
                        responses = get_responses(prompt, test_case, model, runs, pid, cid)

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
                        for response in responses:
                            response["feedback"] = None
                            rid = uuid4().hex[0:8]
                            self.data[pid][cid][model][rid] = response

                        self._save_data()

    def _collect_required_runs(self):
        """
        Collects and returns all the required runs for the prompts, cases, and models.
        """
        required_runs = []

        for pid in self.prompts.keys():
            for cid in self.cases.keys():
                for model in self.models:
                    runs_completed = len(self.data.get(pid, {}).get(cid, {}).get(model, {}).keys())
                    if runs_completed < self.runs:
                        runs_to_do = self.runs - runs_completed

                        # Add a new item for each individual run that hasn't been completed yet
                        for _ in range(runs_to_do):
                            required_runs.append({
                                'pid': pid,
                                'cid': cid,
                                'model': model,
                                'prompt': self.prompts[pid],
                                'test_case': self.cases[cid]
                            })
        return required_runs

    async def async_generate(self, batch_size=30):
        combinations = len(self.prompts) * len(self.cases) * len(self.models) * self.runs
        if self.verbose: print(f"{len(self.prompts)} prompts x {len(self.cases)} cases x {len(self.models)} x runs {self.runs} = {combinations} calls to the OpenAI API")

        # Create a list to collect needed runs
        required_runs = self._collect_required_runs()
        
        # Process the required runs in batches determined by batch_size
        for i in range(0, len(required_runs), batch_size):
            batch = required_runs[i:i+batch_size]
            
            batch_responses = await async_get_responses(batch, verbose=self.verbose)

            for idx, response in enumerate(batch_responses):
                pid, cid, model = batch[idx]['pid'], batch[idx]['cid'], batch[idx]['model']

                # Ensure pid is in the dictionary
                if pid not in self.data:
                    self.data[pid] = {}

                # Ensure cid is in the dictionary associated with pid
                if cid not in self.data[pid]:
                    self.data[pid][cid] = {}

                # If the model is not in the dict, add it
                if model not in self.data[pid][cid]:
                    self.data[pid][cid][model] = {}

                # Add the response to the dictionary
                response["feedback"] = None
                rid = uuid4().hex[0:8]
                self.data[pid][cid][model][rid] = response

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
        file_path = os.path.join(DIR_PATH, f"{self.tid}.json")
        
        try:
            # Check if directory exists, if not create it
            if not os.path.exists(DIR_PATH):
                os.makedirs(DIR_PATH)
            
            # Write the JSON to the file
            with open(file_path, 'w') as file:
                file.write(data_json)
        except Exception as e:
            print(f"Caching failed due to: {e}")


    def _load_data(self, file_path=None):
        """
        Load responses, prompts, cases, and models from a json file.
        """
        if file_path:
            # check the file exists
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"No file found at {file_path}")
            else:
                 # Define the path for the file using the tid value
                json_file_path = os.path.join(DIR_PATH, f"{self.tid}.json")
                csv_file_path = f"{self.tid}.csv"

                # check whether the file is a json file
                if file_path.split(".")[-1] == "json":
                    self._read_from_json(json_file_path)

                # check whether the file is a csv file
                elif file_path.split(".")[-1] == "csv":
                    self._read_from_csv(csv_file_path)
                else:
                    raise TypeError(f"File must be a JSON or CSV file.")
        else:
            csv_file_path = f"{self.tid}.csv"
            # Check if the JSON file exists
            if file_path is not None and os.path.exists(file_path):
                self._read_from_json(file_path)
            
            # Check if the CSV file exists
            
            elif csv_file_path is not None and os.path.exists(csv_file_path):
                self._read_from_csv(csv_file_path)

            else:
                raise FileNotFoundError(f"No data found for tid: {self.tid}")
        
    def _read_from_csv(self, csv_file_path):
        # Load the CSV file into a DataFrame
        csv_df = pd.read_csv(csv_file_path)
        
        def compute_runs(data_dict):
            runs = []
            for pid_content in data_dict.values():
                for cid_content in pid_content.values():
                    for model_content in cid_content.values():
                        runs.append(len(model_content))
            return max(runs) if runs else 0

        # Extract unique values for prompts, cases, models
        prompts = csv_df.drop_duplicates(subset=['PID'])[['PID', 'Prompt']].set_index('PID').to_dict()['Prompt']
        cases = csv_df.drop_duplicates(subset=['CID'])[['CID', 'Case']].set_index('CID').to_dict()['Case']
        models = csv_df['Model'].unique().tolist()
        
        # Adjust prompts based on their type (list or string)
        for pid, prompt_str in prompts.items():
            try:
                prompts[pid] = eval(prompt_str)
                # Convert single strings wrapped in a list to just strings
                if isinstance(prompts[pid], list) and len(prompts[pid]) == 1:
                    prompts[pid] = prompts[pid][0]
            except:
                pass
        
        # Convert cases' string to dictionary format
        for cid, case_str in cases.items():
            cases[cid] = json.loads(case_str)
        
        # Construct the data dictionary
        data = {}
        for _, row in csv_df.iterrows():
            pid = row['PID']
            cid = row['CID']
            model = row['Model']
            rid = row['RID']
            
            # Initialize nested dictionaries if not present
            if pid not in data:
                data[pid] = {}
            if cid not in data[pid]:
                data[pid][cid] = {}
            if model not in data[pid][cid]:
                data[pid][cid][model] = {}
            
            # Handle NaN feedback values
            feedback_value = int(row['Feedback']) if not pd.isna(row['Feedback']) else None
            
            # Add the details under the RID
            data[pid][cid][model][rid] = {
                'content': row['Content'],
                'tokens': row['Tokens'],
                'cost': row['Cost'],
                'prompt_tokens': row['Prompt Tokens'],
                'completion_tokens': row['Completion Tokens'],
                'latency': row['Latency'],
                'feedback': feedback_value
            }
        
        # Compute the runs value
        runs_value = compute_runs(data)
        
        # Combine all parts to form the final structure
        self.data = data
        self.prompts = prompts
        self.cases = cases
        self.models = models
        self.runs = runs_value

    def _read_from_json(self, json_file_path):
        with open(json_file_path, 'r') as file:
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
                    for rid, response in self.data[pid][cid][model].items():
                        # if the response has feedback, skip it
                        if response['feedback'] is not None:
                            continue
                        # Create a dictionary to hold the response data
                        response_data = {
                            'pid': pid,
                            'cid': cid,
                            'model': model,
                            'rid': rid,
                            'content': response["content"],
                        }
                        
                        # Add the response data to the list of responses
                        responses.append(response_data)
        
        # shuffle the order of the responses
        random.shuffle(responses)

        return responses
    
    def _receive_feedback(self, label, pid, cid, model, rid):
        # convert thumbs up / down to 1 / 0
        value = 1 if label.description == "👍" else 0

        # Update the response based on the provided index
        self.data[pid][cid][model][rid]['feedback'] = value

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
                'cost': [],
            }
            # Loop through the cases
            for cid in self.data[pid].keys():
                # Loop through the models
                for model in self.data[pid][cid].keys():
                    # Loop through the responses
                    for response in self.data[pid][cid][model].values():

                        # Add the feedback to the list of scores
                        scores[pid]['feedback'].append(response['feedback'])

                        # Add the tokens to the total
                        scores[pid]['tokens'].append(response['tokens']) 

                        # Add the cost to the total                            
                        scores[pid]['cost'].append(response['cost']) 
        
        # Calculate the average score
        for pid in scores.keys():
            scores[pid]['avg_score'] = sum(scores[pid]['feedback']) / len(scores[pid]['feedback'])
            scores[pid]['avg_tokens'] = sum(scores[pid]['tokens']) / len(scores[pid]['tokens'])
            scores[pid]['avg_cost'] = sum(scores[pid]['cost']) / len(scores[pid]['cost'])
        
        return scores

    def evaluate(self):
        prepped_data = self._prep_for_eval()
        data_len = len(prepped_data)
        labels = ["👎", "👍"]
        label_widgets = [widgets.Button(description=label) for label in labels]

        main_box = widgets.VBox()

        test_id = widgets.Label(value=f"ThumbTest: {self.tid}")
        response_box = widgets.HTML()
        case_box = widgets.HTML()
        progress_bar = widgets.IntProgress(min=0, max=data_len, description="Progress:")

        def update_response():
            nonlocal prepped_data
            if not prepped_data:
                self.export_to_csv()
                stats = ""
                
                # TODO abstract this out into a function
                flattened_data = []
                for pid, pid_data in self.data.items():
                    prompt = self.prompts.get(pid, None)

                    for cid, cid_data in pid_data.items():
                        case = self.cases.get(cid, None)
                        case = json.dumps(case)

                        for model, model_data in cid_data.items():
                            for rid, details in model_data.items():
                                content = details.get('content', None)
                                tokens = details.get('tokens', None)
                                cost = details.get('cost', None)
                                feedback = details.get('feedback', None)
                                latency = details.get('latency', None)
                                prompt_tokens = details.get('prompt_tokens', None)
                                completion_tokens = details.get('completion_tokens', None)

                                flattened_data.append([pid, prompt, cid, case, model, rid, content, tokens, prompt_tokens, completion_tokens, cost, latency, feedback])

                df = pd.DataFrame(data=flattened_data, columns=["PID", "Prompt", "CID", "Case", "Model", "RID", "Content", "Tokens", "Prompt Tokens", "Completion Tokens", "Cost", "Latency", "Feedback"])
                
                stats_df = df.groupby(['PID', 'CID', 'Model']).agg(
                                runs=('PID', 'size'),
                                feedback=('Feedback', 'sum'),
                                score=('Feedback', 'mean'),
                                tokens=('Tokens', 'mean'),
                                cost=('Cost', 'mean'),
                                latency=('Latency', 'mean'),
                                ).reset_index()

                full_stats_df = stats_df.pivot_table(index=['PID', 'CID', 'Model'],
                                                      values=['runs', 'tokens', 'cost', 'latency', 'feedback', 'score'], 
                                                      aggfunc={
                                                        'runs': 'sum',
                                                        'tokens': 'mean',
                                                        'cost': 'mean',
                                                        'latency': 'mean',
                                                        'feedback': 'sum',
                                                        'score': 'mean'
                                                    })
                
                pid_stats_df = stats_df.pivot_table(index=['PID'],
                                                      values=['runs', 'tokens', 'cost', 'latency', 'feedback', 'score'], 
                                                      aggfunc={
                                                        'runs': 'sum',
                                                        'tokens': 'mean',
                                                        'cost': 'mean',
                                                        'latency': 'mean',
                                                        'feedback': 'sum',
                                                        'score': 'mean'
                                                    }).reset_index()

                cid_stats_df = stats_df.pivot_table(index=['CID'],
                                                      values=['runs', 'tokens', 'cost', 'latency', 'feedback', 'score'], 
                                                      aggfunc={
                                                        'runs': 'sum',
                                                        'tokens': 'mean',
                                                        'cost': 'mean',
                                                        'latency': 'mean',
                                                        'feedback': 'sum',
                                                        'score': 'mean'
                                                    }).reset_index()
                
                model_stats_df = stats_df.pivot_table(index=['Model'],
                                                      values=['runs', 'tokens', 'cost', 'latency', 'feedback', 'score'], 
                                                      aggfunc={
                                                        'runs': 'sum',
                                                        'tokens': 'mean',
                                                        'cost': 'mean',
                                                        'latency': 'mean',
                                                        'feedback': 'sum',
                                                        'score': 'mean'
                                                    }).reset_index()

                # always show pid table
                pid_table_output = pid_stats_df.to_html()
                stats += f"<br>{pid_table_output}"

                # - don't show the CID breakdown if base case
                if len(self.cases) == 1:
                    # Reset the multi-index to columns
                    full_stats_df_reset = full_stats_df.reset_index()

                    # Set the index again without 'CID'
                    full_stats_df = full_stats_df_reset.set_index(['PID', 'Model'])

                else:
                    cid_table_output = cid_stats_df.to_html()
                    stats += f"<br>{cid_table_output}"

                # - don't show the model breakdown if only one model
                if len(self.models) == 1:
                    # Reset the multi-index to columns
                    full_stats_df_reset = full_stats_df.reset_index()

                    # Set the index again without 'CID'
                    full_stats_df = full_stats_df_reset.set_index(['PID', 'CID'])

                else:
                    model_table_output = model_stats_df.to_html()
                    stats += f"<br>{model_table_output}"
                
                # only show full stats if there's more than one model or more than one case
                if len(self.models) > 1 or len(self.cases) > 1:
                    full_table_output = full_stats_df.to_html()
                    stats += f"<br>{full_table_output}"
                
                # add the prompt and case key to the end of the stats
                stats += f"<br><br><b>Prompts</b>:<br>"
                for pid, prompt in self.prompts.items():
                    stats += f"{pid}: {prompt}<br>"

                # if there are cases, add them to the stats
                if len(self.cases) > 1:
                    stats += f"<br><b>Cases</b>:<br>"
                    for cid, case in self.cases.items():
                        stats += f"{cid}: {case}<br>"

                response_box.value = f"Evaluation complete! 🎉<br><b>Results</b>: <br>{stats}<br>"
                # Update children of main_box to exclude the label_widget
                main_box.children = [response_box, test_id]
                # cache the feedback
                self._save_data()
                return
            
            next_response = prepped_data[0]["content"]
            case = self.cases.get(prepped_data[0]['cid'], None)
            progress_value = data_len - len(prepped_data)

            response_box.value = next_response
            # show each value in the case if show_cases is True in html
            if self.show_cases:
                case_html = "<br>".join([f"<b>{key}</b>: {value}" for key, value in case.items()])
                case_box.value = case_html
            progress_bar.value = progress_value

        def on_button_clicked(b):
            nonlocal prepped_data
            if not prepped_data:
                return

            response = prepped_data.pop(0)
            pid = response['pid']
            cid = response['cid']
            model = response['model']
            rid = response['rid']

            self._receive_feedback(b, pid, cid, model, rid)
            update_response()

        # add on_click to buttons
        for label_widget in label_widgets:
            label_widget.on_click(on_button_clicked)

        label_box = widgets.HBox(label_widgets)
        html_br = widgets.HTML("<br>")
        
        if self.show_cases:
            main_box.children = [progress_bar, html_br, label_box, case_box, response_box, test_id]
        else:
            main_box.children = [progress_bar, html_br, label_box, response_box, test_id]

        clear_output(wait=True)

        update_response()
        display(main_box)
        
    def export_to_csv(self, filename=None):

        # set the filename
        if not filename:
            # set today's date for folder name
            today = datetime.date.today().strftime("%Y-%m-%d")
            # create the folder if it doesn't exist
            if not os.path.exists(f"thumb-tests/{today}/"):
                os.makedirs(f"thumb-tests/{today}/")
            filename = f"thumb-tests/{today}/ThumbTest-{self.tid}.csv"
        
        # Flattening the data for CSV export
        flattened_data = []

        for pid, pid_data in self.data.items():
            prompt = self.prompts.get(pid, None)

            for cid, cid_data in pid_data.items():
                case = self.cases.get(cid, None)
                case = json.dumps(case)

                for model, model_data in cid_data.items():
                    for rid, details in model_data.items():
                        content = details.get('content', None)
                        tokens = details.get('tokens', None)
                        cost = details.get('cost', None)
                        feedback = details.get('feedback', None)
                        latency = details.get('latency', None)
                        prompt_tokens = details.get('prompt_tokens', None)
                        completion_tokens = details.get('completion_tokens', None)

                        flattened_data.append([pid, prompt, cid, case, model, rid, content, tokens, prompt_tokens, completion_tokens, cost, latency, feedback])

        # Write to CSV
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            # Writing header
            writer.writerow(["PID", "Prompt", "CID", "Case", "Model", "RID", "Content", "Tokens", "Prompt Tokens", "Completion Tokens", "Cost", "Latency", "Feedback"])
            # Writing data
            writer.writerows(flattened_data)
        
        return filename

    def generate_prompt(self):
        # there's no task description and no prompts, throw error
        if not self.task_description and not len(self.prompts) > 0:
            raise ValueError("Please provide a task description or prompt template.")

        # there is a task description but no prompts, use task description
        elif self.task_description and not len(self.prompts) > 0:
            prompt_candidate = build_candidate_prompt(self.task_description, prompt_template=None, 
                test_cases=self.cases, criteria=self.criteria)

        # there is a prompt, use prompt
        elif len(self.prompts) > 0:
            # choose a prompt template at random
            prompt_template = random.choice(list(self.prompts.values()))
            prompt_candidate = build_candidate_prompt(self.task_description, prompt_template=prompt_template, 
                test_cases=self.cases, criteria=self.criteria)

        new_prompt_template = call(prompt_candidate)
        # add the new prompt to the list of prompts
        self.prompts.append(new_prompt_template)
        if self.verbose: print(f"Added prompt: {new_prompt_template}")

    def generate_case(self):
        # if base case is in the keys, none
        if "base-case" in self.cases.keys():
            test_cases = None
        else:
            test_cases = self.cases

        prompt_template = build_case_prompt(prompt_template, test_cases=test_cases)
        new_case = call(prompt_template)

        # add the new case to the list of cases
        self.cases.append(new_case)
        if self.verbose: print(f"Added case: {new_case}")

    # def generate_ratings(self, is_async=True):
    #     # run through the self.data and give a rating for each response
    #     # Dictionary to hold tasks with their corresponding identifiers
    #     tasks_with_identifiers = {}

    #     for pid in self.data.keys():
    #         for cid in self.data[pid].keys():
    #             for model in self.data[pid][cid].keys():
    #                 for rid, response in self.data[pid][cid][model].items():
    #                     for criterion in self.criteria:
    #                         # if the criterion has not been rated yet, rate it
    #                         # could be none, or key might not be there
    #                         if criterion not in response.keys() or response[criterion] is None:
    #                             prompt_template = build_rating_prompt(self.task_description, response, criteria=criterion)
    #                             if is_async:
    #                                 # Create a coroutine for the async call
    #                                 task = asyncio.create_task(acall(prompt_template))
    #                                 # Map the task to its identifiers
    #                                 tasks_with_identifiers[task] = (pid, cid, model, rid, criterion)
    #                             else:
    #                                 new_rating = call(prompt_template)
    #                                 self.data[pid][cid][model][rid][criterion] = new_rating

    #     # If there are async tasks, gather and await them
    #     if is_async and tasks_with_identifiers:
    #         completed_tasks = await asyncio.gather(*tasks_with_identifiers.keys())

    #         # Update self.data with the results from the completed tasks
    #         for task in completed_tasks:
    #             new_rating = task.result()
    #             pid, cid, model, rid, criterion = tasks_with_identifiers[task]
    #             self.data[pid][cid][model][rid][criterion] = new_rating
                                        


    


