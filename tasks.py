from invoke import task

import os
import shutil

TEST_INPUT = "tests/input/test.ipynb"
TEST_OUTPUT = "tests/output/test.converted.ipynb"
IMG_OUT_DIR = "tests/output/img"
WAV_OUT_DIR = "tests/output/wav"

@task
def clean(c):
    """clean generated files"""
    print("remove {0}, {1}, {2} if exists".format(IMG_OUT_DIR, WAV_OUT_DIR, TEST_OUTPUT))
    if os.path.exists(IMG_OUT_DIR):
        shutil.rmtree(IMG_OUT_DIR)
    if os.path.exists(WAV_OUT_DIR):
        shutil.rmtree(WAV_OUT_DIR)
    if os.path.exists(TEST_OUTPUT):
        os.remove(TEST_OUTPUT)

@task(pre=[clean])
def pytest(c):
    """execute pytest"""
    c.run("poetry run pytest")

@task(pre=[clean])
def cuitest(c, debug=False):
    """execute cui script test"""
    debug_arg = "-d" if debug else ""
    print("image extract test")
    c.run("poetry run nbmediasplit -n {0} -i {1} {2}".format(TEST_INPUT, IMG_OUT_DIR, debug_arg))
    print(os.listdir(IMG_OUT_DIR))
    shutil.rmtree(IMG_OUT_DIR)

    print("audio extract test")
    c.run("poetry run nbmediasplit -n {0} -w {1} {2}".format(TEST_INPUT, WAV_OUT_DIR, debug_arg))
    print(os.listdir(WAV_OUT_DIR))
    shutil.rmtree(WAV_OUT_DIR)

    print("both extract test")
    c.run("poetry run nbmediasplit -n {0} -i {1} -w {2} {3}".format(TEST_INPUT, IMG_OUT_DIR, WAV_OUT_DIR, debug_arg))
    print(os.listdir(IMG_OUT_DIR))
    print(os.listdir(WAV_OUT_DIR))
    shutil.rmtree(IMG_OUT_DIR)
    shutil.rmtree(WAV_OUT_DIR)

    print("both extract and convert ipynb test")
    c.run("poetry run nbmediasplit -n {0} -i {1} -w {2} -o {3} --img-prefix img --wav-prefix wav {4}".format(TEST_INPUT, IMG_OUT_DIR, WAV_OUT_DIR, TEST_OUTPUT, debug_arg))
    print(os.listdir(IMG_OUT_DIR))
    print(os.listdir(WAV_OUT_DIR))
    print(os.listdir(os.path.dirname(TEST_OUTPUT)))


@task(pre=[pytest, cuitest])
def test(c):
    print("Executed pytest and cuitest.")

@task
def format(c):
    """format nbmediasplit.py"""
    c.run("poetry run autopep8 -a -i src/nbmediasplit/nbmediasplit.py")

@task
def deploy(c):
    """deplay to pypi"""
    c.run("poetry build")
    c.run("poetry publish")

@task
def deploytest(c):
    """deplay to testpypi"""
    c.run("poetry build")
    c.run("poetry publish -r testpypi")
