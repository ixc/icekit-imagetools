from PIL import Image, ImageCms
import tempfile


with open('srgb.icc') as srgb:
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
    icc = tempfile.mkstemp(suffix='.icc')[1]
    with open(icc, 'w') as f:
        f.write(img.info.get('icc_profile'))
    img = ImageCms.profileToProfile(img, icc, SRGB_PROFILE, outputMode="RGB")
    img.save(outfile, icc_profile=SRGB_BYTES)

    return outfile
