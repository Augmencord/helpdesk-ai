"""
Helpdesk Agent Tools (Skills)
-----------------------------
Custom Python functions that the Gemini agent can invoke to resolve tickets.
Each function acts as a mock service — in production these would call real APIs.
"""

import uuid
from datetime import datetime


def trigger_password_reset(username: str) -> str:
    """Triggers a password reset for the given username and returns a reset link.

    Use this tool when a user reports that they forgot their password
    and needs to reset it.

    Args:
        username: The username or email of the employee requesting a password reset.

    Returns:
        A message containing the password reset link and instructions.
    """
    reset_token = uuid.uuid4().hex[:16]
    reset_link = f"https://helpdesk.example.com/reset?token={reset_token}&user={username}"
    expiry = "30 minutes"

    return (
        f"Password reset initiated for user '{username}'.\n"
        f"Reset link: {reset_link}\n"
        f"This link will expire in {expiry}.\n"
        f"An email has also been sent to the address associated with '{username}'.\n"
        f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )


def check_account_status(username: str) -> str:
    """Checks whether the user account is locked or has other login issues.

    Use this tool when a user reports that their password is incorrect
    or they are unable to log in despite knowing their password.

    Args:
        username: The username or email of the employee experiencing login issues.

    Returns:
        A status report about the account including lock status and recommendations.
    """
    # Mock logic — simulate different statuses based on username patterns
    username_lower = username.lower()
    if "locked" in username_lower or "admin" in username_lower:
        return (
            f"Account Status for '{username}': 🔒 LOCKED\n"
            f"Reason: Multiple failed login attempts detected.\n"
            f"Last failed attempt: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"Action taken: Account has been temporarily unlocked.\n"
            f"Recommendation: Please try logging in again. If the issue persists, "
            f"a password reset is recommended."
        )
    else:
        return (
            f"Account Status for '{username}': ✅ ACTIVE (Not Locked)\n"
            f"Last successful login: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"No failed login attempts detected recently.\n"
            f"Recommendation: The password may have expired. Please use the "
            f"password reset option or verify you are entering the correct credentials. "
            f"Also check that Caps Lock is not enabled."
        )


def get_leave_balance(employee_id: str) -> str:
    """Retrieves the leave balance for an employee by their employee ID.

    Use this tool when a user wants to check their remaining leave
    balance, PTO days, sick days, or vacation days.

    Args:
        employee_id: The unique employee ID (e.g., EMP001, 12345).

    Returns:
        A detailed breakdown of the employee's leave balance.
    """
    # Mock leave data
    return (
        f"Leave Balance for Employee ID '{employee_id}':\n"
        f"┌────────────────────┬───────────┬──────────┬───────────┐\n"
        f"│ Leave Type         │ Allocated │ Used     │ Remaining │\n"
        f"├────────────────────┼───────────┼──────────┼───────────┤\n"
        f"│ Paid Time Off      │ 20 days   │ 6 days   │ 14 days   │\n"
        f"│ Sick Leave          │ 10 days   │ 5 days   │ 5 days    │\n"
        f"│ Personal Days       │ 3 days    │ 1 day    │ 2 days    │\n"
        f"│ Floating Holidays   │ 2 days    │ 0 days   │ 2 days    │\n"
        f"└────────────────────┴───────────┴──────────┴───────────┘\n"
        f"Total remaining leave: 23 days\n"
        f"Note: Leave balances reset on January 1st each year."
    )
