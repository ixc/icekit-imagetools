from __future__ import print_function

import setuptools
import sys

# Convert README.md to reStructuredText.
if {'bdist_wheel', 'sdist'}.intersection(sys.argv):
    try:
        import pypandoc
    except ImportError:
        print('WARNING: You should install `pypandoc` to convert `README.md` '
              'to reStructuredText to use as long description.',
              file=sys.stderr)
    else:
        print('Converting `README.md` to reStructuredText to use as long '
              'description.')
        long_description = pypandoc.convert('README.md', 'rst')

setuptools.setup(
    name='imagetools',
    use_scm_version={'version_scheme': 'post-release'},  # Get version from git tags.
    author='Interaction Consortium',
    author_email='studio@interaction.net.au',
    url='https://github.com/ixc/icekit-imagetools',
    description='Doing cool things to images since 2016',
    long_description=locals().get('long_description', ''),
    license='MIT',
    packages=setuptools.find_packages(),
    include_package_data=True,
    install_requires=[
        'Pillow >= 3.0.0',
    ],
    # extras_require=[
    #     ...
    # ],
    setup_requires=['setuptools_scm'],
)
