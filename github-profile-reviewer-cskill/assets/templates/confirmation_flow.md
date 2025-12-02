# Confirmation Flow Templates

## Double Confirmation Protocol

All destructive actions require TWO explicit confirmations from the user.

### Repository Removal Confirmation

```
===========================================================
         REPOSITORY REMOVAL CONFIRMATION
===========================================================

Repository: {repo_name}
URL: {repo_url}
Classification: {classification}
Reason for Recommendation: {reason}

Last Activity: {last_activity}
Stars: {stars} | Forks: {forks}

THIS ACTION WILL:
- Delete the repository "{repo_name}"
- Remove all code, issues, pull requests, and wiki
- This action CANNOT be undone

===========================================================

To proceed, please type:
"I confirm I want to delete {repo_name}"

Then you will be asked to confirm again.
```

### Second Confirmation

```
===========================================================
         FINAL CONFIRMATION REQUIRED
===========================================================

You have requested to DELETE repository: {repo_name}

Are you ABSOLUTELY SURE?

- All code will be permanently deleted
- All issues and pull requests will be lost
- This CANNOT be reversed

===========================================================

Type "YES" to proceed, or anything else to cancel:
```

### Repository Archiving Confirmation

```
===========================================================
         REPOSITORY ARCHIVE CONFIRMATION
===========================================================

Repository: {repo_name}
Classification: {classification}
Reason: {reason}

THIS ACTION WILL:
- Make the repository read-only
- Preserve all code, history, and metadata
- This CAN be undone by unarchiving later

===========================================================

To proceed, please type:
"I confirm I want to archive {repo_name}"
```

### Repository Visibility Change

```
===========================================================
         VISIBILITY CHANGE CONFIRMATION
===========================================================

Repository: {repo_name}
Current Visibility: {current_visibility}
New Visibility: {new_visibility}

THIS ACTION WILL:
- Change repository from {current_visibility} to {new_visibility}
{visibility_specific_warning}

===========================================================

To proceed, please type:
"I confirm I want to make {repo_name} {new_visibility}"
```

### Bulk Action Confirmation

```
===========================================================
         BULK ACTION CONFIRMATION
===========================================================

You have requested to {action} the following repositories:

{repo_list}

Total: {count} repositories

THIS IS A BULK ACTION - Please review carefully.

===========================================================

To proceed with ALL {count} repositories, type:
"I confirm I want to {action} all {count} repositories"

Or specify individual repositories to process.
```

### Cancellation Response

```
===========================================================
         ACTION CANCELLED
===========================================================

No changes have been made to repository: {repo_name}

Your data remains safe and unchanged.

Would you like to:
1. Review other recommendations
2. Get more information about this recommendation
3. End the review session
```

### Success Response

```
===========================================================
         ACTION COMPLETED
===========================================================

Successfully {action}: {repo_name}

Summary:
- Action: {action}
- Repository: {repo_name}
- Timestamp: {timestamp}

Note: {additional_notes}

Would you like to proceed with other recommendations?
```

## Confirmation State Machine

```
[RECOMMENDATION PRESENTED]
         |
         v
[AWAITING FIRST CONFIRMATION]
         |
    User types confirmation phrase
         |
         v
[AWAITING SECOND CONFIRMATION]
         |
    User types "YES"
         |
         v
[EXECUTING ACTION]
         |
         v
[ACTION COMPLETE / REPORT STATUS]
```

## Error Handling

### Invalid Confirmation

```
I didn't receive a valid confirmation.

To confirm this action, please type exactly:
"{required_phrase}"

Or type "cancel" to abort this action.
```

### Network Error During Action

```
A network error occurred while attempting to {action}.

The action may not have completed. Please:
1. Check your GitHub account to verify the current state
2. Retry the action if needed

Error details: {error}
```

### Permission Denied

```
Unable to {action} repository "{repo_name}".

Reason: Insufficient permissions

To perform this action, you need:
- {required_permission}

Please check your GitHub token permissions or repository access.
```
