.PHONY: test

test:
	poetry run nbmediasplit -n test/test.ipynb -i test/img -w test/wav
