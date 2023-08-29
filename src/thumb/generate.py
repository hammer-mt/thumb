
from langchain.chat_models import ChatOpenAI
from langchain.prompts import HumanMessagePromptTemplate, ChatPromptTemplate

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