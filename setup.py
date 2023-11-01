"""The setup script."""
import pathlib
from setuptools import setup, find_packages
HERE = pathlib.Path(__file__).parent
VERSION = "0.2.6"
PACKAGE_NAME = "thumb"
AUTHOR = "Mike Taylor"
AUTHOR_EMAIL = "mike@saxifrage.xyz"
URL = "https://github.com/hammer-mt/thumb"
LICENSE = "MIT"
DESCRIPTION = "A simple prompt testing library for LLMs."
LONG_DESCRIPTION = (HERE / "README.md").read_text(encoding='utf8')
LONG_DESC_TYPE = "text/markdown"
INSTALL_REQUIRES = [
    "gradio",
    "langchain",
    "ipython",
    "ipywidgets",
    "openai",
]
setup(name=PACKAGE_NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type=LONG_DESC_TYPE,
    author=AUTHOR,
    license=LICENSE,
    author_email=AUTHOR_EMAIL,
    url=URL,
    install_requires=INSTALL_REQUIRES,
    package_dir={"": "src"},
    packages=find_packages(where="src")
    )