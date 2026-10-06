from collections import Counter, defaultdict


REPAIR_PLAYBOOK = {
    "missing_column": {
        "severity": "critical",
        "recommendation": "Map the incoming column name to the expected contract or ask the upstream team to add the field.",
        "example_fix": "Rename 'order date' to 'order_ts' before loading.",
    },
    "missing_value": {
        "severity": "high",
        "recommendation": "Reject rows missing required identifiers and notify the source owner.",
        "example_fix": "Quarantine rows where order_id or customer_id is blank.",
    },
    "type_error": {
        "severity": "high",
        "recommendation": "Apply type casting with strict failure handling and quarantine values that cannot be parsed.",
        "example_fix": "Convert amount with pandas.to_numeric(errors='coerce'), then quarantine null results.",
    },
    "date_parse_error": {
        "severity": "high",
        "recommendation": "Normalize timestamp formats before validation and flag unsupported date strings.",
        "example_fix": "Use pandas.to_datetime(..., utc=True) and quarantine invalid dates.",
    },
    "range_error": {
        "severity": "medium",
        "recommendation": "Add business rules for impossible values like negative amount or zero quantity.",
        "example_fix": "Reject amount <= 0 and quantity <= 0.",
    },
    "duplicate_key": {
        "severity": "high",
        "recommendation": "Deduplicate by business key and keep the first valid event, or merge using source timestamp.",
        "example_fix": "Drop duplicate order_id values before loading clean records.",
    },
    "invalid_domain": {
        "severity": "medium",
        "recommendation": "Validate categorical values against an allowed domain and route unknown values for review.",
        "example_fix": "Only accept payment_method in card, ach, paypal, wire, apple_pay.",
    },
}


def build_repair_suggestions(issues: list[dict]) -> list[dict]:
    grouped = defaultdict(list)
    for issue in issues:
        grouped[issue["issue_type"]].append(issue)

    suggestions = []
    for issue_type, issue_group in grouped.items():
        play = REPAIR_PLAYBOOK.get(
            issue_type,
            {
                "severity": "medium",
                "recommendation": "Review the failed records and add a source-specific rule.",
                "example_fix": "Add a validation branch for this issue type.",
            },
        )
        fields = sorted({issue["field"] for issue in issue_group})
        suggestions.append(
            {
                "severity": play["severity"],
                "issue_type": issue_type,
                "recommendation": f"{play['recommendation']} Affected fields: {', '.join(fields)}.",
                "example_fix": play["example_fix"],
            }
        )
    return suggestions


def explain_run(total_rows: int, clean_rows: int, quarantine_rows: int, issues: list[dict]) -> str:
    if total_rows == 0:
        return "No records were processed. Check whether the source file is empty or the schema is missing required columns."

    issue_counts = Counter(issue["issue_type"] for issue in issues)
    top_issues = ", ".join(f"{name}: {count}" for name, count in issue_counts.most_common(3))
    if quarantine_rows == 0:
        return f"Pipeline completed cleanly. All {clean_rows} records passed validation."
    return (
        f"Pipeline processed {total_rows} records. {clean_rows} records were loaded and "
        f"{quarantine_rows} records were quarantined. Main issues: {top_issues}."
    )
