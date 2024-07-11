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


CONVERSATIONS_MULTI_TURNS = """
 **Customer**: Hi there! I recently placed an order for the Stealth Gaming Chair and I'm wondering if you could give me an update on the status of my order?

**Agent**: Hello! Thank you for reaching out. Let me check on that for you. Could you please provide me with your order number?

**Customer**: Sure, my order number is #123456789.

**Agent**: Thank you. I see that your order is currently in production and is expected to ship within the next 5-7 business days. You will receive an email with tracking information once your order has been shipped.

**Customer**: Great! I'm also interested in any upcoming promotions or discounts that you might have. Are there any sales or coupons available for the Stealth Gaming Chair or other products in your store?

**Agent**: We do have a few promotions running at the moment. There's a 15% discount on all gaming chairs, including the Stealth Gaming Chair, when you use the code "CYMBAL15" at checkout. Additionally, if you sign up for our email newsletter, you'll be the first to know about any future promotions and exclusive offers.

**Customer**: That's awesome! I'll definitely use the code and sign up for the newsletter. By the way, I noticed that the product description for the Stealth Gaming Chair mentions a high-density foam seat and backrest. Can you tell me more about the materials used in the chair?

**Agent**: Absolutely! The Stealth Gaming Chair is made with premium materials to ensure maximum comfort and durability. The seat and backrest are constructed with high-density foam that provides excellent support and conforms to your body shape. The chair is also upholstered in a breathable fabric that keeps you cool and comfortable during long gaming sessions.

**Customer**: That sounds really comfortable. I think I made the right choice in choosing the Stealth Gaming Chair. Thanks for all the information and assistance!

**Agent**: You're very welcome! I'm glad I could help. If you have any further questions or concerns, please don't hesitate to reach out. We're here to assist you.

**Customer**: Okay, thank you! Have a great day!

**Agent**: You too! Take care and enjoy your new gaming chair
"""
CONVERSATIONS = {
            "conversations": [
                {
                    "sentiment": "positive",
                    "agent_id": "15",
                    "description": "Get ready to dominate the competition with the new Stealth Gaming Chair. This chair is designed for gamers who demand the best in comfort and style. With its sleek design and vibrant colors, the Stealth Gaming Chair will make you stand out from the crowd. The chair is also incredibly comfortable, with a high-density foam seat and backrest that will keep you supported during even the longest gaming sessions. And with its adjustable height and tilt, you can find the perfect position for your gaming needs. So take your gaming to the next level with the Stealth Gaming Chair.",
                    "customer_id": "1",
                    "agent_email": "Ashley@customerservices.agents",
                    "product_id": "558",
                    "category": "Office Chair",
                    "rating": "5",
                    "title": "Stealth Gaming Chair",
                    "customer_email": "user9735@sample_user9735.sample",
                    "status": "not resolved",
                    "conversation": " **Customer**: Hi there! I recently placed an order for the Stealth Gaming Chair and I'm wondering if you could give me an update on the status of my order?\n\n**Agent**: Hello! Thank you for reaching out. Let me check on that for you. Could you please provide me with your order number?\n\n**Customer**: Sure, my order number is #123456789.\n\n**Agent**: Thank you. I see that your order is currently in production and is expected to ship within the next 5-7 business days. You will receive an email with tracking information once your order has been shipped.\n\n**Customer**: Great! I'm also interested in any upcoming promotions or discounts that you might have. Are there any sales or coupons available for the Stealth Gaming Chair or other products in your store?\n\n**Agent**: We do have a few promotions running at the moment. There's a 15% discount on all gaming chairs, including the Stealth Gaming Chair, when you use the code \"CYMBAL15\" at checkout. Additionally, if you sign up for our email newsletter, you'll be the first to know about any future promotions and exclusive offers.\n\n**Customer**: That's awesome! I'll definitely use the code and sign up for the newsletter. By the way, I noticed that the product description for the Stealth Gaming Chair mentions a high-density foam seat and backrest. Can you tell me more about the materials used in the chair?\n\n**Agent**: Absolutely! The Stealth Gaming Chair is made with premium materials to ensure maximum comfort and durability. The seat and backrest are constructed with high-density foam that provides excellent support and conforms to your body shape. The chair is also upholstered in a breathable fabric that keeps you cool and comfortable during long gaming sessions.\n\n**Customer**: That sounds really comfortable. I think I made the right choice in choosing the Stealth Gaming Chair. Thanks for all the information and assistance!\n\n**Agent**: You're very welcome! I'm glad I could help. If you have any further questions or concerns, please don't hesitate to reach out. We're here to assist you.\n\n**Customer**: Okay, thank you! Have a great day!\n\n**Agent**: You too! Take care and enjoy your new gaming chair"
                },
                {
                    "sentiment": "positive",
                    "agent_id": "17",
                    "description": "The Ergonomic Office Chair is the perfect addition to any home or office. With its sleek design and comfortable cushioning, this chair will provide you with the support and comfort you need to stay productive throughout your day. The chair is made of high-quality materials that are built to last, and it features a variety of adjustable settings so you can find the perfect position for your body. Whether you're working on a project at your desk or just relaxing in your living room, the Ergonomic Office Chair is the perfect way to unwind and get comfortable.",
                    "customer_id": "1",
                    "agent_email": "Emily@customerservices.agents",
                    "product_id": "615",
                    "category": "Office Chair",
                    "rating": "4",
                    "title": "Ergonomic Office Chair - Blue",
                    "customer_email": "user9735@sample_user9735.sample",
                    "status": "not resolved",
                    "conversation": " **Customer**: Hi there! I recently placed an order for the Ergonomic Office Chair in blue and I'm wondering if you could give me an update on the status of my order?\n\n**Support Agent**: Hello! Thank you for reaching out. Let me check the status of your order. Could you please provide me with your order number?\n\n**Customer**: Sure, my order number is #123456789.\n\n**Support Agent**: Thank you for providing your order number. Let me pull up your order details. It seems that your order is currently in production and is expected to be shipped out within the next 3-5 business days.\n\n**Customer**: Okay, that's great to hear. I'm also interested in any upcoming promotions or discounts that Cymbal Furniture might be offering. Are there any sales or special offers that I should be aware of?\n\n**Support Agent**: We do have a few promotions running at the moment. We're currently offering a 15% discount on all orders over $500. Additionally, if you sign up for our email newsletter, you'll be the first to know about any upcoming sales or special offers.\n\n**Customer**: That's fantastic! I'll definitely sign up for the newsletter. I'm also curious about the warranty and return policy for the Ergonomic Office Chair. Could you provide me with some information on that?\n\n**Support Agent**: Absolutely. The Ergonomic Office Chair comes with a one-year warranty that covers any defects in materials or workmanship. If you're not satisfied with your purchase for any reason, you can return it within 30 days of the purchase date for a full refund.\n\n**Customer**: That's really helpful information. Thank you for clarifying that. Overall, I'm happy with the service and the product I ordered, but I would appreciate it if you could keep me updated on the shipping status of my order.\n\n**Support Agent**: Of course! I'll make sure to send you an email notification as soon as your order is shipped. If you have any other questions or concerns, please don't hesitate to reach out. We're here to assist you.\n\n**Customer**: Thank you so much for your assistance. I appreciate your prompt and helpful responses.\n\n**Support Agent**: You're very welcome! We're glad we could help. Have a great day, and we look forward to serving you again soon.\n\n**Customer**: You too! Goodbye.\n\n"
                },
                {
                    "sentiment": "positive",
                    "agent_id": "14",
                    "description": "Add a pop of color and functionality to your home with this bright pink ottoman. This ottoman is perfect for use as a footrest, extra seating, or even as a coffee table. It's made of durable materials that are easy to clean, and it's filled with a soft, plush cushion that will provide you with hours of comfort. The ottoman is also lightweight and easy to move, so you can easily rearrange your space as needed. Whether you're looking for a stylish accent piece or a functional addition to your home, this bright pink ottoman is the perfect choice.",
                    "customer_id": "1",
                    "agent_email": "Margaret@customerservices.agents",
                    "product_id": "642",
                    "category": "Ottoman",
                    "rating": "4",
                    "title": "Bright Pink Ottoman: A Stylish and Functional Addition to Your Home",
                    "customer_email": "user9735@sample_user9735.sample",
                    "status": "resolved",
                    "conversation": " **Customer**: Hi there! I recently ordered the Bright Pink Ottoman from your store and I'm wondering if you can help me track my return?\n\n**Support Agent**: Of course! I'd be happy to assist you with that. Could you please provide me with your order number or the email address associated with your account?\n\n**Customer**: Sure, my order number is #123456 and the email address is username@example.com.\n\n**Support Agent**: Thank you for providing that information. Let me pull up your order details. Please bear with me for a moment.\n\n**Customer**: No problem, take your time.\n\n**Support Agent**: I've located your order and I see that you initiated a return for the Bright Pink Ottoman. The return was processed and approved on [date]. You should be receiving a confirmation email shortly with details on the return shipping label.\n\n**Customer**: Oh, that's great news! I was hoping to get an update on the return status.\n\n**Support Agent**: I'm glad I could provide you with that information. The return shipping label will be sent to the email address associated with your account. Once you receive the label, you can attach it to the return package and drop it off at the nearest carrier location.\n\n**Customer**: Perfect! Thank you so much for your help. I really appreciate your prompt response and assistance.\n\n**Support Agent**: You're very welcome! I'm happy that I could resolve your query. If you have any further questions or concerns, please don't hesitate to reach out. We're here to help!\n\n**Customer**: Thank you once again for your excellent customer service. I'm really impressed with the way you handled my request. Keep up the great work!\n\n**Support Agent**: Thank you for your kind words. We strive to provide our customers with the best possible experience. I'm glad we could meet your expectations. Have a wonderful day, and we look forward to serving you again in the future!\n\n**Customer**: You too! Take care and stay safe"
                },
                {
                    "sentiment": "positive",
                    "agent_id": "32",
                    "description": "Bring a touch of elegance and comfort to your home with this beautiful pink ottoman. Upholstered in a soft, plush fabric, this ottoman is perfect for putting your feet up after a long day or for extra seating when you have guests. The ottoman is also a great place to store extra blankets or pillows. With its stylish design and durable construction, this ottoman will be a cherished addition to your home for years to come.",
                    "customer_id": "1",
                    "agent_email": "Matthew@customerservices.agents",
                    "product_id": "646",
                    "category": "Ottoman",
                    "rating": "5",
                    "title": "OttomanArt Home & Garden Pink Ottoman",
                    "customer_email": "user9735@sample_user9735.sample",
                    "status": "resolved",
                    "conversation": " **Customer**: Hi there! I recently purchased the OttomanArt Home & Garden Pink Ottoman from your store, but I'm afraid I need to request an exchange.\n\n**Support Agent**: Oh, I'm sorry to hear that. Can you please let me know what seems to be the issue with the ottoman?\n\n**Customer**: The color of the ottoman is not quite what I expected. It appears more like a light purple than a pink.\n\n**Support Agent**: I understand. Color variations can sometimes occur due to differences in lighting or screen settings. Would you be able to send me a photo of the ottoman in natural light so that I can better assess the color?\n\n**Customer**: Sure, I can do that. (Customer sends a photo of the ottoman)\n\n**Support Agent**: Thank you for sending the photo. I can see that the color does indeed appear to be different from what was advertised. I'll go ahead and process an exchange for you. Can you please provide me with your order number and shipping address?\n\n**Customer**: My order number is #123456789 and my shipping address is 123 Main Street, Anytown, CA 12345.\n\n**Support Agent**: Perfect. I've processed the exchange request and you should receive a confirmation email shortly. The new ottoman will be shipped out to you within the next 2-3 business days.\n\n**Customer**: Thank you so much for your help! I really appreciate your prompt response and assistance.\n\n**Support Agent**: You're very welcome! I'm glad I could resolve the issue for you. If you have any further questions or concerns, please don't hesitate to reach out.\n\n**Customer**: I will. Thanks again!\n\n(The support agent ends the chat with a positive sentiment, as the customer's issue was resolved and they expressed gratitude for the assistance provided."
                },
                {
                    "sentiment": "positive",
                    "agent_id": "1",
                    "description": "This bed set includes a white comforter, two black pillows, and a black bed skirt. The comforter is made of a soft, plush material that will keep you warm and cozy all night long. The pillows are filled with a hypoallergenic material that is perfect for people with allergies. The bed skirt is made of a durable fabric that will protect your mattress from dirt and dust. This bed set is perfect for anyone who wants to add a touch of elegance to their bedroom.",
                    "customer_id": "1",
                    "agent_email": "Patricia@customerservices.agents",
                    "product_id": "75",
                    "category": "Bed",
                    "rating": "4",
                    "title": "Black and White Bed Set",
                    "customer_email": "user9735@sample_user9735.sample",
                    "status": "resolved",
                    "conversation": " **Customer**: Hi there! I recently made a purchase for a Black and White Bed Set from your store and I'm wondering if you could help me track my return?\n\n**Support Agent**: Of course! I'd be happy to assist you with that. Could you please provide me with your order number or the email address associated with your account?\n\n**Customer**: Sure, my order number is #123456 and the email address is username@example.com.\n\n**Support Agent**: Thank you for providing that information. Let me pull up your order details. Please bear with me for a moment.\n\n**Customer**: No problem, take your time.\n\n**Support Agent**: I've located your order and can see that the return was processed on [date]. The refund amount of $[amount] has been initiated and should reflect in your account within the next 5-7 business days, depending on your bank's processing time.\n\n**Customer**: That's great news! Thank you for checking that for me. I appreciate your prompt response.\n\n**Support Agent**: You're very welcome! I'm glad I could assist you with your return. Is there anything else I can help you with today?\n\n**Customer**: Actually, I do have one more question. I noticed that the product description mentioned the comforter is made of a soft, plush material. Could you confirm if it's machine-washable?\n\n**Support Agent**: Absolutely! The comforter is indeed machine-washable. You can wash it on a gentle cycle with cold water and tumble dry on low heat. However, please make sure to follow the care instructions on the product label to ensure its longevity.\n\n**Customer**: That's perfect! Thank you for clarifying that. I really appreciate your help today.\n\n**Support Agent**: It's my pleasure! If you have any further questions or concerns, please don't hesitate to reach out. We're here to assist you.\n\n**Customer**: Thank you so much for your excellent customer service. I'm very satisfied with my experience with Cymbal Furniture.\n\n**Support Agent**: You're most welcome! We strive to provide the best possible experience for our customers. Have a wonderful day, and we look forward to serving you again in the future.\n\n**Customer**: You too! Goodbye.\n\n**Support Agent**: Goodbye"
                },
                {
                    "sentiment": "positive",
                    "agent_id": "0",
                    "description": "This blue couch is perfect for relaxing in your living room while enjoying the view of the ocean. The couch is made of a soft and durable fabric that will last for years to come. It is also easy to clean, so you can keep it looking its best. The couch is available in a variety of sizes, so you can find the perfect one for your space. Whether you're looking to curl up with a good book or watch a movie with friends, this blue couch is the perfect place to do it.",
                    "customer_id": "1",
                    "agent_email": "Mary@customerservices.agents",
                    "product_id": "826",
                    "category": "Sofa",
                    "rating": "5",
                    "title": "Blue Couch with a View of the Ocean",
                    "customer_email": "user9735@sample_user9735.sample",
                    "status": "not resolved",
                    "conversation": " **Customer**: Hi there! I'm interested in the Blue Couch with a View of the Ocean. Can you tell me more about it?\n\n**Agent**: Absolutely! The Blue Couch with a View of the Ocean is one of our most popular products. It's a beautiful and comfortable couch that's perfect for relaxing in your living room. The couch is made of a soft and durable fabric that will last for years to come. It's also easy to clean, so you can keep it looking its best.\n\n**Customer**: That sounds great! I'm also curious about the size options. I have a small living room, so I need something that won't take up too much space.\n\n**Agent**: No problem! The Blue Couch with a View of the Ocean comes in three different sizes: small, medium, and large. The small size is perfect for small living rooms, while the medium and large sizes are better suited for larger spaces.\n\n**Customer**: Perfect! I think the small size would be a good fit for my living room. I also love the color. Is it a true blue, or is it more of a navy?\n\n**Agent**: It's a true blue, just like the ocean. It's a beautiful color that will add a pop of color to your living room.\n\n**Customer**: I'm definitely interested in ordering the Blue Couch with a View of the Ocean. Do you have any discounts or promotions available?\n\n**Agent**: We currently have a 10% off sale on all orders over $500. The Blue Couch with a View of the Ocean is $499, so you would qualify for the discount.\n\n**Customer**: That's great! I'll go ahead and place my order now. Thanks for your help!\n\n**Agent**: You're welcome! I'm glad I could help. If you have any other questions, please don't hesitate to contact us.\n\n**Customer**: (A few days later) Hi, I received my couch today, but there's a problem. The color is completely different from what I expected. It's more of a navy blue than a true blue.\n\n**Agent**: I'm so sorry to hear that! We must have made a mistake when processing your order. I'll look into it and get back to you as soon as possible.\n\n**Customer**: Okay, I'm disappointed, but I appreciate your help.\n\n"
                },
                {
                    "sentiment": "positive",
                    "agent_id": "15",
                    "description": "This single bed with nightstand is perfect for small spaces. The bed is made of solid wood and features a sleek, modern design. The nightstand is also made of solid wood and provides ample storage space for your belongings. This bed and nightstand set is perfect for anyone who is looking for a stylish and functional bedroom solution.",
                    "customer_id": "1",
                    "agent_email": "Ashley@customerservices.agents",
                    "product_id": "120",
                    "category": "Bed",
                    "rating": "4",
                    "title": "Single Bed with Nightstand - Perfect for Small Spaces",
                    "customer_email": "user9735@sample_user9735.sample",
                    "status": "resolved",
                    "conversation": " **Customer**: Hi there! I recently purchased the Single Bed with Nightstand from your store, but I'm afraid I need to request an exchange.\n\n**Support Agent**: Oh, I'm sorry to hear that. Can you please let me know what seems to be the issue with the product?\n\n**Customer**: The bed itself is great, but the nightstand arrived damaged. There's a large scratch on the front panel.\n\n**Support Agent**: I completely understand your concern. We take great pride in the quality of our products, and it's unfortunate that the nightstand arrived in less-than-perfect condition. Could you please provide me with your order number so I can pull up your purchase details?\n\n**Customer**: Sure, my order number is #123456.\n\n**Support Agent**: Thank you for providing your order number. Let me just access your order information. Alright, I see your order here. I'm truly sorry for the inconvenience caused by the damaged nightstand. We'll definitely make this right for you.\n\n**Customer**: I appreciate that. What are the options for resolving this issue?\n\n**Support Agent**: We can either send you a replacement nightstand or process a refund for the damaged item, whichever you prefer.\n\n**Customer**: I think a replacement nightstand would be best. I really like the bed and I'd like to keep it.\n\n**Support Agent**: Excellent choice! I'll go ahead and process a replacement nightstand for you right away. You can expect it to be delivered within the next 5-7 business days.\n\n**Customer**: That's great news! Thank you for your prompt assistance.\n\n**Support Agent**: You're very welcome! I'm glad I could help. If you have any further questions or concerns, please don't hesitate to reach out. We're here to ensure your complete satisfaction.\n\n**Customer**: I really appreciate your help. Have a great day!\n\n**Support Agent**: You too! Take care and enjoy your new bed"
                },
                {
                    "sentiment": "neutral",
                    "agent_id": "36",
                    "description": "The black marble dining table with black legs is a stylish and contemporary addition to any dining room. The table is made from high-quality marble and features a sleek, modern design. The black legs provide a sturdy and stylish base for the table, and the marble top is easy to clean and maintain. This dining table is perfect for entertaining guests or for everyday family meals. It is sure to make a statement in any dining room.",
                    "customer_id": "1",
                    "agent_email": "Steven@customerservices.agents",
                    "product_id": "426",
                    "category": "Dining Table",
                    "rating": "2",
                    "title": "Black Marble Dining Table with Black Legs",
                    "customer_email": "user9735@sample_user9735.sample",
                    "status": "resolved",
                    "conversation": " **Customer**: Hi there! I recently purchased the Black Marble Dining Table with Black Legs from your store and I'm having a bit of an issue with it.\n\n**Support Agent**: Oh no! I'm sorry to hear that. What seems to be the problem?\n\n**Customer**: The table is wobbly and I can't seem to figure out how to fix it. I've tried tightening the legs, but it doesn't seem to be helping.\n\n**Support Agent**: I see. Could you please send me a few photos of the table so I can better understand the issue? You can attach them to this chat.\n\n**Customer**: Sure, no problem. Here are a few photos of the table. (Customer attaches photos)\n\n**Support Agent**: Thank you for sending those photos. It looks like the issue may be with the way the legs are attached to the table. I'm going to send you a video tutorial that shows you how to properly attach the legs.\n\n**Customer**: That would be great! Thank you.\n\n**Support Agent**: You're welcome. I've sent the video to your email address. Please let me know if you have any other questions or concerns.\n\n**Customer**: I received the video and it was very helpful! I was able to fix the table and it's now perfectly sturdy. Thank you so much for your help!\n\n**Support Agent**: You're very welcome! I'm glad I could help. If you have any other issues in the future, please don't hesitate to contact us.\n\n**Customer**: I will. Thanks again!\n\n"
                }
            ],
            "reviews": [],
            "customer_info": {
                "customer_id": "1",
                "is_media_follower": False,
                "cart_total": 387.81,
                "channel": "email",
                "city": "Brea",
                "last_activity_date": "2023-03-22",
                "total_value": "34",
                "total_purchases": "76",
                "last_purchase_date": "2023-03-06",
                "last_sign_up_date": "2021-05-02",
                "state": "California",
                "total_emails": "99",
                "loyalty_score": "52",
                "email": "user9735@sample_user9735.sample"
            }
        }
