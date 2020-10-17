
from base64 import urlsafe_b64encode, urlsafe_b64decode

from os import listdir
from os.path import isfile, join


from skipole import FailPage

from ... import tools

## hiddenfields are
#
# propertyname
# sectionindex

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

    blob_folder = skicall.proj_data["blob_folder"]
    if not blob_folder:
        skicall.page_data['nothingfound', 'show'] = True
        skicall.page_data['bloblinks', 'show'] = False
        return
    blobfiles = [f for f in listdir(blob_folder) if isfile(join(blob_folder, f))]
    if not blobfiles:
        skicall.page_data['nothingfound', 'show'] = True
        skicall.page_data['bloblinks', 'show'] = False
        return
    skicall.page_data['nothingfound', 'show'] = False
    skicall.page_data['bloblinks', 'show'] = True

    # The widget has links formed from a list of lists
    # 0 : The url, label or ident of the target page of the link
    # 1 : The displayed text of the link
    # 2 : If True, ident is appended to link even if there is no get field
    # 3 : The get field data to send with the link


    bloblinks = []
    for bf in blobfiles:
        # create a link to blobs/blobfile
        bloblinks.append([ "blobs/" + bf, bf, False, ""])
    skicall.page_data['bloblinks', 'nav_links'] = bloblinks


def get_blob(skicall):
    "Called by SubmitIterator responder to return a blob"

    urlpath = skicall.path

    blob_folder = skicall.proj_data["blob_folder"]
    if not blob_folder:
        raise FailPage("File not found")
    blobfiles = [f for f in listdir(blob_folder) if isfile(join(blob_folder, f))]
    if not blobfiles:
        raise FailPage("File not found")

    # get required server path
    path = None
    if urlpath.startswith("/blobs/"):
        filename = urlpath[7:]
        if filename not in blobfiles:
            raise FailPage("File not found")
        path = join(blob_folder, filename)
        if not isfile(path):
            raise FailPage("File not found")
        with open(path, 'rb') as f:
            file_data = f.read()
        skicall.page_data['mimetype'] = "application/octet-stream"
        skicall.page_data['content-length'] = str(len(file_data))
        return (file_data,)
    raise FailPage("File not found")





