class InitModelAI:
    def __init__(self, provider: BaseLLMProvider):
        self.llm = provider.get_llm()
        self.analysis_chain = None

    def set_analysis_chain(self, prompt_chain):
        """Combine prompt with the LLM to create a full chain."""
        self.analysis_chain = prompt_chain | self.llm