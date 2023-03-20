import os
from pathlib import Path

from django.db.models import QuerySet

from .settings import (
    MILLI_DB_FOLDER,
    MILLI_DB_SIZE,
    MILLI_REBUILD_CACHE_ON_SERVER_START,
    MILLI_INDEX_MODEL_SETTINGS,
    _MILLI_MODEL,
    MILLI_AUTO_ADD_ID_FIELD,
)

from .utils import LazyObject

from milli import Index


def get_milli_connection() -> Index:
    return Index(str(MILLI_DB_FOLDER), map_size=MILLI_DB_SIZE)


MILLI = LazyObject(factory=get_milli_connection)


def milli_db_is_present() -> bool:
    return Path(MILLI_DB_FOLDER / "data.mdb").exists()


def build_index(
    custom_queryset: QuerySet = None, remove_existing: bool = False
) -> None:
    if remove_existing:
        os.remove(Path(MILLI_DB_FOLDER / "data.mdb"))
        os.remove(Path(MILLI_DB_FOLDER / "lock.mdb"))

    qs = custom_queryset if custom_queryset else _MILLI_MODEL.objects.all()
    fields = MILLI_INDEX_MODEL_SETTINGS["fields"]
    if "id" not in fields and MILLI_AUTO_ADD_ID_FIELD:
        fields += ["id"]

    MILLI.add_documents(list(qs.values(*fields)))


def search(search_term: str, return_queryset: bool = True) -> list[dict] | QuerySet:
    """
    Search Milli for documents which match your term.

    If no result is found, an empty list will be returned.
    """
    documents = MILLI.get_documents(MILLI.search(search_term))
    if return_queryset:
        qs = _MILLI_MODEL.objects.filter(
            id__in=[obj.get("id") for obj in documents]
        )
        result_list = []
        for obj in documents:
            for option in qs:
                if option.id == obj['id']:
                    result_list.append(option)
        return result_list
    return documents
