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
from utils.utils_cloud_sql import convert_product_to_dict, Product
from utils.utils_imagen import annotate_image_names, run_image_captions, image_name_to_bytes

with open("app/config.toml", "rb") as f:
    config = tomllib.load(f)

GENERATE_TITLE_DESC_REQUEST = {"product_categories":["Rectangle","Grills","Grill","small","black","handle"],"context":"BBQ GRILL"}
PALM_RESULT_GENERATE_TITLE_DESCRIPTION = {
  "title": "Rectangle BBQ Grill: Small, Black, with Handle",
  "description": "This rectangle BBQ grill is the perfect addition to any outdoor cooking setup. Its compact size makes it ideal for small spaces, while its black color and sleek design add a touch of style to any patio or backyard. The grill is made of durable materials that can withstand high temperatures, and it features a convenient handle for easy transport. With this grill, you can enjoy delicious grilled food all summer long."
}
PALM_RESULT_DETECT_PRODUCT_CATAGORIES = {
    "vision_labels": [
        "Rectangle"
    ],
    "images_features": [
        "small",
        "black",
        "handle"
    ],
    "images_categories": [
        "Grills"
    ],
    "similar_products": [
        "504",
        "526"
    ]
}
# kalschi-csm-5-images/images/0-bbq-grill copy.png
class Test_P2(unittest.TestCase):
    def test_generate_title_description(self):
        """
        test generate_title_description()
        """
        print("*** get_reviews_summary ***")
        response = generate_gemini_pro_text(
            prompt=config["content_creation"][
                "prompt_title_description"
            ].format(GENERATE_TITLE_DESC_REQUEST["product_categories"], GENERATE_TITLE_DESC_REQUEST["context"]),
        )
        response = response.replace("</output>", "")
        response = response.replace("```json", "")
        response = response.replace("```", "")
        result = rate(old_paragraph=f"{PALM_RESULT_GENERATE_TITLE_DESCRIPTION}",
             new_paragraph=response)

        self.assertTrue(float(result['rating']) >= 7)

    def test_detect_product_categories(self):
      """
      test detect_product_categories()
      """
      print("*** detect_product_categories ***")
      images_names = ["0-bbq-grill copy.png"]
      vision_labels = annotate_image_names(images_names)
      images_bytes = [
          image_name_to_bytes(image_name)
          for image_name in images_names
      ]
      # Extract labels with Imagen Captioning
      imagen_captions = asyncio.run(
          run_image_captions(
              images_bytes=images_bytes,
          )
      )
      images_feat_cat = asyncio.run(
          run_predict_text_llm(
              prompts=[
                  config["content_creation"]["prompt_features"].format(
                      "\n".join(imagen_captions)
                  ),
                  config["content_creation"]["prompt_categories"].format(
                      "\n".join(imagen_captions)
                  ),
              ],
          )
      )
      images_feat_cat[0] = images_feat_cat[0].replace("</output>", "")
      images_feat_cat[0] = images_feat_cat[0].replace("```json", "")
      images_feat_cat[0] = images_feat_cat[0].replace("```", "")

      images_feat_cat[1] = images_feat_cat[1].replace("</output>", "")
      images_feat_cat[1] = images_feat_cat[1].replace("```json", "")
      images_feat_cat[1] = images_feat_cat[1].replace("```", "")

      images_features = json.loads(images_feat_cat[0])
      images_categories = json.loads(images_feat_cat[1])
      response = {
        "vision_labels": list(vision_labels),
        "images_features": images_features["product_features"],
        "images_categories": images_categories["product_categories"],
        "similar_products": [
            "504",
            "526"
        ]
      }
      result = rate(old_paragraph=f"{PALM_RESULT_DETECT_PRODUCT_CATAGORIES}",
           new_paragraph=response)

      self.assertTrue(float(result['rating']) >= 7)

if __name__ == '__main__':
    unittest.main()