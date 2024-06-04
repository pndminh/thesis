import logging
import re


class MultilineFormatter(logging.Formatter):
    def format(self, record):
        # Get the original log message
        message = super().format(record)

        # Find strings with escape characters
        escaped_strings = re.findall(r'"([^"\\]*(?:\\.[^"\\]*)+)"', message)

        # Replace escape characters with unescaped characters
        for escaped_string in escaped_strings:
            unescaped_string = escaped_string.encode().decode("unicode_escape")
            message = message.replace(
                f'"{escaped_string}"', f'"""{unescaped_string}"""'
            )

        # Add indentation to each line
        message = message.replace("\n", "\n    ").strip() + "\n--------"
        return message.encode("utf-8", "ignore").decode("ISO-8859-1")


logger = logging.Logger("data_extract", level=logging.INFO)

multiline_formatter = MultilineFormatter(
    "%(asctime)s - " "%(filename)s: " "%(funcName)s(): " "%(lineno)d:\t" "%(message)s\n"
)
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(multiline_formatter)


logging.basicConfig(
    level=logging.INFO,
    format=(
        "%(asctime)s - "
        "%(filename)s: "
        "%(funcName)s(): "
        "%(lineno)d:\t"
        "%(message)s\n-------------"
    ),
    encoding="utf-8",
    errors="replace",
    handlers=[stream_handler],
)


def get_logger():
    return logging.getLogger("data_extractor")