PALM_RESULT_INSIGHT_MULTI_TURNS = """
 **What went well:**

- The agent was able to provide the customer with the status of their order and information about upcoming promotions.
- The agent was able to answer the customer's questions about the product materials.
- The agent was friendly and helpful throughout the conversation.

**What can be done to improve the user experience:**

- The agent could have provided more proactive information about the order status without the customer having to ask.
- The agent could have provided more details about the shipping process and expected delivery date.
- The agent could have offered additional product recommendations or upselling opportunities based on the customer's interests.
- The agent could have followed up with the customer after the conversation to ensure their satisfaction and address any additional questions or concerns."""
PALM_RESULT_SUMMARY_MULTI_TURNS = """
         **Customer Inquiry:**
- Customer inquires about the status of their order (#123456789) for the Stealth Gaming Chair.
- Customer expresses interest in upcoming promotions or discounts for the chair or other products.
- Customer seeks additional information about the materials used in the chair's seat and backrest.

**Agent Response:**
- Confirms that the order is in production and will ship within 5-7 business days; tracking information will be provided via email.
- Informs customer about current promotions: 15% discount on all gaming chairs with code "CYMBAL15" and encourages sign-up for the email newsletter for future offers.
- Provides details about the materials used: high-density foam for seat and backrest, breathable fabric upholstery for comfort during long gaming sessions.

**Outcome:**
- Customer is satisfied with the order status update and appreciates the information about promotions and product details.
- Customer expresses contentment with their choice and thanks the agent for assistance.
        """
