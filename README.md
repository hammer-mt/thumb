# thumb

A simple prompt testing library for LLMs built on Langchain and Gradio.

## Quick start

### 1. Install the library

> `pip install thumb`

### 2. Set up a test

```Python
import os
import thumb

# Set the environment variables (get your API key: https://platform.openai.com/account/api-keys)
os.environ["OPENAI_API_KEY"] = "YOUR_API_KEY_HERE"
os.environ["LANGCHAIN_API_KEY"] = "YOUR_API_KEY_HERE" # optional: for langsmith tracing

# set up a prompt templates for the a/b test
prompt_a = "tell me a joke in the style of {comedian}"
prompt_b = "tell me a family friendly joke in the style of {comedian}"

# set test cases with different input variables
cases = [
  {"comedian": "chris rock"}, 
  {"comedian": "ricky gervais"}, 
  {"comedian": "robin williams"}
  ]

# generate the responses
test = thumb.test([prompt_a, prompt_b], cases)
```

#### Required

- **prompts**: an array of prompt templates to be tested

#### Optional

- **cases**: a dictionary of variables to input into each prompt template (default: `None`)
- **runs**: the number of responses to generate per prompt and test case (default: `30`)
- **models**: a langchain model (or list of models) you want to generate responses from (default: [`gpt-3.5-turbo`])
- **cache**: whether to cache the raw responses locally to JSON to avoid re-running (default: `True`)

If you include variables in your prompt templates (i.e. `{variable}`) you must provide corresponding test cases, otherwise this field is not required. Remember to include a value in your test case for each variable in your template.

If you have 30 test runs with 2 prompt templates and 3 test cases, that's `30 x 2 x 3 = 180` calls to your LLM. Be careful: these can add up quickly!

