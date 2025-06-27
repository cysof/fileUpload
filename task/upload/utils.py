# uploads/utils.py
import cloudinary.uploader

def upload_to_cloudinary(file):
    """
    Uploads a file to Cloudinary and returns a dictionary with the upload result, or a dictionary with an "error" key containing a string representation of the error that occurred.

    Parameters
    ----------
    file : file-like object
        The file to upload to Cloudinary.

    Returns
    -------
    dict
        A dictionary with the Cloudinary upload result, or an error message if the upload fails.
    """
    try:
        return cloudinary.uploader.upload(file)
    except Exception as e:
        return {"error": str(e)}
