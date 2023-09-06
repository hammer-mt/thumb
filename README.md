# thumb

A simple prompt testing library for LLMs.

## Quick start

### 1. Install the library

> `pip install thumb`

### 2. Set up a test

```Python
import os
import thumb

# Set your API key: https://platform.openai.com/account/api-keys
os.environ["OPENAI_API_KEY"] = "YOUR_API_KEY_HERE"

# set up a prompt templates for the a/b test
prompt_a = "tell me a joke"
prompt_b = "tell me a family friendly joke"

# generate the responses
test = thumb.test([prompt_a, prompt_b])
```

### 3. Rate the responses

In Jupyter Notebooks a simple user interface is displayed for blind rating responses (you don't see which prompt generated the response).

![image](/img/thumb.png)

Once all responses have been rated, the following performance statistics are calculated broken down by prompt template:
- `avg_score` amount of positive feedback as a percentage of all runs
- `avg_tokens`: how many tokens were used across the prompt and response
- `avg_cost`: an estimate of how much the prompt cost to run on average

A simple report is displayed in the notebook, and the full data is saved to a CSV file `thumb/ThumbTest-{TestID}.csv`.

![image](/img/eval.png)

## Functionality

### Test cases

Test cases are when you want to test a prompt template with different input variables. For example, if you want to test a prompt template that includes a variable for a comedian's name, you can set up test cases for different comedians.

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

# generate the responses
test = thumb.test([prompt_a, prompt_b], cases)
```

Every test case will be run against every prompt template, so in this example you'll get 6 runs (3 test cases x 2 prompt templates). Every test case must include a value for each variable in the prompt template.

Prompts may have multiple variables in each test case. For example, if you want to test a prompt template that includes a variable for a comedian's name and a joke topic, you can set up test cases for different comedians and topics.

```Python
# set up a prompt templates for the a/b test
prompt_a = "tell me a joke about {subject} in the style of {comedian}"
prompt_b = "tell me a family friendly joke about {subject} in the style of {comedian}"

# set test cases with different input variables
cases = [
  {"subject": "joe biden", "comedian": "chris rock"}, 
  {"subject": "joe biden", "comedian": "ricky gervais"}, 
  {"subject": "joe biden", "comedian": "robin williams"},
  {"subject": "donald trump", "comedian": "chris rock"}, 
  {"subject": "donald trump", "comedian": "ricky gervais"}, 
  {"subject": "donald trump", "comedian": "robin williams"},
  ]

# generate the responses
test = thumb.test([prompt_a, prompt_b], cases)
```

Every case is tested against every prompt, in order to get a fair comparison of the performance of each prompt given the same input data.

### Model testing

```Python
# set up a prompt templates for the a/b test
prompt_a = "tell me a joke"
prompt_b = "tell me a family friendly joke"

# generate the responses
test = thumb.test([prompt_a, prompt_b], models=["gpt-4", "gpt-3.5-turbo"])
```

### Parameters

The `thumb.test` function takes the following parameters:

#### Required

- **prompts**: an array of prompts (strings) to be tested

#### Optional

- **cases**: a dictionary of variables to input into each prompt template (default: `None`)
- **runs**: the number of responses to generate per prompt and test case (default: `10`)
- **models**: a list of OpenAI models you want to generate responses from (default: [`gpt-3.5-turbo`])

If you have 10 test runs with 2 prompt templates and 3 test cases, that's `10 x 2 x 3 = 60` calls to your LLM. Be careful: these can add up quickly!

Langchain tracing to [LangSmith](https://smith.langchain.com/) is automatically enabled if the `LANGCHAIN_API_KEY` is set as an environment variable (optional).

### Loading and adding

the `.test()` function returns a `ThumbTest` object. You can add more prompts or cases to the test, or run it additional times. You can also generate, evaluate and export the test data at any time.

```Python
# set up a prompt templates for the a/b test
prompt_a = "tell me a joke"
prompt_b = "tell me a family friendly joke"

# generate the responses
test = thumb.test([prompt_a, prompt_b])

# add more prompts
test.add_prompts(["tell me a knock knock joke", "tell me a knock knock joke about {subject}"])

# add more cases
test.add_cases([{"subject": "joe biden"}, {"subject": "donald trump"}])

# run each prompt and case 5 more times
test.add_runs(5)

# generate the responses
test.generate()

# rate the responses
test.evaluate()

# export the test data for analysis
test.export_to_csv()
```

Every prompt template gets the same input data from every test case, but the prompt does not need to use all of the variables in the test case. As in the example above, the `tell me a knock knock joke` prompt does not use the `subject` variable, but it is still generated once (with no variables) for each test case.

Test data is cached in a local JSON file `thumb/.cache/{TestID}.json` after every set of runs is generated for a prompt and case combination.
If your test is interrupted, or you want to add to it, you can use the `thumb.load` function to load the test data from the cache.

```Python
# load a previous test
test_id = "abcd1234" # replace with your test id
test = thumb.load(f"thumb/.cache/{test_id}.json")

# run each prompt and case 2 more times
test.add_runs(2)

# generate the responses
test.generate()

# rate the responses
test.evaluate()

# export the test data for analysis
test.export_to_csv()
```
Every run for each combination of prompt and case is stored in the object (and cache), and therefore calling `test.generate()` again will not generate any new responses if more prompts, cases, or runs aren't added. Similarly, calling `test.evaluate()` again will not re-rate the responses you have already rated, and will simply redisplay the results if the test has ended.


## About Prompt Testing

The difference between people just playing around with ChatGPT and those using AI in production is evaluation. LLMs respond non-deterministically, and so it's important to test what results look like when scaled up across a wide range of scenarios. Without an evaluation framework you're left blindly guessing about what's working in your prompts (or not).

Serious [prompt engineers](https://www.saxifrage.xyz/post/prompt-engineering) are testing and learning which inputs lead to useful or desired outputs, reliably and at scale. This process is called [prompt optimization](https://www.saxifrage.xyz/post/prompt-optimization), and it looks like this:

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
