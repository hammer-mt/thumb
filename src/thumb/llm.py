from langchain.chat_models import ChatOpenAI
from langchain.prompts import HumanMessagePromptTemplate, ChatPromptTemplate
from langchain.callbacks.manager import tracing_v2_enabled
from langchain.callbacks import get_openai_callback

def format_chat_prompt(prompt, case):
    human_template = HumanMessagePromptTemplate.from_template(prompt)
    chat_prompt_template = ChatPromptTemplate.from_messages([human_template])
    formatted_prompt = chat_prompt_template.format_prompt(**case)
    final_prompt = formatted_prompt.to_messages()
    
    return final_prompt

def get_responses(prompt, test_case, model, runs, tid, pid, cid):
    chat = ChatOpenAI(model=model)
    formatted_prompt = format_chat_prompt(prompt, test_case)

    responses = []
    with get_openai_callback() as cb:
        for _ in range(runs):
            try:
                response_content = chat(formatted_prompt, tags=[pid, cid]).content
            except Exception as e:
                response_content = str(e)
            finally:
                response_data = {
                    "content": response_content,
                    "tokens": cb.total_tokens or 0,
                    "cost": cb.total_cost or 0,
                }
                
                responses.append(response_data)

    return responses