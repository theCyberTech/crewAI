import os

import pytest
from crewai.utilities.i18n import I18N


PROMPT_FILE = os.path.join(os.path.dirname(__file__), "prompts.json")


def test_load_prompts():
    i18n = I18N()
    i18n.load_prompts()
    role_playing = i18n.slice("role_playing")
    for placeholder in ("{role}", "{backstory}", "{goal}"):
        assert placeholder in role_playing


def test_slice():
    i18n = I18N(prompt_file=PROMPT_FILE)
    i18n.load_prompts()
    assert i18n.slice("role_playing") == "Lorem ipsum dolor sit amet"


def test_tools():
    i18n = I18N(prompt_file=PROMPT_FILE)
    i18n.load_prompts()
    assert i18n.tools("ask_question") == "Lorem ipsum dolor sit amet"


def test_retrieve():
    i18n = I18N(prompt_file=PROMPT_FILE)
    i18n.load_prompts()
    assert i18n.retrieve("slices", "getting_input") == "Lorem ipsum dolor sit amet "


def test_retrieve_not_found():
    i18n = I18N()
    i18n.load_prompts()
    with pytest.raises(
        Exception, match="Prompt for 'nonexistent_kind':'nonexistent_key'"
    ):
        i18n.retrieve("nonexistent_kind", "nonexistent_key")


def test_prompt_file():
    i18n = I18N(prompt_file=PROMPT_FILE)
    i18n.load_prompts()
    assert isinstance(i18n.retrieve("slices", "role_playing"), str)
    assert i18n.retrieve("slices", "role_playing") == "Lorem ipsum dolor sit amet"
