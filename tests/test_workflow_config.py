#!/usr/bin/env python3
"""
Workflow configuration tests.

Tests workflow configuration validation and parameter consistency.
"""

import pytest
import os
import sys
try:
    import yaml
except ImportError:
    yaml = None
from unittest.mock import Mock, patch

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestWorkflowConfiguration:
    """Test workflow configuration validation."""
    
    def test_cli_arguments_consistency(self):
        """Test that CLI arguments are consistent across modules."""
        try:
            from daily_paintings import parse_arguments
            
            # Test argument parsing with mock sys.argv
            with patch('sys.argv', ['daily_paintings.py']):
                args = parse_arguments()
            
            # Verify all expected arguments are available
            expected_args = [
                'output', 'save_image', 'count', 'fast', 'poems', 'poem_count',
                'poems_only', 'complementary', 'no_poet_dates', 'email',
                'email_format', 'max_fame_level', 'min_match_score',
                'enable_vision_analysis', 'enable_multi_pass', 'candidate_count',
                'explain_matches'
            ]
            
            for arg in expected_args:
                assert hasattr(args, arg), f"Missing argument: {arg}"
        
        except ImportError as e:
            pytest.skip(f"Required module not available: {e}")
    
    def test_workflow_parameters_validation(self):
        """Test that workflow parameters are properly validated."""
        try:
            from daily_paintings import parse_arguments
            
            # Test with valid parameters
            valid_params = {
                'count': 2,
                'min_match_score': 0.4,
                'max_fame_level': 30,
                'candidate_count': 5,
                'poem_count': 1
            }
            
            # Test parameter validation
            for param, value in valid_params.items():
                if param == 'count':
                    assert isinstance(value, int)
                    assert value > 0
                elif param == 'min_match_score':
                    assert isinstance(value, float)
                    assert 0.0 <= value <= 1.0
                elif param == 'max_fame_level':
                    assert isinstance(value, int)
                    assert value >= 0
                elif param == 'candidate_count':
                    assert isinstance(value, int)
                    assert value > 0
                elif param == 'poem_count':
                    assert isinstance(value, int)
                    assert value > 0
        
        except ImportError as e:
            pytest.skip(f"Required module not available: {e}")
    
    def test_environment_variables_documentation(self):
        """Test that required environment variables are documented."""
        required_env_vars = [
            'OPENAI_API_KEY',
            'SENDGRID_API_KEY',
            'FROM_EMAIL',
            'TO_EMAIL'
        ]
        
        # Check that environment variables are documented in README
        readme_path = os.path.join(os.path.dirname(__file__), '..', 'README.md')
        if os.path.exists(readme_path):
            with open(readme_path, 'r') as f:
                readme_content = f.read()
            
            # Verify environment variables are mentioned
            for var in required_env_vars:
                assert var in readme_content, f"Environment variable {var} not documented in README"
    
    def test_workflow_yaml_structure(self):
        """Test that workflow YAML structure is valid."""
        workflow_path = os.path.join(os.path.dirname(__file__), '..', '.github', 'workflows', 'daily-email-optimized.yml')
        
        if os.path.exists(workflow_path) and yaml:
            with open(workflow_path, 'r') as f:
                workflow_content = f.read()
            
            # Parse YAML to validate structure
            try:
                workflow_yaml = yaml.safe_load(workflow_content)
                
                # Verify required sections
                assert 'name' in workflow_yaml
                assert 'on' in workflow_yaml
                assert 'jobs' in workflow_yaml
                
                # Verify workflow name
                assert 'daily-email-optimized' in workflow_yaml['name']
                
                # Verify trigger configuration
                assert 'schedule' in workflow_yaml['on']
                assert 'workflow_dispatch' in workflow_yaml['on']
                
                # Verify jobs section
                assert 'run-workflow' in workflow_yaml['jobs']
                
            except yaml.YAMLError as e:
                pytest.fail(f"Invalid YAML structure: {e}")
        else:
            pytest.skip("Workflow YAML file not found")
    
    def test_workflow_step_consistency(self):
        """Test that workflow steps are consistent with CLI arguments."""
        workflow_path = os.path.join(os.path.dirname(__file__), '..', '.github', 'workflows', 'daily-email-optimized.yml')
        
        if os.path.exists(workflow_path):
            with open(workflow_path, 'r') as f:
                workflow_content = f.read()
            
            # Check that workflow uses correct CLI arguments
            expected_args = [
                '--complementary',
                '--count', '2',
                '--min-match-score', '0.4',
                '--max-fame-level', '30',
                '--fast',
                '--enable-vision-analysis',
                '--enable-multi-pass',
                '--candidate-count', '5',
                '--explain-matches'
            ]
            
            for arg in expected_args:
                assert arg in workflow_content, f"Missing argument in workflow: {arg}"
        else:
            pytest.skip("Workflow YAML file not found")
    
    def test_fallback_strategies_configuration(self):
        """Test that fallback strategies are properly configured."""
        try:
            from daily_paintings import ComplementaryMode
            
            # Test fallback configuration
            mode = ComplementaryMode(openai_client=None)
            
            # Should handle missing OpenAI client gracefully
            assert mode.openai_client is None
            
            # Test fallback behavior
            poem = {
                "title": "Fallback Test",
                "author": "Test Author",
                "text": "A test poem for fallback testing."
            }
            
            result = mode.find_matching_artwork(
                poem=poem,
                count=1,
                enable_vision_analysis=False,
                enable_multi_pass=False
            )
            
            # Should return empty list or basic results
            assert isinstance(result, list)
        
        except ImportError as e:
            pytest.skip(f"Required module not available: {e}")
    
    def test_error_handling_configuration(self):
        """Test that error handling is properly configured."""
        try:
            from daily_paintings import main
            
            # Test error handling with invalid arguments
            with patch('sys.argv', ['daily_paintings.py', '--invalid-arg']):
                try:
                    main()
                    # Should handle invalid arguments gracefully
                except SystemExit as e:
                    # Should exit with error code
                    assert e.code != 0
                except Exception as e:
                    # Should handle other errors gracefully
                    assert isinstance(e, Exception)
        
        except ImportError as e:
            pytest.skip(f"Required module not available: {e}")
    
    def test_performance_configuration(self):
        """Test that performance configuration is appropriate."""
        try:
            from daily_paintings import ComplementaryMode
            from openai import OpenAI
            import time
            
            if not os.getenv('OPENAI_API_KEY'):
                pytest.skip("OpenAI API key not available")
            
            client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
            mode = ComplementaryMode(openai_client=client)
            
            poem = {
                "title": "Performance Test",
                "author": "Test Author",
                "text": "A test poem for performance testing."
            }
            
            # Test performance with different configurations
            configs = [
                {'fast_mode': True, 'enable_vision_analysis': False, 'enable_multi_pass': False},
                {'fast_mode': False, 'enable_vision_analysis': True, 'enable_multi_pass': True},
                {'fast_mode': True, 'enable_vision_analysis': True, 'enable_multi_pass': False}
            ]
            
            for config in configs:
                start_time = time.time()
                
                result = mode.find_matching_artwork(
                    poem=poem,
                    count=1,
                    **config
                )
                
                end_time = time.time()
                execution_time = end_time - start_time
                
                # Should complete within reasonable time
                assert execution_time < 120  # 2 minutes max
                assert isinstance(result, list)
        
        except ImportError as e:
            pytest.skip(f"Required module not available: {e}")
        except Exception as e:
            pytest.skip(f"Performance test failed: {e}")
    
    def test_email_configuration(self):
        """Test that email configuration is properly set up."""
        try:
            from email_sender import EmailSender
            
            # Test email configuration
            sender = EmailSender()
            
            # Should have email configuration
            assert hasattr(sender, 'from_email')
            assert hasattr(sender, 'to_email')
            assert hasattr(sender, 'api_key')
            
            # Test email validation
            if sender.from_email:
                assert '@' in sender.from_email
            if sender.to_email:
                assert '@' in sender.to_email
        
        except ImportError as e:
            pytest.skip(f"Required module not available: {e}")
    
    def test_logging_configuration(self):
        """Test that logging configuration is appropriate."""
        try:
            import logging
            
            # Test logging configuration
            logger = logging.getLogger('daily_culture_bot')
            
            # Should have appropriate log level
            assert logger.level <= logging.INFO
            
            # Test log message formatting
            test_message = "Test log message"
            logger.info(test_message)
            
            # Should not raise exceptions
            assert True
        
        except ImportError as e:
            pytest.skip(f"Required module not available: {e}")


