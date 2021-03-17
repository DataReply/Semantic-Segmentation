import boto3
import os
import sys
import uuid
from pathlib import Path
from urllib.parse import unquote_plus
from PIL import Image
import PIL.Image


s3_client = boto3.client('s3')


def resize_image(source, target):
	with Image.open(source) as image:
		# we have to convert to RGB to save JPEG
		if image.mode != 'RGB':
			print('converting to RGB')
			image = image.convert('RGB')
		
		w, h = image.size
		if max(w, h) > 1200:
			ratio = 1200 / max(w, h)
			print(f'reducing the resolution {100*ratio}%')
			image.thumbnail((w * ratio, h * ratio))

		image.save(target)
		print("successfully processed the image")


def lambda_handler(event, context):
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = unquote_plus(record['s3']['object']['key'])  # this is the newly uploaded file
        key_jpg = str(Path(key).with_suffix('.jpg'))
        

        source_path = f'/tmp/{uuid.uuid4()}'
        target_path = f'/tmp/{uuid.uuid4()}.jpg'

        s3_client.download_file(bucket, key, source_path)
        resize_image(source_path, target_path)
        s3_client.upload_file(target_path, bucket, key_jpg.replace('staging', 'processed'))
    

