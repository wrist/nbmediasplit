from invoke import task

import os
import shutil

@task
def pytest(c):
    """execute pytest"""
    c.run("poetry run pytest")

@task
def cuitest(c, debug=False):
    """execute cui script test"""
    debug_arg = "-d" if debug else ""
    print("image extract test")
    c.run("poetry run nbmediasplit -n test/test.ipynb -i test/img {0}".format(debug_arg))
    print(os.listdir("test/img"))
    shutil.rmtree("test/img")

    print("audio extract test")
    c.run("poetry run nbmediasplit -n test/test.ipynb -w test/wav {0}".format(debug_arg))
    print(os.listdir("test/wav"))
    shutil.rmtree("test/wav")

    print("both extract test")
    c.run("poetry run nbmediasplit -n test/test.ipynb -i test/img -w test/wav {0}".format(debug_arg))
    print(os.listdir("test/img"))
    print(os.listdir("test/wav"))
    shutil.rmtree("test/wav")
    shutil.rmtree("test/img")

    print("both extract and convert ipynb test")
    c.run("poetry run nbmediasplit -n test/test.ipynb -i test/img -w test/wav -o test/test.converted.ipynb --img-prefix img --wav-prefix wav {0}".format(debug_arg))

@task
def format(c):
    """format nbmediasplit.py"""
    c.run("poetry run autopep8 -a -i src/nbmediasplit/nbmediasplit.py")

@task
def clean(c):
    """clean generated files"""
    print("remove test/wav, test/img, test/test.converted.ipynb if exists")
    if os.path.exists("test/wav"):
        shutil.rmtree("test/wav")
    if os.path.exists("test/img"):
        shutil.rmtree("test/img")
    if os.path.exists("test/test.converted.ipynb"):
        os.remove("test/test.converted.ipynb")

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
