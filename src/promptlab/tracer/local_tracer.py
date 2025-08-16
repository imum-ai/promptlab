from datetime import datetime, timezone
from typing import Any, Dict, List
import json

from sqlalchemy import text
from sqlalchemy.orm import joinedload

from promptlab.types import ExperimentConfig, TracerConfig, Dataset, PromptTemplate
from promptlab.sqlite.session import get_session
from promptlab.sqlite.database_manager import db_manager
from promptlab.enums import AssetType
from promptlab.sqlite.sql import SQLQuery
from promptlab.tracer.tracer import Tracer
from promptlab.sqlite.models import (
    Experiment as ORMExperiment,
    ExperimentResult as ORMExperimentResult,
    User,
)
from promptlab.sqlite.models import Asset as ORMAsset


class LocalTracer(Tracer):
    def __init__(self, tracer_config: TracerConfig):
        # Use centralized database manager
        db_manager.initialize_database(tracer_config.db_file)

    def _create_asset(self, asset: ORMAsset):
        session = get_session()
        try:
            session.add(asset)
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def _make_serializable(self, experiment_config: ExperimentConfig) -> Dict:
        """Make experiment config serializable by removing non-serializable objects and creating model dict."""
        # Serialize completion model configuration
        completion_model_config = None
        if experiment_config.completion_model_config is not None:
            config_copy = experiment_config.completion_model_config.model_copy()
            config_copy.model = None  # Remove model instance before serialization
            completion_model_config = config_copy.model_dump()

        # Serialize embedding model configuration
        embedding_model_config = None
        if experiment_config.embedding_model_config is not None:
            config_copy = experiment_config.embedding_model_config.model_copy()
            config_copy.model = None  # Remove model instance before serialization
            embedding_model_config = config_copy.model_dump()

        return {
            "completion_model_config": completion_model_config,
            "embedding_model_config": embedding_model_config,
        }

    def create_dataset(self, dataset: Dataset):
        if dataset.version is None:
            dataset.version = 0
        binary = {"file_path": dataset.file_path}
        asset = ORMAsset(
            asset_name=dataset.name,
            asset_version=dataset.version,
            asset_description=dataset.description,
            asset_type=AssetType.DATASET.value,
            asset_binary=json.dumps(binary),
            created_at=datetime.now(timezone.utc),
            user_id=self.get_user_by_username(dataset.user).id,
        )

        self._create_asset(asset)

    def create_prompttemplate(self, template: PromptTemplate):
        if template.version is None:
            template.version = 0
        binary = f"""
            <<system>>
                {template.system_prompt}
            <<user>>
                {template.user_prompt}
        """
        asset = ORMAsset(
            asset_name=template.name,
            asset_version=template.version,
            asset_description=template.description,
            asset_type=AssetType.PROMPT_TEMPLATE.value,
            asset_binary=binary,
            created_at=datetime.now(timezone.utc),
            user_id=self.get_user_by_username(template.user).id,
        )

        self._create_asset(asset)

    def trace_experiment(
        self, experiment_config: ExperimentConfig, experiment_summary: List[Dict]
    ) -> None:
        session = get_session()
        try:
            experiment_id = experiment_summary[0]["experiment_id"]

            model = self._make_serializable(experiment_config)

            asset = {
                "prompt_template_name": experiment_config.prompt_template.name
                if experiment_config.prompt_template
                else None,
                "prompt_template_version": experiment_config.prompt_template.version
                if experiment_config.prompt_template
                else None,
                "dataset_name": experiment_config.dataset.name,
                "dataset_version": experiment_config.dataset.version,
            }

            exp = ORMExperiment(
                experiment_id=experiment_id,
                model=json.dumps(model),
                asset=json.dumps(asset),
                created_at=datetime.now(),
                user_id=self.get_user_by_username(experiment_config.user).id,
            )
            session.add(exp)
            results = [
                ORMExperimentResult(
                    experiment_id=record["experiment_id"],
                    dataset_record_id=record["dataset_record_id"],
                    completion=record["completion"],
                    prompt_tokens=record["prompt_tokens"],
                    completion_tokens=record["completion_tokens"],
                    latency_ms=record["latency_ms"],
                    evaluation=json.dumps(record["evaluation"])
                    if isinstance(record["evaluation"], (dict, list))
                    else record["evaluation"],
                    created_at=datetime.now(),
                )
                for record in experiment_summary
            ]
            session.add_all(results)
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def get_asset(self, asset_name: str, asset_version: int) -> ORMAsset:
        session = get_session()
        try:
            asset = (
                session.query(ORMAsset)
                .filter_by(asset_name=asset_name, asset_version=asset_version)
                .first()
            )
            if not asset:
                raise ValueError(
                    f"Asset {asset_name} with version {asset_version} not found."
                )
            return asset
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def get_assets_by_type(self, asset_type: str) -> List[Any]:
        session = get_session()
        try:
            if asset_type not in AssetType._value2member_map_:
                raise ValueError(f"Invalid asset type: {asset_type}")
            assets = (
                session.query(ORMAsset)
                .options(joinedload(ORMAsset.user))
                .filter(ORMAsset.asset_type == asset_type)
                .all()
            )
            return assets
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def get_latest_asset(self, asset_name: str) -> ORMAsset:
        session = get_session()
        try:
            asset = (
                session.query(ORMAsset)
                .filter_by(asset_name=asset_name)
                .order_by(ORMAsset.asset_version.desc())
                .first()
            )
            return asset
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def get_user_by_username(self, username: str) -> User:
        session = get_session()
        try:
            user = session.query(User).filter_by(username=username).first()
            if not user:
                raise ValueError(f"User {username} not found.")
            return user
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def get_experiments(self):
        session = get_session()
        try:
            return (
                session.execute(text(SQLQuery.SELECT_EXPERIMENTS_QUERY))
                .mappings()
                .all()
            )
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def get_users(self):
        session = get_session()
        try:
            return session.query(User).filter(User.status == 1).all()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def create_user(self, user: User):
        session = get_session()
        try:
            session.add(user)
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def deactivate_user_by_username(self, username: str):
        session = get_session()
        try:
            user = session.query(User).filter_by(username=username).first()
            if not user:
                raise ValueError(f"User {username} not found.")
            user.status = 0  # Deactivate user
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def me(self) -> User:
        _current_username = (
            "admin"  # This should be replaced with the actual current user logic
        )
        session = get_session()
        try:
            user = (
                session.query(User).filter_by(username=_current_username).first()
            )  # Assuming user with ID 1 is the current user
            if not user:
                raise ValueError("Current user not found.")
            return user
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
