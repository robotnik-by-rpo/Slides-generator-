export .env
.PHONY: install, test

pip3 = .venv/bin/pip3

venv:
	python3 -m venv .venv
	. .venv/bin/activate

install: venv
	${pip3} install --upgrade pip && \
	${pip3} install -r requirements.txt

test: install
	pytest tests -v

docker-build:
	docker compose build

docker-up:


e:
	${pip3} install -e .