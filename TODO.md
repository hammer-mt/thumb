## TODOs

### on deck
- add to readme details on async and message based prompts
- add a test name and display to the interface
- refactor the interface to show results in a table not a list
- add a name for each prompt and display to the interface
- load data from csv not just json
- spin up gradio user interface
- generate new prompt variations

### test
- ability to merge two tests together
- make the full test call stack async not just runs
- handle reference answers for test cases
- handle prompts being langchain templates, chains, agents
    - handle non-openai chat models
    - add a unique model id instead of relying on name
    - check if the model is a string, chain, model, or agent
    - handle the case where the model is a chain
    - handle the case where the model is an agent
    - handle the case where the model is a model object

### evals
- set custom criteria for ratings
- automatic rating model with GPT-4
- integrate with langchain's eval criteria
- handle custom labels instead of thumbs
- early stopping mechanism once 95% confidence reached
- calculate the embedding distance between the reference and the response
- ordered ranking instead of thumbs
- pass your own custom eval function
- add a user id to evaluation
- add ability to redo or clear evals

### stats
- calculate the confidence with bayesian stats
- estimate the lift using bayesian stats
- support pricing of alternatives to openai (anthropic, etc)
- set the success metric for eval (not just thumbs up)
- set the control prompt / model for lift calculation

## interface
- upload to gradio spaces for non-technical teams
- share URL with external people
- add a generate interface
    - show number of calls needed
    - add a cancel button to stop tests
    - add a progress bar (or print tqdm)

## generate
- generate test cases for prompts

## other ideas
- full testing suite to spot breaking changes
- types and errors when the format is wrong
- image model testing as well as LLMs