PALM_RESULT_TASKS_MULTI_TURNS = """
         **Pending tasks from the customer perspective:**

- None.

**Pending tasks from the agent perspective:**

- Send the customer an email with the tracking information once the order has been shipped.
        """
PALM_RESULT_NBS_MULTI_TURNS = """
 Based on the conversation between the call center agent and the customer, the following next best actions are recommended to increase the ability of customers to find information and resolve issues by themselves:

- **Improve product documentation, FAQ page, or product page**: The customer had to reach out to the call center to get information about the status of their order, upcoming promotions, and product materials. This suggests that the product page, FAQ section, or order tracking information may not be easily accessible or comprehensive enough. Improving these resources can help customers find the information they need without needing to contact the call center.


- **Personalize content and recommendations**: The customer expressed interest in upcoming promotions and discounts. By personalizing content and recommendations based on user preferences and behavior, the furniture store can proactively provide relevant information and offers to the customer, increasing the chances of repeat purchases and customer satisfaction.


- **Run satisfaction surveys and NPS scores**: To measure user loyalty and identify areas for improvement in the long term, the furniture store can send out satisfaction surveys or calculate NPS (Net Promoter Score) to gather feedback from customers. This will help the store understand how well they are meeting customer expectations and make data-driven decisions to improve their services.


- **Respond to user reviews and social media comments**: The furniture store should make an effort to respond to user reviews and social media comments, both positive and negative. This shows that the store values customer feedback and is committed to addressing concerns and improving their products and services.
"""

