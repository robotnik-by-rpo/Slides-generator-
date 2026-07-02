export .env
.PHONY: install, test, demo, e

pip3 = .venv/bin/pip3

venv:
	python3 -m venv .venv
	. .venv/bin/activate

install: venv
	${pip3} install --upgrade pip && \
	${pip3} install -r requirements.txt

test: install
	pytest tests -v

test-cov:
	pytest --cov=.

docker-build:
	docker compose build

docker-up:
	docker compose up -d

docker-down:
	docker compose down -v

docker-no-cache:
	docker compose build --no-cache

demo:
	docker compose run --rm slider-generator  --plan data/examples/simple.md   --output a  --format all

demo-update:
	docker compose run --rm slider-generator  --update output/a --format all

run-cli:
	@if [ -z "$(PLAN)" ]; then \
		echo "Error: PLAN is required. Usage: make run-cli PLAN=path/to/lesson.md OUTPUT=path/to/output"; \
		exit 1; \
	fi
	@if [ -z "$(OUTPUT)" ]; then \
		echo "Error: OUTPUT is required. Usage: make run-cli PLAN=path/to/lesson.md OUTPUT=path/to/output"; \
		exit 1; \
	fi
	docker compose run --rm slider-generator  --plan $(PLAN)   $(OUTPUT) a  --format all

update-cli:
	@if [ -z "$(DIR)" ]; then \
		echo "Error: DIR is required. Usage: make update-cli DIR=path/to/directory FORMAT=pdf"; \
		exit 1; \
	fi
	docker compose run --rm slider-generator  --update $(DIR) --format $(or $(FORMAT),all)
e:
	${pip3} install -e .