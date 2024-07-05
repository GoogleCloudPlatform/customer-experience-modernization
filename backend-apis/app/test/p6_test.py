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


class Test_P6(unittest.TestCase):
    def __init__(self):
        pass
    # def test_generate_agent_activity(self):
    #     """
    #     test generate_agent_activity
    #     """
    #     print("*** generate_agent_activity ***")

    #     response_palm = generate_gemini_pro_text(
    #         prompt=config["field_service_agent"][
    #             "prompt_agent_activity"
    #         ].format(conversation)
    #     ).replace("</output>", "")
    #     print(response_palm)
    #     response = json.loads(response_palm)
    #     result = rate(old_paragraph=f"{PALM_RESULT_INSIGHT_MULTI_TURNS}",
    #          new_paragraph=insights)
    #     self.assertTrue(float(result['rating']) >= 7)
        

if __name__ == '__main__':
    unittest.main()