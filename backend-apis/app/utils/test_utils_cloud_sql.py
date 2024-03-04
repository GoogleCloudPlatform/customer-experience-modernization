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
"""
Test the conversion of a Product object to a dictionary.
"""

import unittest

from .utils_cloud_sql import Product, convert_product_to_dict


class TestProductConversion(unittest.TestCase):
    """
    Test the conversion of a Product object to a dictionary.
    """

    def test_convert_product_to_dict(self):
        """
        Test the conversion of a Product object to a dictionary.
        """
        product = Product(
            id=1,
            title="",
            description="",
            image="",
            features="",
            categories="",
            price=10.0,
            quantity=1,
        )
        result = convert_product_to_dict(product)
        self.assertEqual(
            result,
            {
                "id": 1,
                "title": "",
                "description": "",
                "image": "",
                "features": [],
                "categories": [],
                "price": 10.0,
                "quantity": 1,
            },
        )

    def test_categories_string_to_list_conversion(self):
        """
        Test the conversion of a Product object to a dictionary.
        """
        product = Product(
            id=1,
            title="",
            description="",
            image="",
            features="",
            categories="['category1','category2']",
            price=10.0,
            quantity=1,
        )
        result = convert_product_to_dict(product)
        self.assertEqual(
            result,
            {
                "id": 1,
                "title": "",
                "description": "",
                "image": "",
                "features": [],
                "categories": ["category1", "category2"],
                "price": 10.0,
                "quantity": 1,
            },
        )
