import logging

from .settings import (
    MILLI_INDEX_MODEL_SETTINGS,
    _MILLI_MODEL,
    MILLI_AUTO_ADD_ID_FIELD,
    MILLI_NO_LOGGING,
)
from . import MILLI

import milli

logger = logging.getLogger(__name__)


def post_save_handler(sender, **kwargs):
    """
    Handle a create or update operation on a model.

    Since we don't know what kind of operation it is, we first figure that out
    by checking the `created` attribute that's passed in. After that, we can
    either insert a new object into the index OR we can replace an object in
    the index -- the only way to perform an update.
    """
    if sender != _MILLI_MODEL:
        # Not the model we're looking for. Carry on.
        return

    instance = kwargs["instance"]
    fields = MILLI_INDEX_MODEL_SETTINGS["fields"]
    if MILLI_AUTO_ADD_ID_FIELD:
        if "id" not in fields:
            fields += ["id"]

    MILLI.add_documents(
        [
            {k: getattr(instance, k) for k in fields},
        ],
        milli.IndexDocumentsMethod.ReplaceDocuments if not kwargs["created"] else None,
    )


def pre_delete_handler(sender, **kwargs):
    """
    Handle a delete operation on a model.

    Find the object in the index that we are getting rid of and nuke it.
    This is much more difficult than it sounds because the base Milli
    engine doesn't support filtering by select fields, so we have to
    search for the object, find it in the results, use that to get the
    internal Milli ID, and nuke _that_.

    Thankfully, the removal of entities happens a lot less often than
    the adding of entities, so it's less of a concern.
    """
    if sender != _MILLI_MODEL:
        # Not the model we're looking for. Carry on.
        return

    fields = MILLI_INDEX_MODEL_SETTINGS["fields"]
    obj_repr = {k: getattr(kwargs["instance"], k) for k in fields}
    # now that we have the object we're looking for, we have to find the damn thing.
    # Get the value of the first key of the representation and search by it.
    results = MILLI.search(str(obj_repr[list(obj_repr.keys())[0]]))
    if len(results) == 1:
        # we got lucky and there's only one possible option. Remove it.
        MILLI.delete_documents(results)
    else:
        deleted = False
        for option in results:
            cache_obj = MILLI.get_document(option)
            if cache_obj == obj_repr:
                MILLI.delete_documents([option])
                deleted = True
        if not deleted and not MILLI_NO_LOGGING:
            # we did our search and tried to find the thing, but failed.
            logging.error(f"Failed to remove object `{cache_obj}` from cache!")
