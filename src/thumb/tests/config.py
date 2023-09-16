# Global variables:
NUM_RUNS = 2

prompt_a = "tell me a joke"
prompt_b = "tell me a family friendly joke"

single_case_prompt_a = "tell me a joke in the style of {comedian}"
single_case_prompt_b = "tell me a family friendly joke in the style of {comedian}"
single_cases = [
    {"comedian": "chris rock"},
    {"comedian": "ricky gervais"},
    {"comedian": "robin williams"},
]

multiple_cases_prompt_a = "tell me a joke about {subject} in the style of {comedian}"
multiple_cases_prompt_b = (
    "tell me a family friendly joke about {subject} in the style of {comedian}"
)

multiple_cases = [
    {"subject": "joe biden", "comedian": "chris rock"},
    {"subject": "joe biden", "comedian": "ricky gervais"},
    {"subject": "donald trump", "comedian": "chris rock"},
    {"subject": "donald trump", "comedian": "ricky gervais"},
]
multiple_varying_cases = [
    {"subject": "joe biden", "comedian": "chris rock"},
    {"subject": "joe biden"},
]