class Test_P5(unittest.TestCase):
    def test_generate_insights_conversations_greater_than_1_insights(self):
        """
        test generate_insights_conversations:insights conversations > 1
        """
        print("*** generate_insights_conversations:insights conversations > 1***")

        prompt_insights = config["search-persona5"][
            "prompt_insights_multi_conversations"
        ]
        input_text = json.dumps({"conversations": CONVERSATIONS_MULTI_TURNS})

        insights = generate_gemini_pro_text(
            prompt=prompt_insights.format(input_text)
        )
        result = rate(old_paragraph=f"{PALM_RESULT_INSIGHT_MULTI_TURNS}",
             new_paragraph=insights)
        print(f"""
===insights multi===
{insights}
===insights===
              """)
        self.assertTrue(float(result['rating']) >= 7)
        
    def test_generate_insights_conversations_greater_than_1_summary(self):
        """
        test generate_insights_conversations:summary conversations = 1
        """
        print("*** generate_insights_conversations:summary conversations = 1***")

        prompt_summary = config["search-persona5"][
            "prompt_summary_multi_conversations"
        ]
        input_text = json.dumps({"conversations": CONVERSATIONS_MULTI_TURNS})

        summary = generate_gemini_pro_text(
            prompt=prompt_summary.format(input_text)
        )
        print(f"""
===summary multi===
{summary}
===insights===
              """)
        result = rate(old_paragraph=f"{PALM_RESULT_SUMMARY_MULTI_TURNS}",
             new_paragraph=summary)

        self.assertTrue(float(result['rating']) >= 7)

    def test_generate_insights_conversations_greater_than_1_tasks(self):
        """
        test generate_insights_conversations:tasks conversations > 1
        """
        print("*** generate_insights_conversations:tasks conversations > 1***")

        prompt_tasks = config["search-persona5"][
            "prompt_pending_tasks_multi_conversations"
        ]
        input_text = json.dumps({"conversations": CONVERSATIONS_MULTI_TURNS})

        tasks = generate_gemini_pro_text(
            prompt=prompt_tasks.format(input_text)
        )
        print(f"""
===tasks multi===
{tasks}
===insights===
              """)
        result = rate(old_paragraph=f"{PALM_RESULT_TASKS_MULTI_TURNS}",
             new_paragraph=tasks)

        self.assertTrue(float(result['rating']) >= 7)


    def test_generate_insights_conversations_greater_than_1_nbs(self):
        """
        test generate_insights_conversations:nbs conversations > 1
        """
        print("*** generate_insights_conversations:nbs conversations > 1***")

        prompt_nbs = config["search-persona5"][
            "prompt_nbs_multi_conversations"
        ]
        input_text = json.dumps({"conversations": CONVERSATIONS_MULTI_TURNS})

        nbs = generate_gemini_pro_text(
            prompt=prompt_nbs.format(input_text)
        )
        print(f"""
===nbs multi===
{nbs}
===insights===
              """)
        result = rate(old_paragraph=f"{PALM_RESULT_NBS_MULTI_TURNS}",
             new_paragraph=nbs)

        self.assertTrue(float(result['rating']) >= 7)

    ## ------- SINGLE TURN ------
    # def test_generate_insights_conversations_insights(self):
    #     """
    #     test generate_insights_conversations:insights conversations > 1
    #     """
    #     print("*** generate_insights_conversations:insights conversations > 1***")

    #     prompt_insights = config["search-persona5"][
    #         "prompt_insights_conversation"
    #     ]
    #     input_text = json.dumps({"conversations": CONVERSATIONS_MULTI_TURNS})

    #     insights = generate_gemini_pro_text(
    #         prompt=prompt_insights.format(input_text)
    #     )
    #     result = rate(old_paragraph=f"{PALM_RESULT_INSIGHT_MULTI_TURNS}",
    #          new_paragraph=insights)

    #     self.assertTrue(float(result['rating']) >= 7)
        
    # def test_generate_insights_conversations_1_summary(self):
    #     """
    #     test generate_insights_conversations:summary conversations = 1
    #     """
    #     print("*** generate_insights_conversations:summary conversations = 1***")

    #     prompt_summary = config["search-persona5"][
    #         "prompt_summary_conversation"
    #     ]
    #     input_text = json.dumps({"conversations": CONVERSATIONS_MULTI_TURNS})

    #     summary = generate_gemini_pro_text(
    #         prompt=prompt_summary.format(input_text)
    #     )
    #     result = rate(old_paragraph=f"{PALM_RESULT_SUMMARY_MULTI_TURNS}",
    #          new_paragraph=summary)

    #     self.assertTrue(float(result['rating']) >= 7)

    # def test_generate_insights_conversations_1_tasks(self):
    #     """
    #     test generate_insights_conversations:tasks conversations > 1
    #     """
    #     print("*** generate_insights_conversations:tasks conversations > 1***")

    #     prompt_tasks = config["search-persona5"][
    #         "prompt_pending_tasks_conversation"
    #     ]
    #     input_text = json.dumps({"conversations": CONVERSATIONS_MULTI_TURNS})

    #     tasks = generate_gemini_pro_text(
    #         prompt=prompt_tasks.format(input_text)
    #     )
    #     result = rate(old_paragraph=f"{PALM_RESULT_TASKS_MULTI_TURNS}",
    #          new_paragraph=tasks)

    #     self.assertTrue(float(result['rating']) >= 7)

    # def test_generate_insights_conversations_1_nbs(self):
    #     """
    #     test generate_insights_conversations:nbs conversations > 1
    #     """
    #     print("*** generate_insights_conversations:nbs conversations > 1***")

    #     prompt_nbs = config["search-persona5"][
    #         "prompt_nbs_conversation"
    #     ]
    #     input_text = json.dumps({"conversations": CONVERSATIONS_MULTI_TURNS})

    #     nbs = generate_gemini_pro_text(
    #         prompt=prompt_nbs.format(input_text)
    #     )
    #     result = rate(old_paragraph=f"{PALM_RESULT_NBS_MULTI_TURNS}",
    #          new_paragraph=nbs)

    #     self.assertTrue(float(result['rating']) >= 7)


if __name__ == '__main__':
    unittest.main()