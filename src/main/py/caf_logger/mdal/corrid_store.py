from contextvars import ContextVar
from contextvars import Token
from typing import List
import uuid
from caf_logger.mdal import utils
from caf_logger.mdal import constants


_uuid_corr_id: ContextVar[str] = ContextVar("uuid_corr_id", default="")
_attr_corr_id: ContextVar[List[str]] = ContextVar("attr_corr_id", default=[])
_log_context: ContextVar[List[str]] = ContextVar("log_context", default=[])


def init_headers():
    set_corr_id(str(uuid.uuid4()))


def set_headers(corr_ids: List[str]):
    clean()
    flat_corr_ids = utils.flatten_list(corr_ids)
    uuid_corr_id = utils.get_uuid_corr_id(flat_corr_ids)
    attr_corr_ids = utils.get_attr_corr_id(flat_corr_ids)

    if(not uuid_corr_id):
        init_headers()
    else:
        set_corr_id(uuid_corr_id)

    for attr in attr_corr_ids:
        add_attr(attr)


def set_corr_id(corr_id: str) -> Token:
    return _uuid_corr_id.set(corr_id)


def get_corr_id() -> str:
    return _uuid_corr_id.get()


def add_attr(attr: str) -> Token:
    attrs = _attr_corr_id.get()
    attrs.append(attr)
    return _attr_corr_id.set(attrs)


def get_attrs() -> List[str]:
    return _attr_corr_id.get()


def get_headers() -> List[str]:
    headers = []
    uuid_corr_id = get_corr_id()
    if(not uuid_corr_id):
        init_headers()
        uuid_corr_id = get_corr_id()

    headers.append("{}{}".format(constants.UUID_CORRID_LABEL, uuid_corr_id))

    attr_corr_ids = get_attrs()
    attr_corr_ids_with_label = list(map(lambda item: "{}{}".format(constants.ATTR_CORRID_LABEL, item), attr_corr_ids))
    headers.extend(attr_corr_ids_with_label)

    return headers


def clean():
    _uuid_corr_id.set("")
    _attr_corr_id.set([])
    _log_context.set([])


def add_context(log_context: str) -> Token:
    ctx = _log_context.get()
    ctx.append(log_context)
    return _log_context.set(ctx)


def remove_top_context():
    ctx = _log_context.get()
    ctx = ctx[:-1]
    return _log_context.set(ctx)


def remove_all_contexts():
    return _log_context.set([])


def get_current_context():
    return _log_context.get()
