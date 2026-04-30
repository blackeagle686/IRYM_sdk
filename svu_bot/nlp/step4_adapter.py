"""
SVU BOT - NLP PIPELINE STEP 4: OUTPUT ADAPTER
=============================================
Purpose:
    This module is a post-generation processor. It takes the raw output from
    the AI and "adapts" it to match the university's communication standards.

Responsibilities (Member 4):
    1. Enrich text with useful administrative links based on the response content.
    2. Normalize tone or formatting if the AI becomes too informal.
    3. Inject mandatory footers or contact details for specific response types.

Returns:
    An enriched and formatted string ready for the end-user.
"""

class OutputAdapter:
    """Handled by Member 4 of the NLP team."""
    @staticmethod
    def process(llm_output: str) -> str:
        # If the bot mentions a program, ensure the official link is present
        if "program" in llm_output.lower():
            if "https://www.svuonline.org/en/programs" not in llm_output:
                llm_output += "\n\n[Official Link]: https://www.svuonline.org/en/programs"
        return llm_output
