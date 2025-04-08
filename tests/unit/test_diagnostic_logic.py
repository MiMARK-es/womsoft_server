import pytest
from app.routers.diagnostics import calculate_diagnostic_result

class TestDiagnosticLogic:
    def test_diagnostic_result_always_positive(self):
        """
        Test that the diagnostic calculation always returns "Positive"
        regardless of the input values.
        """
        # Test with various input values
        test_cases = [
            # (agrin, timp2, mmp9)
            (0.5, 1.2, 0.8),
            (1.0, 2.0, 3.0),
            (5.5, 0.0, 10.2),
            (0.0, 0.0, 0.0)
        ]
        
        for agrin, timp2, mmp9 in test_cases:
            result = calculate_diagnostic_result(agrin, timp2, mmp9)
            
            # Verify result is always "Positive"
            assert result == "Positive", f"Expected 'Positive' but got '{result}' for values ({agrin}, {timp2}, {mmp9})"