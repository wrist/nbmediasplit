#!/usr/bin/env python
# vim:fileencoding=utf-8

"""extract base64 encoded image and pcm and save them into specified directories.
   [usage] $ nbmediasplit ipynb_file img_dir wav_dir
"""

import os
import json
import base64
import copy
from pprint import pprint as pp

import bs4
import click


def mkdir_p(target_dir):
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)


class IpynbController:
    def __init__(self, ipynb_file):
        self.png_bin_dict = {}
        self.wav_bin_dict = {}
        self.png_count = 0
        self.wav_count = 0
        self.ipynb_file = ipynb_file

        self.img_out_dir = ""
        self.wav_out_dir = ""

        self.copied_ipynb_json = None


    def is_code_cell(self, cell):
        return cell["cell_type"] == "code"


    def is_output_include_images(self, output):
        return ("data" in output) and ("image/png" in output["data"])


    def is_output_include_html(self, output):
        return ("data" in output) and ("text/html" in output["data"])


    def save_binaries(self, fname_bin_dict):
        for fname, binary in fname_bin_dict.items():
            with open(fname, "wb") as wfp:
                wfp.write(binary)


    def save_images(self):
        self.save_binaries(self.png_bin_dict)


    def save_waves(self):
        self.save_binaries(self.wav_bin_dict)


    def processing_image(self, data, image_base64):
        png_bin = base64.b64decode(image_base64)
        png_fname = "{0}/{1}.png".format(self.img_out_dir, self.png_count)
        self.png_bin_dict[png_fname] = png_bin
        self.png_count += 1

        # remove "image/png" entry and add "text/html" entry to add img tag
        new_html = data.get("text/html", [])
        # img_tag = '<img src=\"/{0}\" />'.format(png_fname)  # for blog
        img_tag = '<img src=\"{0}\" />'.format(png_fname)
        new_html.append(img_tag)
        return new_html


    def processing_bs4_audio_tag(self, audio_tag):
        src_tag = audio_tag.find("source")
        wav_b64 = src_tag.get("src").split(",")[-1]
        wav_bin = base64.b64decode(wav_b64)
        wav_fname = "{0}/{1}.wav".format(self.wav_out_dir, self.wav_count)
        self.wav_bin_dict[wav_fname] = wav_bin
        self.wav_count += 1

        # update content in "text/html" with new audio tag
        new_tag = '<audio controls preload=\"none\"><source src=\"{0}\" type=\"audio/wav\" /></audio>'.format(wav_fname.replace("files", ""))
        # new_tag = '<audio controls src=\"{0}\"></audio>'.format(wav_fname.replace("files", ""))
        return new_tag


    def convert_and_save_ipynb(self, img_out_dir, wav_out_dir):
        self.img_out_dir = img_out_dir
        self.wav_out_dir = wav_out_dir
        with open(self.ipynb_file, "r") as fp:
            ipynb_json = json.load(fp)
            self.copied_ipynb_json = copy.deepcopy(ipynb_json)

            del self.copied_ipynb_json["cells"]
            self.copied_ipynb_json["cells"] = []

            for cell in ipynb_json["cells"]:
                new_cell = copy.deepcopy(cell)

                if self.is_code_cell(cell):
                    for j, output in enumerate(cell["outputs"]):
                        if self.is_output_include_images(output):
                            new_html = self.processing_image(output["data"], output["data"]["image/png"])

                            del new_cell["outputs"][j]["data"]["image/png"]
                            new_cell["outputs"][j]["data"]["text/html"] = new_html

                        if self.is_output_include_html(output):
                            html = "".join(output["data"]["text/html"])
                            soup = bs4.BeautifulSoup(html, features="lxml")
                            audio_tag = soup.find("audio")
                            if audio_tag:
                                new_tag = self.processing_bs4_audio_tag(audio_tag)
                                new_cell["outputs"][j]["data"]["text/html"] = new_tag
                            else:
                                print("no audio tag")

                self.copied_ipynb_json["cells"].append(new_cell)


    def save_new_json(self, new_ipynb_filename):
        with open(new_ipynb_filename, "w") as wfp:
            json.dump(self.copied_ipynb_json, wfp, ensure_ascii=False, indent=4, sort_keys=True)


@click.command(help='extract base64 encoded image and pcm and save them into specified directories.')
@click.option('-n', '--ipynb', 'ipynb_file', type=str, help='input ipynb file', required=True)
@click.option('-i', '--imgdir', 'img_out_dir', type=str, help='directory to store image', required=True)
@click.option('-w', '--wavdir', 'wav_out_dir', type=str, help='directory to store audio', required=True)
def main(ipynb_file, img_out_dir, wav_out_dir):
    # mkdir recursively if not exists
    mkdir_p(img_out_dir)
    mkdir_p(wav_out_dir)

    new_ipynb_filename = ipynb_file + ".new.ipynb"

    ipynb_controller = IpynbController(ipynb_file)

    ipynb_controller.convert_and_save_ipynb(img_out_dir, wav_out_dir)
    ipynb_controller.save_images()
    ipynb_controller.save_waves()
    ipynb_controller.save_new_json(new_ipynb_filename)


if __name__ == '__main__':
    main()
