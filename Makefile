.PHONY: test

test:
	poetry run nbmediasplit -n test/test.ipynb -i img -w wav
	mv wav test/
	mv img test/