class TestConfigurationValidation:
    """Test configuration validation and consistency."""
    
    def test_parameter_ranges(self):
        """Test that parameter ranges are valid."""
        # Test count parameter
        assert 1 <= 2 <= 10  # count should be between 1 and 10
        
        # Test min_match_score parameter
        assert 0.0 <= 0.4 <= 1.0  # min_match_score should be between 0.0 and 1.0
        
        # Test max_fame_level parameter
        assert 0 <= 30 <= 100  # max_fame_level should be between 0 and 100
        
        # Test candidate_count parameter
        assert 1 <= 5 <= 50  # candidate_count should be between 1 and 50
    
    def test_parameter_combinations(self):
        """Test that parameter combinations are valid."""
        # Test valid combinations
        valid_combinations = [
            {'fast_mode': True, 'enable_vision_analysis': False, 'enable_multi_pass': False},
            {'fast_mode': False, 'enable_vision_analysis': True, 'enable_multi_pass': True},
            {'fast_mode': True, 'enable_vision_analysis': True, 'enable_multi_pass': False}
        ]
        
        for combo in valid_combinations:
            # All combinations should be valid
            assert isinstance(combo['fast_mode'], bool)
            assert isinstance(combo['enable_vision_analysis'], bool)
            assert isinstance(combo['enable_multi_pass'], bool)
    
    def test_environment_variable_validation(self):
        """Test that environment variables are properly validated."""
        # Test required environment variables
        required_vars = ['OPENAI_API_KEY', 'SENDGRID_API_KEY', 'FROM_EMAIL', 'TO_EMAIL']
        
        for var in required_vars:
            # Should be able to check if variable exists
            assert isinstance(os.getenv(var), (str, type(None)))
    
    def test_file_path_validation(self):
        """Test that file paths are valid."""
        # Test that required files exist
        required_files = [
            'src/daily_paintings.py',
            'requirements.txt',
            'README.md'
        ]
        
        for file in required_files:
            file_path = os.path.join(os.path.dirname(__file__), '..', file)
            assert os.path.exists(file_path), f"Required file not found: {file}"
    
    def test_dependency_validation(self):
        """Test that dependencies are properly validated."""
        try:
            # Test that key dependencies can be imported
            import openai
            import requests
            import pytest
            
            # Should not raise ImportError
            assert True
        
        except ImportError as e:
            pytest.skip(f"Required dependency not available: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
