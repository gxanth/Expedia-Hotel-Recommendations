[![Python](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/github/license/gxanth/expedia-personalized-recommendations)](LICENSE)
[![Build](https://img.shields.io/github/actions/workflow/status/gxanth/expedia-personalized-recommendations/ci.yml?branch=main&label=build)](https://github.com/gxanth/expedia-personalized-recommendations/actions)
[![Polars](https://img.shields.io/badge/polars-Polars-blue)](https://www.pola.rs/)
[![XGBoost](https://img.shields.io/badge/XGBoost-XGBoost-green)](https://xgboost.readthedocs.io/)
[![Optuna](https://img.shields.io/badge/Optuna-Optuna-blueviolet)](https://optuna.org/)
[![Dash](https://img.shields.io/badge/Dash-Plotly%20Dash-0098D9)](https://dash.plotly.com/)

# Expedia Personalized Hotel Ranking

**Based on the [Kaggle Competition: Personalize Expedia Hotel Searches - ICDM 2013](https://www.kaggle.com/competitions/expedia-personalized-sort)**  
Learning to rank hotels to maximize purchases and personalize Expedia search results.

A robust, modular machine learning pipeline for Expedia hotel ranking optimization, featuring XGBRanker, Polars, Optuna, and a modern Dash dashboard for diagnostics and model management.

---

## Features

* Modular ML pipeline: Clean separation of data, features, modeling, and evaluation.
* XGBRanker: State-of-the-art learning-to-rank with per-query NDCG@k.
* Optuna Hyperparameter Tuning: Automated, reproducible search for best model parameters.
* Polars & Pandas: Fast, memory-efficient data processing.
* Dash Dashboard: Interactive, modular diagnostics and model comparison.
* Kaggle Submission Integration: One-command submit and score tracking.
* Reproducible Artifacts: All model outputs versioned and organized by model name.

---

## 📂 Project Structure
```
├── README.md
├── Makefile                # Common tasks: lint, test, train, dash, etc.
├── requirements.txt        # Pinned dependencies
├── setup.py / pyproject.toml
├── configs/               # All YAML configs (no code/data)
├── data/                  # 4-layer data pattern (raw, interim, processed, dashboard)
├── models/                # Model artifacts by version
├── scripts/               # Standalone scripts (train, submit, debug)
├── src/expedia_ranker/    # Main Python package (commands, features, modeling, dash_app, utils)
└── ...
```

---

## ⚡️ Quickstart

### 1. **Install dependencies**
```bash
python3 -m venv exp_personal
source exp_personal/bin/activate
pip install -r requirements.txt
```

### 2. **Prepare data**
- Place raw data in `data/raw/`.
- Run preprocessing pipeline (see Makefile or scripts).

### 3. **Train a model**
```bash
python scripts/train_xgbranker_from_yaml.py configs/models/base_model.yaml
```
- For hyperparameter tuning with Optuna:
```bash
python scripts/train_xgbranker_from_yaml.py configs/models/base_model.yaml --tune --n_trials 50
```

### 4. **Launch the dashboard**
```bash
make dash
# or
python src/expedia_ranker/dash_app/main.py
```

### 5. **Submit to Kaggle**
```bash
python scripts/submit_kaggle.py --competition <COMP_NAME> --file <SUBMISSION_CSV> --model_dir models/<MODEL_NAME>
```

---

## 🏗️ Key Components

- **configs/**: All experiment, feature, and pipeline configs in YAML.
- **data/**: Layered data storage (raw, interim, processed, dashboard-ready).
- **models/**: Each model version has its own folder with all artifacts (model, metrics, feature importance, learning curves, Optuna results, etc).
- **src/expedia_ranker/**: Main package with commands, features, modeling, dashboard, and utilities.
- **scripts/**: Standalone scripts for training, submission, and debugging.
- **app/**: Dash dashboard code (layout, callbacks, assets).

---

## 🧩 Modular Workflow
1. **Config-driven**: All steps (features, model, pipeline) are controlled by YAML configs.
2. **Training**: Run training script, outputs all artifacts to `models/<model_name>/`.
3. **Tuning**: Optuna integration for hyperparameter search, with results saved and retraining on best params.
4. **Diagnostics**: Dash dashboard for model selection, metrics, learning curves, feature importance, and hyperparams.
5. **Submission**: One-command Kaggle submission and score tracking.

---

## Development & Contribution
- Use the Makefile for common tasks: `make lint`, `make test`, `make train`, `make dash`.
- All code should be modular, PEP8-compliant, and documented.
- Add new features as modules in `src/expedia_ranker/` and register them in the CLI/dashboard as needed.
- Tests should go in `tests/`, mirroring the `src/` structure.

---

## Documentation
- See `docs/` for architecture, API, and design notes.
- Notebooks in `notebooks/` for exploration and demos.

---

## Contact & Acknowledgments

**Author:** Georgios Xanthopoulos  
- Email: [xanthopoulos.geo@outlook.com](mailto:xanthopoulos.geo@outlook.com)  
- LinkedIn: [linkedin.com/in/gxantho](https://www.linkedin.com/in/gxantho/)  
- GitHub: [github.com/gxanth](https://github.com/gxanth)  
- Webpage: [gxanth.github.io](https://gxanth.github.io/)

**Acknowledgments:**
- Inspired by the Expedia Group team for their pioneering work in travel recommendation systems.
- Thanks to the Kaggle community for invaluable discussions, notebooks, and tutorials.
- Special appreciation to the Data Mining course staff at Vrije Universiteit Amsterdam for their guidance and support.

---

## License
See [LICENSE](LICENSE) for details.

---

## References

If you use this code or data, please cite the original competition:

```bibtex
@misc{expedia-personalized-sort,
    author = {Adam and Ben Hamner and Dan Friedman and SSA_Expedia},
    title = {Personalize Expedia Hotel Searches - ICDM 2013},
    year = {2013},
    howpublished = {\url{https://kaggle.com/competitions/expedia-personalized-sort}},
    note = {Kaggle}
}
```
