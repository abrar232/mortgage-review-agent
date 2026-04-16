from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from functools import lru_cache


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # ── AWS Core ──────────────────────────────────────────────────────────────
    aws_region: str = Field("eu-west-2", description="Primary AWS region (London)")
    aws_account_id: str = Field(..., description="AWS account ID")
    anthropic_api_key: str = Field(...)

    # ── AWS Bedrock ───────────────────────────────────────────────────────────
    bedrock_model_id: str = Field("anthropic.claude-3-5-sonnet-20241022-v2:0")
    bedrock_max_tokens: int = Field(4096)
    bedrock_temperature: float = Field(0.0, ge=0.0, le=1.0)

    # ── AWS OpenSearch ────────────────────────────────────────────────────────
    opensearch_endpoint: str = Field(...)
    opensearch_index_name: str = Field("mortgage-policy-docs")
    opensearch_username: str = Field("admin")
    opensearch_password: str = Field(...)

    # ── AWS DynamoDB ──────────────────────────────────────────────────────────
    dynamodb_state_table: str = Field("mortgage-agent-state")
    dynamodb_memory_table: str = Field("mortgage-agent-memory")

    # ── AWS SQS ───────────────────────────────────────────────────────────────
    sqs_ingestion_queue_url: str = Field(...)
    sqs_compliance_queue_url: str = Field(...)
    sqs_handoff_queue_url: str = Field(...)

    # ── AWS S3 ────────────────────────────────────────────────────────────────────
    s3_documents_bucket: str = Field("mortgage-application-documents")
    s3_policy_docs_bucket: str = Field("mortgage-policy-store")

    # ── Agent behaviour ───────────────────────────────────────────────────────
    agent_max_steps: int = Field(20)
    compliance_confidence_threshold: float = Field(0.75, ge=0.0, le=1.0)
    rag_top_k: int = Field(5)

    # ── AWS CloudWatch ────────────────────────────────────────────────────────────
    cloudwatch_log_group: str = Field("/mortgage-review-agent/prod")
    cloudwatch_metrics_namespace: str = Field("MortgageReviewAgent")


@lru_cache
def get_settings() -> Settings:
    return Settings()