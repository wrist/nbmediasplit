#!/usr/bin/env python
# vim:fileencoding=utf-8

import os
import json
import base64
import copy
import logging
from pprint import pprint as pp

import bs4
import click

# logging.basicConfig(level=logging.DEBUG)


def mkdir_p(target_dir):
    """mkdir recursively if not exists"""
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)


class NBMediaSplitter:
    def __init__(self, ipynb_file):
        self.png_bin_dict = {}
        self.wav_bin_dict = {}
        self.png_count = 0
        self.wav_count = 0
        self.ipynb_file = ipynb_file

        self.encoding = "utf-8"

        self.img_out_dir = None
        self.wav_out_dir = None

        self.img_prefix = None
        self.wav_prefix = None

        self.copied_ipynb_json = None

    def _is_code_cell(self, cell):
        return cell["cell_type"] == "code"

    def _is_output_include_images(self, output):
        return ("data" in output) and ("image/png" in output["data"])

    def _is_output_include_html(self, output):
        return ("data" in output) and ("text/html" in output["data"])

    def _save_binaries(self, fname_bin_dict):
        for fname, binary in fname_bin_dict.items():
            with open(fname, "wb") as wfp:
                wfp.write(binary)

    def _processing_image(self, data, image_base64):
        png_bin = base64.b64decode(image_base64)

        png_fname = "{0}/{1}.png".format(self.img_out_dir, self.png_count)
        self.png_bin_dict[png_fname] = png_bin

        if self.img_prefix is not None:
            png_fname = "{0}/{1}.png".format(self.img_prefix, self.png_count)

        self.png_count += 1

        # remove "image/png" entry and add "text/html" entry to add img tag
        new_html = data.get("text/html", [])
        img_tag = '<img src=\"{0}\" />'.format(png_fname)
        new_html.append(img_tag)

        logging.debug(new_html)

        return new_html

    def _processing_bs4_audio_tag(self, audio_tag):
        src_tag = audio_tag.find("source")
        wav_b64 = src_tag.get("src").split(",")[-1]
        wav_bin = base64.b64decode(wav_b64)

        wav_fname = "{0}/{1}.wav".format(self.wav_out_dir, self.wav_count)
        self.wav_bin_dict[wav_fname] = wav_bin

        if self.wav_prefix is not None:
            wav_fname = "{0}/{1}.wav".format(self.wav_prefix, self.wav_count)

        self.wav_count += 1

        # update content in "text/html" with new audio tag
        new_tag = '<audio controls preload=\"none\"><source src=\"{0}\" type=\"audio/wav\" /></audio>'.format(wav_fname)
        # new_tag = '<audio controls src=\"{0}\"></audio>'.format(wav_fname)

        logging.debug(new_tag)

        return new_tag

    def set_encoding(self, encoding):
        self.encoding = encoding

    def set_img_out_dir(self, img_out_dir):
        mkdir_p(img_out_dir)
        self.img_out_dir = img_out_dir

    def set_wav_out_dir(self, wav_out_dir):
        mkdir_p(wav_out_dir)
        self.wav_out_dir = wav_out_dir

    def set_img_prefix(self, img_prefix):
        self.img_prefix = img_prefix

    def set_wav_prefix(self, wav_prefix):
        self.wav_prefix = wav_prefix

    def save_images(self):
        self._save_binaries(self.png_bin_dict)

    def save_waves(self):
        self._save_binaries(self.wav_bin_dict)

    def extract_and_convert_ipynb(self):
        with open(self.ipynb_file, "r", encoding=self.encoding) as fp:
            ipynb_json = json.load(fp)
            self.copied_ipynb_json = copy.deepcopy(ipynb_json)

            del self.copied_ipynb_json["cells"]
            self.copied_ipynb_json["cells"] = []

            for cell in ipynb_json["cells"]:
                new_cell = copy.deepcopy(cell)

                if self._is_code_cell(cell):
                    for i, output in enumerate(cell["outputs"]):
                        if self._is_output_include_images(output):
                            if self.img_out_dir is not None:
                                new_html = self._processing_image(output["data"], output["data"]["image/png"])

                                del new_cell["outputs"][i]["data"]["image/png"]
                                new_cell["outputs"][i]["data"]["text/html"] = new_html

                        if self._is_output_include_html(output):
                            html = "".join(output["data"]["text/html"])
                            soup = bs4.BeautifulSoup(html, features="lxml")
                            audio_tag = soup.find("audio")
                            if audio_tag:
                                if self.wav_out_dir is not None:
                                    new_tag = self._processing_bs4_audio_tag(audio_tag)
                                    new_cell["outputs"][i]["data"]["text/html"] = new_tag
                            else:
                                logging.debug("no audio tag in {0}".format(html))

                self.copied_ipynb_json["cells"].append(new_cell)

    def save_new_json(self, new_ipynb_filename):
        with open(new_ipynb_filename, "w") as wfp:
            json.dump(self.copied_ipynb_json, wfp, ensure_ascii=False, indent=4, sort_keys=True)


@click.command(help='extract base64 encoded image and pcm and save them into specified directories.')
@click.option('-n', '--ipynb', 'ipynb_file', type=str, help='input ipynb file path', required=True)
@click.option('-i', '--imgdir', 'img_out_dir', type=str, help='directory to store image', required=False)
@click.option('-w', '--wavdir', 'wav_out_dir', type=str, help='directory to store audio', required=False)
@click.option('-o', '--output', 'new_ipynb_filename', type=str, help='output ipynb file path', required=False)
@click.option('-e', '--encoding', 'encoding', type=str, help='input ipynb encoding', required=False)
@click.option('--img-prefix', 'img_prefix', type=str, help='path prefix for src attribute of img tag', required=False)
@click.option('--wav-prefix', 'wav_prefix', type=str,
              help='path prefix for src attribute of source tag under audio tag', required=False)
def main(ipynb_file, img_out_dir=None, wav_out_dir=None, new_ipynb_filename=None, img_prefix=None, wav_prefix=None, encoding="utf-8"):
    splitter = NBMediaSplitter(ipynb_file)

    splitter.set_encoding(encoding)

    if img_out_dir is not None:
        splitter.set_img_out_dir(img_out_dir)
    if wav_out_dir is not None:
        splitter.set_wav_out_dir(wav_out_dir)

    if img_prefix is not None:
        splitter.set_img_prefix(img_prefix)
    if wav_prefix is not None:
        splitter.set_wav_prefix(wav_prefix)

    splitter.extract_and_convert_ipynb()

    if img_out_dir is not None:
        splitter.save_images()
    if wav_out_dir is not None:
        splitter.save_waves()

    if new_ipynb_filename is not None:
        splitter.save_new_json(new_ipynb_filename)


if __name__ == '__main__':
    main()
