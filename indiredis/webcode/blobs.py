
from base64 import urlsafe_b64encode, urlsafe_b64decode

from os.path import isfile


def _safekey(key):
    """Provides a base64 encoded key from a given key"""
    b64binarydata = urlsafe_b64encode(key.encode('utf-8')).rstrip(b"=")  # removes final '=' padding
    return b64binarydata.decode('ascii')


def _fromsafekey(safekey):
    """Decodes a base64 encoded key"""
    b64binarydata = safekey.encode('utf-8') # get the received data and convert to binary
    # add padding
    b64binarydata = b64binarydata + b"=" * (4-len(b64binarydata)%4)
    return urlsafe_b64decode(b64binarydata).decode('utf-8') # b64 decode, and convert to string


def setup(skicall):
    "Fills in the blobs management page"

    if not skicall.ident_data:
        # there is no device properties information
        skicall.page_data['backtoproperties', 'show'] = False

    blob_folder = skicall.proj_data["blob_folder"]
    if not blob_folder:
        skicall.page_data['nothingfound', 'show'] = True
        skicall.page_data['bloblinks', 'show'] = False
        return
    blobfiles = [f.name for f in blob_folder.iterdir() if f.is_file()]
    if not blobfiles:
        skicall.page_data['nothingfound', 'show'] = True
        skicall.page_data['bloblinks', 'show'] = False
        return
    skicall.page_data['nothingfound', 'show'] = False
    skicall.page_data['bloblinks', 'show'] = True

    # The widget has links formed from a list of lists
    # 0 : The url, label or ident of the target page of the link
    # 1 : The displayed filename of the link
    # 2 : If True, download attribute is set in the link    

    blobfiles.sort(reverse=True)
    bloblinks = []
    for bf in blobfiles:
        # create a link to blobs/blobfile
        bloblinks.append([ "blobs/" + bf, bf, True])
    skicall.page_data['bloblinks', 'file_links'] = bloblinks




