## Active Tasks

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


## Ideas Roadmap
- support other user interfaces (ipython, streamlit)
- full testing suite to spot breaking changes
- upload to gradio spaces for non-technical teams
- early stopping mechanism once 95% confidence reached
- support pricing of alternatives to openai (anthropic)
- image model testing as well as LLMs
- add async to the calls
- move tags to metadata not tracing
- merging two tests together
- handle prompts being strings or arrays
- handle non chat models
- handle non openai models
- handle prompts being langchain templates, chains, agents
- handle reference answers for test cases