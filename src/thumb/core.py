import asyncio
import csv
import datetime
import json
import os
import random
from collections import defaultdict
from itertools import product
from typing import Any, Dict, List, Union
from uuid import uuid4

import ipywidgets as widgets
import pandas as pd
from IPython.display import clear_output, display

from thumb.errors import PromptNotFoundError, VaryingCasesLengthError
from thumb.llm import async_get_responses, get_responses
from thumb.utils import hash_id

DIR_PATH = "thumb/.cache"


def load(tid: str):
    """
    Create an instance of the ThumbTest class using the provided tid.

    Args:
        tid (str): The unique identifier or file path used to create the ThumbTest instance.

    Returns:
        ThumbTest: The created instance of the ThumbTest class.

    Summary:
    The load function is used to create an instance of the ThumbTest class. It takes a tid parameter, which can be either a file path or a unique identifier. If the tid is a file path, it creates a ThumbTest instance using the file data. If the tid is not a file path, it creates a new ThumbTest instance with the provided tid.

    Example Usage:
    thumb = load("test.json")

    In this example, the load function is used to create a ThumbTest instance by providing a file path as the tid parameter. The function checks if the file exists and then creates the instance using the data from the file.

    Code Analysis:
    Inputs:
    - tid (string): The unique identifier or file path used to create the ThumbTest instance.

    Flow:
    1. The function checks if the tid parameter is a file path by using the os.path.exists function.
    2. If the tid is a file path, it creates a ThumbTest instance using the file_path parameter of the ThumbTest constructor.
    3. If the tid is not a file path, it creates a new ThumbTest instance using the tid parameter of the ThumbTest constructor.

    Outputs:
    - ThumbTest instance: The created instance of the ThumbTest class.
    """
    # check if the tid is a file path
    if os.path.exists(tid):
        return ThumbTest(file_path=tid)
    else:
        return ThumbTest(tid)


def test(
    prompts: List[Union[str, List[str]]],
    cases: Union[Dict[str, str], None] = [],
    runs: int = 10,
    models: List[str] = ["gpt-3.5-turbo"],
    async_generate: bool = True,
):
    """
    Conducts evaluation tests on the OpenAI API using the ThumbTest class.

    Args:
        prompts (List[str] or str): The prompts to be used in the evaluation test.
        cases (List[dict]): The test cases to be used in the evaluation test. Defaults to None.
        runs (int): The number of runs for each combination of prompts, cases, and models.
        models (List[str]): The models to be used in the evaluation test.
        async_generate (bool): Whether to generate responses asynchronously or not.

    Returns:
        ThumbTest: The ThumbTest instance that was used to conduct the evaluation test.
    """
    thumb = ThumbTest()
    thumb.add_prompts(prompts)
    thumb.add_cases(cases)
    thumb.add_models(models)
    thumb.add_runs(runs)
    if async_generate:
        asyncio.run(thumb.async_generate())
    else:
        thumb.generate()

    thumb.evaluate()
    thumb.export_to_csv()
    return thumb


