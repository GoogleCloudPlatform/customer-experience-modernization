import json
import os
import sys
from unittest.mock import MagicMock 
from LLM_reviewer import rate

import tomllib
import unittest

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(SCRIPT_DIR, os.pardir))

from utils.utils_gemini import generate_gemini_pro_text
from utils.utils_cloud_sql import convert_product_to_dict, Product

with open("app/config.toml", "rb") as f:
    config = tomllib.load(f)

PRODUCT = Product()
PRODUCT.features = []
PRODUCT.categories = "Bath Robe"
PRODUCT.id = 1
PRODUCT.title = "White Cotton Robe - Feel relaxed and comfortable"
PRODUCT.description = "Our white cotton robe is the perfect way to relax and unwind after a long day. Made from 100% cotton, this robe is soft, breathable, and absorbent. It features a shawl collar, two front pockets, and a tie waist. This robe is available in one size and is suitable for both men and women.\n\nThis robe is perfect for lounging around the house, going to the spa, or getting ready for bed. It makes a great gift for yourself or someone special."
PRODUCT.image = "https://storage.googleapis.com/csm-dataset/products_images_dataset/dataset/Bath Robe/1/img2.png",
PRODUCT.price = 52
PRODUCT.quantity = 77

PRODUCT2 = Product()
PRODUCT2.features = []
PRODUCT2.categories = "Bath Robe"
PRODUCT2.id = 2
PRODUCT2.title = "White Cotton Robe"
PRODUCT2.description = "A luxurious, white cotton robe that is perfect for a relaxing day at home. This robe is made from 100% cotton and features a shawl collar, two patch pockets, and a self-tie belt. It is available in sizes S-XL.",
PRODUCT2.image = "https://storage.googleapis.com/csm-dataset/products_images_dataset/dataset/Bath Robe/1/img3.png",
PRODUCT2.price = 78.28
PRODUCT2.quantity = 59

REVIEWS = {
  "reviews": [
    {
      "review": " Hi Cymbal team!\n\nI recently purchased the White Cotton Robe and I'm really happy with it! It's super soft and comfortable, and it's perfect for relaxing after a long day. I love the shawl collar and the two front pockets, and the tie waist is really convenient. I've already washed it a few times and it's still holding up great.\n\nI would definitely recommend this robe to anyone looking for a comfortable and stylish way to relax. It's also a great gift idea!\n\nThanks,\n[Your Name]",
      "sentiment": "positive",
      "stars": 5
    },
    {
      "review": " The white cotton robe is soft and comfortable, but it is a bit thin and not very absorbent.",
      "sentiment": "neutral",
      "stars": 4
    },
    {
      "review": " As a long-time customer of Cymbal, I highly recommend their White Cotton Robe for its luxurious comfort and versatility, making it a must-have for relaxation and self-care.",
      "sentiment": "positive",
      "stars": 5
    },
    {
      "review": " Snuggle up in comfort and style with this soft, breathable, and absorbent 100% cotton robe, perfect for relaxation and self-care.",
      "sentiment": "positive",
      "stars": 5
    },
    {
      "review": " Indulge in ultimate comfort and relaxation with our luxurious white cotton robe, crafted from premium 100% cotton for a soft, breathable, and absorbent experience.",
      "sentiment": "positive",
      "stars": 4
    },
    {
      "review": " The white cotton robe is a comfortable and versatile choice for relaxation, made with soft and absorbent 100% cotton material, featuring a shawl collar, pockets, and a tie waist, suitable for both men and women.",
      "sentiment": "neutral",
      "stars": 3
    },
    {
      "review": " The white cotton robe is soft and comfortable, perfect for relaxing after a long day.",
      "sentiment": "neutral",
      "stars": 2
    },
    {
      "review": " The White Cotton Robe from Cymbal retailer is incredibly soft, comfortable, and perfect for unwinding after a long day.",
      "sentiment": "positive",
      "stars": 5
    },
    {
      "review": " As a long-time customer, I am disappointed with the poor quality of the White Cotton Robe.",
      "sentiment": "negative",
      "stars": 1
    },
    {
      "review": " This robe is not as soft as advertised and it shrank after the first wash.",
      "sentiment": "negative",
      "stars": 1
    }
  ]
}

