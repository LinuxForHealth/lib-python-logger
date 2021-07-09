import json
import os
import os.path
import logging
import logging.config
import traceback
from caf_logger import logging_codes
from caf_logger.level_type import LevelType
from caf_logger.mdal import corrid_store
import sys

_ENABLED_JSON_FORMAT = os.getenv('WHI_CAF_LOGGING_DEFAULT_FORMAT', 'Text') == 'Json'

class CAFLogger:
    def __init__(self, logger):
        self.logger = logger

    def _internal_error(self, level, msg_template):
        try:
            log_id, msg = logging_codes.WHI_CAF_LOGGER_BAD_ARGUMENTS
            extra = {'log_id': log_id, 'corr_id': corrid_store.get_corr_id()}
            self.logger.error(msg, msg_template, level, extra=extra, exc_info=True)
        except BaseException:
            print("Failed to print logger error")
            traceback.print_exc(file=sys.stdout)

    def _log_at_level(self, level, msg_template, *args, level_type=LevelType.LEVEL1, exc_info=None):
        logger_method = self.logger.info
        normalized_level = level.upper()
        if normalized_level == "INFO":
            logger_method = self.logger.info
        elif normalized_level == "WARNING":
            logger_method = self.logger.warning
        elif normalized_level == "ERROR":
            logger_method = self.logger.error
        elif normalized_level == "APM":
            logger_method = self.logger.apm

        try:
            log_id, msg = msg_template
            extra = {'log_id': log_id, 'corr_id': corrid_store.get_corr_id(), 'security_level': level_type.value}
            if args:
                logger_method(msg, *args, extra=extra, exc_info=exc_info)
            else:
                logger_method(msg, extra=extra, exc_info=exc_info)
        except BaseException:
            self._internal_error(normalized_level, msg_template)

    def info(self, msg_template, *args, level_type=LevelType.LEVEL1, exc_info=None):
        self._log_at_level("INFO", msg_template, *args, level_type=level_type, exc_info=exc_info)

    def warn(self, msg_template, *args, level_type=LevelType.LEVEL1, exc_info=None):
        self._log_at_level("WARNING", msg_template, *args, level_type=level_type, exc_info=exc_info)

    def error(self, msg_template, *args, level_type=LevelType.LEVEL1, exc_info=None):
        self._log_at_level("ERROR", msg_template, *args, level_type=level_type, exc_info=exc_info)

    def apm(self, msg_template, *args, level_type=LevelType.LEVEL1):
        self._log_at_level("APM", msg_template, *args, level_type=level_type, exc_info=None)