class ThumbTest:
    """
    The `ThumbTest` class is a tool for conducting evaluation tests on the OpenAI API. It allows users to define prompts, test cases, models, and the number of runs for each combination. The class provides methods for generating responses from the API, collecting feedback on the responses, and exporting the data to CSV format.

    Example Usage:
        thumb = ThumbTest()
        thumb.add_prompts(["What is the capital of {country}?", "Who is the current president of {country}?"])
        thumb.add_cases([{"country": "France"}, {"country": "United States"}])
        thumb.add_models(["gpt-3.5-turbo"])
        thumb.add_runs(10)
        thumb.generate()
        thumb.evaluate()
        thumb.export_to_csv()

    Methods:
        - __init__(self, tid=None, file_path=None): Initializes a new instance of the `ThumbTest` class.
        - add_prompts(self, prompts: Union[List[str], str]) -> None: Adds prompts to the test.
        - add_cases(self, cases: Union[List[dict], None] = None) -> None: Adds test cases to the test.
        - add_models(self, models: List[str]) -> None: Adds models to the test.
        - add_runs(self, runs: Any) -> None: Sets the number of runs for each combination.
        - generate(self) -> None: Generates responses from the OpenAI API for each combination.
        - async_generate(self, batch_size=30) -> None: Asynchronously generates responses from the OpenAI API for each combination.
        - evaluate(self) -> None: Collects feedback on the generated responses.
        - export_to_csv(self, filename=None) -> Union[str, Any]: Exports the collected data to a CSV file.

    Fields:
        - data: A dictionary that stores the generated responses and feedback for each combination.
        - prompts: A dictionary that stores the prompts added to the test, with their corresponding IDs.
        - cases: A dictionary that stores the test cases added to the test, with their corresponding IDs.
        - models: A list that stores the models added to the test.
        - runs: An integer that stores the number of runs for each combination."""

    def __init__(self, tid=None, file_path=None):
        self.data = defaultdict(dict)

        self.prompts = {}
        self.cases = {"base-case": None}
        self.models = []
        self.runs = 0

        if tid:
            # get just the tid from the file path if its a filepath
            if "/" in tid:
                tid = tid.split("/")[-1].split(".")[0]
            elif "." in tid:
                tid = tid.split(".")[0]

            self.tid = tid
            self._load_data()
        elif file_path:
            self.tid = file_path.split("/")[-1].split(".")[0]
            self._load_data(file_path)
        else:
            self.tid = uuid4().hex[0:8]

        if os.environ.get("LANGCHAIN_API_KEY", None):
            os.environ["LANGCHAIN_TRACING_V2"] = "true"
            os.environ["LANGCHAIN_PROJECT"] = f"ThumbTest: {self.tid}"
            os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"

    def __str__(self):
        combinations = (
            len(self.prompts) * len(self.cases) * len(self.models) * self.runs
        )
        if "base-case" in self.cases.keys():
            return f"ThumbTest: {self.tid}\n\nPrompts: {len(self.prompts)}\nCases: {len(self.cases) - 1}\nModels: {len(self.models)}\nRuns: {self.runs}\n\n{len(self.prompts)} x {len(self.cases) - 1} x {len(self.models)} x {self.runs} = {combinations}"
        return f"ThumbTest: {self.tid}\n\nPrompts: {len(self.prompts)}\nCases: {len(self.cases)}\nModels: {len(self.models)}\nRuns: {self.runs}\n\n{len(self.prompts)} x {len(self.cases)} x {len(self.models)} x {self.runs} = {combinations}"

    def add_prompts(self, prompts: List[Union[str, List[str]]] = []) -> None:
        # If the list is empty:
        if not prompts:
            raise PromptNotFoundError(
                "No prompts provided. You must provide at least one prompt."
            )

        for prompt in prompts:
            # If the prompt is a string, convert it to a list:
            if isinstance(prompt, str):
                prompt = [prompt]

            msg_string = "\n".join(prompt)
            pid = f"{hash_id(msg_string)}"
            if pid not in self.prompts.keys():
                self.prompts[pid] = prompt

    def add_cases(self, cases: Union[List[dict], list] = []) -> None:
        if not cases:
            return

        num_vars = None
        for case in cases:
            if num_vars is None:
                num_vars = len(case)
            elif len(case) != num_vars:
                raise VaryingCasesLengthError(
                    "All cases must have the same number of variables for each iteration. For example, if one case has 2 variables, all cases must have 2 variables."
                )

        for case in cases:
            cid = f"{hash_id(json.dumps(case))}"
            if cid not in self.cases.keys():
                # if base still in cases, remove it
                if "base-case" in self.cases.keys():
                    del self.cases["base-case"]
                self.cases[cid] = case

    def add_models(self, models: List[str]) -> None:
        for model in models:
            if model not in self.models:
                self.models.append(model)

    def add_runs(self, runs: Any) -> None:
        # Check if runs is an int:
        if not isinstance(runs, int):
            raise TypeError("runs must be an integer")

        # If runs is a float or string, try to convert it to an int:
        elif isinstance(runs, float) or isinstance(runs, str):
            try:
                runs = int(runs)
            except:
                raise TypeError("Runs must be an integer")

        # Check if runs is greater than 0:
        if runs < 1:
            raise ValueError("runs must be greater than 0")

        self.runs += runs

    def generate(self) -> None:
        combinations = (
            len(self.prompts) * len(self.cases) * len(self.models) * self.runs
        )
        print(
            f"{len(self.prompts)} prompts x {len(self.cases)} cases x {len(self.models)} x runs {self.runs} = {combinations} calls to the OpenAI API"
        )

        # Get combinations of prompt ids, case ids, and models:
        for pid, cid, model in product(
            self.prompts.keys(), self.cases.keys(), self.models
        ):
            print(cid)
            runs_completed = len(self.data.get(pid, {}).get(cid, {}).get(model, {}))

            if runs_completed < self.runs:
                # Process this combination:
                runs_needed = self.runs - runs_completed
                prompt = self.prompts[pid]
                test_case = self.cases[cid]

                responses = get_responses(
                    prompt, test_case, model, runs_needed, pid, cid
                )

                # Setting defaults:
                self.data.setdefault(pid, {}).setdefault(cid, {}).setdefault(model, {})

                for response in responses:
                    response["feedback"] = None
                    rid = uuid4().hex[:8]
                    self.data[pid][cid][model][rid] = response

                self._save_data()

    def _collect_required_runs(self) -> list:
        """
        Collects and returns all the required runs for the prompts, cases, and models.
        """
        required_runs = []

        for pid, cid, model in product(
            self.prompts.keys(), self.cases.keys(), self.models
        ):
            runs_completed = len(self.data.get(pid, {}).get(cid, {}).get(model, {}))

            if runs_completed < self.runs:
                runs_to_do = self.runs - runs_completed

                # Add a new item for each individual run that hasn't been completed yet
                for _ in range(runs_to_do):
                    required_runs.append(
                        {
                            "pid": pid,
                            "cid": cid,
                            "model": model,
                            "prompt": self.prompts[pid],
                            "test_case": self.cases[cid],
                        }
                    )

        return required_runs

    def _update_data_structure(self, pid, cid, model, response):
        """
        Helper function to update self.data with the given response
        """
        # Using setdefault to simplify dictionary structure initialization:
        model_data = (
            self.data.setdefault(pid, {}).setdefault(cid, {}).setdefault(model, {})
        )

        response["feedback"] = None
        rid = uuid4().hex[:8]
        model_data[rid] = response

    async def async_generate(self, batch_size=30) -> None:
        combinations = (
            len(self.prompts) * len(self.cases) * len(self.models) * self.runs
        )
        print(
            f"{len(self.prompts)} prompts x {len(self.cases)} cases x {len(self.models)} x runs {self.runs} = {combinations} calls to the OpenAI API"
        )

        # Create a list to collect needed runs
        required_runs = self._collect_required_runs()

        # Process the required runs in batches determined by batch_size:
        for i in range(0, len(required_runs), batch_size):
            batch = required_runs[i : i + batch_size]
            batch_responses = await async_get_responses(batch)

            for idx, response in enumerate(batch_responses):
                pid, cid, model = (
                    batch[idx]["pid"],
                    batch[idx]["cid"],
                    batch[idx]["model"],
                )

            # Update self.data structure with response:
            self._update_data_structure(pid, cid, model, response)
            self._save_data()

    def _save_data(self) -> None:
        """
        Save responses, prompts, cases, and models to a json file.
        """
        # Create a dictionary to hold the relevant data
        data = {
            "data": self.data,
            "prompts": self.prompts,
            "cases": self.cases,
            "models": self.models,
            "runs": self.runs,
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
            with open(file_path, "w") as file:
                file.write(data_json)
        except Exception as e:
            print(f"Caching failed due to: {e}")

    def _load_data(self, file_path=None) -> None:
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
            # Check if the JSON file exists
            if os.path.exists(json_file_path):
                self._read_from_json(json_file_path)

            # Check if the CSV file exists
            elif os.path.exists(csv_file_path):
                self._read_from_csv(csv_file_path)

            else:
                raise FileNotFoundError(f"No data found for tid: {self.tid}")

    def _read_from_csv(self, csv_file_path: str) -> None:
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
        prompts = (
            csv_df.drop_duplicates(subset=["PID"])[["PID", "Prompt"]]
            .set_index("PID")
            .to_dict()["Prompt"]
        )
        cases = (
            csv_df.drop_duplicates(subset=["CID"])[["CID", "Case"]]
            .set_index("CID")
            .to_dict()["Case"]
        )
        models = csv_df["Model"].unique().tolist()

        # Adjust prompts based on their type (list or string):
        for pid, prompt_str in prompts.items():
            try:
                prompts[pid] = eval(prompt_str)
                # Convert single strings wrapped in a list to just strings
                if isinstance(prompts[pid], list) and len(prompts[pid]) == 1:
                    prompts[pid] = prompts[pid][0]
            except:
                pass

        # Convert cases' string to dictionary format:
        for cid, case_str in cases.items():
            cases[cid] = json.loads(case_str)

        # Construct the data dictionary:
        data = {}
        for _, row in csv_df.iterrows():
            pid = row["PID"]
            cid = row["CID"]
            model = row["Model"]
            rid = row["RID"]

            # Initialize nested dictionaries if not present:
            if pid not in data:
                data[pid] = {}
            if cid not in data[pid]:
                data[pid][cid] = {}
            if model not in data[pid][cid]:
                data[pid][cid][model] = {}

            # Handle NaN feedback values:
            feedback_value = (
                int(row["Feedback"]) if not pd.isna(row["Feedback"]) else None
            )

            # Add the details under the RID:
            data[pid][cid][model][rid] = {
                "content": row["Content"],
                "tokens": row["Tokens"],
                "cost": row["Cost"],
                "prompt_tokens": row["Prompt Tokens"],
                "completion_tokens": row["Completion Tokens"],
                "latency": row["Latency"],
                "feedback": feedback_value,
            }

        # Compute the runs value:
        runs_value = compute_runs(data)

        # Combine all parts to form the final structure:
        self.data = data
        self.prompts = prompts
        self.cases = cases
        self.models = models
        self.runs = runs_value

    def _read_from_json(self, json_file_path) -> None:
        with open(json_file_path, "r") as file:
            data = json.load(file)

        # Update the instance variables with the loaded data
        self.data = data.get("data", {})
        self.prompts = data.get("prompts", {})
        self.cases = data.get("cases", {})
        self.models = data.get("models", [])
        self.runs = data.get("runs", 0)

    def _prep_for_eval(self) -> list:
        """
        Prepare the responses for evaluation.
        """
        responses = []

        # Loop through the prompts:
        for pid in self.data.keys():
            # Loop through the cases:
            for cid in self.data[pid].keys():
                # Loop through the models
                for model in self.data[pid][cid].keys():
                    # Loop through the responses
                    for rid, response in self.data[pid][cid][model].items():
                        # If the response has feedback, skip it:
                        if response["feedback"] is not None:
                            continue
                        response_data = {
                            "pid": pid,
                            "cid": cid,
                            "model": model,
                            "rid": rid,
                            "content": response["content"],
                        }

                        # Add the response data to the list of responses:
                        responses.append(response_data)

        # Shuffle the order of the responses:
        random.shuffle(responses)
        return responses

    def _receive_feedback(self, label, pid, cid, model, rid) -> None:
        # Convert thumbs up / down to 1 / 0:
        value = 1 if label.description == "👍" else 0

        # Update the response based on the provided index:
        self.data[pid][cid][model][rid]["feedback"] = value

    def stats(self):
        scores = {}

        # Loop through the prompts, cases, models:
        for pid, cid, model in product(
            self.data.keys(), self.data[pid].keys(), self.data[pid][cid].keys()
        ):
            prompt = self.prompts[pid]

            # Initialize scores for pid if not present:
            if pid not in scores:
                scores[pid] = {
                    "prompt": prompt,
                    "feedback": [],
                    "tokens": [],
                    "cost": [],
                }

            for response in self.data[pid][cid][model].values():
                scores[pid]["feedback"].append(response["feedback"])
                scores[pid]["tokens"].append(response["tokens"])
                scores[pid]["cost"].append(response["cost"])

        # Calculate the average scores, tokens, and cost:
        for pid, score_data in scores.items():
            score_data["avg_score"] = sum(score_data["feedback"]) / len(
                score_data["feedback"]
            )
            score_data["avg_tokens"] = sum(score_data["tokens"]) / len(
                score_data["tokens"]
            )
            score_data["avg_cost"] = sum(score_data["cost"]) / len(score_data["cost"])

        return scores

    def evaluate(self) -> None:
        # TODO - Clean up this function, into a separate module:
        prepped_data = self._prep_for_eval()
        data_len = len(prepped_data)
        labels = ["👎", "👍"]
        label_widgets = [widgets.Button(description=label) for label in labels]

        main_box = widgets.VBox()

        test_id = widgets.Label(value=f"ThumbTest: {self.tid}")
        response_box = widgets.HTML()
        progress_bar = widgets.IntProgress(min=0, max=data_len, description="Progress:")

        def update_response() -> None:
            nonlocal prepped_data
            if not prepped_data:
                stats = ""

                # TODO abstract this out into a function:
                flattened_data = []
                for pid, pid_data in self.data.items():
                    prompt = self.prompts.get(pid, None)

                    for cid, cid_data in pid_data.items():
                        case = self.cases.get(cid, None)
                        case = json.dumps(case)

                        for model, model_data in cid_data.items():
                            for rid, details in model_data.items():
                                content = details.get("content", None)
                                tokens = details.get("tokens", None)
                                cost = details.get("cost", None)
                                feedback = details.get("feedback", None)
                                latency = details.get("latency", None)
                                prompt_tokens = details.get("prompt_tokens", None)
                                completion_tokens = details.get(
                                    "completion_tokens", None
                                )

                                flattened_data.append(
                                    [
                                        pid,
                                        prompt,
                                        cid,
                                        case,
                                        model,
                                        rid,
                                        content,
                                        tokens,
                                        prompt_tokens,
                                        completion_tokens,
                                        cost,
                                        latency,
                                        feedback,
                                    ]
                                )

                df = pd.DataFrame(
                    data=flattened_data,
                    columns=[
                        "PID",
                        "Prompt",
                        "CID",
                        "Case",
                        "Model",
                        "RID",
                        "Content",
                        "Tokens",
                        "Prompt Tokens",
                        "Completion Tokens",
                        "Cost",
                        "Latency",
                        "Feedback",
                    ],
                )

                stats_df = (
                    df.groupby(["PID", "CID", "Model"])
                    .agg(
                        runs=("PID", "size"),
                        feedback=("Feedback", "sum"),
                        score=("Feedback", "mean"),
                        tokens=("Tokens", "mean"),
                        cost=("Cost", "mean"),
                        latency=("Latency", "mean"),
                    )
                    .reset_index()
                )

                full_stats_df = stats_df.pivot_table(
                    index=["PID", "CID", "Model"],
                    values=["runs", "tokens", "cost", "latency", "feedback", "score"],
                    aggfunc="first",
                )

                pid_stats_df = stats_df.pivot_table(
                    index=["PID"],
                    values=["runs", "tokens", "cost", "latency", "feedback", "score"],
                    aggfunc="first",
                ).reset_index()

                cid_stats_df = stats_df.pivot_table(
                    index=["CID"],
                    values=["runs", "tokens", "cost", "latency", "feedback", "score"],
                    aggfunc="first",
                ).reset_index()

                model_stats_df = stats_df.pivot_table(
                    index=["Model"],
                    values=["runs", "tokens", "cost", "latency", "feedback", "score"],
                    aggfunc="first",
                ).reset_index()

                # Always show pid table:
                pid_table_output = pid_stats_df.to_html()
                stats += f"<br>{pid_table_output}"

                # - Don't show the CID breakdown if base case:
                if len(self.cases) == 1:
                    # Reset the multi-index to columns:
                    full_stats_df_reset = full_stats_df.reset_index()

                    # Set the index again without 'CID':
                    full_stats_df = full_stats_df_reset.set_index(["PID", "Model"])

                else:
                    cid_table_output = cid_stats_df.to_html()
                    stats += f"<br>{cid_table_output}"

                # - Don't show the model breakdown if only one model:
                if len(self.models) == 1:
                    # Reset the multi-index to columns:
                    full_stats_df_reset = full_stats_df.reset_index()

                    # Set the index again without 'CID':
                    full_stats_df = full_stats_df_reset.set_index(["PID", "CID"])

                else:
                    model_table_output = model_stats_df.to_html()
                    stats += f"<br>{model_table_output}"

                # Only show full stats if there's more than one model or more than one case:
                if len(self.models) > 1 or len(self.cases) > 1:
                    full_table_output = full_stats_df.to_html()
                    stats += f"<br>{full_table_output}"

                # Add the prompt and case key to the end of the stats:
                stats += f"<br><br><b>Prompts</b>:<br>"
                for pid, prompt in self.prompts.items():
                    stats += f"{pid}: {prompt}<br>"

                # If there are cases, add them to the stats:
                if len(self.cases) > 1:
                    for cid, case in self.cases.items():
                        stats += f"<br><b>Cases</b>:<br>"
                        stats += f"{cid}: {case}<br>"

                response_box.value = (
                    f"Evaluation complete! 🎉<br><b>Results</b>: <br>{stats}<br>"
                )
                # Update children of main_box to exclude the label_widget:
                main_box.children = [response_box, test_id]
                # Cache the feedback:
                self._save_data()
                return

            next_response = prepped_data[0]["content"]
            progress_value = data_len - len(prepped_data)

            response_box.value = next_response
            progress_bar.value = progress_value

        def on_button_clicked(b) -> None:
            nonlocal prepped_data
            if not prepped_data:
                return

            response = prepped_data.pop(0)
            pid = response["pid"]
            cid = response["cid"]
            model = response["model"]
            rid = response["rid"]

            self._receive_feedback(b, pid, cid, model, rid)
            update_response()

        # Add on_click to buttons:
        for label_widget in label_widgets:
            label_widget.on_click(on_button_clicked)

        label_box = widgets.HBox(label_widgets)
        main_box.children = [label_box, progress_bar, response_box, test_id]

        clear_output(wait=True)

        update_response()
        display(main_box)

    def export_to_csv(self, filename=None) -> Union[str, Any]:
        # set today's date for folder name
        today = datetime.date.today().strftime("%Y-%m-%d")
        # create the folder if it doesn't exist
        if not os.path.exists(today):
            os.makedirs(today)

        # set the filename
        if not filename:
            filename = f"{today}/ThumbTest-{self.tid}.csv"

        # Flattening the data for CSV export
        flattened_data = []

        for pid, pid_data in self.data.items():
            prompt = self.prompts.get(pid, None)

            for cid, cid_data in pid_data.items():
                case = self.cases.get(cid, None)
                case = json.dumps(case)

                for model, model_data in cid_data.items():
                    for rid, details in model_data.items():
                        content = details.get("content", None)
                        tokens = details.get("tokens", None)
                        cost = details.get("cost", None)
                        feedback = details.get("feedback", None)
                        latency = details.get("latency", None)
                        prompt_tokens = details.get("prompt_tokens", None)
                        completion_tokens = details.get("completion_tokens", None)

                        flattened_data.append(
                            [
                                pid,
                                prompt,
                                cid,
                                case,
                                model,
                                rid,
                                content,
                                tokens,
                                prompt_tokens,
                                completion_tokens,
                                cost,
                                latency,
                                feedback,
                            ]
                        )

        with open(filename, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(
                [
                    "PID",
                    "Prompt",
                    "CID",
                    "Case",
                    "Model",
                    "RID",
                    "Content",
                    "Tokens",
                    "Prompt Tokens",
                    "Completion Tokens",
                    "Cost",
                    "Latency",
                    "Feedback",
                ]
            )
            # Writing data:
            writer.writerows(flattened_data)
        return filename
