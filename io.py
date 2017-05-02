import sys

def print_upload_progress(bytes_sent, total_bytes):
    percent_complete = bytes_sent * 100 / total_bytes if total_bytes > 0 else 100
    if percent_complete < 100:
        sys.stdout.write('\r\tUpload {:6.2f}% complete'.format(percent_complete))
        sys.stdout.flush()
    else:
        sys.stdout.write('\r\tUpload {:6.2f}% complete\n'.format(percent_complete))
