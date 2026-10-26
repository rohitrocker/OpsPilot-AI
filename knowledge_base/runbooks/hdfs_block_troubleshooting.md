# HDFS Block Troubleshooting

## Purpose

Investigate HDFS logs related to block receiving, writing, replication,
and storage failures.

## Symptoms

-   A block write operation fails.
-   Logs repeatedly report block replication errors.
-   A DataNode becomes unavailable.
-   The same block identifier appears in repeated failure messages.

## Diagnostic steps

1.  Search surrounding logs for the same block ID.
2.  Check for `ERROR`, `Exception`, `failed`, or timeout messages.
3.  Identify the relevant NameNode and DataNode.
4.  Check DataNode health and disk availability.
5.  Review block replication status using approved Hadoop tools.
6.  Compare findings with the system's operational documentation.

## Possible causes

-   DataNode connectivity problems.
-   Insufficient disk space.
-   Disk I/O failures.
-   Replication or network issues.

## Recovery

Follow the approved operational procedure for the confirmed cause. Do
not restart services or delete blocks solely because a model flags a log
as anomalous.

## Verification

Confirm service health and check whether the related errors continue
after the corrective action.

## Safety

An `INFO` message about receiving a block can be normal. Confirm a
failure using surrounding logs and system evidence.

## Source and maintenance

-   Use the official Apache Hadoop documentation to validate
    environment-specific steps: https://hadoop.apache.org/docs/
-   This is a starter runbook for the OpsPilot AI project, not an
    official Apache procedure.
-   Review and adapt the steps before using them in a real environment.
