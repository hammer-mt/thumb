
from langchain.chat_models import ChatOpenAI
from langchain.prompts import HumanMessagePromptTemplate, ChatPromptTemplate

from .utils import hash_id

def generate_single(call):
    model = ChatOpenAI(model=call["model"])

    formatted_prompt = format_chat_prompt(call["prompt"], call["case"])

    response = model(formatted_prompt)

    data = call.copy()
    data["response"] = response.content

    return data

def format_chat_prompt(prompt, case):
    human_template = HumanMessagePromptTemplate.from_template(prompt)
    chat_prompt_template = ChatPromptTemplate.from_messages([human_template])
    formatted_prompt = chat_prompt_template.format_prompt(**case)
    final_prompt = formatted_prompt.to_messages()
    
    return final_prompt

def create_calls(prompts, cases, models, runs):
    calls = []
    for template in prompts:
            pid = f"pid_{hash_id(template)}"
            for case in cases:
                cid = f"cid_{hash_id(str(case))}"
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

    return calls