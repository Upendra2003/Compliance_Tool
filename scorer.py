"""
DPDP Act Compliance Scoring Engine

This module calculates compliance scores based on check results.
All scoring logic is centralized here for maintainability and scalability.
"""

# =========================================
# CONFIGURATION
# =========================================

DPDP_CONFIG = {
    # Total DPDP categories
    "total_categories": 5,
    "category_weight": 100 / 5,  # 20% each

    # All DPDP categories
    "all_categories": [
        "Notice & Transparency",
        "Consent Management",
        "Data Minimization",
        "Retention",
        "Deletion"
    ],

    # Category to group mapping (maps category name to check group)
    "category_to_group": {
        "Notice & Transparency": "notice",
        "Consent Management": "consent",
        "Data Minimization": "data_minimization",
        "Retention": "retention",
        "Deletion": "deletion",
    },

    # Check metadata for each implemented category
    "check_metadata": {
        "notice": {
            "privacy_policy_exists": {
                "label": "Privacy Policy Exists",
                "weight": 1/3  # Equal weighting for 3 checks
            },
            "clear_language": {
                "label": "Clear Language",
                "weight": 1/3
            },
            "indian_languages": {
                "label": "Indian Languages",
                "weight": 1/3
            }
        },
        "consent": {
            "opt_in_or_opt_out": {
                "label": "Checks Opt in or Opt Out Mechanism",
                "weight": 1/2,
            },
            "consent_for_training":{
                "label": "Consent for training",
                "weight": 1/2,
            },
        },
        "retention": {
            "retention_period": {
                "label": "Checks retention periods",
                "weight": 1/2,
            },
            "specific_timeframe":{
                "label": "Specific Timeframe of the retention",
                "weight": 1/2,
            },
        },
        "deletion": {
            "deletion_doc": {
                "label": "Deletion mechanism documented",
                "weight": 1/2,
            },
            "offers_deletion": {
                "label": "Offers deletion options",
                "weight": 1/2,
            },
        },
        "data_minimization": {
            "data_min": {
                "label": "Only necessary data has to be processed",
                "weight": 1,
            }
        }
    },

    # Grading thresholds
    "grade_thresholds": {
        "HIGH": 75,
        "MODERATE": 60
    }
}


# =========================================
# CORE SCORING FUNCTIONS
# =========================================


def calculate_category_score(check_results, group_name):
    metadata = DPDP_CONFIG["check_metadata"].get(group_name, {})

    if not metadata:
        return {
            "score": 0,
            "score_percent": 0,
            "breakdown": []
        }

    total_score = 0
    total_weight = 0
    breakdown = []

    for check in check_results:
        check_id = check["id"]
        check_meta = metadata.get(check_id)

        if check_meta:
            weight = check_meta["weight"]
            individual_score = check.get("score",0)
            contribution = individual_score * weight

            total_score += contribution
            total_weight += weight

            breakdown.append({
                "id": check_id,
                "label": check_meta["label"],
                "passed": check["passed"],
                "raw_score": individual_score,
                "weight": weight,
                "contribution": contribution,
                "message": check["message"]
            })

    # Calculate category score as percentage (0-1)
    category_score = total_score / total_weight if total_weight > 0 else 0

    return {
        "score": category_score,
        "score_percent": round(category_score * 100, 1),
        "breakdown": breakdown
    }


def determine_grade(overall_score):
    """
    Determine compliance grade based on overall score.

    Args:
        overall_score (float): Overall score (0-100)

    Returns:
        str: Grade (HIGH, MODERATE, or LOW)
    """
    if overall_score >= DPDP_CONFIG["grade_thresholds"]["HIGH"]:
        return "HIGH"
    elif overall_score >= DPDP_CONFIG["grade_thresholds"]["MODERATE"]:
        return "MODERATE"
    else:
        return "LOW"


def determine_status(grade):
    """
    Determine compliance status based on grade.

    Args:
        grade (str): Compliance grade

    Returns:
        str: Status message
    """
    if grade == "HIGH":
        return "COMPLIANT"
    else:
        return "NEEDS IMPROVEMENT"


# =========================================
# MAIN SCORING FUNCTION
# =========================================

def calculate_compliance_score(check_results):
    print(f"SCORER: Starting score calculation for {len(check_results)} check results")

    # Group results by category
    grouped_results = {}

    for result in check_results:
        group = result["group"]
        if group not in grouped_results:
            grouped_results[group] = []
        grouped_results[group].append(result)

    print(f"SCORER: Grouped results into {len(grouped_results)} categories: {list(grouped_results.keys())}")

    # Calculate scores for each category
    category_scores = []
    total_contribution = 0

    for category_name in DPDP_CONFIG["all_categories"]:
        group_name = DPDP_CONFIG["category_to_group"].get(category_name)

        if group_name and group_name in grouped_results:
            # This category is implemented
            print(f"SCORER: Calculating score for '{category_name}' (group: {group_name})")

            category_data = calculate_category_score(
                grouped_results[group_name],
                group_name,
            )

            contribution = category_data["score"] * DPDP_CONFIG["category_weight"]
            total_contribution += contribution

            print(f"SCORER:   - Category score: {category_data['score_percent']}%")
            print(f"SCORER:   - Contribution to overall: {contribution:.2f}")

            category_scores.append({
                "category": category_name,
                "score_percent": category_data["score_percent"],
                "weight": round(DPDP_CONFIG["category_weight"], 2),
                "contribution": round(contribution, 2),
                "implemented": True,
                "breakdown": category_data["breakdown"]
            })
        else:
            # This category is not yet implemented
            print(f"SCORER: Skipping '{category_name}' (not implemented)")

            category_scores.append({
                "category": category_name,
                "score_percent": None,
                "weight": round(DPDP_CONFIG["category_weight"], 2),
                "contribution": 0,
                "implemented": False,
                "breakdown": []
            })

    # Calculate overall score and determine grade/status
    overall_score = round(total_contribution, 2)
    grade = determine_grade(overall_score)
    status = determine_status(grade)

    print(f"\nSCORER: Final Results:")
    print(f"SCORER:   - Overall Score: {overall_score}/100")
    print(f"SCORER:   - Grade: {grade}")
    print(f"SCORER:   - Status: {status}")

    # Build complete scoring report
    scoring_report = {
        "overall": {
            "score": overall_score,
            "grade": grade,
            "status": status
        },
        "categories": category_scores
    }

    return scoring_report


# =========================================
# HELPER FUNCTIONS FOR ADDING NEW POLICIES
# =========================================

def add_policy_category(category_name, group_name, checks_config):
    """
    Helper function to add a new policy category configuration.

    Usage example:
        add_policy_category(
            "Consent Management",
            "consent",
            {
                "explicit_consent": {"label": "Explicit Consent", "weight": 0.5},
                "consent_withdrawal": {"label": "Consent Withdrawal", "weight": 0.5}
            }
        )

    Args:
        category_name (str): Display name of the category
        group_name (str): Internal group name used in check results
        checks_config (dict): Dict of check_id -> {label, weight}
    """
    DPDP_CONFIG["category_to_group"][category_name] = group_name
    DPDP_CONFIG["check_metadata"][group_name] = checks_config
    print(f"✓ Added policy category: {category_name} (group: {group_name})")
