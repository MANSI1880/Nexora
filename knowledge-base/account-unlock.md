# Account Unlock Guide

## Issue
User account is locked due to too many failed login attempts.

## Symptoms
- "Account locked" error message
- Cannot access Active Directory services
- Cannot access VPN

## Possible Causes
- Incorrect password entered multiple times
- Cached old credentials on a mobile device
- Brute force security protection

## Troubleshooting Steps
1. Verify the user's identity using standard Helpdesk procedures.
2. Check the Active Directory logs to confirm the lockout reason.
3. If locked due to bad passwords, use the self-service unlock tool or unlock manually via AD.
4. Advise the user to update saved passwords on all mobile devices.

## When to Escalate
If the account locks out repeatedly after being unlocked, escalate to the Security Team for investigation.

## Warnings
Do not unlock accounts without verifying the user's identity first.
