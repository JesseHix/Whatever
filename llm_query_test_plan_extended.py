
# EXTENDED TEST PLAN AND EVALUATION SCRIPT FOR LLM-TO-ELASTICSEARCH TRANSLATIONS

from elasticsearch import Elasticsearch
import re
from typing import List, Tuple

# Connect to local Elasticsearch instance
es = Elasticsearch("http://localhost:9200")

# Define test cases with user input and expected DSL query pattern
test_cases = [
    {
        "user_input": "Show me error logs from the past day",
        "expected_pattern": r'"match":\s*\{\s*"message":\s*"error"\s*\}.*"range":\s*\{\s*"@timestamp":\s*\{\s*"gte":\s*"now-1d/d"',
        "description": "Error logs from past 1 day"
    },
    {
        "user_input": "List failed login attempts in the last 7 days",
        "expected_pattern": r'"match":\s*\{\s*"event\.outcome":\s*"failure"\s*\}.*"range":\s*\{\s*"@timestamp":\s*\{\s*"gte":\s*"now-7d/d"',
        "description": "Failed login attempts in last 7 days"
    },
    {
        "user_input": "Get all logs where the user is admin",
        "expected_pattern": r'"match":\s*\{\s*"user\.name":\s*"admin"\s*\}',
        "description": "Logs for user admin"
    },
    {
        "user_input": "Show successful logins in the last hour",
        "expected_pattern": r'"match":\s*\{\s*"event\.outcome":\s*"success"\s*\}.*"range":\s*\{\s*"@timestamp":\s*\{\s*"gte":\s*"now-1h/h"',
        "description": "Successful logins in last hour"
    },
    {
        "user_input": "Find documents with log level ERROR",
        "expected_pattern": r'"match":\s*\{\s*"log\.level":\s*"ERROR"\s*\}',
        "description": "Log level ERROR"
    }
]

# Dummy LLM function (replace with your model’s actual generation)
def llm_generate_query(prompt: str) -> str:
    prompt = prompt.lower()
    if "error logs" in prompt:
        return """GET /_search
{
  "query": {
    "bool": {
      "must": [
        { "match": { "message": "error" }}
      ],
      "filter": {
        "range": {
          "@timestamp": {
            "gte": "now-1d/d"
          }
        }
      }
    }
  }
}"""
    elif "failed login" in prompt:
        return """GET /_search
{
  "query": {
    "bool": {
      "must": [
        { "match": { "event.outcome": "failure" }}
      ],
      "filter": {
        "range": {
          "@timestamp": {
            "gte": "now-7d/d"
          }
        }
      }
    }
  }
}"""
    elif "user is admin" in prompt:
        return """GET /_search
{
  "query": {
    "match": {
      "user.name": "admin"
    }
  }
}"""
    elif "successful logins" in prompt:
        return """GET /_search
{
  "query": {
    "bool": {
      "must": [
        { "match": { "event.outcome": "success" }}
      ],
      "filter": {
        "range": {
          "@timestamp": {
            "gte": "now-1h/h"
          }
        }
      }
    }
  }
}"""
    elif "log level" in prompt and "error" in prompt:
        return """GET /_search
{
  "query": {
    "match": {
      "log.level": "ERROR"
    }
  }
}"""
    return ""

# Validate structure and optionally execute against ES
def evaluate_llm_responses(test_cases: List[dict], execute=False) -> List[Tuple[str, bool, str]]:
    results = []
    for test in test_cases:
        query = llm_generate_query(test["user_input"])
        normalized_query = query.replace("\n", "").replace(" ", "").replace("\t", "")
        match = re.search(test["expected_pattern"], normalized_query, re.DOTALL)
        success = bool(match)
        status = "PASS" if success else "FAIL"
        print(f"{test['description']:<45} | Structure Test: {status}")

        if execute and success:
            try:
                query_body = query.split("GET /_search")[1].strip()
                response = es.search(body=query_body)
                print(f"{'':<45} | Execution Test: PASS | Hits: {response['hits']['total']['value']}")
            except Exception as e:
                print(f"{'':<45} | Execution Test: FAIL | Error: {e}")
        elif execute:
            print(f"{'':<45} | Execution Skipped: DSL malformed")

    return results

# Set to True to actually run the queries against Elasticsearch
evaluate_llm_responses(test_cases, execute=True)
