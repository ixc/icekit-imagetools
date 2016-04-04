"""
Create OpenSeadragon-compatible Deepzoom tilesets from supplied images.

Based in large part on
https://github.com/openzoom/deepzoom.py/blob/develop/deepzoom.py

Adapted to use Django default storage.
"""

import cStringIO
import PIL
import os
from django.core.files.storage import default_storage
from imagetools.zoom.zoom_descriptor import DeepZoomImageDescriptor


RESIZE_FILTERS = {
    'cubic': PIL.Image.CUBIC,
    'bilinear': PIL.Image.BILINEAR,
    'bicubic': PIL.Image.BICUBIC,
    'nearest': PIL.Image.NEAREST,
    'antialias': PIL.Image.ANTIALIAS,
}


class ZoomImageCreator(object):
    def __init__(
        self,
        source,
        tile_size=254,
        tile_overlap=1,
        tile_format='jpg',
        image_quality=0.8,
        resize_filter='antialias',
    ):
        """
        :param source: A filename or file pointer
        :param tile_size: How big to make each tile.
        :param tile_overlap: Overlap of the tiles in pixels (0-10).
        :param tile_format: Image format of the tiles (jpg or png).
        :param image_quality: Quality of the image output (0-1).
        :param resize_filter: Type of filter for resizing (bicubic, nearest, bilinear, antialias (best).
        :return:
        """
        self.tile_size = tile_size
        self.tile_overlap = tile_overlap
        self.tile_format = tile_format
        self.image_quality = image_quality
        self.resize_filter = RESIZE_FILTERS.get(resize_filter, PIL.Image.ANTIALIAS)

        self.image = PIL.Image.open(source)
        self.width, self.height = self.image.size
        self.descriptor = DeepZoomImageDescriptor(
            width=self.width,
            height=self.height,
            tile_size=self.tile_size,
            tile_overlap=self.tile_overlap,
            tile_format=self.tile_format
        )


    def get_image(self, level):
        """Returns the bitmap image at the given level."""
        assert 0 <= level and level < self.descriptor.num_levels, 'Invalid pyramid level'
        width, height = self.descriptor.get_dimensions(level)
        # don't transform to what we already have
        if self.descriptor.width == width and self.descriptor.height == height:
            return self.image
        return self.image.resize((width, height), self.resize_filter)

    def tiles(self, level):
        """Generator for all tiles in the given level. Returns (column, row) of a tile."""
        columns, rows = self.descriptor.get_num_tiles(level)
        for column in xrange(columns):
            for row in xrange(rows):
                yield (column, row)

    def create(
            self,
            destination_path,
            storage=None,
    ):
        """
        Generate a pyramid of Deepzoom tiles based on the given file.

        The path at `destination_path` will be created, and will contain `image_files` - the folder of tiles, and
        image.dzi, the descriptive metadata.

        :param input_file: a File object containing the source image
        :param destination_path: the folder, relative to the given storage, to store the files.
        :return:
        """
        if storage is None:
            storage = default_storage

        for level in xrange(self.descriptor.num_levels):
            level_dir = os.path.join(destination_path, "image_files", str(level))

            try:
                # for local storage, create the parent folder
                p = storage.path(level_dir) # throws an error if not local storage
                os.makedirs(p)
            except OSError: # already exists
                pass
            except NotImplementedError: # not a local storage
                pass

            level_image = self.get_image(level)
            for (column, row) in self.tiles(level):
                bounds = self.descriptor.get_tile_bounds(level, column, row)
                tile_img = level_image.crop(bounds)
                format = self.descriptor.tile_format

                # save the image to an in-memory string
                mem_file = cStringIO.StringIO()
                if self.descriptor.tile_format == 'jpg':
                    jpeg_quality = int(self.image_quality * 100)
                    tile_img.save(mem_file, 'JPEG', quality=jpeg_quality)
                else:
                    tile_img.save(mem_file)

                tile_path = os.path.join(level_dir,
                                         '%s_%s.%s'%(column, row, format))
                print tile_path
                storage.save(tile_path, mem_file)

        # Create descriptor
        self.descriptor.save(os.path.join(destination_path, 'image.dzi'), storage)
