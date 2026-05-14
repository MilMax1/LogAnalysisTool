from typing import List, Dict, Any

Rule = Dict[str, Any]
ParsedLog = Dict[str, Any]
DetectedEvent = Dict[str, Any]

RULES: List[Rule] = [

        {
        "id": "error_level",
        "type": "error_log",
        "severity": "high",
        "field": "level",
        "contains": ["ERROR", "FATAL"],
        "description": "Row with ERROR or FATAL."
    },

    {
        "id": "warning_level",
        "type": "warning_log",
        "severity": "medium",
        "field": "level",
        "contains": ["WARN", "WARNING"],
        "description": "Row with WARN or WARNING."
    },
      {
        "id": "exception_detected",
        "type": "exception",
        "severity": "high",
        "field": "message",
        "contains": ["exception", "stacktrace"],
        "description": "Row with exception or stacktrace."
    },
        {
        "id": "timeout_detected",
        "type": "timeout",
        "severity": "high",
        "field": "message",
        "contains": ["timeout", "timed out"],
        "description": "Row with timeout-related event."
    },
        {
        "id": "failure_detected",
        "type": "failure",
        "severity": "high",
        "field": "message",
        "contains": ["failed", "failure", "could not", "unable"],
        "description": "Row with failed operation."
    },
        {
        "id": "replica_or_block_issue",
        "type": "hdfs_block_replica_issue",
        "severity": "high",
        "field": "message",
        "contains": ["replica", "block missing", "missing block", "corrupt block"],
        "description": "Row with possible block or replica issue."
    },
        {
        "id": "datanode_issue",
        "type": "datanode_issue",
        "severity": "medium",
        "field": "message",
        "contains": ["datanode"],
        "description": "Row with DataNode-related event."
    },
        {
        "id": "namenode_issue",
        "type": "namenode_issue",
        "severity": "medium",
        "field": "message",
        "contains": ["namenode"],
        "description": "Row with NameNode-related event."
    }
]