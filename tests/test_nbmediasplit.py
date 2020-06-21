from nbmediasplit import __version__
from nbmediasplit import nbmediasplit

import pytest
import os
import shutil
import json
import filecmp
import subprocess

import bs4

cwd = os.path.dirname(__file__)

INPUT_DIR = "{0}/input".format(cwd)
input_ipynb = "{0}/test.ipynb".format(INPUT_DIR)
out_dir = "{0}/output".format(cwd)
output_ipynb = "{0}/test.converted.ipynb".format(out_dir)
IMG_OUT_DIR = "{0}/img".format(out_dir)
WAV_OUT_DIR = "{0}/wav".format(out_dir)

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

LIST_IMAGE_CODE_CELL = r"""
  {
   "cell_type": "code",
   "execution_count": 3,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "image/png": [
       "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YA\n",
       "AAAASUVORK5CYII=\n"
       ],
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
    "# assume matplotlib plot (embeded as list)"
   ]
  }
"""

# embeded audio wave is the first 1pt of 1kHz sin wave in FS48kHz
AUDIO_CODE_CELL = r"""
  {
   "cell_type": "code",
   "execution_count": 2,
   "metadata": {},
   "outputs": [
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      ""
     ]
    },
    {
     "data": {
      "text/html": [
       "\n",
       "                <audio  controls=\"controls\" >\n",
       "                    <source src=\"data:audio/wav;base64,UklGRiYAAABXQVZFZm10IBAAAAABAAEAgLsAAAB3AQACABAAZGF0YQIAAAAAAA==\" type=\"audio/wav\" />\n",
       "                    Your browser does not support the audio element.\n",
       "                </audio>\n",
       "              "
      ],
      "text/plain": [
       "<IPython.lib.display.Audio object>"
      ]
     },
     "execution_count": 2,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "# assume embeded by IPython.display.Audio"
   ]
  }
"""

def clean_outdir():
    if os.path.exists(out_dir):
        shutil.rmtree(out_dir)

def test_version():
    assert __version__ == '0.2.0'


@pytest.fixture
def splitter():
    splitter = nbmediasplit.NBMediaSplitter(input_ipynb)
    clean_outdir()

    yield splitter

    # tear down
    clean_outdir()


@pytest.fixture
def empty_splitter():
    empty_splitter = nbmediasplit.NBMediaSplitter(None)
    clean_outdir()

    yield empty_splitter

    # tear down
    clean_outdir()


def test_set_img_out_dir(splitter):
    assert not os.path.exists(out_dir)
    splitter.set_img_out_dir(IMG_OUT_DIR)
    assert os.path.exists(IMG_OUT_DIR)

def test_set_wav_out_dir(splitter):
    assert not os.path.exists(out_dir)
    splitter.set_img_out_dir(WAV_OUT_DIR)
    assert os.path.exists(WAV_OUT_DIR)

def test_processing_image(empty_splitter):
    cell = json.loads(IMAGE_CODE_CELL)
    empty_splitter.set_img_out_dir(IMG_OUT_DIR)

    png_fname = empty_splitter._processing_image(cell["outputs"][0]["data"]["image/png"])
    exp_fname = "{0}/0.png".format(IMG_OUT_DIR)

    assert png_fname == exp_fname
    # check png_bin_dict
    assert exp_fname in empty_splitter.png_bin_dict
    # FIXME: check png_bin_dict[png_fname] binary is whether expected image or not

def test_processing_list_image(empty_splitter):
    cell = json.loads(LIST_IMAGE_CODE_CELL)
    empty_splitter.set_img_out_dir(IMG_OUT_DIR)

    png_fname = empty_splitter._processing_image(cell["outputs"][0]["data"]["image/png"])
    exp_fname = "{0}/0.png".format(IMG_OUT_DIR)

    assert png_fname == exp_fname
    # check png_bin_dict
    assert exp_fname in empty_splitter.png_bin_dict
    # FIXME: check png_bin_dict[png_fname] binary is whether expected image or not


def test_processing_audio(empty_splitter):
    cell = json.loads(AUDIO_CODE_CELL)
    empty_splitter.set_wav_out_dir(WAV_OUT_DIR)

    for i, output in enumerate(cell["outputs"]):
        if empty_splitter._is_output_include_html(output):
            html = "".join(output["data"]["text/html"])
            soup = bs4.BeautifulSoup(html, features="lxml")
            audio_tag = soup.find("audio")

            if audio_tag:
                if empty_splitter.wav_out_dir is not None:
                    new_tag = empty_splitter._processing_bs4_audio_tag(audio_tag)

                    exp_fname = "{0}/0.wav".format(WAV_OUT_DIR)
                    exp_tag = '<audio controls preload=\"none\"><source src=\"{0}\" type=\"audio/wav\" /></audio>'.format(exp_fname)

                    assert new_tag == exp_tag
                    assert exp_fname in empty_splitter.wav_bin_dict

    empty_splitter.save_waves()
    assert filecmp.cmp(exp_fname, "{0}/sin1kHz_1pt_FS48kHz.wav".format(INPUT_DIR))


def test_command_line():
    """same as `inv cuitest`"""
    clean_outdir()

    # image extract test
    result = subprocess.run(["poetry", "run", "nbmediasplit", input_ipynb, "-i", IMG_OUT_DIR])

    assert result.returncode == 0
    assert os.path.exists(out_dir)
    assert os.path.exists(IMG_OUT_DIR)
    assert not os.path.exists(WAV_OUT_DIR)

    image_list = os.listdir(IMG_OUT_DIR)
    assert len(image_list) > 0

    clean_outdir()

    # audio extract test
    result = subprocess.run(["poetry", "run", "nbmediasplit", input_ipynb, "-w", WAV_OUT_DIR])

    assert result.returncode == 0
    assert os.path.exists(out_dir)
    assert os.path.exists(WAV_OUT_DIR)
    assert not os.path.exists(IMG_OUT_DIR)

    audio_list = os.listdir(WAV_OUT_DIR)
    assert len(audio_list) > 0

    clean_outdir()

    # both extract test
    result = subprocess.run(["poetry", "run", "nbmediasplit", input_ipynb, "-i", IMG_OUT_DIR, "-w", WAV_OUT_DIR])

    assert result.returncode == 0
    assert os.path.exists(out_dir)
    assert os.path.exists(WAV_OUT_DIR)
    assert os.path.exists(IMG_OUT_DIR)

    image_list = os.listdir(IMG_OUT_DIR)
    assert len(image_list) > 0
    audio_list = os.listdir(WAV_OUT_DIR)
    assert len(audio_list) > 0

    clean_outdir()

    # both extract and convert ipynb test
    assert not os.path.exists(output_ipynb)

    result = subprocess.run(["poetry", "run", "nbmediasplit", input_ipynb,
        "-i", IMG_OUT_DIR, "-w", WAV_OUT_DIR, "-o", output_ipynb, "--img-prefix", "img", "--wav-prefix", "wav"])

    assert result.returncode == 0
    assert os.path.exists(out_dir)
    assert os.path.exists(WAV_OUT_DIR)
    assert os.path.exists(IMG_OUT_DIR)
    assert os.path.exists(output_ipynb)

    image_list = os.listdir(IMG_OUT_DIR)
    assert len(image_list) > 0
    audio_list = os.listdir(WAV_OUT_DIR)
    assert len(audio_list) > 0

    clean_outdir()
