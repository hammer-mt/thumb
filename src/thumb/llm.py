from langchain.chat_models import ChatOpenAI
from langchain.prompts import HumanMessagePromptTemplate, ChatPromptTemplate
from langchain.callbacks.manager import tracing_v2_enabled


def format_chat_prompt(prompt, case):
    human_template = HumanMessagePromptTemplate.from_template(prompt)
    chat_prompt_template = ChatPromptTemplate.from_messages([human_template])
    formatted_prompt = chat_prompt_template.format_prompt(**case)
    final_prompt = formatted_prompt.to_messages()
    
    return final_prompt

def get_responses(prompt, case, model, runs, tid, pid, cid, tracing):
    chat = ChatOpenAI(model=model)
    formatted_prompt = format_chat_prompt(prompt, case)

    responses = []
    print(f"Running {pid} for {cid} with {model}:")
    if tracing:
        with tracing_v2_enabled(project_name=f"ThumbTest-{tid}", tags=[pid, cid]):
            for i in range(runs):
                try:
                    print(f"{i+1}/{runs}")
                    response = chat(formatted_prompt).content
                    responses.append(response)
                except Exception as e:
                    responses.append(str(e))
    else:
        for i in range(runs):
            try:
                print(f"{i+1}/{runs}")
                response = chat(formatted_prompt).content
                responses.append(response)
            except Exception as e:
                responses.append(str(e))

    return responses