from all_policies import ALL_CHECK_GROUPS

# Mapping for display names
GROUP_DISPLAY_NAMES = {
    "notice": "Notice & Transparency",
    "consent": "Consent Management",
    "retention": "Retention",
    "deletion": "Deletion",
    "data_minimization":"Data Minimization"
}

def run_all_checks_with_progress(policy_doc, progress_callback=None):
    """
    Run all checks with optional progress callback.

    Args:
        policy_doc: The policy document to check
        progress_callback: Optional function(message_type, data) to report progress

    Returns:
        List of check results
    """
    all_results = []
    print(f"CHECKER: Running checks for {len(ALL_CHECK_GROUPS)} policy groups")

    for group_name, module in ALL_CHECK_GROUPS.items():
        display_name = GROUP_DISPLAY_NAMES.get(group_name, group_name.replace('_', ' ').title())

        print(f"CHECKER: Processing group '{group_name}' ({len(module.CHECKS)} checks)")

        # Notify that we're starting this category
        if progress_callback:
            progress_callback('category_start', {
                'category': display_name,
                'group': group_name,
                'total_checks': len(module.CHECKS)
            })

        for meta in module.CHECKS:
            check_id = meta["id"]
            print(f"CHECKER:   - Running check '{check_id}'...")

            fn = module.IMPLEMENTATIONS[check_id]
            score, passed, msg = fn(policy_doc)

            print(f"CHECKER:     Result: {'PASS' if passed else 'FAIL'} (score: {score:.2f})")

            all_results.append({
                "group": group_name,
                **meta,
                "passed": passed,
                "score": score,
                "message": msg,
            })

        # Notify that we've completed this category
        if progress_callback:
            progress_callback('category_complete', {
                'category': display_name,
                'group': group_name
            })

    print(f"CHECKER: Completed all checks - {len(all_results)} total results")
    return all_results