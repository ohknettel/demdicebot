from .baccarat import *;
from .keno import *;
from .wheel import *;
from PIL.Image import Image;
import io;

def to_bytes(images: typing.Union[Image, typing.List[Image]]):
	_bytes = io.BytesIO();
	if isinstance(images, list):
		images[0].save(
			_bytes,
			save_all=True,
			append_images=images[1:],
			duration=40,
			loop=0,
			disposal=2,
			format="GIF");
	else:
		images.save(_bytes, format="PNG");

	_bytes.seek(0);
	return _bytes;