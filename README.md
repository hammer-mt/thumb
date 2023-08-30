# thumb

A simple prompt testing library for LLMs.

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
- **runs**: the number of responses to generate per prompt and test case (default: `10`)
- **models**: a list of OpenAI models you want to generate responses from (default: [`gpt-3.5-turbo`])

If you include variables in your prompt templates (i.e. `{variable}`) you must provide corresponding test cases, otherwise this field is not required. Remember to include a value in your test case for each variable in your template.

If you have 10 test runs with 2 prompt templates and 3 test cases, that's `10 x 2 x 3 = 60` calls to your LLM. Be careful: these can add up quickly!

Langchain tracing to [LangSmith](https://smith.langchain.com/) is automatically enabled if the `LANGCHAIN_API_KEY` is set as an environment variable (optional).

### 3. Rate the responses

When you run a `thumb` test in jupyter notebook, a simple ipython user interface spins up, and you are given a URL to visit to rate each response. Each combination of prompt template and test case is displayed in a random order for blind rating (you don't see which prompt template, just the response) so you do not bias the results. 

Once all responses have been rated, the following performance statistics are calculated broken down by prompt template and test case:
- `score` amount of positive feedback as a percentage of all runs
- `tokens`: how many tokens were used across the prompt and response


## About Prompt Optimization

The difference between people just playing around with ChatGPT and those using AI in production is evaluation. LLMs respond non-deterministically, and so it's important to test what results look like when scaled up across a wide range of scenarios. Without an evaluation framework you're left blindly guessing about what's working in your prompts (or not).

Serious [prompt engineers](https://www.saxifrage.xyz/post/prompt-engineering) are testing and learning which inputs lead to useful or desired outputs, reliably and at scale. This process is called [prompt optimization](https://www.saxifrage.xyz/post/prompt-optimization), and the process looks like this:

1. Metrics – Establish how you'll measure the performance of the responses from the AI.
2. Hypothesis – Design one or more prompts that may work, based on the latest research.
3. Testing – Generate responses for your different prompts against multiple test cases.
4. Analysis – Evaluate the performance of your prompts and use them to inform the next test.

Thumb testing fills the gap between large scale professional evaluation mechanisms, and blindly prompting through trial and error. If you are transitioning a prompt into a production environment, using `thumb` to test your prompt can help you catch edge cases, and get early user or team feedback on the results.

## Contributors

These people are building `thumb` for fun in their spare time. 👍

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
