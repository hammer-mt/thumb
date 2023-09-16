class PromptNotFoundError(Exception):
    """Raised when a prompt cannot be found."""

    pass


class VaryingCasesLengthError(Exception):
    """Raised when the number of cases is not equal across all of the cases provided."""

    pass
