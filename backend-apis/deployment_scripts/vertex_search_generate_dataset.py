# Copyright 2023 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import asyncio
import itertools
import json
import os
import random
import time

from google.cloud import storage
from app.routers.p2_content_creator import *


# TODO (renatoleite) Include copy to GCS

html_template = """<html><head><meta http-equiv="Content-Type" content="text/html; charset=windows-1252"></head><body><div class="row mt-5">
	<nav aria-label="breadcrumb">
		<ol class="breadcrumb">
			<li class="breadcrumb-item">Home</li>
			<li class="breadcrumb-item">Categories</li>
			<li class="breadcrumb-item active" aria-current="page">{categories}</li>
		</ol>
	</nav>
	<div class="card mb-12">
		<div class="row g-0">
			<div class="col-md-4 text-center">
				<img src="{image_uri}" class="img-fluid rounded-start" alt="..." style="max-height:500px">
			</div>
			<div class="col-md-8">
				<div class="card-body">
					<h3 class="card-title">{title}</h3>
					<h4 class="card-subtitle text-body-secondary mb-2">${price}</h4>
					<p class="card-text"><small>{description}</small></p>
				</div>
			</div>
		</div>
	</div>
</div> 
</body></html>"""


def get_blobs(
        bucket_name: str,
        prefix: str,
        match_glob: str = "**.png"
):
    return [i.name for i in storage_client.list_blobs(
                bucket_or_name=bucket_name, 
                prefix=prefix,
                match_glob=match_glob)]


def download_blob(
        bucket: storage.Bucket,
        blob_name: str
):
    blob = bucket.blob(blob_name)
    return blob.download_as_string()


def retrieve_images_uri(
        blobs: list,
        bucket_name: str,
        filename: str = "images_uri.jsonl"
):
    with open(filename, "a") as f:
        for i, blob in enumerate(blobs):
            images_uri = {
                "id": str(i),
                "uri": "https://storage.googleapis.com/" + bucket_name + "/" + blob
            }
            f.write(json.dumps(images_uri) + "\n")


def batched(iterable, n):
    if n < 1:
        raise ValueError('n must be at least one')
    it = iter(iterable)
    while batch := tuple(itertools.islice(it, n)):
        yield batch


def generate_images_captioning(
        filename: str,
        output_file: str
):
    with open(filename, "r") as f:
        lines = f.readlines()

    images_batched = list(batched(lines, 20))

    ref_i = 0
    images_captions = []
    for batch in images_batched:
        print(f"Processing {ref_i*20} - {ref_i*20 + 20}")
        ref_i += 1
        products = [json.loads(b) for b in batch]
        images_uri = [product["uri"] for product in products]

        images_caption = asyncio.run(
                utils_imagen.run_image_captions(
                    images_uri=images_uri, 
                    imagen_model=imagen_model))

        for product, caption in zip(products, images_caption):
            images_captions.append({
                "id":product["id"],
                "uri":product["uri"],
                "caption":caption
            })

        time.sleep(1)

    with open(output_file, "a") as f:
        for i in images_captions:
            f.write(json.dumps(i) + "\n")


def extract_categories_from_captions(
        filename: str,
        output_file: str
):
    with open(filename, "r") as f:
        lines = f.readlines()

    captions_batched = list(batched(lines, 20))

    ref_i = 0
    images_categories = []
    for batch in captions_batched:
        print(f"Processing {ref_i*20} - {ref_i*20 + 20}")
        ref_i += 1

        products = [json.loads(b) for b in batch]
        batch_captions = [product["caption"] for product in products]

        prompts = [
            config["content_creation"]["prompt_categories"].format("\n".join(c))
                for c in batch_captions]
        
        batch_categories = asyncio.run(
            utils_palm.run_predict_text_llm(
                prompts=prompts,
                model=text_gen_client
            )
        )

        images_categories_dict = []
        for c in batch_categories:
            try:
                category_dict = json.loads(c)
                if ("product_categories" in category_dict and 
                    isinstance(category_dict["product_categories"], list)):
                    images_categories_dict.append(category_dict)
                else:
                    images_categories_dict.append({"product_categories":[]})
            except:
                images_categories_dict.append({"product_categories":[]})

        for category, product in zip(images_categories_dict, products):
            images_categories.append(
                {
                    "id":product["id"],
                    "uri":product["uri"],
                    "caption":product["caption"],
                    "categories":category["product_categories"]
                }
            )
        time.sleep(20)

    with open(output_file, "a") as f:
        for cat in images_categories:
            f.write(json.dumps(cat) + "\n")


