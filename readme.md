# nbmediasplit

`nbmediasplit` is a script to extract base64 encoded image and audio pcm embedded in .ipynb file and save them into specified directories.

## usage

### extract image files from ipynb

`nbmediasplit -n input.ipynb -i image_out_dir`

or

`nbmediasplit --ipynb input.ipynb --imgdir image_out_dir`

Above command extract image files from `input.ipynb` and store them to `image_out_dir`.
`-n` or `--ipynb` specifies input ipynb file.
`-i` or `--imgdir` specifies directory to store image files.
Stored filenames of image are named with sequential number(`0.png`, ...).

### extract audio files from ipynb

`nbmediasplit -n input.ipynb -w wav_out_dir`

or

`nbmediasplit --ipynb input.ipynb --wavdir wav_out_dir`

Above command extract audio files from `input.ipynb` and store them to `wav_out_dir`.
`-n` or `--ipynb` specifies input ipynb file.
`-w` or `--wavdir` specifies directory to store audio files.
Stored filenames of audio are named with sequential number(`0.wav`, ...).

### extract image and audio files from ipynb

`nbmediasplit -n input.ipynb -i image_out_dir -w wav_out_dir`

or

`nbmediasplit --ipynb input.ipynb --imgdir image_out_dir --wavdir wav_out_dir`

Above command do below things.

* extract image files from `input.ipynb` and store them to `image_out_dir`
* extract audio files from `input.ipynb` and store them to `wav_out_dir`.

`-n` or `--ipynb` specifies input ipynb file.
`-i` or `--imgdir` specifies directory to store image files.
`-w` or `--wavdir` specifies directory to store audio files.
Stored filenames of image are named with sequential number(`0.png`, ...).
Stored filenames of audio are named with sequential number(`0.wav`, ...).

### extract image and audio files from ipynb and convert ipynb

If you use `-o` or `--output` option like below command,
you can convert `input.ipynb` to new ipynb file which refers stored image files and audio files directly.

`nbmediasplit -n input.ipynb -i image_out_dir -w wav_out_dir -o converted.ipynb`

or

`nbmediasplit --ipynb input.ipynb --imgdir image_out_dir --wavdir wav_out_dir --output converted.ipynb`

Above command extract image files and audio files, and store them to specified directories, and generate new ipynb file `converted.ipynb`.
`converted.ipynb` includes same content as `input.ipynb`, but base64 encoded image and audio data are replaced to html tag refers stored files directly like below.

* image tag
    * `<img src="${image_out_dir}/${n}.png" />`
* audio tag
    * `<audio controls preload="none"><source  src="${wav_out_dir}/${n}.wav" type="audio/wav" /></audio>`

Also, you can use `--img-prefix` and `--wav-prefix` options.
These options can change the path embeded in src attribute of output html like below(actual files are stored `image_out_dir` and `wav_out_dir`).

* image tag
    * `<img src="${img-prefix}/${n}.png" />`
* audio tag
    * `<audio controls preload="none"><source  src="${wav-prefix}/${n}.wav" type="audio/wav" /></audio>`

### show help

`nbmediasplit --help`

## note ##

Unless you trust the notebook converted by nbmediasplit in jupyter, you can't load audio source because of html sanitaization.
To trust notebook in jupyterlab, go to command pallet in left sidebar(on osx, type `shift+cmd+c`) and execute `trust notebook`,
then you'll load audio source if the source path is correct.
