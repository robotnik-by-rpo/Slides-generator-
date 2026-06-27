export .env
.PHONY: install

pip3 = .venv/bin/pip3

venv:
	python3 -m venv .venv
	. .venv/bin/activate

install: venv
	${pip3} install --upgrade pip && \
	${pip3} install -r requirements.txt

e:
	${pip3} install -e .