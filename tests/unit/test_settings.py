"""
Unit tests for the settings and configuration module.
"""

import pytest
from config.settings import get_settings, Settings


class TestSettingsDefaults:

    def test_settings_loads(self):
        settings = get_settings()
        assert settings is not None

    def test_aws_region_default(self):
        settings = get_settings()
        assert settings.aws_region == "eu-west-2"

    def test_opensearch_index_default(self):
        settings = get_settings()
        assert settings.opensearch_index_name == "mortgage-policy-docs"

    def test_dynamodb_state_table_default(self):
        settings = get_settings()
        assert settings.dynamodb_state_table == "mortgage-agent-state"

    def test_dynamodb_memory_table_default(self):
        settings = get_settings()
        assert settings.dynamodb_memory_table == "mortgage-agent-memory"

    def test_rag_top_k_default(self):
        settings = get_settings()
        assert settings.rag_top_k == 5

    def test_agent_max_steps_default(self):
        settings = get_settings()
        assert settings.agent_max_steps == 20


class TestSettingsValidation:

    def test_compliance_threshold_between_0_and_1(self):
        settings = get_settings()
        assert 0.0 <= settings.compliance_confidence_threshold <= 1.0

    def test_bedrock_temperature_between_0_and_1(self):
        settings = get_settings()
        assert 0.0 <= settings.bedrock_temperature <= 1.0

    def test_aws_account_id_is_set(self):
        settings = get_settings()
        assert settings.aws_account_id is not None
        assert len(settings.aws_account_id) > 0

    def test_anthropic_api_key_is_set(self):
        settings = get_settings()
        assert settings.anthropic_api_key is not None
        assert settings.anthropic_api_key.startswith("sk-")

    def test_opensearch_endpoint_is_set(self):
        settings = get_settings()
        assert settings.opensearch_endpoint is not None
        assert settings.opensearch_endpoint.startswith("http")


class TestSettingsCaching:

    def test_get_settings_returns_same_instance(self):
        s1 = get_settings()
        s2 = get_settings()
        assert s1 is s2