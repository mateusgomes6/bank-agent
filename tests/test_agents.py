"""Tests for Agent components."""
import pytest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.triage_agent import TriageAgent
from src.tools.auth_tools import validate_cpf_format, validate_date_format, authenticate_client


class TestTriageAgent:
    """Test Triage Agent functionality."""
    
    def test_triage_agent_initialization(self):
        """Test agent initialization."""
        agent = TriageAgent()
        assert agent.agent_name == "Agente de Triagem"
        assert agent.authenticated is False
        assert agent.auth_attempts == 0
    
    def test_cpf_validation(self):
        """Test CPF format validation."""
        # Valid CPF
        assert validate_cpf_format("12345678901") is True
        assert validate_cpf_format("123.456.789-01") is True
        
        # Invalid CPF
        assert validate_cpf_format("123") is False
        assert validate_cpf_format("123456789") is False
        assert validate_cpf_format("abcdefghijk") is False
    
    def test_date_validation(self):
        """Test date format validation."""
        # Valid dates
        assert validate_date_format("1990-05-15") is True
        assert validate_date_format("2000-12-25") is True
        
        # Invalid dates
        assert validate_date_format("1990/05/15") is False
        assert validate_date_format("05-15-1990") is False
        assert validate_date_format("1990-13-01") is False
        assert validate_date_format("invalid") is False
    
    def test_authentication_valid(self):
        """Test successful authentication."""
        success, client_data = authenticate_client("12345678901", "1990-05-15")
        assert success is True
        assert client_data is not None
        assert client_data.get('nome') == 'João Silva'
    
    def test_authentication_invalid_cpf(self):
        """Test authentication with invalid CPF."""
        success, client_data = authenticate_client("12345678900", "1990-05-15")
        assert success is False
        assert client_data is None
    
    def test_authentication_invalid_date(self):
        """Test authentication with wrong birth date."""
        success, client_data = authenticate_client("12345678901", "1990-06-15")
        assert success is False
        assert client_data is None
    
    def test_authentication_limits(self):
        """Test max attempts limit."""
        agent = TriageAgent()
        assert agent.has_max_attempts_exceeded() is False
        
        # Simulate failed attempts
        for _ in range(3):
            agent.auth_attempts += 1
        
        assert agent.has_max_attempts_exceeded() is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
