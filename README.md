## whi-caf-python-lib-logger

## How to use

whi-caf-python-lib-logger provides two separate APIs for logging. One is used for regular logging (info, warn, error etc.) and the other one provides a special logger API for using MDAL logging that auto injects the state (correlation id, context and global attributes) into the log message.

### How to use regular logger

```
1 import caf_logger.logger as caflogger
2 
3 logger = caflogger.get_logger("test")
4 logger.info(("LOGCODE001", "Log message template. {}s are replaced by arguments provided to the logger"), "argument")
5 logger.error(("LOGERROR001", "Log message template. pass exc_info=True or exc_info=<some exception> to log a stacktrace along with the message"), exc_info=True)
```

After importing the logger, we need to create a logger using the get_logger(<logger_name>) function. This is done in line 3 in the above code.

Once a logger has been created, we can call the info, warn, error and apm methods of the logger to log messages at these levels. Each of these methods takes a tuple containing the log message ID and the log message template, next these methods takes arguments (0 to many) that will be added to the message template. This is done in line 4 in the above code.

The logger methods also take an optional, keyword only argument exc_info that, if truthy, will cause the logger to also log the current stacktrace. This is done in line 5 of the above code.

The full method definitions are:

```
info(msg_tuple, *args, exc_info=Non
warn(msg_tuple, *args, exc_info=Non
error(msg_tuple, *args, exc_info=Non
apm(msg_tuple, *args):
```

The `apm` method does not log the stacktrace.

#### Passing in the message_tuple
While it is fine to pass in the message tuple directly in the method call, a better pattern (and the motivation for this design) is to store these tuple in separate variables with descriptive names and pass these to the logger methods instead. Example:

```
file: logging_codes.py

WHI_CAF_SHELL_RECEVIED_STUDY = ("CAFLOG001", "The CAF shell received the study with ID {}")
WHI_CAF_SHELL_PROCESSED_STUDY = ("CAFLOG002", "The CAF shell processed the study with ID {}, the results were a {}")

file: shell.py

import logging_codes
import caf_logger.logger as caflogger

logger = caflogger.get_logger("SHELL")
logger.info(logging_codes.WHI_CAF_SHELL_RECEVIED_STUDY, <study_id>)
try:
    #process study capturing result
    logger.info(logging_codes.WHI_CAF_SHELL_PROCESSED_STUDY, <study_id>, "success")
except BaseException as e:
    logger.warn(logging_codes.WHI_CAF_SHELL_PROCESSED_STUDY, <study_id>, "failure", exc_info=e)
```