def generate_title_description(
        filename: str,
        output_file: str
):
    with open(filename, "r") as f:
        lines = f.readlines()

    categories_batched = list(batched(lines, 20))

    ref_i = 0
    all_title_desc = []
    for batch in categories_batched:
        print(f"Processing {ref_i*20} - {ref_i*20 + 20}")
        ref_i += 1

        products = [json.loads(b) for b in batch]
        batch_captions = [product["caption"] for product in products]
        batch_categories = [product["categories"] for product in products]
        batch_uri = [product["uri"] for product in products]

        # Generate Titles and Descriptions
        prompts_title_description = []
        for caption, category, uri in zip(batch_captions, batch_categories, batch_uri):
            prompts_title_description.append(
                config["content_creation"]["prompt_title_description"].format(
                    uri.split(sep="/")[-3] + " ".join(category),
                    caption
                )
            )

        titles_descriptions = asyncio.run(
                utils_palm.run_predict_text_llm(
                    prompts=prompts_title_description,
                    model=text_gen_client,
                    temperature=0.9
                )
            )

        for desc, product in zip(titles_descriptions, products):
            batch_title_description = {
                "id":product["id"],
                "uri":product["uri"],
                "caption":product["caption"],
                "categories":product["categories"]
            }

            try:
                title_dict = json.loads(desc)
                if ("title" in title_dict and
                    "description" in title_dict and
                    isinstance(title_dict["title"], str) and
                    isinstance(title_dict["description"], str)):
                    batch_title_description["title"] = title_dict["title"]
                    batch_title_description["description"] = title_dict["description"]
                else:
                    batch_title_description["title"] = \
                        product["uri"].split(sep="/")[-3]
                    batch_title_description["description"] = \
                        product["caption"]
            except:
                batch_title_description["title"] = \
                    product["uri"].split(sep="/")[-3]
                batch_title_description["description"] = \
                    product["caption"]

            all_title_desc.append(batch_title_description)
        
        time.sleep(20)

    with open(output_file, "a") as f:
        for t in all_title_desc:
            f.write(json.dumps(t) + "\n")

    
def generate_price_range(
        blobs: list,
        output_file: str
):
    # Define prices
    top_level_categories = set()
    for blob in blobs:
        top_level_categories.add(
            blob.split(sep="/")[2]
        )

    prompts_price = []
    for level in top_level_categories:
        prompts_price.append(
            config["content_creation"]["prompt_price"].format(level))

    prices_range = asyncio.run(
        utils_palm.run_predict_text_llm(
            prompts=prompts_price,
            model=text_gen_client
        )
    )

    prices_dict = {}
    for price, level in zip(prices_range, top_level_categories):
        try:
            price = json.loads(price)
        except:
            price = {"min": 1.0, "max": 999.9}
        prices_dict[level] = price

    with open(output_file, "w") as f:
        f.write(json.dumps(prices_dict))


