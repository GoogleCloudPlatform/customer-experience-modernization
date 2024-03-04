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
Utils for Imagen

"""

import asyncio
import functools
import tomllib
import uuid

from google.api_core.exceptions import GoogleAPICallError
from google.cloud import storage
from google.cloud import vision_v1 as vision
from requests.exceptions import ReadTimeout
from vertexai.preview.vision_models import ImageGenerationModel
from vertexai.vision_models import Image, ImageCaptioningModel

with open("app/config.toml", "rb") as f:
    config = tomllib.load(f)

images_bucket_name = config["global"]["images_bucket_name"]

storage_client = storage.Client()
bucket = storage_client.bucket(images_bucket_name)

vision_client = vision.ImageAnnotatorClient()
image_caption_model = ImageCaptioningModel.from_pretrained("imagetext")
image_generate_model = ImageGenerationModel.from_pretrained(
    "imagegeneration@002"
)


def image_name_to_bytes(image_name: str) -> bytes:
    """

    Args:
        image_name: string
            Name of the image

    Returns:
        bytes
            Bytes of the image with this name from Cloud Storage

    """
    image_blob = bucket.blob(f"images/{image_name}")
    return image_blob.download_as_bytes()


def upload_image_to_storage(image: bytes) -> str:
    """

    Args:
        image: bytes
            Image

    Returns:
        str
            UUID4 image name used to upload the image to Cloud Storage

    """
    image_name = str(uuid.uuid4())
    image_blob = bucket.blob(f"images/{image_name}")
    image_blob.upload_from_string(image, content_type="image/png")
    return image_name


def annotate_image_names(images_names: list[str]) -> set[str]:
    """

    Args:
        images_names: list[str]
            List of image names from Cloud Storage

    Returns:
        set[str]
            Set of labels from Vision API

    """
    images_requests = []
    for image_name in images_names:
        source = vision.ImageSource(
            gcs_image_uri=(f"gs://{images_bucket_name}/images/{image_name}")
        )
        feature = vision.Feature(type_=vision.Feature.Type.LABEL_DETECTION)

        images_requests.append(
            vision.AnnotateImageRequest(
                image=vision.Image(source=source),
                features=[feature],
            )
        )

    # Extract labels with Vision API
    results = vision_client.batch_annotate_images(
        request=vision.BatchAnnotateImagesRequest(requests=images_requests)
    )

    vision_labels = set()
    for response in results.responses:
        for i in response.label_annotations:
            if i.score > 0.85:
                vision_labels.add(i.description)
    return vision_labels


async def async_get_image_captions(image_bytes: bytes) -> list:
    """

    Args:
        imagen_model:
        uri:

    Returns:

    """
    loop = asyncio.get_running_loop()
    try:
        captions = await loop.run_in_executor(
            None,
            functools.partial(
                image_caption_model.get_captions,
                image=Image(image_bytes=image_bytes),
                number_of_results=1,
                language="en",
            ),
        )
        if not captions:
            return ["awesome funiture product"]
    except (GoogleAPICallError, ReadTimeout) as e:
        print(e)
        return ["awesome funiture product"]

    return captions


async def run_image_captions(images_bytes: list[bytes]):
    """

    Args:
        images_uri:
        imagen_model:

    Returns:

    """
    tasks = [
        async_get_image_captions(image_bytes=image_bytes)
        for image_bytes in images_bytes
    ]
    results = await asyncio.gather(*tasks)
    return [result[0] for result in results]
