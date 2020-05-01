.PHONY: test

test:
	poetry run nbmediasplit -n test/test.ipynb -i test/img -w test/wav -o test/test.converted.ipynb --img-prefix img --wav-prefix wav

clean:
	rm -rf test/wav
	rm -rf test/img
	rm test/test.converted.ipynb
