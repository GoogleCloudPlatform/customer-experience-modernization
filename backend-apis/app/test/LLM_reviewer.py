import json
import os
import sys
from unittest.mock import MagicMock 
import tomllib
import unittest

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(SCRIPT_DIR, os.pardir))

from utils.utils_gemini import generate_gemini_pro_text

PROMPT = f"""
You are a reviewer, you read the given paragraph, and compare the paragraph with the new updated paragraph.
If the two paragraph are contextual similar, the publisher will replace the old paragraph with the updated one.

you rate by their simularity from 1 to 10.
The higher the rate the more similar these two paragraph are.
The updated paragraph is considered ready to release only when you give a rating greater than 7 
You should give a rating greater than 7 as long as the core message remains consistent.
If the core message remains the same, and the updated version gived more context, give a rating greater than 7.

Your response should be in the following JSON fomat:

"rating": rating score,
"reason": reason of the rating score
"old": old paragraph
"new": udpated paragraph


PARAGRAPH:
{{PARAGRAPH}}

UPDATED PARAGRAPH:
{{UPDATED_PARAGRAPH}}

Your rating:
"""

def rate(old_paragraph:str, new_paragraph:str) -> dict:
    rating = generate_gemini_pro_text(
        prompt = PROMPT.format(PARAGRAPH=old_paragraph, UPDATED_PARAGRAPH=new_paragraph)
    )
    print(rating)

    rating = rating.lstrip("```json")
    if "```" in rating:
        rating = rating[:rating.index("```") - 1]
    return json.loads(rating)