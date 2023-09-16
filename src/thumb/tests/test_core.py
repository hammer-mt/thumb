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
import thumb
from thumb.errors import PromptNotFoundError, VaryingCasesLengthError
import pytest


class TestErrorHandling:
    # @pytest.mark.skip(reason="This test is currently being debugged."
    def test_if_no_prompt_is_provided(self):
        with pytest.raises(PromptNotFoundError):
            thumb.test(prompts=[])

    def test_if_multiple_cases_with_different_numbers_are_provided(self):
        with pytest.raises(VaryingCasesLengthError):
            thumb.test(
                prompts=[multiple_cases_prompt_a, multiple_cases_prompt_b],
                cases=multiple_varying_cases,
            )


class TestThumbTestGeneration:
    """White integration box parameterized texts for:
    - synchronous/asynchronous generation:
    - single/multiple/no cases
    """

    @pytest.mark.parametrize("async_generate", [True, False])
    @pytest.mark.parametrize(
        "prompts, cases",
        [
            ([prompt_a, prompt_b], []),
            ([single_case_prompt_a, single_case_prompt_b], single_cases),
            ([multiple_cases_prompt_a, multiple_cases_prompt_b], multiple_cases),
        ],
    )
    # TODO - Make this test async, rather than solely using @pytest.mark.parametrize
    async def test_if_thumbtest_is_generated_with_single_multiple_and_no_cases_both_async_and_sync(
        self, async_generate, prompts, cases
    ):
        thumb_test = await thumb.test(
            prompts=prompts, runs=NUM_RUNS, async_generate=async_generate, cases=cases
        )
        assert isinstance(thumb_test, thumb.core.ThumbTest)
        # TODO: Add more assertions here.
