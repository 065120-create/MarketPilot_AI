class MarketPilotError(Exception):
    """Base exception for MarketPilot AI"""
    pass

class DataValidationError(MarketPilotError):
    pass

class AgentExecutionError(MarketPilotError):
    pass

class RAGRetrievalError(MarketPilotError):
    pass

class BudgetConstraintError(MarketPilotError):
    pass

class LLMProviderError(MarketPilotError):
    pass

class NormalizationError(MarketPilotError):
    pass

class N8NIntegrationError(MarketPilotError):
    pass

class JobNotFoundError(MarketPilotError):
    pass

class InvalidDatasetError(MarketPilotError):
    pass
