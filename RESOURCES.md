# Resources
Here is a list of helpful resources and tools we found while building `thumb`, or were sent after releasing the library. As our tool is open-source we might not be the right solution for your company, and therefore we've linked to every other prompt optimization tool we have found in case you want to review them. If you have any suggestions for additions, please [open an issue](/CONTRIBUTING.md). 


## Content Featuring `thumb`
- [Prompt Experiment: AI Writing Styles](https://www.saxifrage.xyz/post/ai-writing-style-prompt-experiment) - a prompt experiment using `thumb` to test different writing styles to make AI-generated content sound more human.
- [ChatGPT doesn’t respect wordcount](https://www.saxifrage.xyz/post/chatgpt-wordcount) - a test of whether ChatGPT obeys a stated wordcount in the prompt (it doesn't).

## Prompt Testing & Optimization Content
- [Prompt Engineering vs. Blind Prompting](https://mitchellh.com/writing/prompt-engineering-vs-blind-prompting) - makes the distinction between trial and error and proper testing.
- [Building LLM applications for production](https://huyenchip.com/2023/04/11/llm-engineering.html) - strong overview of the common problems with LLMs in production and the importance of testing.
- [Prompt Engineering](https://lilianweng.github.io/posts/2023-03-15-prompt-engineering/) - covers much of the important literature on prompt engineering.
- [OpenAI Best Practices](https://platform.openai.com/docs/guides/gpt-best-practices/strategy-test-changes-systematically) - They specifically recommend testing changes systematically.
- [Prompt Engineering](https://www.saxifrage.xyz/post/prompt-engineering) - Covers the five principles of prompting, one of which is 'Evaluate Quality'.
- [Prompt Optimization](https://www.saxifrage.xyz/post/prompt-optimization) - Covers the process of testing and optimizing prompts, and why it's important / valuable.
- [LangSmith Cookbook](https://github.com/langchain-ai/langsmith-cookbook/tree/main) - all about testing and evaluation in Langchain, logged to LangSmith.
- [Learn Prompting](https://learnprompting.org/) - a course for prompt engineering with lots of good references to papers.
- [Promptgen](https://github.com/AUTOMATIC1111/stable-diffusion-webui-promptgen) - An extension for webui that lets you generate prompts.
- [MagicPrompt - Stable Diffusion](https://huggingface.co/Gustavosta/MagicPrompt-Stable-Diffusion) - a GPT-2 model trained on Stable Diffusion prompts from Lexica.art, for generating prompts.
- [Lexica.art](https://lexica.art/) - a collection of prompt templates for image models.
- [The Complete Prompt Engineering for AI Bootcamp (2023)](https://www.udemy.com/course/prompt-engineering-for-ai/) ($) - a comprehensive course on prompt engineering based on the five principles of prompting.
- [Working with feedback](https://docs.smith.langchain.com/evaluation/capturing-feedback) - Langchain's documentation on evaluators is helpful.
- [Prompt Engineering Guide](https://www.promptingguide.ai/techniques/ape) - talks about Automatic Prompt Engineer (APE) and a number of other techniques.
- [Prompt engineering for Claude's long context window](https://www.anthropic.com/index/prompting-long-context) - how to test RAG architecture and retrieval with long context windwows.
- [Exploring zephyr-7b-alpha Through the Lens of Evaluation Driven Development](https://levelup.gitconnected.com/exploring-zephyr-7b-alpha-through-the-lens-of-evaluation-driven-development-faf69e9d9ec7) – a good example of how to use evaluation driven development to test a new model.
- [Evaluation Driven Development, the Swiss Army Knife for RAG Pipelines](https://levelup.gitconnected.com/evaluation-driven-development-the-swiss-army-knife-for-rag-pipelines-dba24218d47e) – a big push in the general movement towards Eval-Driven Development.
- [“Optimization by Prompting” for RAG](https://docs.llamaindex.ai/en/latest/examples/prompts/prompt_optimization.html) – cool way of optimizing your RAG prompts automatically.

## Prompt Testing & Optimization Tools
- [Prompts Royale](https://promptsroyale.com/) - a browser-based interface for generating prompts and testing them head-to-head.
- [gpt-prompt-engineer](https://github.com/mshumer/gpt-prompt-engineer) - automated prompt generation and elo rating.
- [PromptPerfect](https://promptperfect.jina.ai/) ($) - automated prompt engineering.
- [👨🏻‍🎤 ChatGPT Prompt Generator 👨🏻‍🎤](https://huggingface.co/spaces/merve/ChatGPT-prompt-generator) - a BART model trained to write ChatGPT prompts.
- [AnyAPI](https://anyapi.netlify.app/) - A/B testing of prompts
- [AI Tuner](https://www.pulseinsights.com/ai-tuner) ($) - collect feedback from clients for optimization.
- [Rompt](https://rompt.ai/) - prompt experimentation tool
- [Prompt Wrangler](https://prompt-wrangler.com/) - turn prompts into structured APIs
- [Auto-Evaluator](https://autoevaluator.langchain.com/) - Langchain tool for evaluating retrieval chains.
- [RAGAS](https://github.com/explodinggradients/ragas) - Evaluation framework for your Retrieval Augmented Generation (RAG) pipelines
- [HumanLoop](https://humanloop.com/) ($) - collaborative prompt and ml ops workspace.
- [OpenAI Evals](https://github.com/openai/evals) - evaluation framework for models and prompts.
- [Prompt Layer](https://promptlayer.com/) ($) - a tool for visually managing prompt templates and tracking usage.
- [Promptfoo](https://github.com/promptfoo/promptfoo) - a tool for testing and evaluating LLM outputs.
- [LangSmith](https://smith.langchain.com/) - the Langchain tracing and monitoring tool.
- [Weights & Biases](https://wandb.ai/site/) ($) - a general purpose ML monitoring tool.
- [Portkey](https://portkey.ai/) ($) - Logging and tracing of prompt chains.
- [Freeplay](https://freeplay.ai/blog/introducing-freeplay-prompt-engineering-tools-for-product-teams) ($) - Prompt engineering, testing & evaluation tools for product teams.
- [SpaCy Annotator](https://github.com/ieriii/spacy-annotator) - an open source tool for annotating text data.
- [LLama Index Evaluation)[https://gpt-index.readthedocs.io/en/v0.7.2/how_to/evaluation/evaluation.html] – Evaluation library for LLMs.

## Prompt Engineering Papers
- [Large Language Models Are Human-Level Prompt Engineers](https://arxiv.org/abs/2211.01910) - shows that AI models are good at writing prompts for themselves (meta prompting).
- [Re3: Generating Longer Stories With Recursive Reprompting and Revision](https://arxiv.org/abs/2210.06774) - good system for generating longform coherent content.
- [ChatGPT is fun, but it is not funny! Humor is still challenging Large Language Models](https://arxiv.org/abs/2306.04563) - 90% of jokes generated by ChatGPT are duplicates.
- [Language Models are Few-Shot Learners](https://arxiv.org/pdf/2005.14165.pdf) - The GPT-3 paper. Demonstrates the value of prompting and providing examples (shots) vs fine-tuning.
- [Training language models to follow instructions with human feedback](https://arxiv.org/pdf/2203.02155.pdf) - The RLHF paper. Dig into the labeler selection process and performance metrics.
- [Large Language Models are not Fair Evaluators](https://arxiv.org/abs/2305.17926) - casts doubt on the ability of LLMs to evaluate their own performance, as is done in some prompt optimization tools.
- [Calibrate Before Use: Improving Few-Shot Performance of Language Models](https://arxiv.org/abs/2102.09690) - shows the ordering of examples and various other factors make a big difference to the results.
- [What Makes Good In-Context Examples for GPT-3?](https://arxiv.org/abs/2101.06804) - retrieving examples that are semantically similar to the task is important for performance.
- [Fantastically Ordered Prompts and Where to Find Them: Overcoming Few-Shot Prompt Order Sensitivity](https://arxiv.org/abs/2104.08786) - testing the ordering of examples in prompts.
- [AutoPrompt: Eliciting Knowledge from Language Models with Automatically Generated Prompts](https://arxiv.org/abs/2010.15980) - a method for automatically generating prompts.
- [Prefix-Tuning: Optimizing Continuous Prompts for Generation](https://arxiv.org/abs/2101.00190) - a lightweight way to fine-tune prompts instead of model weights.
- [The Power of Scale for Parameter-Efficient Prompt Tuning](https://arxiv.org/abs/2104.08691) - 
- [How Many Data Points is a Prompt Worth?](https://arxiv.org/abs/2103.08493) - shows you need a few hundred to thousands of data points for fine-tuning to beat prompt engineering.
- [The Power of Scale for Parameter-Efficient Prompt Tuning](https://arxiv.org/abs/2104.08691) - automatic tuning of prompts based on a goal.
- [Large Language Models as Optimizers](https://arxiv.org/abs/2309.03409) - claims that LLMs are better prompt engineers than people.
- [SDXL: Improving Latent Diffusion Models for High-Resolution Image Synthesis](https://arxiv.org/abs/2307.01952) - a good example of how to evaluate image models.
- [Can large language models provide useful feedback on research papers? A large-scale empirical analysis.](https://arxiv.org/pdf/2310.01783.pdf) - shows that human peer reviewers agree with GPT-4 as much as they agree with each other.


## Collections of Prompts
- [Awesome ChatGPT Prompts](https://github.com/f/awesome-chatgpt-prompts) - role-based prompts for ChatGPT for various use cases.
- [Langchain Hub](https://smith.langchain.com/hub?page=1) - a home for uploading, browsing, pulling, and managing your prompts.
- [McKay's Prompts](https://github.com/mckaywrigley/prompts/tree/main) - McKay Wrigley's prompts for software development workflows.
- [AIPRM](https://www.aiprm.com/prompts/) – a chrome extension with a built in prompt library.