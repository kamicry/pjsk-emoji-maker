"""Mock AstrBot modules for testing"""
from unittest.mock import Mock, MagicMock
import sys


class MockFilter:
    """Mock filter decorator"""
    @staticmethod
    def command(command_name):
        def decorator(func):
            func._command_name = command_name
            return func
        return decorator


class MockLogger:
    """Mock logger"""
    @staticmethod
    def info(msg):
        pass
    
    @staticmethod
    def debug(msg):
        pass
    
    @staticmethod
    def warning(msg):
        pass
    
    @staticmethod
    def error(msg):
        pass


class MockAstrMessageEvent:
    """Mock message event"""
    def __init__(self):
        self.message_str = ""
        self.session_id = "test_session"
        self.platform = "test"
    
    def get_sender_name(self):
        return "TestUser"
    
    def get_messages(self):
        return []
    
    def plain_result(self, text):
        return text


class MockMessageEventResult:
    """Mock message event result"""
    pass


class MockContext:
    """Mock context"""
    def __init__(self):
        self.config = {}
        self.logger = MockLogger()


class MockStar:
    """Mock Star base class"""
    def __init__(self, context):
        self.context = context


def mock_register(name, author, desc, version):
    """Mock register decorator"""
    def decorator(cls):
        cls._plugin_name = name
        cls._plugin_author = author
        cls._plugin_desc = desc
        cls._plugin_version = version
        return cls
    return decorator


def setup_mocks():
    """Setup all mock modules"""
    event_module = MagicMock()
    event_module.filter = MockFilter()
    event_module.AstrMessageEvent = MockAstrMessageEvent
    event_module.MessageEventResult = MockMessageEventResult
    
    star_module = MagicMock()
    star_module.Context = MockContext
    star_module.Star = MockStar
    star_module.register = mock_register
    
    api_module = MagicMock()
    api_module.event = event_module
    api_module.star = star_module
    api_module.logger = MockLogger()
    
    astrbot_module = MagicMock()
    astrbot_module.api = api_module
    
    sys.modules['astrbot'] = astrbot_module
    sys.modules['astrbot.api'] = api_module
    sys.modules['astrbot.api.event'] = event_module
    sys.modules['astrbot.api.star'] = star_module
    
    return astrbot_module
