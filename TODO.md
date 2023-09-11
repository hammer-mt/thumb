# TODOs

## Active tasks

### on deck
- refactor the interface to show results in a table not a list
- load data from csv not just json - check cache first then this
- generate new prompt variations for an existing test
- generate new test cases for an existing test
- spin up gradio user interface

### bugs / feedback
- I struggled with some more prompts containing a { } (notably JSON outputs)
- There wasn’t the ability to test prompts with functions

## Ideas by area

### test
- add a test name and display to the interface
- add a name for each prompt and display to the interface
- ability to merge two tests together
- handle reference answers for test cases
- handle prompts being langchain templates, chains, agents
    - handle non-openai chat models
    - add a unique model id instead of relying on name
    - check if the model is a string, chain, model, or agent
    - handle the case where the model is a chain
    - handle the case where the model is an agent
    - handle the case where the model is a model object
- add a test description
- add a prompt description
- add a test case description
- add a test case name
- add the ability to change filepath for caching
- switch caching on/off or set batch size

### evals
- set custom criteria for ratings
- automatic rating model with GPT-4 based on criteria
- automatic ranking model with GPT-4 based on criteria
- integrate with langchain's eval criteria
- handle custom labels instead of thumbs
- early stopping mechanism once 95% confidence reached
- calculate the embedding distance between the reference and the response
- ordered ranking instead of thumbs
- pass your own custom eval function
- add a user id to evaluation
- add ability to redo or clear evals
- set JSON parsing or an output parser as eval

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

