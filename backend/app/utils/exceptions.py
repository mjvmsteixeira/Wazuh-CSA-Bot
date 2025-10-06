"""Custom exceptions for the application."""


class WazuhAPIError(Exception):
    """Raised when Wazuh API requests fail."""

    pass


class AIServiceError(Exception):
    """Raised when AI service operations fail."""

    pass


class AgentNotFoundError(Exception):
    """Raised when requested agent doesn't exist."""

    pass


class CheckNotFoundError(Exception):
    """Raised when requested SCA check doesn't exist."""

    pass


class PDFGenerationError(Exception):
    """Raised when PDF generation fails."""

    pass
