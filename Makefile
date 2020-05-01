.PHONY: test

test:
	# image extract test
	poetry run nbmediasplit -n test/test.ipynb -i test/img
	ls test/img
	rm -rf test/img
	# audio extract test
	poetry run nbmediasplit -n test/test.ipynb -w test/wav
	ls test/wav
	rm -rf test/wav
	# both extract test
	poetry run nbmediasplit -n test/test.ipynb -i test/img -w test/wav
	ls test/img
	ls test/wav
	rm -rf test/img
	rm -rf test/wav
	poetry run nbmediasplit -n test/test.ipynb -i test/img -w test/wav -o test/test.converted.ipynb --img-prefix img --wav-prefix wav
	ls test/img
	ls test/wav

clean:
	rm -rf test/wav
	rm -rf test/img
	rm test/test.converted.ipynb
