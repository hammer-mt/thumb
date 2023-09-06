## TODOs

### test
- add async to the calls
- move tags to metadata not tracing
- merging two tests together
- handle prompts being strings or arrays
- move models to having unique ids instead of calling by name
- handle non chat models
- handle non openai models
- handle prompts being langchain templates, chains, agents
- handle reference answers for test cases
- calculate number of tests and display
- add a cancel button to stop the tests
- add a confirmation before running tests

### evals
- set custom criteria for ratings
- automatic rating modeln with GPT-4
- integrate with langchain's eval criteria
- handle custom labels instead of thumbs
- early stopping mechanism once 95% confidence reached
- calculate the embedding distance between the reference and the response
- move the thumbs to the right hand side
- train a reward model to predict thumbs
- ranking instead of thumbs

### stats
- calculate the confidence with bayesian stats
- estimate the lift using bayesian stats
- openai price estimate based on tokens
- support pricing of alternatives to openai (anthropic)
- set the success metric
- set the control prompt / model
- add latency to the stats

## interface
- spin up gradio user interface
- add a CLI
- support other user interfaces (gradio, streamlit)
- upload to gradio spaces for non-technical teams
- share URL with external people

## other ideas
- full testing suite to spot breaking changes
- types and errors when the format is wrong
- image model testing as well as LLMs
- generate new prompts, test cases with GPT-4
