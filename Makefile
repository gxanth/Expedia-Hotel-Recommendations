# Makefile for Expedia Personalized Hotel Ranking
.PHONY: requirements lint train tune dash submit clean help

# Python interpreter
PYTHON = python3

## Install Python dependencies
requirements:
	$(PYTHON) -m pip install --upgrade pip setuptools wheel
	$(PYTHON) -m pip install -r requirements.txt

## Lint code using flake8
lint:
	flake8 src app scripts

## Train a model from YAML config
train:
	$(PYTHON) scripts/train_xgbranker_from_yaml.py configs/models/base_model.yaml

## Hyperparameter tuning with Optuna
# Usage: make tune N_TRIALS=50
TUNE_CONFIG=configs/models/base_model.yaml
N_TRIALS?=30

tune:
	$(PYTHON) scripts/train_xgbranker_from_yaml.py $(TUNE_CONFIG) --tune --n_trials $(N_TRIALS)

## Launch the Dash dashboard
# Usage: make dash

dash:
	$(PYTHON) src/expedia_ranker/dash_app/main.py

## Submit to Kaggle
# Usage: make submit COMP=<competition> FILE=<submission.csv> MODEL_DIR=<model_dir>
COMP=
FILE=
MODEL_DIR=
submit:
	$(PYTHON) scripts/submit_kaggle.py --competition $(COMP) --file $(FILE) --model_dir $(MODEL_DIR)

## Clean up Python cache and artifacts
clean:
	find . -type f -name '*.py[co]' -delete
	find . -type d -name '__pycache__' -delete

.DEFAULT_GOAL := help

## Show this help message
help:
	@echo "Available targets:"
	@grep -E '^##' Makefile | sed 's/^## //'
	@grep -E '^[a-zA-Z_-]+:' Makefile | grep -v '.PHONY' | sed 's/:.*//' | awk '{print "  -", $$0}'
