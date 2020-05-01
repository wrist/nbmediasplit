## nbmediasplit ##

`nbmediasplit` is a script to extract base64 encoded image and audio pcm embedded in .ipynb file and save them into specified directories.

### usage ###

`nbmediasplit -n xxx.ipynb -i image_out_dir -w wav_out_dir -o xxx.converted.ipynb`

or

`nbmediasplit --ipynb xxx.ipynb --imgdir image_out_dir --wavdir wav_out_dir --output xxx.converted.ipynb`

Other options are shown by `nbmediasplit --help`

### note ###

Unless you trust the notebook converted by nbmediasplit in jupyter notebook/jupyter lab, you can't load audio source in Jupyter.
In jupyter lab, go to command pallet in left sidebar(in osx, `shift+cmd+c`) and execute `trust notebook`,
then you'll load embedded audio date written in output of code cell if the source path is correct.
