from PIL import Image, ImageCms
from tempfile import NamedTemporaryFile
import os

__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

with open(os.path.join(__location__, 'srgb.icc')) as srgb:
    SRGB_BYTES = srgb.read()
SRGB_PROFILE = ImageCms.createProfile("sRGB")


def convert_to_srgb(infile, outfile):
    """
    Process an image file of unknown color profile.
    Transform to sRGB profile, convert the color space to RGB, write the image
    and return the path to the result.

    :param infile: the path to a file with arbitrary colorspace and color profile
    :param outfile: the destination path to write to
    :return: None
    """

    img = Image.open(infile)
    # get its color profile, write to a temp file
    # icc_file, icc_path = tempfile.mkstemp(suffix='.icc')
    icc_file = NamedTemporaryFile(suffix='.icc', delete=True)
    # with open(icc_path, 'w') as f:

    profile = img.info.get('icc_profile')
    if profile:
        icc_file.write(profile)
        icc_file.flush()
        img = ImageCms.profileToProfile(img, icc_file.name, SRGB_PROFILE, outputMode="RGB")

    img.save(outfile, icc_profile=SRGB_BYTES)

    icc_file.close()
    return outfile