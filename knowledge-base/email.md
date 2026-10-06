# Email Troubleshooting Guide

## Issue
User is experiencing issues sending or receiving emails.

## Symptoms
- Emails are not arriving in the inbox
- Outbound emails are stuck in the outbox
- "Mailbox full" warning
- Cannot connect to Exchange server

## Possible Causes
- Mailbox quota exceeded
- Outlook client in offline mode
- Network connectivity issues

## Troubleshooting Steps
1. Check if the user's mailbox has exceeded its storage quota.
2. Verify that the Outlook client says "Connected to Microsoft Exchange" at the bottom.
3. If it says "Working Offline", toggle the offline mode button.
4. Test sending an email via the Outlook Web Access (OWA) portal to rule out client issues.

## When to Escalate
If OWA is also failing or multiple users report the same issue, escalate to the Exchange/O365 Admin team.

## Warnings
Do not delete user emails to free up space without their explicit permission.
