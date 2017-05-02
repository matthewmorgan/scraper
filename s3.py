import os

from boto.exception import S3ResponseError, S3CreateError
from boto.s3.key import Key
from boto.s3.connection import S3Connection

import io


class BucketNotFound(Exception):
    pass


class BucketCreationError(Exception):
    pass


def create_bucket(conn, bucket_name):
    """Create bucket in S3 if possible"""

    bucket = None
    print('Attempting to create bucket \'{}\'...'.format(bucket_name))

    try:
        conn.create_bucket(bucket_name)
        print('Bucket \'{}\' created'.format(bucket_name))
    except S3CreateError:
        raise BucketCreationError('A bucket named \'{}\' already exists!'.format(bucket_name))
    except S3ResponseError:
        raise BucketCreationError('Unable to create bucket. You may not have permission to create S3 buckets at this time.')

    return bucket


def get_bucket(conn, bucket_name, create=False):
    """Get bucket from S3"""

    bucket = None

    try:
        bucket = conn.get_bucket(bucket_name)
    except S3ResponseError:
        if create:
            bucket = create_bucket(conn, bucket_name)
        else:
            raise BucketNotFound('The bucket name you specified may not exist, or your credentials are invalid. Use --create-bucket to attempt creation of the specified bucket')

    return bucket


def recursive_upload(bucket, version, path):
    if os.path.exists(path):
        paths = []
        for (trunk, branches, leaves) in os.walk(path):
            paths.extend([os.path.join(trunk, leaf) for leaf in leaves])

        for path in paths:
            key = Key(bucket)
            key.key = os.path.join(version, path)
            print('Uploading {} to s3://{}/{}'.format(path, bucket.name, key.key))
            key.set_contents_from_filename(path, cb=io.print_upload_progress)
    else:
        print('Directory \'{}\' does not exist! Skipping.'.format(path))


def connect():
    return S3Connection()

