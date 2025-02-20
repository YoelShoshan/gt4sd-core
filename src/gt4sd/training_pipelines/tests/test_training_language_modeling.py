"""Language modeling trainer unit tests."""

from typing import cast

import pkg_resources
from pytorch_lightning.callbacks.model_checkpoint import ModelCheckpoint

from gt4sd.training_pipelines import (
    TRAINING_PIPELINE_MAPPING,
    LanguageModelingTrainingPipeline,
)
from gt4sd.training_pipelines.pytorch_lightning.language_modeling.lm_datasets import (
    CGMDataModule,
    CLMDataModule,
    MLMDataModule,
    PLMDataModule,
)
from gt4sd.training_pipelines.pytorch_lightning.language_modeling.models import (
    CGMModule,
    CLMModule,
    MLMModule,
    PLMModule,
)

template_config = {
    "model_args": {
        "tokenizer": "albert-base-v2",
        "model_name_or_path": "albert-base-v2",
        "model_config_name": "albert-base-v2",
        "type": "mlm",
        "lr": 2e-5,
        "lr_decay": 0.5,
        "cache_dir": "/tmp/dci_",
    },
    "dataset_args": {
        "max_length": 512,
        "mlm_probability": 0.15,
        "plm_probability": 0.1666,
        "max_span_length": 5,
        "batch_size": 8,
        "train_file": "ade_corpus_v2",
        "validation_file": "ade_corpus_v2",
        "cache_dir": "/tmp/dci_",
    },
    "trainer_args": {
        "default_root_dir": "here",
        "val_check_interval": 5000,
        "max_epochs": 1,
        "accumulate_grad_batches": 1,
        "limit_val_batches": 500,
        "log_every_n_steps": 500,
        "monitor": "val_loss",
        "save_top_k": 2,
        "mode": "min",
        "every_n_train_steps": 50000,
    },
}


def test_get_data_and_model_modules_mlm():

    pipeline = TRAINING_PIPELINE_MAPPING.get("language-modeling-trainer")

    assert pipeline is not None

    test_pipeline = cast(LanguageModelingTrainingPipeline, pipeline())

    config = template_config.copy()

    file_path = pkg_resources.resource_filename(
        "gt4sd",
        "training_pipelines/tests/lm_example.jsonl",
    )

    config["dataset_args"]["train_file"] = file_path

    config["dataset_args"]["validation_file"] = file_path
    config["model_args"]["type"] = "mlm"

    data_module, model_module = test_pipeline.get_data_and_model_modules(
        config["model_args"], config["dataset_args"]  # type: ignore
    )

    assert isinstance(model_module, MLMModule)
    assert isinstance(data_module, MLMDataModule)

    check_model_config(model_module, config["model_args"])
    check_data_config(data_module, config["dataset_args"])


def test_get_data_and_model_modules_clm():

    pipeline = TRAINING_PIPELINE_MAPPING.get("language-modeling-trainer")

    assert pipeline is not None

    test_pipeline = cast(LanguageModelingTrainingPipeline, pipeline())

    config = template_config.copy()

    file_path = pkg_resources.resource_filename(
        "gt4sd",
        "training_pipelines/tests/lm_example.jsonl",
    )

    config["dataset_args"]["train_file"] = file_path
    config["dataset_args"]["validation_file"] = file_path
    config["model_args"]["type"] = "clm"
    config["model_args"]["model_name_or_path"] = "gpt2"

    data_module, model_module = test_pipeline.get_data_and_model_modules(
        config["model_args"], config["dataset_args"]  # type: ignore
    )

    assert isinstance(model_module, CLMModule)
    assert isinstance(data_module, CLMDataModule)

    check_model_config(model_module, config["model_args"])
    check_data_config(data_module, config["dataset_args"])


def test_get_data_and_model_modules_cgm():

    pipeline = TRAINING_PIPELINE_MAPPING.get("language-modeling-trainer")

    assert pipeline is not None

    test_pipeline = cast(LanguageModelingTrainingPipeline, pipeline())

    config = template_config.copy()

    file_path = pkg_resources.resource_filename(
        "gt4sd",
        "training_pipelines/tests/lm_example.jsonl",
    )

    config["dataset_args"]["train_file"] = file_path
    config["dataset_args"]["validation_file"] = file_path
    config["model_args"]["type"] = "cgm"
    config["model_args"]["model_name_or_path"] = "t5-base"

    data_module, model_module = test_pipeline.get_data_and_model_modules(
        config["model_args"], config["dataset_args"]  # type: ignore
    )

    assert isinstance(model_module, CGMModule)
    assert isinstance(data_module, CGMDataModule)

    check_model_config(model_module, config["model_args"])
    check_data_config(data_module, config["dataset_args"])


def test_get_data_and_model_modules_plm():

    pipeline = TRAINING_PIPELINE_MAPPING.get("language-modeling-trainer")

    assert pipeline is not None

    test_pipeline = cast(LanguageModelingTrainingPipeline, pipeline())

    config = template_config.copy()

    file_path = pkg_resources.resource_filename(
        "gt4sd",
        "training_pipelines/tests/lm_example.jsonl",
    )

    config["dataset_args"]["train_file"] = file_path
    config["dataset_args"]["validation_file"] = file_path
    config["model_args"]["type"] = "plm"
    config["model_args"]["model_name_or_path"] = "xlnet-base-cased"

    data_module, model_module = test_pipeline.get_data_and_model_modules(
        config["model_args"], config["dataset_args"]  # type: ignore
    )

    assert isinstance(model_module, PLMModule)
    assert isinstance(data_module, PLMDataModule)

    check_model_config(model_module, config["model_args"])
    check_data_config(data_module, config["dataset_args"])


def test_add_callbacks():

    pipeline = TRAINING_PIPELINE_MAPPING.get("language-modeling-trainer")

    assert pipeline is not None

    callbacks_input = {
        "model_checkpoint_callback": {
            "monitor": "val_loss",
            "save_top_k": 2,
            "mode": "min",
            "every_n_train_steps": 50000,
        }
    }

    callbacks = pipeline().add_callbacks(callbacks_input)  # type: ignore

    assert len(callbacks) == 1
    assert isinstance(callbacks[0], ModelCheckpoint)


def check_model_config(module, config):
    for entry in module.model_args:
        assert entry in config
        assert config[entry] == module.model_args[entry]


def check_data_config(module, config):
    for entry in module.dataset_args:
        assert entry in config
        assert config[entry] == module.dataset_args[entry]
