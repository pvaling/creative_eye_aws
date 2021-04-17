#Copyright 2020 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#PDX-License-Identifier: MIT-0 (For details, see https://github.com/awsdocs/amazon-rekognition-custom-labels-developer-guide/blob/master/LICENSE-SAMPLECODE.)

import boto3
import io
from PIL import Image, ImageDraw, ExifTags, ImageColor, ImageFont

def display_image(bucket,photo,response):
    # Load image from S3 bucket
    s3_connection = boto3.resource('s3')

    s3_object = s3_connection.Object(bucket,photo)
    s3_response = s3_object.get()

    stream = io.BytesIO(s3_response['Body'].read())
    image=Image.open(stream)

    # Ready image to draw bounding boxes on it.
    imgWidth, imgHeight = image.size
    draw = ImageDraw.Draw(image)

    # calculate and display bounding boxes for each detected custom label
    print('Detected custom labels for ' + photo)
    for customLabel in response['CustomLabels']:
        print('Label ' + str(customLabel['Name']))
        print('Confidence ' + str(customLabel['Confidence']))
        if 'Geometry' in customLabel:
            box = customLabel['Geometry']['BoundingBox']
            left = imgWidth * box['Left']
            top = imgHeight * box['Top']
            width = imgWidth * box['Width']
            height = imgHeight * box['Height']

            fnt = ImageFont.truetype('/Library/Fonts/Arial.ttf', 50)
            draw.text((left, top), customLabel['Name'], fill='#00d400', font=fnt)

            print('Left: ' + '{0:.0f}'.format(left))
            print('Top: ' + '{0:.0f}'.format(top))
            print('Label Width: ' + "{0:.0f}".format(width))
            print('Label Height: ' + "{0:.0f}".format(height))

            points = (
                (left,top),
                (left + width, top),
                (left + width, top + height),
                (left , top + height),
                (left, top))
            draw.line(points, fill='#00d400', width=5)

    # image.show()
    return image

def show_custom_labels(model,bucket,photo, min_confidence):
    client = boto3.client('rekognition')

    out_img = None

    #Call DetectCustomLabels
    response = client.detect_custom_labels(Image={'S3Object': {'Bucket': bucket, 'Name': photo}},
        MinConfidence=min_confidence,
        ProjectVersionArn=model)

    # For object detection use case, uncomment below code to display image.
    if len(response['CustomLabels']):
        out_img = display_image(bucket, photo, response)

    return len(response['CustomLabels']), out_img

def handler(event, context):
    s3_object = event.get('Records', [])

    s3_item = s3_object[0]

    input_bucket_name = s3_item['s3']['bucket']['name']
    key = s3_item['s3']['object']['key']
    file_with_path = key

    input_filename = file_with_path.split('/')[-1]


    s3_connection = boto3.resource('s3')
    s3_client = boto3.client('s3')

    bucket = input_bucket_name
    out_bucket = 'creative-tags-out-labeled'
    bucket = s3_connection.Bucket(bucket)

    photo = key
    model = 'arn:aws:rekognition:eu-central-1:295181168698:project/creative_eye/version/creative_eye.2021-04-16T07.56.58/1618549018936'
    min_confidence = 50
    label_count, img = show_custom_labels(model, bucket.name, photo, min_confidence)
    print("Custom labels detected: " + str(label_count))
    if img:
        in_mem_file = io.BytesIO()
        img.save(in_mem_file, format=img.format)
        in_mem_file.seek(0)

        # Upload image to s3
        s3_client.upload_fileobj(
            in_mem_file,  # This is what i am trying to upload
            out_bucket,
            'labeled-' + key,
            # ExtraArgs={
            #     'ACL': 'public-read'
            # }
        )