class CAFActivityLogger():
    def __init__(self, logger):
        self.logger = logger

    def _internal_error(self, level, msg_template):
        try:
            log_id, msg = logging_codes.WHI_CAF_LOGGER_BAD_ARGUMENTS
            extra = {'log_id': log_id, 'corr_id': corrid_store.get_corr_id()}
            self.logger.error(msg, msg_template, level, extra=extra, exc_info=True)
        except BaseException:
            print("Failed to print logger error")
            traceback.print_exc(file=sys.stdout)

    def add_context(self, context):
        corrid_store.add_context(context)

    def remove_top_context(self):
        corrid_store.remove_top_context()

    def remove_all_contexts(self):
        corrid_store.remove_all_contexts()

    def log_event(self, msg_template=logging_codes.WHI_CAF_MDAL_MESSAGE, *args, event_info={}):
        try:
            log_id, msg = msg_template
            if _ENABLED_JSON_FORMAT:
                extra = self._collect_extra_info_for_mdal_json_format(log_id, event_info)
            else:
                extra = self._collect_extra_info_for_mdal_text_format(log_id)
                if msg_template==logging_codes.WHI_CAF_MDAL_MESSAGE and event_info:
                    msg += ' {}'.format(json.dumps(event_info))
            if args:
                self.logger.mdal(msg, *args, extra=extra)
            else:
                self.logger.mdal(msg, extra=extra)
        except BaseException:
            self._internal_error("MDAL", msg_template)

    def _collect_extra_info_for_mdal_text_format(self, log_id):
        current_context = corrid_store.get_current_context()
        if len(current_context):
            corr_id = "{}/{}".format(corrid_store.get_corr_id(), '|'.join(current_context))
        else:
            corr_id = corrid_store.get_corr_id()
        log_attribute = ','.join(corrid_store.get_attrs())
        return {'log_id': log_id, 'corr_id': corr_id, 'log_attribute': log_attribute}

    def _collect_extra_info_for_mdal_json_format(self, log_id, event_info):
        current_context = corrid_store.get_current_context()
        extra = {'log_id': log_id, 'corr_id': corrid_store.get_corr_id(), 'WHI-CONTEXT': '|'.join(current_context)}
        if event_info is not None:
            extra['event'] = event_info
        for attr in corrid_store.get_attrs():
            splitted_attr = attr.split(':', 1)
            extra[splitted_attr[0]] = splitted_attr[1]
        return extra

    def add_attribute(self, attr_name, attr_value):
        try:
            if _ENABLED_JSON_FORMAT:
                log_id, msg = logging_codes.WHI_CAF_MDAL_ADD_ATTRIBUTE_JSON
                extra = self._collect_extra_info_for_mdal_json_format(log_id, None)
                extra[attr_name] = attr_value
                self.logger.mdal(msg, extra=extra)
            else:
                log_id, msg = logging_codes.WHI_CAF_MDAL_ADD_ATTRIBUTE_TEXT
                extra = self._collect_extra_info_for_mdal_text_format(log_id)
                self.logger.mdal(msg, attr_name, attr_value, extra=extra)
        except BaseException:
            self._internal_error("MDAL", (attr_name, attr_value))

    def get_current_context(self):
        return corrid_store.get_current_context()

    def add_global_attribute(self, attr_name, attr_value):
        corrid_store.add_attr("{}:{}".format(attr_name, attr_value))

    def get_current_global_attributes(self):
        return corrid_store.get_attrs()


class LogRecord(logging.LogRecord):
    def getMessage(self):
        if self.name.startswith('WHI') or self.name.startswith('MDAL'):
            msg = self.msg
            if self.args:
                if isinstance(self.args, dict):
                    msg = msg.format(**self.args)
                else:
                    msg = msg.format(*self.args)
            return msg
        else:
            msg = self.msg
            if self.args:
                msg = msg % self.args
            return msg


def get_logger(logger_name: str):
    if _logger_initialized:
        return CAFLogger(logging.getLogger("WHI." + logger_name))
    else:
        print("Logger is not initialized, see earlier errors")


def get_mdal_logger(logger_name: str):
    if _logger_initialized:
        return CAFActivityLogger(logging.getLogger("MDAL." + logger_name))
    else:
        print("Logger is not initialized, see earlier errors")


def _get_logger_config():
    global _logging_config_file
    if not (os.path.exists(_logging_config_file) and os.path.isfile(_logging_config_file)):
        package_directory = os.path.dirname(os.path.abspath(__file__))
        _logging_config_file = os.path.join(package_directory,
                                            "logging_json.conf" if _ENABLED_JSON_FORMAT else "logging.conf")


def _log_apm(self, message, *args, **kws):
    if self.isEnabledFor(APM_LEVEL_NUM):
        self._log(APM_LEVEL_NUM, message, args, **kws)


def _log_mdal(self, message, *args, **kws):
    if self.isEnabledFor(MDAL_LEVEL_NUM):
        self._log(MDAL_LEVEL_NUM, message, args, **kws)


APM_LEVEL_NUM = 21
APM_LEVEL_NAME = "APM"
MDAL_LEVEL_NUM = 22
MDAL_LEVEL_NAME = "MDAL"
_logger_initialized = False
_logging_config_file = os.getenv('WHI_CAF_LOGGING_CONFIG', '/var/app/config/caf-logging.cfg')

try:
    _get_logger_config()
    print("loading logging configuration from: {}".format(_logging_config_file))
    logging.config.fileConfig(_logging_config_file)
    logging.setLogRecordFactory(LogRecord)
    logging.addLevelName(APM_LEVEL_NUM, APM_LEVEL_NAME)
    logging.addLevelName(MDAL_LEVEL_NUM, MDAL_LEVEL_NAME)
    logging.Logger.apm = _log_apm
    logging.Logger.mdal = _log_mdal
    _logger_initialized = True
except Exception:
    print("Failed to initialize logger")
    traceback.print_exc(file=sys.stdout)