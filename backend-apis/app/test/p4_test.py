import asyncio
import json
import os
import sys
from unittest.mock import MagicMock 
from LLM_reviewer import rate

import tomllib
import unittest

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(SCRIPT_DIR, os.pardir))

from utils.utils_gemini import generate_gemini_pro_text, run_predict_text_llm

with open("app/config.toml", "rb") as f:
    config = tomllib.load(f)

PALM_RESULT_REPHRASE_TEXT = {
  "rephrase_text_output": " \"Hello, my name is Michael. I'm here to assist you. How can I make your experience better today?\""
}
PALM_RESULT_CONVERSATION_SUMMARY_AND_TITLE = {
  "summary": " **Summary of the conversation:** The conversation is between a call center agent and a customer of an online furniture store. The customer reported that the back of their chair is broken and they want to return it. The agent responded with safety instructions and advised the customer to contact customer service immediately. The customer then asked for more specific details on the return process. **What went well:** - The agent responded promptly to the customer's messages. - The agent provided safety instructions to the customer. - The agent was polite and used a friendly tone. **What can be improved:** - The agent could have provided more specific details on the return process when the customer asked for it. - The agent could have offered to initiate the return process for the customer. **Pending tasks:** - The customer needs to contact customer service to initiate the return process. - The agent needs to provide the customer with more specific details on the return process.",
  "title": "Broken Chair Issue"
}
PALM_RESULT_AUTO_SUGGEST_AND_QUERY = "Find information about chair back replacement for online furniture store."
CONVERSATION_SUMMARY_AND_TITLE_MESSAGES = [
{
    "author": "User",
    "language": "zh-TW",
    "sentiment_magnitude": 0.800000011920929,
    "sentiment_score": 0.800000011920929,
    "text": "椅背壞掉了",
    "timestamp": "April 2, 2024 at 12:22:52 PM UTC+8"
},
{
    "author": "Agent",
    "language": "en-US",
    "sentiment_magnitude": 1.100000023841858,
    "sentiment_score": -0.20000000298023224,
    "text":"If the back of your chair is broken, you should not use it until it has been repaired. Keep the chair away from open flames and other heat sources. [4] You should also contact customer service immediately. [2, 3]",
    "timestamp": "April 2, 2024 at 12:23:31 PM UTC+8"
},
{
    "author": "Agent",
    "language": "en-US",
    "sentiment_magnitude":1.5,
    "sentiment_score": 0.20000000298023224,
    "text":" Certainly! Please provide me with more specific details or questions so that I can assist you better. I'm here to help and ensure your satisfaction.",
    "timestamp": "April 2, 2024 at 12:22:37 PM UTC+8"
},
{
    "author": "User",
    "language": "en-US",
    "sentiment_magnitude": 0.6000000238418579,
    "sentiment_score": -0.6000000238418579,
    "text": "my chair back is broken",
    "timestamp": "April 2, 2024 at 12:22:05 PM UTC+8"
},
{
    "author": "User",
    "language": "en-US",
    "sentiment_magnitude": 0.800000011920929,
    "sentiment_score": -0.800000011920929,
    "text": "my chair back is broken",
    "timestamp": "April 2, 2024 at 12:22:05 PM UTC+8"
}
]

chat_summarize_prompt_template = config["salesforce"][
    "chat_summarize_prompt_template"
]


chat_title_prompt_template = config["salesforce"]["chat_title_prompt_template"]


class Test_P4(unittest.TestCase):
    def test_rephrase_text(self):
        """
        test rephrase_text()
        """
        print("*** rephrase_text ***")
        rephrase_prompt_template = config["salesforce"]["rephrase_prompt_template"]

        llm_response = generate_gemini_pro_text(
        prompt=rephrase_prompt_template.format("My name is Michael, How may I help you")
    )
        result = rate(old_paragraph=f"{PALM_RESULT_REPHRASE_TEXT}",
             new_paragraph=llm_response)

        self.assertTrue(float(result['rating']) >= 7)

    def test_conversation_summary_and_title(self):
        """
        test conversation_summary_and_title()
        """
        # USER_ID = "nbL7Z6QGD0Nmc10l9e79pGDbaNo1"
        # CONVERSATION_ID = "Lth1D2CFSirkd4Z7Bnts"
        print("*** conversation_summary_and_title ***")
        summary = "Empty conversation."
        title = "Empty conversation."
        conversation_str = json.dumps(
                {"messages": CONVERSATION_SUMMARY_AND_TITLE_MESSAGES},
                default=str,
            )

        summary, title = asyncio.run(
                run_predict_text_llm(
                    prompts=[
                        chat_summarize_prompt_template.format(
                            conversation_str
                        ),
                        chat_title_prompt_template.format(conversation_str),
                    ]
                )
            )

        if not summary:
            summary = "Closed case"
        if not title:
            title = "Closed case"
        print(f"""
=====> chat_summarize <======
{summary}
=============================
               """)
        result = rate(old_paragraph=PALM_RESULT_CONVERSATION_SUMMARY_AND_TITLE["summary"],
             new_paragraph=summary)
        self.assertTrue(float(result['rating']) >= 7)

        result = rate(old_paragraph=PALM_RESULT_CONVERSATION_SUMMARY_AND_TITLE["title"],
             new_paragraph=summary)
        print(f">>>{result}<<<")
        self.assertTrue(float(result['rating']) >= 7)

    def test_auto_suggest_query_text(self):
        """
        test auto_suggest_query_text()
        """
        print("*** test_auto_suggest_query_text ***")
        input_text = "Hello, my chair back is broken"
        auto_suggest_prompt_template = config["salesforce"]["auto_suggest_prompt_template"]

        llm_response = ""

        try:
            llm_response = generate_gemini_pro_text(
                prompt=auto_suggest_prompt_template.format(input_text)
            )
        except:
            llm_response = "No suggestions for now"

        result = rate(old_paragraph=PALM_RESULT_AUTO_SUGGEST_AND_QUERY,
             new_paragraph=llm_response)

        self.assertTrue(float(result['rating']) >= 7)
 
if __name__ == '__main__':
    unittest.main()