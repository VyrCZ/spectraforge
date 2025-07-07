import os
import datetime

class Log:
    LOG_DIRECTORY = "logs"
    LOG_TEMPLATE = "[$DATETIME] [$CHANNEL] [$LOGTYPE]: $MESSAGE"
    _current_log_file = None
    
    @staticmethod
    def _setup_log_file():
        if not os.path.exists(Log.LOG_DIRECTORY):
            os.makedirs(Log.LOG_DIRECTORY)
        
        log_filename = f'{datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.log'
        Log._current_log_file = os.path.join(Log.LOG_DIRECTORY, log_filename)

    def _make_log(log_type, channel, message):
        if not Log._current_log_file:
            Log._setup_log_file()

        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = Log.LOG_TEMPLATE\
            .replace("$DATETIME", now)\
            .replace("$CHANNEL", str(channel))\
            .replace("$LOGTYPE", log_type)\
            .replace("$MESSAGE", str(message))

        print(log_entry)
        with open(Log._current_log_file, "a", encoding="utf-8") as f:
            f.write(log_entry + "\n")


    @staticmethod
    def info(channel, message):
        """Log an informational message."""
        Log._make_log("INFO", channel, message)
    
    @staticmethod
    def warn(channel, message):
        """Log a warning message."""
        Log._make_log("WARN", channel, message)

    @staticmethod
    def error(channel, message):
        """Log an error message."""
        Log._make_log("ERROR", channel, message)

    @staticmethod
    def debug(channel, message):
        """Log a debug message."""
        Log._make_log("DEBUG", channel, message)

    @staticmethod
    def get_log_channel(log_message):
        """Extract the log type from a log message."""
        if not log_message:
            return None
        parts = log_message.split(" ")
        if len(parts) < 3:
            return None
        return parts[1].strip("[]")

    @staticmethod
    def get_log_messages(filter_channel = None):
        """Retrieve all log messages from the current log file."""
        if not Log._current_log_file or not os.path.exists(Log._current_log_file):
            return []

        with open(Log._current_log_file, "r", encoding="utf-8") as f:
            log_messages = f.readlines()
        if filter_channel:
            log_messages = [msg for msg in log_messages if Log.get_log_channel(msg) == filter_channel]
        return log_messages