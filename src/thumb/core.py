
import os
import csv
import random
from uuid import uuid4
from dotenv import load_dotenv

load_dotenv()

from langchain.callbacks.manager import tracing_v2_enabled

from .generate import create_calls, generate_single

def test(*args, **kwargs):
    thumb = ThumbTest()
    return thumb.test(*args, **kwargs)

def load(file_path):
    filename = file_path.split('/')[-1]
    tid = filename.replace(".csv", "").split("-")[-1]

    # load the csv to get the data
    data = []
    with open(file_path, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            data.append(row)

    return ThumbTest(tid, data)


class ThumbTest:
    
    def __init__(self, tid=None, data=None):
        self.tid = tid or uuid4().hex[0:8]
        self.data = data or []
        self.langchain_api_key = os.environ.get("LANGCHAIN_API_KEY", None)

    def test(self, 
             prompts, 
             cases, 
             runs = 30, 
             models = ['gpt-3.5-turbo'], 
             cache = True):
        
        # create a unique id for the test
        tid = uuid4().hex[0:8]

        # loop through to create the calls
        calls = create_calls(prompts, cases, models, runs)
        print(f"Created {len(calls)} calls for test {tid}")
        print(calls)

        # randomize the calls
        random.shuffle(calls)
        print(f"Randomized calls for test {tid}")
        print(calls)

        # set up the test instance
        test_instance = Test(tid=tid, calls=calls)

        # generate responses
        test_instance.generate(tracing=self.langchain_api_key is not None, 
                               cache=cache)
        
        return test_instance

    def _generate(self, calls):

        responses = []
        counter = 1
        for call in calls:
            if self.langchain_api_key:
                with tracing_v2_enabled(
                    project_name=f"thumb_test_{call['tid']}", 
                    tags=[call['pid'], call['cid']]):
                    
                    data = generate_single(call)

            else:
                data = generate_single(call)

            responses.append(data)
            counter += 1
        
        return responses
    
    def evals(labels=None):
        labels = labels or ["👎", "👍"]
        return labels

thumb = Thumb()
