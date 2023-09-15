from thumb.tests.config import (
    NUM_RUNS,
    prompt_a,
    prompt_b,
    single_case_prompt_a,
    single_case_prompt_b,
    multiple_cases_prompt_a,
    multiple_cases_prompt_b,
    single_cases,
    multiple_cases,
    multiple_varying_cases,
)
from collections import defaultdict
import thumb
from thumb.core import ThumbTest
from thumb.errors import PromptNotFoundError, VaryingCasesLengthError
import pytest


class ThumbTestGeneration:
    def test_if_no_prompt_is_provided(self):
        with pytest.raises(PromptNotFoundError):
            thumb.test(prompts=[])

    def test_if_multiple_cases_with_different_numbers_are_provided(self):
        with pytest.raises(VaryingCasesLengthError):
            thumb.test(
                prompts=[multiple_cases_prompt_a, multiple_cases_prompt_b],
                cases=multiple_varying_cases,
            )

    # # Conducts evaluation tests on the OpenAI API using default parameters:
    # def test_default_parameters(self):
    #     thumb = test([], async_generate=False)
    #     assert thumb.prompts == {}
    #     #
    #     assert thumb.cases == {"base-case": None}
    #     assert thumb.models == ["gpt-3.5-turbo"]
    #     assert thumb.runs == 10

    # # Conducts evaluation tests on the OpenAI API using custom parameters:
    # def test_custom_parameters(self):
    #     prompts = [
    #         "What is the capital of France?",
    #         "Who is the current president of the United States?",
    #     ]
    #     cases = [{"country": "France"}, {"country": "United States"}]
    #     runs = 2
    #     models = ["gpt-3.5-turbo"]
    #     async_generate = False

    #     thumb_test = thumb.test(prompts, cases, runs, models, async_generate)

    #     # The prompts and cases are hashed and stored in the prompts and cases, therefore, just look for the length of the prompts and cases keys instead:
    #     assert len(thumb.prompts) == 2
    #     assert len(thumb.cases) == 2

    #     assert thumb.models == ["gpt-3.5-turbo"]
    #     assert thumb.runs == 2

    # # Conducts evaluation test with default values.
    # def test_conducts_evaluation_test_with_default_values(self):
    #     thumb = test([], None, 10, ["gpt-3.5-turbo"], True)
    #     assert isinstance(thumb, ThumbTest)
    #     assert len(thumb.prompts) == 0
    #     assert len(thumb.cases) == 1
    #     assert thumb.runs == 10
    #     assert thumb.models == ["gpt-3.5-turbo"]

    # # Conducts evaluation test with multiple prompts and cases.
    # def test_conducts_evaluation_test_with_multiple_prompts_and_cases(self):
    #     prompts = [
    #         "What is the capital of France?",
    #         "Who is the current president of the United States?",
    #     ]
    #     cases = [{"country": "France"}, {"country": "United States"}]
    #     runs = 10
    #     models = ["gpt-3.5-turbo"]
    #     async_generate = True

    #     thumb = test(prompts, cases, runs, models, async_generate)

    #     assert thumb.prompts == {
    #         "e8b4e8a7": ["What is the capital of France?"],
    #         "f8b4e8a7": ["Who is the current president of the United States?"],
    #     }
    #     assert thumb.cases == {
    #         "base-case": None,
    #         "e8b4e8a7": {"country": "France"},
    #         "f8b4e8a7": {"country": "United States"},
    #     }
    #     assert thumb.models == ["gpt-3.5-turbo"]
    #     assert thumb.runs == 10

    # # Conducts evaluation tests on the OpenAI API with no prompts.
    # def test_no_prompts(self):
    #     thumb = test([], async_generate=False)
    #     assert thumb.prompts == {}
    #     assert thumb.cases == {"base-case": None}
    #     assert thumb.models == ["gpt-3.5-turbo"]
    #     assert thumb.runs == 10
    #     assert thumb.data == defaultdict(dict)

    # # Conducts evaluation tests on the OpenAI API with no cases.
    # def test_conducts_evaluation_tests_with_no_cases(self):
    #     prompts = [
    #         "What is the capital of France?",
    #         "Who is the current president of the United States?",
    #     ]
    #     cases = None
    #     runs = 10
    #     models = ["gpt-3.5-turbo"]
    #     async_generate = True

    #     thumb = test(prompts, cases, runs, models, async_generate)

    #     assert thumb.prompts == {
    #         "e8b4e8a7": ["What is the capital of France?"],
    #         "f6d2f6b1": ["Who is the current president of the United States?"],
    #     }
    #     assert thumb.cases == {"base-case": None}
    #     assert thumb.models == ["gpt-3.5-turbo"]
    #     assert thumb.runs == 10

    # # Conducts evaluation tests on the OpenAI API with no models.
    # def test_no_models(self):
    #     thumb = test(
    #         prompts=["What is the capital of France?"],
    #         cases=None,
    #         runs=10,
    #         models=[],
    #         async_generate=False,
    #     )
    #     assert thumb.models == []
    #     assert thumb.runs == 10
    #     assert len(thumb.prompts) == 1
    #     assert len(thumb.cases) == 1
    #     assert len(thumb.data) == 1
    #     assert len(thumb.data["prompt_1"]) == 1
    #     assert len(thumb.data["prompt_1"]["base-case"]) == 0
    #     assert thumb.data["prompt_1"]["base-case"] == {}

    # # Conducts evaluation tests on the OpenAI API with runs = 0.
    # def test_runs_zero(self):
    #     thumb = test(prompts=["What is the capital of France?"], runs=0)
    #     assert thumb.runs == 0
