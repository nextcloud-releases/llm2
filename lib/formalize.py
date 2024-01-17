from typing import List, Dict, Any, Optional
from langchain.base_language import BaseLanguageModel
from langchain.schema.prompt_template import BasePromptTemplate
from langchain.prompts import PromptTemplate
from langchain.callbacks.manager import CallbackManagerForChainRun
from langchain.text_splitter import CharacterTextSplitter
from langchain.chains.base import Chain
from pydantic import Extra


class FormalizeChain(Chain):
    """
    A formalize chain
    """

    prompt: BasePromptTemplate = PromptTemplate(
        input_variables=["text"],
        template="""
        Rewrite the following text and rephrase it to use only formal language and be very polite:
        "
        {text}
        "
        Write the above text again, rephrase it to use only formal language and be very polite.
        """
    )

    """Prompt object to use."""
    llm: BaseLanguageModel
    output_key: str = "text"  #: :meta private:

    class Config:
        """Configuration for this pydantic object."""

        extra = Extra.forbid
        arbitrary_types_allowed = True

    @property
    def input_keys(self) -> List[str]:
        """Will be whatever keys the prompt expects.

        :meta private:
        """
        return [self.output_key]

    @property
    def output_keys(self) -> List[str]:
        """Will always return text key.

        :meta private:
        """
        return [self.output_key]

    def _call(
            self,
            inputs: Dict[str, Any],
            run_manager: Optional[CallbackManagerForChainRun] = None,
    ) -> Dict[str, str]:
        text_splitter = CharacterTextSplitter(
            separator='\n\n|\\.|\\?|\\!', chunk_size=1000, chunk_overlap=0, keep_separator=True)
        texts = text_splitter.split_text(inputs['text'])
        out = self.llm.generate_prompt([self.prompt.format_prompt(text=t) for t in texts])
        texts = [t[0].text for t in out.generations]

        return {self.output_key: '\n\n'.join(texts)}

    @property
    def _chain_type(self) -> str:
        return "simplify_chain"