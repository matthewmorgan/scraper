import boto3
import json


def copy_to_s3(bucket='ithaka-labs-data', filename='in.txt'):
    print('Copying local {filename} to s3 {bucket}'.format(filename=filename, bucket=bucket))
    s3 = boto3.resource('s3')
    s3.Bucket(bucket).put_object(Key=filename, Body=open(filename, 'rb'))


def read_from_local(filename='in.txt'):
    print('Reading from local file {}'.format(filename))
    with open(filename, 'r') as infile:
        results = json.load(infile)
    return results


def write_to_local(data=None, filename='out.txt'):
    print('Writing results to local file {}'.format(filename))
    data = data or []
    with open(filename, 'w') as outfile:
        json.dump(data, outfile)
