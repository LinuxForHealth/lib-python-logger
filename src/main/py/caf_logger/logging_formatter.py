import platform

from pythonjsonlogger import jsonlogger

_ATTR_MAP = {
    'levelname': 'level',
    'asctime': '@timestamp',
    'name': 'logger_name',
    'threadName': 'thread_name',
    'corr_id': 'WHI-CORRID'
}


class CAFJsonFormatter(jsonlogger.JsonFormatter):

    def process_log_record(self, log_record):
        log_record['HOSTNAME'] = platform.node()
        for k, v in _ATTR_MAP.items():
            if k in log_record:
                log_record[v] = log_record.pop(k)
        return jsonlogger.JsonFormatter.process_log_record(self, log_record)