def create_jsonl_html_dataset(
        bucket_name: str,
        products_filename: str,
        prices_filename: str,
        output_dir: str
):
    with open(products_filename, "r") as f:
        products = f.readlines()

    with open(prices_filename, "r") as f:
        prices = json.loads(f.read())

    for product in products:
        product_dict = json.loads(product)
        category = product_dict["uri"].split(sep="/")[-3]

        current_price = prices[category]
        price_max = current_price["max"]
        price_min = current_price["min"]
        
        price_float = random.uniform(price_min, price_max)
        cost = "%.2f" % (price_float * 0.2)
        price = "%.2f" % price_float
        html_page = html_template.format(
                categories = category,
                image_uri = product_dict["uri"],
                title = product_dict["title"],
                price = price,
                description = product_dict["description"])

        id = product_dict['id'] if product_dict['id'] != "0" else "1000"
        with open(os.path.join(
            output_dir, f"html_pages/product_{id}.html"
        ), "w") as f:
            f.write(html_page)

        with open(os.path.join(
            output_dir, "recommendation_products.jsonl"
        ), "a") as f:
            json_data = json.dumps({
                "title": product_dict["title"],
                "uri": "https://storage.googleapis.com/" + \
                    bucket_name + "/csm_html_dataset/" + \
                        f"product_{id}.html",
                "price": price,
                
                "categories": [category],
                "images": [{"uri": product_dict["uri"], 
                            "name":product_dict["uri"].split(sep="/")[-1]}]
            })
            f.write(
                json.dumps(
                    {
                        "id":id,
                        "categories": category,
                        "title": product_dict["title"],
                        "description": product_dict["description"],
                        "language_code": "en",
                        "priceInfo": {
                            "currencyCode": "USD", 
                            "price":price, 
                            "originalPrice":price,
                            "cost":cost
                        },
                        "availableTime": "2023-08-26T23:00:17Z",
                        "availableQuantity": random.randint(1,100),
                        "images": [
                            {
                                "uri": product_dict["uri"],
                                "height": 1024, 
                                "width": 1024
                            }
                        ]
                    }
                )
            )
            f.write("\n")

        with open(os.path.join(
            output_dir, "search_products.jsonl"
        ), "a") as f:
            json_data = json.dumps({
                "title": product_dict["title"],
                "description": product_dict["description"],
                "price": price,
            })
            f.write(
                json.dumps(
                    {
                        "id":id,
                        "jsonData": json_data,
                        "content": {
                            "mimeType":"text/html",
                            "uri":"gs://" + \
                                bucket_name + "/csm_html_dataset/" + \
                                    f"product_{id}.html"
                        }
                    }
                )
            )
            f.write("\n")


if __name__ == "__main__":
    storage_client = storage.Client()

    parser = argparse.ArgumentParser()
    parser.add_argument("bucket_name")
    parser.add_argument("prefix")
    parser.add_argument("output_dir")
    args = parser.parse_args()

    blobs = get_blobs(
        bucket_name=args.bucket_name,
        prefix=args.prefix)

    if not os.path.exists(os.path.join(args.output_dir, "images_uri.jsonl")):
        # Step 1 - Retrieve Images URI
        retrieve_images_uri(
            blobs=blobs,
            bucket_name=args.bucket_name,
            filename=os.path.join(args.output_dir, "images_uri.jsonl")
        )

    if (os.path.exists(os.path.join(args.output_dir, "images_uri.jsonl")) and 
        not os.path.exists(os.path.join(args.output_dir, "images_captions.jsonl"))):
        # Step 2 - Generate Image captions
        generate_images_captioning(
            filename=os.path.join(args.output_dir, "images_uri.jsonl"),
            output_file=os.path.join(args.output_dir, "images_captions.jsonl")
        )

    if (os.path.exists(os.path.join(args.output_dir, "images_captions.jsonl")) and 
        not os.path.exists(os.path.join(args.output_dir, "images_categories.jsonl"))):
        # Step 3 - Extract categories from captions
        extract_categories_from_captions(
            filename=os.path.join(args.output_dir, "images_captions.jsonl"),
            output_file=os.path.join(args.output_dir, "images_categories.jsonl")
        )

    if (os.path.exists(os.path.join(args.output_dir, "images_categories.jsonl")) and 
        not os.path.exists(os.path.join(args.output_dir, "images_title_description.jsonl"))):
        # Step 4 - Generate title and description
        generate_title_description(
            filename=os.path.join(args.output_dir, "images_categories.jsonl"),
            output_file=os.path.join(args.output_dir, "images_title_description.jsonl")
        )

    # Step 5 - Generate price range
    if not os.path.exists(os.path.join(args.output_dir, "price_ranges.jsonl")):
        generate_price_range(
            blobs=blobs,
            output_file=os.path.join(args.output_dir, "price_ranges.json")
        )

    print("aqui")
    if (os.path.exists(os.path.join(args.output_dir, "images_title_description.jsonl")) and 
        os.path.exists(os.path.join(args.output_dir, "price_ranges.json")) and
        not os.path.exists(os.path.join(args.output_dir, "recommendation_products.jsonl"))):
        # Step 6 - Generate HTMLs and JSONL
        create_jsonl_html_dataset(
            bucket_name=args.bucket_name,
            products_filename=os.path.join(args.output_dir, "images_title_description.jsonl"),
            prices_filename=os.path.join(args.output_dir, "price_ranges.json"),
            output_dir=args.output_dir
        )

