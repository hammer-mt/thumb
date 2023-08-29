
import os
import random
from uuid import uuid4
from dotenv import load_dotenv

load_dotenv()

from langchain.callbacks.manager import tracing_v2_enabled

from .utils import hash_id
from .generate import generate_single

class Test:

    def __init__(self, tid, responses):
        self.tid = tid
        self.responses = responses


class Thumb:
    
    def __init__(self):
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
        calls = []

        for template in prompts:
            pid = f"pid_{hash_id(template)}"
            for case in cases:
                cid = f"cid_{hash_id(case)}"
                formatted_prompt = template.format(**case)
                for model in models:
                    for _ in range(runs):
                        calls.append({
                            "pid": pid,
                            "cid": cid,
                            "prompt": formatted_prompt,
                            "template": template,
                            "model": model
                        })

        # randomize the calls
        calls = random.shuffle(calls)

        # generate responses
        responses = self._generate(calls)

        # set up the test object
        test_instance = Test(tid=tid, responses=responses)
        
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
