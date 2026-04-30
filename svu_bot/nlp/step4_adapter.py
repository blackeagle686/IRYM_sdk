class OutputAdapter:
    """Step 4: Handled by Member 4 of the NLP team."""
    @staticmethod
    def process(llm_output: str) -> str:
        if "program" in llm_output.lower():
            llm_output += "\n\n[Official Link]: https://www.svuonline.org/en/programs"
        return llm_output
