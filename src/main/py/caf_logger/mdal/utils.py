from caf_logger.mdal import constants


def flatten_list(in_list, delimiter=','):
    flat_list = []
    for item in in_list:
        ids = item.split(delimiter)
        flat_list.extend(ids)
    return flat_list


def get_uuid_corr_id(corr_id_list):
    uuid_corr_id_list = list(filter(lambda item: item.startswith(constants.UUID_CORRID_LABEL), corr_id_list))
    corr_id = uuid_corr_id_list[0] if len(uuid_corr_id_list) > 0 else None
    corr_id_tokens = corr_id.split(':') if corr_id else None
    return corr_id_tokens[1] if corr_id_tokens is not None and len(corr_id_tokens) > 1 else None


def _map_corr_id_value(full_corr_id):
    split_corr_id = full_corr_id.split(':', 1)
    return split_corr_id[1] if len(split_corr_id) > 1 else None


def get_attr_corr_id(corr_id_list):
    attr_corr_id_list = filter(lambda item: item.startswith(constants.ATTR_CORRID_LABEL), corr_id_list)
    attr_corr_ids = map(_map_corr_id_value, attr_corr_id_list)
    return list(filter(None, attr_corr_ids))
