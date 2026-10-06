# Application Access Request

## Issue
User needs access to a specific enterprise application (e.g., Jira, Confluence, Salesforce).

## Symptoms
- "Access Denied" error
- Application does not appear in the SSO portal

## Possible Causes
- User is not in the correct AD group
- License limit reached
- Role change

## Troubleshooting Steps
1. Identify the specific application and the required access level.
2. Check if the user belongs to the corresponding Active Directory or SSO group.
3. If the user is missing the group, request Manager approval for access.
4. Once approved, add the user to the appropriate group.

## When to Escalate
If the application requires a paid license and no licenses are available, escalate to IT Procurement.

## Warnings
Do not grant Admin access to applications unless explicitly approved by the system owner.
