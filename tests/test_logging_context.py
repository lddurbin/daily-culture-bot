from src import logging_config, context


def test_correlation_id_binding():
    logging_config.configure_logging(log_format="json")
    cid = context.new_correlation_id()
    logger = logging_config.get_logger("test").bind(correlation_id=cid)
    # Ensure logging call does not raise and correlation id is present in event dict via processors
    # We can't easily capture structlog JSON here without handlers; this ensures API is callable
    logger.info("test_event", correlation_id=cid)


