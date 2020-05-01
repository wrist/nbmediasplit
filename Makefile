.PHONY: test

test:
	poetry run nbmediasplit -n test/test.ipynb -i img -w wav -o test/test.converted.ipynb
	mv wav test/
	mv img test/
