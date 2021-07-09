import importlib
import os
import sys
import unittest
from contextlib import contextmanager
from contextlib import redirect_stdout
from io import StringIO

import caf_logger.logger as caflogger
import logging_codes
from caf_logger.level_type import LevelType
from caf_logger.mdal import corrid_store


@contextmanager
def captured_output():
    new_out, new_err = StringIO(), StringIO()
    old_out, old_err = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = new_out, new_err
        yield sys.stdout, sys.stderr
    finally:
        sys.stdout, sys.stderr = old_out, old_err


class TestShell(unittest.TestCase):

    def setUp(self):
        importlib.reload(caflogger)
        importlib.reload(corrid_store)

    def tearDown(self) -> None:
        caflogger._logging_config_file = None
        caflogger._logger_initialized = False

    """
    :test_procedure: test configuration loading for python shell
    """

    def test_get_logger(self):
        logger1 = caflogger.get_logger("testlogger")
        logger2 = caflogger.get_logger("testlogger")
        self.assertEqual(logger1.logger, logger2.logger)

    def test_get_logger_with_invalid_config(self):
        logging_config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "loggingdoesnotexist.conf")
        os.environ['WHI_CAF_LOGGING_CONFIG'] = logging_config_file

        caflogger.get_logger("testlogger")

        del os.environ['WHI_CAF_LOGGING_CONFIG']

    def test_logger_format(self):
        with StringIO() as out:
            with redirect_stdout(out):
                importlib.reload(caflogger)
                logger = caflogger.get_logger("testlogger1")

                logger.info(logging_codes.WHI_CAF_LOGGER_TEST_LOG_MESSAGE, "arg1")
                output = out.getvalue().strip()
                self.assertTrue(
                    "[MainThread] [INFO] [WHI.testlogger1] - [] - CAFLOGTEST001: Logging a test message with arguments: arg1" in output)

                logger.warn(logging_codes.WHI_CAF_LOGGER_TEST_LOG_MESSAGE, "arg1")
                output = out.getvalue().strip()
                self.assertTrue(
                    "[MainThread] [WARNING] [WHI.testlogger1] - [] - CAFLOGTEST001: Logging a test message with arguments: arg1" in output)

                logger.error(logging_codes.WHI_CAF_LOGGER_TEST_LOG_MESSAGE, "arg2")
                output = out.getvalue().strip()
                self.assertTrue(
                    "[MainThread] [ERROR] [WHI.testlogger1] - [] - CAFLOGTEST001: Logging a test message with arguments: arg2" in output)

                logger.apm(logging_codes.WHI_CAF_LOGGER_TEST_LOG_MESSAGE, "arg1")
                output = out.getvalue().strip()
                self.assertTrue(
                    "[MainThread] [APM] [WHI.testlogger1] - [] - CAFLOGTEST001: Logging a test message with arguments: arg1" in output)

    def test_logger_format_no_message_args(self):
        with StringIO() as out:
            with redirect_stdout(out):
                importlib.reload(caflogger)
                logger = caflogger.get_logger("testlogger2")

                logger.info(logging_codes.WHI_CAF_LOGGER_TEST_LOG_MESSAGE_NO_ARGS)
                output = out.getvalue().strip()
                self.assertTrue(
                    "[MainThread] [INFO] [WHI.testlogger2] - [] - CAFLOGTEST003: Logging a test message without arguments" in output)

                logger.warn(logging_codes.WHI_CAF_LOGGER_TEST_LOG_MESSAGE_NO_ARGS)
                output = out.getvalue().strip()
                self.assertTrue(
                    "[MainThread] [WARNING] [WHI.testlogger2] - [] - CAFLOGTEST003: Logging a test message without arguments" in output)

                logger.error(logging_codes.WHI_CAF_LOGGER_TEST_LOG_MESSAGE_NO_ARGS)
                output = out.getvalue().strip()
                self.assertTrue(
                    "[MainThread] [ERROR] [WHI.testlogger2] - [] - CAFLOGTEST003: Logging a test message without arguments" in output)

                logger.apm(logging_codes.WHI_CAF_LOGGER_TEST_LOG_MESSAGE_NO_ARGS)
                output = out.getvalue().strip()
                self.assertTrue(
                    "[MainThread] [APM] [WHI.testlogger2] - [] - CAFLOGTEST003: Logging a test message without arguments" in output)

    def test_logger_error_handling(self):
        with StringIO() as out:
            with redirect_stdout(out):
                importlib.reload(caflogger)
                logger = caflogger.get_logger("testlogger3")

                logger.info(logging_codes.WHI_CAF_LOGGER_TEST_LOG_MESSAGE_INVALID)
                output = out.getvalue().strip()
                self.assertTrue(
                    "[MainThread] [ERROR] [WHI.testlogger3] - [] - CAFLOG001: Failed to log message [CAFLOGTEST002] at INFO level correctly, see following stacktrace for details" in output)

    def test_mdal_logger_event_format(self):
        with StringIO() as out:
            with redirect_stdout(out):
                importlib.reload(caflogger)
                logger = caflogger.get_mdal_logger("testlogger4")

                logger.log_event(logging_codes.WHI_CAF_LOGGER_TEST_MDAL_EVENT, "eventA", "started")
                output = out.getvalue().strip()
                self.assertTrue(
                    '[MainThread] [MDAL] [MDAL.testlogger4] - [] - [] - CAFLOGTESTMDAL001: [ event: {"name": "eventA", "status": "started"}]' in output)

                corrid_store.set_headers(["corrid:cid1"])
                logger.log_event(logging_codes.WHI_CAF_LOGGER_TEST_MDAL_EVENT, "eventA", "started")
                output = out.getvalue().strip()
                self.assertTrue(
                    '[MainThread] [MDAL] [MDAL.testlogger4] - [cid1] - [] - CAFLOGTESTMDAL001: [ event: {"name": "eventA", "status": "started"}]' in output)

    def test_mdal_logger_context_handling(self):
        with StringIO() as out:
            with redirect_stdout(out):
                importlib.reload(caflogger)
                logger = caflogger.get_mdal_logger("testlogger5")

                logger.add_context("ctx1")
                logger.log_event(logging_codes.WHI_CAF_LOGGER_TEST_MDAL_EVENT, "eventA", "started")
                output = out.getvalue().strip()
                self.assertTrue(
                    '[MainThread] [MDAL] [MDAL.testlogger5] - [/ctx1] - [] - CAFLOGTESTMDAL001: [ event: {"name": "eventA", "status": "started"}]' in output)
                logger.remove_all_contexts()

                corrid_store.set_headers(["corrid:cid1"])
                logger.log_event(logging_codes.WHI_CAF_LOGGER_TEST_MDAL_EVENT, "eventA", "started")
                output = out.getvalue().strip()
                self.assertTrue(
                    '[MainThread] [MDAL] [MDAL.testlogger5] - [cid1] - [] - CAFLOGTESTMDAL001: [ event: {"name": "eventA", "status": "started"}]' in output)

                logger.add_context("ctx1")
                logger.log_event(logging_codes.WHI_CAF_LOGGER_TEST_MDAL_EVENT, "eventA", "started")
                output = out.getvalue().strip()
                self.assertTrue(
                    '[MainThread] [MDAL] [MDAL.testlogger5] - [cid1/ctx1] - [] - CAFLOGTESTMDAL001: [ event: {"name": "eventA", "status": "started"}]' in output)

                logger.add_context("subctx2")
                logger.add_context("subctx3.0")
                logger.log_event(logging_codes.WHI_CAF_LOGGER_TEST_MDAL_EVENT, "eventA", "started")
                output = out.getvalue().strip()
                self.assertTrue(
                    '[MainThread] [MDAL] [MDAL.testlogger5] - [cid1/ctx1|subctx2|subctx3.0] - [] - CAFLOGTESTMDAL001: [ event: {"name": "eventA", "status": "started"}]' in output)

                logger.remove_top_context()
                logger.log_event(logging_codes.WHI_CAF_LOGGER_TEST_MDAL_EVENT, "eventA", "started")
                output = out.getvalue().strip()
                self.assertTrue(
                    '[MainThread] [MDAL] [MDAL.testlogger5] - [cid1/ctx1|subctx2] - [] - CAFLOGTESTMDAL001: [ event: {"name": "eventA", "status": "started"}]' in output)

                logger.remove_all_contexts()
                logger.log_event(logging_codes.WHI_CAF_LOGGER_TEST_MDAL_EVENT, "eventA", "started")
                output = out.getvalue().strip()
                self.assertTrue(
                    '[MainThread] [MDAL] [MDAL.testlogger5] - [cid1] - [] - CAFLOGTESTMDAL001: [ event: {"name": "eventA", "status": "started"}]' in output)

    def test_mdal_logger_local_attribute_format(self):
        with StringIO() as out:
            with redirect_stdout(out):
                importlib.reload(caflogger)
                logger = caflogger.get_mdal_logger("testlogger6")

                logger.add_attribute("attr1", "value1")
                output = out.getvalue().strip()
                self.assertTrue(
                    '[MainThread] [MDAL] [MDAL.testlogger6] - [] - [] - MDALATTR: [ attribute: {"attr1": "value1"} ]' in output)
                logger.remove_all_contexts()

    def test_mdal_logger_global_attribute_format(self):
        with StringIO() as out:
            with redirect_stdout(out):
                importlib.reload(caflogger)
                logger = caflogger.get_mdal_logger("testlogger7")

                logger.add_global_attribute("global_attr1", "value1")
                logger.log_event(logging_codes.WHI_CAF_LOGGER_TEST_MDAL_EVENT, "eventA", "started")
                output = out.getvalue().strip()
                self.assertTrue(
                    '[MainThread] [MDAL] [MDAL.testlogger7] - [] - [global_attr1:value1] - CAFLOGTESTMDAL001: [ event: {"name": "eventA", "status": "started"}]' in output)

                logger.add_global_attribute("global_attr2", "value2")
                logger.log_event(logging_codes.WHI_CAF_LOGGER_TEST_MDAL_EVENT, "eventA", "started")
                output = out.getvalue().strip()
                self.assertTrue(
                    '[MainThread] [MDAL] [MDAL.testlogger7] - [] - [global_attr1:value1,global_attr2:value2] - CAFLOGTESTMDAL001: [ event: {"name": "eventA", "status": "started"}]' in output)

                global_attrs = logger.get_current_global_attributes()
                self.assertTrue('global_attr1:value1' in global_attrs)
                self.assertTrue('global_attr2:value2' in global_attrs)

    def test_mdal_logger_Json_format(self):
        with StringIO() as out:
            with redirect_stdout(out):
                os.environ['WHI_CAF_LOGGING_DEFAULT_FORMAT'] = 'Json'
                importlib.reload(caflogger)
                logger = caflogger.get_mdal_logger("testlogger7")

                logger.add_attribute("attr1", "value1")
                event_info = {'name': 'eventA', 'status': 'started'}
                logger.add_context("ctx1")
                logger.add_context("ctx2")
                logger.add_global_attribute('STUDY', '1.2.3.4')
                logger.add_global_attribute('ORDER', '5.6.7.8')
                logger.log_event(event_info=event_info)

                output = out.getvalue().strip()
                self.assertTrue('"message": "Event recorded"' in output)
                self.assertTrue('"log_id": "MDALEVENT"' in output)
                self.assertTrue('"WHI-CORRID": ""' in output)
                self.assertTrue('"WHI-CONTEXT": "ctx1|ctx2"' in output)
                self.assertTrue('"event": {"name": "eventA", "status": "started"}' in output)
                self.assertTrue('"level": "MDAL"' in output)
                self.assertTrue('"@timestamp": ' in output)
                self.assertTrue('"HOSTNAME": ' in output)
                self.assertTrue('"logger_name": "MDAL.testlogger7"' in output)
                self.assertTrue('"thread_name": "MainThread"' in output)
                logger.remove_all_contexts()
                del os.environ['WHI_CAF_LOGGING_DEFAULT_FORMAT']

    def test_logger_Json_format(self):
        with StringIO() as out:
            with redirect_stdout(out):
                os.environ['WHI_CAF_LOGGING_DEFAULT_FORMAT'] = 'Json'
                importlib.reload(caflogger)
                logger = caflogger.get_logger("testlogger8")

                logger.info(logging_codes.WHI_CAF_LOGGER_TEST_LOG_MESSAGE, "arg1")

                output = out.getvalue().strip()
                self.assertTrue('"message": "Logging a test message with arguments: arg1"' in output)
                self.assertTrue('"log_id": "CAFLOGTEST001"' in output)
                self.assertTrue('"WHI-CORRID": ""' in output)
                self.assertTrue('"security_level": 1' in output)
                self.assertTrue('"level": "INFO"' in output)
                self.assertTrue('"@timestamp": ' in output)
                self.assertTrue('"HOSTNAME": ' in output)
                self.assertTrue('"logger_name": "WHI.testlogger8"' in output)
                self.assertTrue('"thread_name": "MainThread"' in output)
                del os.environ['WHI_CAF_LOGGING_DEFAULT_FORMAT']

                # Verify Level type
                logger.info(logging_codes.WHI_CAF_LOGGER_TEST_LOG_MESSAGE, "arg1", level_type=LevelType.LEVEL5)
                output = out.getvalue().strip()
                self.assertTrue('"security_level": 5' in output)


if __name__ == '__main__':
    unittest.main()
