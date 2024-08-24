import logging

from workflow.logger_setup import init_logger

init_logger()


def handler(event, context):
    try:
        logging.info("Got event")

        from workflow import secrets_manager
        secrets_manager.update_secrets()

        from workflow.run import run
        run()
    except Exception:
        logging.exception("Lambda function failed")
        raise
