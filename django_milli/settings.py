from pathlib import Path

from django.conf import settings
import os

from .settings_utils import perform_import
from .utils import LazyObject


class DjangoMilliConfigException(Exception):
    ...


MILLI_DB_SIZE: int = getattr(settings, "MILLI_DB_SIZE", 2**30 * 2)  # 2gb
MILLI_DB_FOLDER: Path = getattr(settings, "MILLI_DB_FOLDER", None)
MILLI_BUILD_CACHE_ON_SERVER_START: bool = getattr(
    settings, "MILLI_BUILD_CACHE_ON_SERVER_START", True
)
MILLI_REBUILD_CACHE_ON_SERVER_START: bool = getattr(
    settings, "MILLI_REBUILD_CACHE_ON_SERVER_START", True
)
MILLI_INDEX_MODEL_SETTINGS: dict = getattr(settings, "MILLI_INDEX_MODEL_SETTINGS", {})
MILLI_AUTO_ADD_ID_FIELD: bool = getattr(settings, "MILLI_AUTO_ADD_ID_FIELD", True)
MILLI_NO_LOGGING: bool = getattr(settings, "MILLI_NO_LOGGING", False)

"""
Example:

MILLI_INDEX_MODEL_SETTINGS = {
    'model': 'myapp.models.MyFavoritePeople',
    'fields': [
        'id',
        'name'
    ]
}
"""

if MILLI_INDEX_MODEL_SETTINGS == {}:
    raise DjangoMilliConfigException("Missing information on model to index!")

if not isinstance(MILLI_INDEX_MODEL_SETTINGS, dict):
    raise DjangoMilliConfigException(
        "Cannot parse MILLI_INDEX_MODEL_SETTINGS. Please check the documentation."
    )

if not MILLI_INDEX_MODEL_SETTINGS.get("model"):
    raise DjangoMilliConfigException(
        "Missing model to index in MILLI_INDEX_MODEL_SETTINGS!"
    )

if not MILLI_INDEX_MODEL_SETTINGS.get("fields"):
    model_name = MILLI_INDEX_MODEL_SETTINGS.get("model")
    raise DjangoMilliConfigException(
        f"Missing fields to index on {model_name} in MILLI_INDEX_MODEL_SETTINGS!"
    )

if not MILLI_DB_FOLDER:
    if not settings.BASE_DIR:
        raise DjangoMilliConfigException("Missing MILLI_DB_LOCATION!")
    else:
        if isinstance(settings.BASE_DIR, str):
            # old style string
            MILLI_DB_FOLDER = Path(settings.BASE_DIR)
        else:
            # path obj
            MILLI_DB_FOLDER = settings.BASE_DIR

if not MILLI_DB_FOLDER.parent.exists():
    raise DjangoMilliConfigException(
        f"Directory {MILLI_DB_FOLDER} doesn't appear valid!"
    )


def get_model():
    try:
        return perform_import(
            MILLI_INDEX_MODEL_SETTINGS.get("model"), "MILLI_INDEX_MODEL_SETTINGS[model]"
        )
    except ImportError:
        raise DjangoMilliConfigException(
            f"Model '{MILLI_INDEX_MODEL_SETTINGS.get('model')}' appears invalid!"
        ) from None


_MILLI_MODEL = LazyObject(factory=get_model)
