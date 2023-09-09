from langchain.chat_models import ChatOpenAI
from langchain.prompts import HumanMessagePromptTemplate, SystemMessagePromptTemplate, AIMessagePromptTemplate, ChatPromptTemplate
from tqdm.auto import tqdm
import time
from langchain.callbacks.openai_info import standardize_model_name, MODEL_COST_PER_1K_TOKENS, get_openai_token_cost_for_model
import asyncio

def format_chat_prompt(messages, test_case):
    message_templates = []
    
    # if there is only one messages in the array, make it a HumanMessage
    if isinstance(messages, list) and len(messages) == 1:
        human_template = HumanMessagePromptTemplate.from_template(messages[0])
        message_templates.append(human_template)
    
    # if there are multiple messages, the first is a SystemMessage and the rest alternate between HumanMessage and AIMessage
    elif isinstance(messages, list) and len(messages) > 1:
        system_template = SystemMessagePromptTemplate.from_template(messages[0])
        message_templates.append(system_template)
        for i, prompt in enumerate(messages[1:]):
            if i % 2 == 0:
                human_template = HumanMessagePromptTemplate.from_template(prompt)
                message_templates.append(human_template)
            else:
                ai_template = AIMessagePromptTemplate.from_template(prompt)
                message_templates.append(ai_template)
            
    chat_prompt_template = ChatPromptTemplate.from_messages(message_templates)
    if test_case:
        formatted_prompt = chat_prompt_template.format_prompt(**test_case)
    else:
        formatted_prompt = chat_prompt_template.format_prompt()
    
    return formatted_prompt.to_messages()

def estimate_openai_cost(prompt_tokens, completion_tokens, model_name):
    total_cost = 0
    model_name = standardize_model_name(model_name)
    if model_name in MODEL_COST_PER_1K_TOKENS:
        completion_cost = get_openai_token_cost_for_model(
            model_name, completion_tokens, is_completion=True
        )
        prompt_cost = get_openai_token_cost_for_model(model_name, prompt_tokens)
        total_cost += prompt_cost + completion_cost
    return total_cost

def get_responses(prompt, test_case, model, runs, pid, cid):
    chat = ChatOpenAI(model=model)
    formatted_prompt = format_chat_prompt(prompt, test_case)

    responses = []
    for _ in tqdm(range(runs)):
        try:
            start_time = time.time()
            resp = chat.generate([formatted_prompt], tags=[f"pid_{pid}", f"cid_{cid}"])
            end_time = time.time()
            response_data = parse_generate_response(resp)
            response_data["latency"] = end_time - start_time or 0
        except Exception as e:
            response_data = {"content": str(e)}
        finally:                
            responses.append(response_data)

    return responses

def parse_generate_response(resp):
    response_content = resp.generations[0][0].text
    token_usage = resp.llm_output["token_usage"]
    model_name = resp.llm_output["model_name"]
    tokens = token_usage["total_tokens"]
    prompt_tokens = token_usage["prompt_tokens"]
    completion_tokens = token_usage["completion_tokens"]
    cost = estimate_openai_cost(prompt_tokens, completion_tokens, model_name)

    response_data = {
        "content": response_content,
        "tokens": tokens or 0,
        "cost": cost or 0,
        "prompt_tokens": prompt_tokens or 0,
        "completion_tokens": completion_tokens or 0,
    }
    return response_data

async def async_generate(chat, formatted_prompt, tags=[]):
    try:
        start_time = time.time()
        resp = await chat.agenerate([formatted_prompt], tags=tags)
        end_time = time.time()
        response_data = parse_generate_response(resp)
        response_data["latency"] = end_time - start_time or 0
    except Exception as e:
        response_data = {"content": str(e)}
    finally:
        return response_data

async def async_get_responses(prompt, test_case, model, runs, pid, cid):
    chat = ChatOpenAI(model=model)
    formatted_prompt = format_chat_prompt(prompt, test_case)

    tasks = []

    for _ in tqdm(range(runs)):
        task = async_generate(chat, formatted_prompt, tags=[f"pid_{pid}", f"cid_{cid}"])
        tasks.append(task)

    responses = await asyncio.gather(*tasks)

    return responses
