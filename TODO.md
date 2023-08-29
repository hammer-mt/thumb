## Active Tasks

### test function
- catch langchain api key and set up tracing
- handle the setup of prompt templates
- handle the setup of test cases
- handle the setup of the models
- create permutations of each prompt and test case and model combo
- run the models in a loop or async
- handle caching of each response
- handle prompts being strings or arrays
- handle prompts being langchain templates, chains, agents
- handle additional metadata passed with prompt
- create unique id hash for each prompt template (pid), test case (cid), run (rid), and test (tid)
- unpack dictionary as args to format prompt `result = prompt_template.format(**params)`
- handle reference answers for test cases

### evals function
- spin up gradio user interface
- shuffle responses and loop through
- share URL flow
- set custom criteria
- automatic rating model
- call the stats model
- choose the control in gradio
- choose the success metric in gradio
- handle saving of CSV locally
- integrate with langchain's eval criteria
- handle custom labels

### stats function
- calculate the score
- calculate the confidence with bayesian stats
- estimate the lift using bayesian stats
- tiktoken to calculate token usage
- openai price estimate based on tokens 

### load function
- load an existing model


## Ideas Roadmap
- support other user interfaces (ipython, streamlit)
- full testing suite to spot breaking changes
- upload to gradio spaces for non-technical teams
- early stopping mechanism once 95% confidence reached
- support pricing of alternatives to openai (anthropic)
- image model testing as well as LLMs