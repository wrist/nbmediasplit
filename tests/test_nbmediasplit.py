from nbmediasplit import __version__
from nbmediasplit import nbmediasplit

import pytest
import os

cwd = os.path.dirname(__file__)

input_ipynb = "{0}/../test/test.ipynb".format(cwd)
out_dir = "{0}/out".format(cwd)

def test_version():
    assert __version__ == '0.1.2'


@pytest.fixture
def splitter():
    splitter = nbmediasplit.NBMediaSplitter(input_ipynb)
    yield splitter

    # tear down
    os.rmdir(out_dir)


def test_set_img_out_dir(splitter):
    assert not os.path.exists(out_dir)
    splitter.set_img_out_dir(out_dir)
    assert os.path.exists(out_dir)
