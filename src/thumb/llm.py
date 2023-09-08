from langchain.chat_models import ChatOpenAI
from langchain.prompts import HumanMessagePromptTemplate, ChatPromptTemplate
from langchain.callbacks import get_openai_callback
from tqdm.auto import tqdm
from tqdm.asyncio import tqdm_asyncio
import time

def format_chat_prompt(prompt, case):
    human_template = HumanMessagePromptTemplate.from_template(prompt)
    chat_prompt_template = ChatPromptTemplate.from_messages([human_template])
    if case:
        formatted_prompt = chat_prompt_template.format_prompt(**case)
    else:
        formatted_prompt = chat_prompt_template.format_prompt()
    
    return formatted_prompt.to_messages()

def get_responses(prompt, test_case, model, runs, pid, cid):
    chat = ChatOpenAI(model=model)
    formatted_prompt = format_chat_prompt(prompt, test_case)

    responses = []
    with get_openai_callback() as cb:
        for _ in tqdm(range(runs)):
            try:
                start_time = time.time()
                response_content = chat(formatted_prompt, tags=[pid, cid]).content
                end_time = time.time()
            except Exception as e:
                response_content = str(e)
            finally:                
                response_data = {
                    "content": response_content,
                    "tokens": cb.total_tokens or 0,
                    "cost": cb.total_cost or 0,
                    "latency": end_time - start_time,
                    "prompt_tokens": cb.prompt_tokens or 0,
                    "completion_tokens": cb.completion_tokens or 0,
                }
                
                responses.append(response_data)

    return responses


async def async_get_responses(prompt, test_case, model, runs, pid, cid):
    chat = ChatOpenAI(model=model)
    formatted_prompt = format_chat_prompt(prompt, test_case)

    responses = []
    # async with get_openai_callback() as cb:
    # for _ in tqdm_asyncio(range(runs)):
    for _ in range(runs):
        print('formatted_prompt', formatted_prompt)
        try:
            start_time = time.time()
            print("start_time", start_time)
            response = await chat.agenerate(formatted_prompt, tags=[pid, cid])
            print('response', response)
            response_content = response.content
            print('response_content', response_content)
            end_time = time.time()
            print("end_time", end_time)
        except Exception as e:
            response_content = str(e)
        finally:                
            response_data = {
                "content": response_content,
                # "tokens": cb.total_tokens or 0,
                # "cost": cb.total_cost or 0,
                # "latency": end_time - start_time,
                # "prompt_tokens": cb.prompt_tokens or 0,
                # "completion_tokens": cb.completion_tokens or 0,
            }
            
            responses.append(response_data)

    return responses