PALM_RESULT_REVIEW_SUMMARY = "The White Cotton Robe from Cymbal has received mixed reviews from customers. While many reviewers praised its softness, comfort, and absorbency, others found it to be thin and not very absorbent. Some reviewers also mentioned that the robe shrank after washing. Overall, the robe seems to be a good choice for those looking for a comfortable and stylish robe for relaxation, but it may not be the best option for those looking for a highly absorbent robe."
PALM_RESULT_PRODUCT_SUMMARY = " **White Cotton Robe**\n\n- Material: 100% cotton\n- Features: shawl collar, two front pockets, tie waist\n- Size: one size fits all\n- Suitable for both men and women\n- Perfect for lounging, spa, or bedtime\n- Great gift idea\n\n**Price: $52.00**\n\n**Quantity: 77**"
PALM_REQUEST_COMPARISION = {"products":["{\"categories\":[\"Office Chair\"],\"id\":543,\"quantity\":15,\"price\":93.78,\"features\":[],\"title\":\"Ergonomic Office Chair - Gray\",\"image\":\"https://storage.googleapis.com/csm-dataset/products_images_dataset/dataset/Office Chair/images1/img3.png\",\"description\":\"Sit comfortably and work productively with this ergonomic office chair. The chair is made of high-quality materials and features a comfortable mesh back and seat. The chair is also adjustable, so you can find the perfect position for your body. \"}","{\"image\":\"https://storage.googleapis.com/csm-dataset/products_images_dataset/dataset/Office Chair/images1/img8.png\",\"id\":548,\"title\":\"Ergonomic Office Chair - Black\",\"price\":423.41,\"features\":[],\"description\":\"Sit comfortably and work productively with this ergonomic office chair. The chair is made of high-quality materials and features a comfortable mesh back and seat. It is also adjustable, so you can find the perfect position for your body. The chair is also easy to clean, so you can keep it looking its best for years to come.\\n\\nHere are some of the features of this ergonomic office chair:\\n\\n* Breathable mesh back and seat keep you cool and comfortable all day long\\n* Adjustable height and tilt let you find the perfect position for your body\\n* Durable construction ensures that the chair will last for years\\n* Easy to clean so you can keep it looking its best\\n\\nOrder your ergonomic office chair today and start working in comfort!\",\"quantity\":87,\"categories\":[\"Office Chair\"]}"]}
PALM_RESULT_COMPARISION = """
```html
<table>
<thead>
<tr>
<th>Feature</th>
<th>Ergonomic Office Chair - Gray</th>
<th>Ergonomic Office Chair - Black</th>
</tr>
</thead>
<tbody>
<tr>
<td>Ergonomic Design</td>
<td>✅</td>
<td>✅</td>
</tr>
<tr>
<td>Mesh Back and Seat</td>
<td>✅</td>
<td>✅</td>
</tr>
<tr>
<td>Adjustable Height</td>
<td>✅</td>
<td>✅</td>
</tr>
<tr>
<td>Adjustable Tilt</td>
<td>✅</td>
<td>✅</td>
</tr>
<tr>
<td>Easy to Clean</td>
<td>⛔️</td>
<td>✅</td>
</tr>
<tr>
<td>Breathable Material</td>
<td>⛔️</td>
<td>✅</td>
</tr>
<tr>
<td>Durable Construction</td>
<td>⛔️</td>
<td>✅</td>
</tr>
</tbody>
</table>
```
"""

class Test_P1(unittest.TestCase):
    def test_get_reviews_summary(self):
        """
        test get_reviews_summary()
        """
        print("*** get_reviews_summary ***")
        product_dict = convert_product_to_dict(PRODUCT)
        reviews_json = json.dumps(
                {
                    "product": product_dict,
                    "reviews": REVIEWS,
                }
            )
        summary = generate_gemini_pro_text(
            prompt=config["summary"]["prompt_reviews"].format(
                reviews=reviews_json
            ),
            max_output_tokens=1024,
            temperature=0.2,
            top_k=40,
            top_p=0.8,
        )

        result = rate(old_paragraph=PALM_RESULT_REVIEW_SUMMARY,
             new_paragraph=summary)

        self.assertTrue(float(result['rating']) >= 7)

    def test_get_product_summary(self):
        """
        test get_product_summary()
        """
        print("*** test_get_product_summary ***")
        product_dict = convert_product_to_dict(PRODUCT)
        product_json = json.dumps(product_dict)
        summary = generate_gemini_pro_text(
            prompt=config["summary"]["prompt_product"].format(
                product=product_json
            ),
            max_output_tokens=1024,
            temperature=0.2,
            top_k=40,
            top_p=0.8,
        )

        result = rate(old_paragraph=PALM_RESULT_PRODUCT_SUMMARY,
            new_paragraph=summary)

        self.assertTrue(float(result['rating']) >= 8)
    
    def test_compare_products(self):
        print("*** test_compare_products ***")
        comparison = generate_gemini_pro_text(
            prompt=config["compare"]["prompt_compare"].format(
                product_title_1="Ergonomic Office Chair - Gray",
                product_description_1="Sit comfortably and work productively with this ergonomic office chair. The chair is made of high-quality materials and features a comfortable mesh back and seat. The chair is also adjustable, so you can find the perfect position for your body.",
                product_title_2="Ergonomic Office Chair - Black",
                product_description_2="Sit comfortably and work productively with this ergonomic office chair. The chair is made of high-quality materials and features a comfortable mesh back and seat. It is also adjustable, so you can find the perfect position for your body. The chair is also easy to clean, so you can keep it looking its best for years to come.\\n\\nHere are some of the features of this ergonomic office chair:\\n\\n* Breathable mesh back and seat keep you cool and comfortable all day long\\n* Adjustable height and tilt let you find the perfect position for your body\\n* Durable construction ensures that the chair will last for years\\n* Easy to clean so you can keep it looking its best\\n\\nOrder your ergonomic office chair today and start working in comfort!"
            ),
            temperature=0.2,
            top_k=40,
            top_p=0.8
        )

        result = rate(old_paragraph=PALM_RESULT_COMPARISION,
            new_paragraph=comparison)
        print(result)
        self.assertTrue(float(result['rating']) >= 8)
if __name__ == '__main__':
    unittest.main()