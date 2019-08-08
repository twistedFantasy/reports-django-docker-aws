import os
from io import BytesIO

import magic
import boto3
from botocore.exceptions import ClientError

from srt.core.helpers import delimit


S3_BASE_URL = 'https://%s.s3.amazonaws.com'


class S3:

    def __init__(self, key, secret, bucket, dir='', region='us-east-1'):
        """
        The optional dir let's you set a base directory for all of the methods. For example:

          s3 = S3(key, secret, 'mybucket', dir='mydir')
          path = s3.download('/tmp/myfile.txt')

        will download the s3 object from s3://mybucket/mydir/myfile.txt to /tmp/myfile.txt.
        """
        self.key = key
        self.secret = secret
        self.bucket = bucket
        self.dir = (os.path.normpath(dir) + os.path.sep) if dir else ''
        self.region = region
        self.client = None

    def connect(self):
        if not self.client:
            self.client = boto3.client('s3',
                aws_access_key_id=self.key,
                aws_secret_access_key=self.secret,
                region_name=self.region,
                use_ssl=True)

    def list(self, remote=None, include_dirs=True, include_files=True, delimiter='/'):
        self.connect()
        items = []
        remote = self.get_remote(remote).rstrip('/') + '/'

        # collect all
        params = {'Bucket': self.bucket, 'Prefix': remote, 'Delimiter': delimiter}
        truncated = True
        while truncated:
            response = self.client.list_objects_v2(**params)
            if response.get('KeyCount'):
                if response.get('Contents'):
                    items.extend(response['Contents'])
                if response.get('CommonPrefixes'):
                    items.extend(response['CommonPrefixes'])
            truncated = response['IsTruncated']
            if truncated:
                params['ContinuationToken'] = response['NextContinuationToken']

        # return all
        for item in items:
            is_dir = item.get('Prefix')
            if is_dir:
                if include_dirs:
                    yield os.path.basename(item['Prefix'][:-1])
            else:
                if include_files:
                    yield os.path.basename(item['Key'])

    def upload(self, src, remote=None, public=False, content_type=None, download_filename=None, encoding='utf-8'):
        """ src can be a file object, a file path, or content in string/bytes format. """
        self.connect()
        needs_closing = True

        # prepare
        remote = self.get_remote(remote or os.path.basename(src))
        content_type = content_type or self.get_mimetype(src)
        if hasattr(src, 'seek'):
            needs_closing = False
        elif isinstance(src, bytes):
            src = BytesIO(src)
        elif isinstance(src, str):
            if os.path.exists(src):
                src = open(src, 'rb')  # convert path to file object
            else:
                src = BytesIO(src.encode(encoding))
        else:
            raise Exception('Unexpected input type: %s' % type(src))

        # upload
        params = {
            'ACL': 'public-read' if public else 'private',
            'ContentType': content_type,
        }
        if download_filename:
            params['ContentDisposition'] = 'attachment; filename="%s"' % download_filename
        try:
            self.client.upload_fileobj(src, self.bucket, remote, ExtraArgs=params)
        finally:
            if needs_closing:
                src.close()

    def download(self, local, remote=None):
        self.connect()
        remote = self.get_remote(remote or os.path.basename(local))
        self.client.download_file(Bucket=self.bucket, Key=remote, Filename=local)

    def download_object(self, remote=None):
        self.connect()
        remote = self.get_remote(remote)
        temp = BytesIO()
        self.client.download_fileobj(Bucket=self.bucket, Key=remote, Fileobj=temp)
        return temp.getvalue()

    def last_modified(self, remote):
        self.connect()
        remote = self.get_remote(remote)
        metadata = self.client.head_object(Bucket=self.bucket, Key=remote)
        return metadata['LastModified']

    def exists(self, remote):
        try:
            self.last_modified(remote)
            return True
        except ClientError:
            return False

    def delete(self, remote):
        self.connect()
        remote = self.get_remote(remote)
        self.client.delete_object(Bucket=self.bucket, Key=remote)

    def get_mimetype(self, src):
        if isinstance(src, str):
            try:
                mimetype = magic.from_file(src, mime=True)
            except FileNotFoundError:
                mimetype = 'text/plain'
        else:
            mimetype = magic.from_buffer(src, mime=True)
        return mimetype

    def get_remote(self, path):
        if not path:
            path = os.path.dirname(self.dir) or ''
        elif self.dir:
            path = os.path.join(self.dir, path)
        return path

    def get_url(self, path):
        parts = [S3_BASE_URL % self.bucket, self.get_remote(path)]
        return delimit([part.strip('/') for part in parts], sep='/')
