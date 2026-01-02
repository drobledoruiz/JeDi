SHELL := /bin/bash
VENV := .venv
PYTHON := $(VENV)/bin/python
SNAKEMAKE := uv run snakemake
DOCKER_IMAGE := jedi-pipeline
DOCKER_SNAKEMAKE := uv run snakemake

# Data directory parameter (required for sample/population targets)
DATA ?=
OUTPUT_SUFFIX ?= /output

.PHONY: help
help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: install
install: sync ## Install Python dependencies using uv

.PHONY: sync
sync: ## Sync dependencies with uv
	@echo "Installing/syncing Python dependencies with uv..."
	uv sync

.PHONY: install-tools
install-tools: ## Install bioinformatics tools (conda/mamba required)
	@echo "Installing bioinformatics tools with conda/mamba..."
	@echo "Make sure conda/mamba is installed and available."
	mamba install -c conda-forge -c bioconda stacks bcftools vcftools samtools bedtools mawk graphviz piawka

.PHONY: clean
clean: ## Remove output directories and logs
	@echo "Cleaning up outputs and logs..."
	cd sample_analysis && rm -rf 00-data 00-reads 01-gstacks 02-bcftools_call 03-vcftools_filter 04-bcftools_merge 05-python_filter 06-genomic_diversity .snakemake logs/*.log scripts/__pycache__
	cd population_analysis && rm -rf 06-genomic_diversity .snakemake logs/*.log scripts/__pycache__
	rm -rf tests/__pycache__ .pytest_cache .ruff_cache .coverage
	@echo "Clean complete"

.PHONY: local-dry-sample
local-dry-sample: sync ## Run Sample Analysis with dry-run locally (no execution)
	@echo "Running Sample Analysis dry-run..."
	cd sample_analysis && $(SNAKEMAKE) --dry-run -j 1

.PHONY: local-dry-population
local-dry-population: sync ## Run Population Analysis with dry-run locally (no execution)
	@echo "Running Population Analysis dry-run..."
	cd population_analysis && $(SNAKEMAKE) --dry-run -j 1

.PHONY: build
build: ## Build Docker image with all dependencies
	@echo "Ensuring Docker image $(DOCKER_IMAGE) exists..."
	@docker image inspect $(DOCKER_IMAGE) >/dev/null 2>&1 || docker build -t $(DOCKER_IMAGE) .

.PHONY: run
run: ## Start interactive Docker container
	@echo "Starting Docker container..."
	docker run -it --rm -v $(PWD):/workspace $(DOCKER_IMAGE)

.PHONY: sample_analysis
sample_analysis: build ## Run Sample Analysis (Usage: make sample_analysis DATA=/path/to/data)
	@if [ -z "$(DATA)" ]; then \
		echo "Error: DATA parameter required. Usage: make sample_analysis DATA=/path/to/data"; \
		exit 1; \
	fi
	@echo "Running Sample Analysis with input: $(DATA)"
	@echo "Cleaning workspace intermediate files..."
	@cd sample_analysis && rm -rf 00-data 00-reads 01-gstacks 02-bcftools_call 03-vcftools_filter 04-bcftools_merge 05-python_filter 06-genomic_diversity logs/*.log
	@OUTPUT_DIR="$(DATA)$(OUTPUT_SUFFIX)/sample_analysis" && \
	rm -rf "$$OUTPUT_DIR" 2>/dev/null || true && \
	mkdir -p "$$OUTPUT_DIR" && \
	docker run --rm \
		-m 8g \
		-v $(PWD):/workspace \
		-v "$(DATA):/data:ro" \
		-v "$$OUTPUT_DIR:/output" \
		$(DOCKER_IMAGE) bash -c "cd /workspace/sample_analysis && $(DOCKER_SNAKEMAKE) -j 1 --config input_dir=/data output_dir=/output"

.PHONY: population_analysis
population_analysis: build ## Run Population Analysis (Usage: make population_analysis DATA=/path/to/data)
	@if [ -z "$(DATA)" ]; then \
		echo "Error: DATA parameter required. Usage: make population_analysis DATA=/path/to/data"; \
		exit 1; \
	fi
	@echo "Running Population Analysis with input: $(DATA)"
	@echo "Cleaning workspace intermediate files..."
	@cd population_analysis && rm -rf 06-genomic_diversity logs/*.log
	@OUTPUT_DIR="$(DATA)$(OUTPUT_SUFFIX)/population_analysis" && \
	SAMPLE_OUTPUT="$(DATA)$(OUTPUT_SUFFIX)/sample_analysis" && \
	rm -rf "$$OUTPUT_DIR" 2>/dev/null || true && \
	mkdir -p "$$OUTPUT_DIR" && \
	docker run --rm \
		-v $(PWD):/workspace \
		-v "$(DATA):/data:ro" \
		-v "$$OUTPUT_DIR:/output" \
		-v "$$SAMPLE_OUTPUT:/sample_output:ro" \
		$(DOCKER_IMAGE) bash -c "cd /workspace/population_analysis && $(DOCKER_SNAKEMAKE) -j 4 --config input_dir=/data output_dir=/output sample_output=/sample_output"

.PHONY: clean-docker
clean-docker: ## Clean up Docker containers and images
	@echo "Cleaning up Docker containers..."
	docker ps -a | grep $(DOCKER_IMAGE) | awk '{print $$1}' | xargs -r docker rm -f

.PHONY: lint
lint: sync ## Check code with ruff and isort
	@echo "Running ruff and isort checks..."
	uv run ruff check sample_analysis population_analysis tests
	uv run isort --check-only sample_analysis population_analysis tests

.PHONY: format
format: sync ## Format code with ruff and isort
	@echo "Formatting code with ruff and isort..."
	uv run ruff format sample_analysis population_analysis tests
	uv run isort sample_analysis population_analysis tests

.PHONY: test
test: sync ## Run unit tests with pytest
	@echo "Running pytest..."
	uv run --group dev pytest -q
