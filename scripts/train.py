import json
import os
import traceback
from datetime import datetime

import click
import joblib
import pandas as pd
import shap
import yaml
from loguru import logger
from matplotlib import pyplot as plt

from src.config import settings
from src.config.models import ExperimentConfig
from src.modelling import eval_utils, model_utils


@click.command()
@click.option(
    "--config-path",
    default=settings.CONFIG_DIR / "default.yaml",
    help="Path to the experiment configuration yaml file",
)
def train(config_path):

    # Experiment Configuration: Load and validate yaml #
    with open(config_path, "r") as config_file:
        raw_config_yaml = yaml.safe_load(config_file)
    config = ExperimentConfig.parse_obj(raw_config_yaml)

    # Data Preparation #

    # Read in data
    data_df = pd.read_csv(config.data_params.csv_path)
    logger.info(f"Loaded {len(data_df):,} rows from {config.data_params.csv_path}")

    # Remove (impute) any rows with nulls
    impute_cols = config.data_params.impute_cols
    strategy = config.data_params.impute_strategy
    data_df = model_utils.simple_impute(df=data_df, cols=impute_cols, strategy=strategy)

    # Prepare features and target
    target_col = config.data_params.target_col
    feature_cols = config.data_params.infer_selected_features(data_df.columns)
    logger.info(f"Target: {target_col}, {len(feature_cols)} Features: {feature_cols}, ")

    # Check for nulls after impute
    for col in feature_cols:
        logger.info(f"{data_df[col].isna().sum()} rows with nulls for column {col}.")

    # Remove null values
    grp = config.dict()["spatial_cv_params"]["groups"]
    filt = feature_cols + [target_col] + [grp]
    reduced_df = data_df.loc[:, filt]

    if reduced_df.isnull().values.any() > 0:
        orig_count = len(reduced_df)
        logger.warning(f"Removing any null rows. Initial data count: {orig_count:,}")

        reduced_df.dropna(how="any", inplace=True)
        reduced_df.reset_index(drop=True, inplace=True)

        null_rows = orig_count - len(reduced_df)

        if null_rows > 0:
            logger.warning(
                f"Dropped {null_rows:,} rows with nulls. Final data count: {len(reduced_df):,}"
            )

    X = reduced_df[feature_cols]
    y = reduced_df[target_col].values

    # Prepare output dir
    out_dir = config.out_dir / datetime.today().strftime("%Y-%m-%d_%H-%M-%S")
    if not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    # Model Training and Evaluation #
    nested_cv_results = model_utils.nested_cv(config.dict(), X, y, out_dir=out_dir)
    logger.info(f"\nNested CV results: {json.dumps(nested_cv_results, indent=4)}")

    spatial_cv_results = model_utils.spatial_cv(config.dict(), reduced_df, X, y)
    logger.info(f"\nSpatial CV results: {json.dumps(spatial_cv_results, indent=4)}")

    cv = model_utils.get_cv(config.dict())
    cv.fit(X, y)
    logger.info(f"Best estimator: {cv.best_estimator_}")

    # Generate SHAP charts for feature importance #

    try:
        logger.info("Generating SHAP charts")
        # Generate feature importance
        # The cv.best_estimator_ is an sklearn pipeline object, generated by model_utils._get_pipeline
        # The pipeline steps are: [scaler, selector, model]
        model = cv.best_estimator_[-1]
        transformations = cv.best_estimator_[:-1]

        X_transformed = X.copy()
        for transformation in transformations:
            X_transformed = transformation.transform(X_transformed)

        # TODO make code automatically pick the right explainer based on the model type
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(X_transformed)
        shap_df = pd.DataFrame(shap_values).set_axis(X.columns, axis=1)

        # Save Feature Importance -  (simplified shap plot - similar to SHAP's bar chart but colored accdg to correlation)
        eval_utils.generate_simplified_shap(
            shap_df, X, out_dir / "shap_summary_custom_bar.png"
        )

        # Save Feature Importance -  (raw SHAP summary plots)
        shap.summary_plot(shap_values, features=X, show=False)
        plt.savefig(out_dir / "shap_summary_beeswarm.png", bbox_inches="tight", dpi=400)
        plt.clf()

        shap.summary_plot(shap_values, features=X, show=False, plot_type="bar")
        plt.savefig(out_dir / "shap_summary_bar.png", bbox_inches="tight", dpi=400)
    except Exception:
        traceback.print_exc()
        logger.error("Error in producing SHAP charts.")

    # Serialize Model and Results #

    # Save Nested CV results
    with open(out_dir / "nested_cv_results.json", "w") as f:
        json.dump(nested_cv_results, f, indent=4)

    # Save Spatial CV results
    with open(out_dir / "spatial_cv_results.json", "w") as f:
        json.dump(spatial_cv_results, f, indent=4)

    # Save Model
    joblib.dump(cv.best_estimator_, out_dir / "best_model.pkl")
    with open(out_dir / "best_model_params.txt", "w") as f:
        print(str(cv.best_estimator_), file=f)

    # Copy over config file so we keep track of the configuration
    with open(out_dir / "config.yaml", "w") as f:
        yaml.dump(raw_config_yaml, f, default_flow_style=False)


if __name__ == "__main__":
    train()
