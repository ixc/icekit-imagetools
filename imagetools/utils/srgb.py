from logging import warning

from PIL import Image, ImageCms
from tempfile import NamedTemporaryFile
import os

__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

# Pillow needs to be built with Color Management
# Install lcms with e.g.
# $ sudo apt-get install liblcms2-dev
# then
# pip install pillow

# TODO: fail gracefully if lcms isn't available
with open(os.path.join(__location__, 'srgb.icc')) as srgb:
    SRGB_BYTES = srgb.read()

try:
    SRGB_PROFILE = ImageCms.createProfile("sRGB")
except ImportError: # probably
    warning("Couldn't create sRGB profile. Try compiling Pillow with little-cms support.")
    SRGB_PROFILE = None


def convert_to_srgb(infile, outfile):
    """
    Process an image file of unknown color profile.
    Transform to sRGB profile, convert the color space to RGB, write the image
    and return the path to the result.

    :param infile: the path to a file with arbitrary colorspace and color profile
    :param outfile: the destination path to write to
    :return: None
    """

    # TODO: issue a warning and just copy the file if lcms isn't available.
    if not SRGB_PROFILE:
        return infile # no-op

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
