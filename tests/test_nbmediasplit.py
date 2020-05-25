from nbmediasplit import __version__
from nbmediasplit import nbmediasplit

import pytest
import os
import json

cwd = os.path.dirname(__file__)

input_ipynb = "{0}/../test/test.ipynb".format(cwd)
out_dir = "{0}/out".format(cwd)

# embeded image is 1px x 1px black
IMAGE_CODE_CELL = r"""
  {
   "cell_type": "code",
   "execution_count": 3,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "image/png": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII=",
      "text/plain": [
       "<Figure size 1x1 with 1 Axes>"
      ]
     },
     "metadata": {
      "needs_background": "light"
     },
     "output_type": "display_data"
    }
   ],
   "source": [
    "# assume matplotlib plot"
   ]
  }
"""

def test_version():
    assert __version__ == '0.1.2'


@pytest.fixture
def splitter():
    splitter = nbmediasplit.NBMediaSplitter(input_ipynb)
    yield splitter

    # tear down
    os.rmdir(out_dir)


@pytest.fixture
def empty_splitter():
    empty_splitter = nbmediasplit.NBMediaSplitter(None)
    yield empty_splitter

    # tear down
    os.rmdir(out_dir)


def test_set_img_out_dir(splitter):
    assert not os.path.exists(out_dir)
    splitter.set_img_out_dir(out_dir)
    assert os.path.exists(out_dir)


def test_processing_image(empty_splitter):
    cell = json.loads(IMAGE_CODE_CELL)
    empty_splitter.set_img_out_dir(out_dir)
    png_fname = empty_splitter._processing_image(cell["outputs"][0]["data"]["image/png"])
    exp_fname = "{0}/0.png".format(out_dir)
    assert png_fname == exp_fname
    # check png_bin_dict
    assert exp_fname in empty_splitter.png_bin_dict
    # FIXME: check png_bin_dict[png_fname] binary is whether expected image or not
