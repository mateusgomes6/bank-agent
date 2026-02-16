"""Tests for Tool components."""
import pytest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.tools.auth_tools import validate_cpf_format, validate_date_format
from src.tools.score_tools import calculate_credit_score
from src.tools.csv_tools import get_cliente_by_cpf, read_csv
from src.utils.config import CLIENTES_CSV


class TestAuthTools:
    """Test authentication tools."""
    
    def test_cpf_validation(self):
        """Test CPF validation."""
        assert validate_cpf_format("12345678901") is True
        assert validate_cpf_format("123") is False
    
    def test_date_validation(self):
        """Test date validation."""
        assert validate_date_format("1990-05-15") is True
        assert validate_date_format("invalid") is False


class TestScoreTools:
    """Test score calculation tools."""
    
    def test_score_calculation_formal_employee(self):
        """Test score calculation for formal employee."""
        score = calculate_credit_score(
            renda_mensal=5000,
            tipo_emprego="formal",
            despesas_fixas=2000,
            num_dependentes=1,
            tem_dividas="não"
        )
        assert 0 <= score <= 1000
        assert isinstance(score, float)
    
    def test_score_calculation_self_employed(self):
        """Test score calculation for self-employed."""
        score = calculate_credit_score(
            renda_mensal=4000,
            tipo_emprego="autônomo",
            despesas_fixas=1500,
            num_dependentes=0,
            tem_dividas="sim"
        )
        assert 0 <= score <= 1000
    
    def test_score_calculation_unemployed(self):
        """Test score calculation for unemployed."""
        score = calculate_credit_score(
            renda_mensal=0,
            tipo_emprego="desempregado",
            despesas_fixas=1000,
            num_dependentes=2,
            tem_dividas="sim"
        )
        # Unemployed should have low score
        assert score >= 0
    
    def test_score_with_many_dependents(self):
        """Test score calculation with many dependents."""
        score = calculate_credit_score(
            renda_mensal=5000,
            tipo_emprego="formal",
            despesas_fixas=2000,
            num_dependentes=5,  # Should be treated as 3+
            tem_dividas="não"
        )
        assert 0 <= score <= 1000


class TestCSVTools:
    """Test CSV tools."""
    
    def test_read_client_data(self):
        """Test reading client from CSV."""
        cliente = get_cliente_by_cpf("12345678901")
        assert cliente is not None
        assert cliente.get('nome') == 'João Silva'
        assert cliente.get('score') == 750
    
    def test_read_nonexistent_client(self):
        """Test reading non-existent client."""
        cliente = get_cliente_by_cpf("99999999999")
        assert cliente is None
    
    def test_read_csv_file(self):
        """Test reading CSV file."""
        df = read_csv(CLIENTES_CSV)
        assert len(df) > 0
        assert 'cpf' in df.columns
        assert 'nome' in df.columns


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
