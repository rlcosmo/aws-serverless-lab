"""Classified processing errors for the SQS consumer."""


class PermanentProcessingError(Exception):
    """A validly decoded event that conflicts with durable business state."""


class TransientProcessingError(Exception):
    """A temporary processing or dependency failure that can succeed on retry."""
