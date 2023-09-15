import asyncio
import time
from typing import Any, List, Union

from langchain.callbacks.openai_info import (
    MODEL_COST_PER_1K_TOKENS,
    get_openai_token_cost_for_model,
    standardize_model_name,
)
from langchain.chat_models import ChatOpenAI
from langchain.prompts import (
    AIMessagePromptTemplate,
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain.schema import BaseMessage
from tqdm.auto import tqdm


def format_chat_prompt(
    messages: [List[str], None], test_case: Union[str, None]
) -> List[BaseMessage]:
    message_templates = []

    if (messages is None) or (len(messages) == 0):
        raise ValueError("messages must be a non-empty list of strings")

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


def estimate_openai_cost(prompt_tokens: int, completion_tokens: int, model_name: str):
    total_cost = 0
    model_name = standardize_model_name(model_name)
    if model_name in MODEL_COST_PER_1K_TOKENS:
        completion_cost = get_openai_token_cost_for_model(
            model_name, completion_tokens, is_completion=True
        )
        prompt_cost = get_openai_token_cost_for_model(model_name, prompt_tokens)
        total_cost += prompt_cost + completion_cost
    return total_cost


def get_responses(prompt: str, test_case: str, model, runs: int, pid: str, cid: str):
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


def parse_generate_response(resp: Any):
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


async def async_generate(
    chat: ChatOpenAI, formatted_prompt: List[BaseMessage], tags=[]
):
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


async def async_get_responses(batch: List[Any]) -> List[Any]:
    """
    Asynchronously generates responses for a batch of prompts.

    Args:
        batch (List[Any]): A list of dictionaries, where each dictionary contains the following keys:
            - "prompt": A string representing the prompt to generate a response for.
            - "test_case": A single case value associated with the prompt.
            - "model": A string representing the name of the OpenAI chat model to use.
            - "pid": An integer representing the ID of the prompt_id associated with the prompt.
            - "cid": An integer representing the ID of the case associated with the prompt.

    Returns:
        List[Any]: A list of responses generated by the chat model, in the same order as the input batch.
    """

    tasks = []

    for item in batch:
        prompt = item["prompt"]
        test_case = item["test_case"]
        model = item["model"]
        pid = item["pid"]
        cid = item["cid"]

        chat = ChatOpenAI(model=model)
        formatted_prompt = format_chat_prompt(prompt, test_case)

        task = async_generate(chat, formatted_prompt, tags=[f"pid_{pid}", f"cid_{cid}"])
        tasks.append(task)

    responses = await asyncio.gather(*tasks)
    return responses
