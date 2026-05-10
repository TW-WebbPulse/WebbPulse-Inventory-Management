# Contributing

Thanks for your interest in contributing. This project is open-sourced as-is from a working codebase, so contributions are reviewed on a best-effort basis.

## Before you start

For anything beyond a small fix, please open an issue first to discuss the change. This avoids surprises and saves your time if a PR isn't going to be a fit.

## Development setup

See the **Getting started** section in [README.md](README.md). The short version:

1. Clone the repo and install the Firebase CLI
2. Point `.firebaserc` at your own Firebase project and regenerate the FlutterFire config files
3. Drop a service-account key at `functions/gcp_key.json`
4. `firebase emulators:start` to run the backend locally
5. `cd flutter && flutter run` to run the client

You don't need a Verkada or SendGrid account to work on most parts of the codebase. Those integrations only activate when their respective settings/credentials are present.

## Project layout

```
flutter/                      Flutter client (web, mobile, desktop)
  lib/src/apps/               Authed and non-authed app shells
  lib/src/shared/             Providers, widgets, services
functions/                    Python Cloud Functions
  main.py                     Entry-point registrations
  src/callable_functions/     Callable functions (org admin / member / global)
  src/firestore_triggered_functions/
  src/scheduled_functions/    Scheduled syncers and cleaners (Verkada)
  src/helper_functions/       Shared business logic
firestore.rules               Firestore security rules
firestore.indexes.json        Composite indexes
firebase.json                 Firebase project config (functions, hosting, emulators)
.github/workflows/            CI/CD reference (workflow_dispatch only)
```

## Code style

### Flutter / Dart
- Run `flutter analyze` before submitting; it must pass with no warnings.
- Follow `flutter_lints` rules (configured in `flutter/analysis_options.yaml`).
- Use `ChangeNotifier` providers for state — match the existing patterns in `flutter/lib/src/shared/providers/`.

### Python (Cloud Functions)
- Match the style of existing files in `functions/src/`.
- New callable functions: re-use the patterns in `functions/src/callable_functions/` for auth checks (`check_user_is_authed`, `check_user_is_email_verified`, `check_user_token_current`, role checks). Don't roll your own.
- New rate-limited callable functions: register them in `functions/src/rate_limit_config.py`.
- Don't import secrets at module top-level — load them inside function bodies so cold-start failures don't take down the whole codebase.

## Security-sensitive changes

Be especially careful with changes that touch:

- `firestore.rules` — review the whole file after editing; the recursive `{document=**}` rule has subtle interaction with the explicit `sensitiveConfigs` exclusion
- Custom auth claim logic in `functions/src/helper_functions/users/`
- Anything reading or writing `organizations/{orgId}/sensitiveConfigs/`

If you're touching authn/authz, please call it out explicitly in your PR description.

## Pull request process

1. Fork the repo and create a topic branch from `master`
2. Make your changes in focused commits with clear messages
3. Run `flutter analyze` and `flutter test` (the latter if you've changed Dart code)
4. Open a PR using the [PR template](.github/pull_request_template.md)
5. Be patient — reviews are best-effort

A PR is most likely to be accepted when it:
- Targets a single concern (don't bundle unrelated changes)
- Includes a brief description of what changed and why
- Doesn't widen the surface area of `sensitiveConfigs` or weaken Firestore rules without strong justification
- Doesn't add new dependencies without a reason

## Reporting security issues

Please **don't** open public GitHub issues for security vulnerabilities. Instead, contact the maintainer directly via the email associated with the GitHub account on this repository.

## License

By contributing, you agree that your contributions will be licensed under the [MIT License](LICENSE).
