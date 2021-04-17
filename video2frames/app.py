import os
import json
import boto3


def handler(event, context):
    print("Received event: " + json.dumps(event, indent=2))

    s3 = boto3.client('s3')

    if event.get('input_video_file'):
        input_bucket_name = 'creative-tags'
        input_filename = event.get('input_video_file', None)
    else:
        s3_object = event.get('Records', [])
        if len(s3_object):
            s3_item = s3_object[0]

            input_bucket_name = s3_item['s3']['bucket']['name']
            file_with_path = s3_item['s3']['object']['key']

            input_filename = file_with_path.split('/')[-1]

    out_bucket = 'creative-tags-out'
    s3.download_file(input_bucket_name, file_with_path, '/tmp/' + input_filename)

    out_full_path = f'/tmp/out_{input_filename}_%04d.png'.format(input_filename=input_filename)

    cmd = 'ffmpeg -i {input_file} -r 0.25 {out_file} -y'.format(
        input_file='/tmp/' + input_filename, out_file=out_full_path)
    print(cmd)

    os.system(cmd)

    try:

        for filename in os.listdir('/tmp'):
            if filename.endswith(".png"):
                print(filename)
                s3.upload_file('/tmp/' + filename, out_bucket, filename)

        return {
            'statusCode': 200,
            'body': json.dumps('Hello from Lambda!')
        }
    except Exception as e:
        raise e

    # TODO implement