Langchain tracing to [LangSmith](https://smith.langchain.com/) is automatically enabled if the `LANGCHAIN_API_KEY` is set as an environment variable (optional).

### 3. Rate the responses

```Python
test.evals()
```

For manual rating, a Gradio user interface spins up, and you are given a URL to visit to rate each response. Each combination of prompt template and test case is displayed in a random order for blind rating (you don't see which prompt template, just the response) so you do not bias the results. 

Once all responses have been rated, the following performance statistics are calculated broken down by prompt template and test case:
- `score` number of positive ratings as a percentage of all runs
- `confidence`: the probability of winning if you ran the test again
- `lift`: uplift in percentage terms versus the control
- `tokens`: how many tokens were used across the prompt and response
- `cost`: an estimate of the average cost per call based on tokens used

By default the worst performing prompt is set as control, but you can update this by selecting a different variant in the Gradio user interface, and the metrics will recalculate.

### Advanced Features

The `.evals()` function has a number of advanced features and customization options to suit your testing needs.

#### Optional
- **labels**: displayed when blind rating the responses for feedback (default: `["👎", "👍"]`)
- **success**: the labels that will be considered to be succesful responses in calculating stats (default: `["👍"]`)
- **criteria**: a list of rules dictating how the response should be rated (default: `None`)
- **auto**: automatically rate responses using an LLM based on the list of provided criteria (default: `None`)
- **model**: a langchain model you want to use to automatically evaluate the test (default: `gpt-4`)
- **share**: this creates a shareable link to share externally with another participant in the ratings (default: `False`)
- **save**: whether to save the feedback data locally as a csv to save re-rating (default: `True`)

##### Criteria

For manual rating criteria will be displayed above the response to be rated, and multiple criteria will cause each response to be rated multiple times, once for each criteria.

##### Auto Evaluation

If you provide multiple criteria a seperate call to the model will be made for each criteria, so 180 responses with 2 criteria would cause `180 x 2 = 360` calls to the LLM, incurring additional cost. 

If you set `auto=True` but no criteria is provided, the responses will be rated based on Langchain's `HELPFULLNESS` critera: `"Is the submission helpful, insightful, and appropriate? If so, response Y. If not, respond N."`. 

##### Custom Labels

You don't have to use thumbs up / thumbs down! Common custom label options include:
- ["👎", "👍"] (default)
- ["❌", "✅"]
- ["n", "y"]
- ["🙁", "😐", "🙂"]
- ["1", "2", "3", "4", "5"]

The convention is for ratings to go from least favorable to most favorable, from left to right.

By default the label furthest to the right (at the end of the list) will be set as the success metric, but you can set this with the `success` parameter.

##### Re-Running Evals

You can run the `.evals()` function multiple times on the same test, and the scores will continue to aggregate. This is helpful in case you get interrupted or lose your session. To do so, simply load the prior test results and run the function again.

```Python
filename = "thumb_test-abcd1234.csv"
test = thumb.load(filename)
test.evals()
```
##### Shareable Links

Shareable links rely on [Gradio's ability to share](https://www.gradio.app/guides/sharing-your-app) app demos for 72 hours, with the processing happening on your computer (so long as it stays on!). Every response is logged and saved locally on your computer (so long as you didn't set `save=False`), so you can continue to make multiple calls to `.eval()` until you're satisfied you have enough feedback. Each user is asked for a username which is appended to their rating data to join multiple sessions. When sharing is active, the results tab is disabled, and you must load the data with `thumb.load(filename)` in order to see the stats.

##### Prompt Formation

Prompts can be strings or arrays, and they can be Langchain prompt templates, chains or agents. When prompts are strings, they will be served as the user message for chat models. If you pass an array, the first message will be the `system` message, and following prompts in the array will be considered `user` and `ai` messages in alternating fashion (i.e. system, user, ai, user, ai, user... and so on). You may also pass the prompt as a dictionary, with a `name`, `hypothesis`, `control`, and `pid` (prompt id), to have this displayed in the Gradio web interface and in the exported CSV.

```Python
# set up a prompt templates for the a/b test
prompt_a = {
            "prompt": "tell me a joke", 
            "name": "simple",
            "hypothesis":"the simpler the better", 
            "control": True,
            "pid": "10001"
            }
prompt_b = {
            "prompt": "tell me a family friendly joke", 
            "name": "family",
            "hypothesis":"mentioning family makes jokes less offensive", 
            "control": False,
            "pid": "10002"
            }

# generate the responses
test = thumb.test([prompt_a, prompt_b])
```

##### Reference Answers

For more advanced evalution, it's possible to pass a reference answer to each test case, which represents a good quality response. This can be used in either manual evaluation as a guide, or automatic evaluation using an LLM, or embedding distance (the similarity between the response and the reference, lower is better).

```Python
# set up a prompt templates for the a/b test
prompt_a = "tell me a joke in the style of {comedian}"
prompt_b = "tell me a family friendly joke in the style of {comedian}"

# set test cases with different input variables
cases = [
  {"comedian": "chris rock"}, 
  {"comedian": "ricky gervais"}, 
  {"comedian": "robin williams"}
  ]

# set reference answers for each test case
references = [
  "You ever notice how WiFi signals are like relationships? At first, you got all bars. Strong connection. But go into the next room? Suddenly it's 'connection lost.' And just like that, your Netflix and chill turns into buffering and frustration!",
  "You know, I was at the zoo the other day, and I saw this sign: 'Do not feed the animals.' And I thought, 'Blimey! That's a bit harsh. They must be absolutely starving!' I mean, who's running this place, my old PE teacher? 'No lunch for you, lion, you missed the jump!'",
  "You know, the universe is a crazy place! If aliens ever land on Earth and ask to meet our leader, we'll probably just show them our Wi-Fi password and say, 'Good luck getting a signal up there!' Ha! The real final frontier is just getting two bars in my living room!"
  ]

# generate the responses
test = thumb.test([prompt_a, prompt_b], cases, references=references)
```

When passing references ensure they're in the same order as your test cases. When references are passed they are displayed above the response as a comparison guide for manual rating. They are also used as a guide for automatic rating by LLM, and the embedding distance is calculated as an additional performance metric. You can also pass a unique id with each test case (`cid`) and the same id with a reference, to associate them in any order.

##### Model Testing

You can pass multiple models in an array to the test parameter, in order to split test each prompt against each model. Models can be a string that refers to an OpenAI model, or a Langchain LLM or Chat model.

```Python
# set up a prompt templates for the a/b test
prompt_a = "tell me a joke"
prompt_b = "tell me a family friendly joke"

# generate the responses
test = thumb.test([prompt_a, prompt_b], models=["gpt-4", "gpt-3.5-turbo"])
```

### Running Web UI locally

Below are the step-by-step instructions for both Mac and Windows users to operate the provided scripts to run the Web UI for `thumb` locally:

#### Instructions for Mac Users:

##### Prerequisites:
1. Ensure you have Python3 installed. You can verify by typing `python3 --version` in the terminal. If not installed, you can get it from [Python's official website](https://www.python.org/downloads/mac-osx/).

##### Operating the `webui.sh` script:
1. Open the Terminal.
2. Navigate to the directory containing the `webui.sh` script using the `cd` command. For example, `cd path/to/directory`.
3. Make the script executable by running: `chmod +x webui.sh`.
4. Execute the script: `./webui.sh`.
5. The script will set up the necessary virtual environment, install required packages, and launch the Gradio app.
6. Once you're done using the app, close it and the terminal will indicate "Server closed."

#### Instructions for Windows Users:

##### Prerequisites:
1. Ensure you have Python installed. You can verify by typing `python --version` in the Command Prompt. If not installed, you can get it from [Python's official website](https://www.python.org/downloads/windows/). Make sure to check the box that says "Add Python to PATH" during installation.

##### Operating the `webui.bat` script:
1. Open Command Prompt (you can press `Windows + R`, type `cmd`, and hit Enter).
2. Navigate to the directory containing the `webui.bat` script using the `cd` command. For example, `cd path\to\directory`.
3. Execute the script by typing `webui.bat` and pressing Enter.
4. The script will set up the necessary virtual environment, install required packages, and launch the Gradio app.
5. Once you're done using the app, close it, and the Command Prompt will indicate "Server closed."

For both Mac and Windows users, the first time you run these scripts, they'll create a virtual environment and install the necessary libraries. The subsequent runs will use the already created environment unless you delete it.


## About Prompt Optimization

The difference between people just playing around with ChatGPT and those using AI in production is evaluation. LLMs respond non-deterministically, and so it's important to test what results look like when scaled up across a wide range of scenarios. Without an evaluation framework you're left blindly guessing about what's working in your prompts (or not).

Serious [prompt engineers](https://www.saxifrage.xyz/post/prompt-engineering) are testing and learning which inputs lead to useful or desired outputs, reliably and at scale. This process is called [prompt optimization](https://www.saxifrage.xyz/post/prompt-optimization), and the process looks like this:

1. Metrics – Establish how you'll measure the performance of the responses from the AI.
2. Hypothesis – Design one or more prompts that may work, based on the latest research.
3. Testing – Generate responses for your different prompts against multiple test cases.
4. Analysis – Evaluate the performance of your prompts and use them to inform the next test.

Thumb testing fills the gap between large scale professional evaluation mechanisms, and blindly prompting through trial and error. If you are transitioning a prompt into a production environment, using `thumb` to test your prompt can help you catch edge cases, and get early user or team feedback on the results.

## Contributors

These people are building `thumb` for fun in their spare time. Cheers! 🍻

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tr>
    <td align="center"><a href="https://twitter.com/hammer_mt"><img src="https://avatars.githubusercontent.com/u/5264596?s=96&v=4" width="100px;" alt=""/><br /><sub><b>hammer-mt</b></sub></a><br /><a href="https://github.com/hammer-mt/thumb/commits?author=hammer-mt" title="Code">💻</a></td>
    
  </tr>
</table>

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->
