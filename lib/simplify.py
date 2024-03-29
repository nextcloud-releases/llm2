"""A simplify chain
"""

from typing import Any, Optional

from langchain.base_language import BaseLanguageModel
from langchain.callbacks.manager import CallbackManagerForChainRun
from langchain.chains.base import Chain
from langchain.prompts import PromptTemplate
from langchain.schema.prompt_template import BasePromptTemplate
from langchain.text_splitter import CharacterTextSplitter
from pydantic import Extra


class SimplifyChain(Chain):
    """A summarization chain
    """

    prompt: BasePromptTemplate = PromptTemplate(
        input_variables=["text"],
        template="""
        Rewrite and rephrase the following text to make it easier to understand, so that a 5-year-old child can understand it.
        "
        {text}
        "
        Rewrite and rephrase the above text to make it easier to understand, so that a 5-year-old child can understand it. Describe difficult concepts in the text instead of using jargon terms directly. Do not make up anything new that is not in the original text. Only return the new, rewritten text.
        """,
    )

    """Prompt object to use."""
    llm: BaseLanguageModel
    output_key: str = "text"  #: :meta private:

    class Config:
        """Configuration for this pydantic object."""

        extra = Extra.forbid
        arbitrary_types_allowed = True

    @property
    def input_keys(self) -> list[str]:
        """Will be whatever keys the prompt expects.

        :meta private:
        """
        return [self.output_key]

    @property
    def output_keys(self) -> list[str]:
        """Will always return text key.

        :meta private:
        """
        return [self.output_key]

    def _call(
        self,
        inputs: dict[str, Any],
        run_manager: Optional[CallbackManagerForChainRun] = None,
    ) -> dict[str, str]:
        text_splitter = CharacterTextSplitter(
            separator="\n\n|\\.|\\?|\\!", chunk_size=1000, chunk_overlap=0, keep_separator=True
        )
        texts = text_splitter.split_text(inputs["text"])
        out = self.llm.generate_prompt([self.prompt.format_prompt(text=t) for t in texts])
        texts = [t[0].text for t in out.generations]

        return {self.output_key: "\n\n".join(texts)}

    @property
    def _chain_type(self) -> str:
        return "simplify_chain"
