# WebbPulse Inventory Management

A full-stack inventory management system built with Flutter and Firebase, designed for tracking device checkout status with optional Verkada Command integration.

> Originally built to run at `inventory.webbpulse.com`. The codebase is published here under the MIT License so others can self-host, fork, or learn from it.

## Features

### Core inventory management
- Device check-in / check-out with real-time status updates via Firestore
- Tracking by unique serial numbers, with per-organization regex validation
- Free-text checkout notes for context
- Live multi-user synchronization
- Per-device history of who checked out what, and when
- CSV export of device lists

### Organizations and access control
- Users can belong to multiple organizations simultaneously
- Three roles, enforced via Firebase Auth custom claims and Firestore rules:
  - **Org Admin** — full administrative privileges
  - **Desk Station** — can check out devices on behalf of other users
  - **Org Member** — self-service checkout for themselves
- Admin tools for adding/removing members and changing roles
- Per-org settings: device serial regex, background image

### Verkada Command integration (optional)
- Sync Verkada device IDs, types, and sites into Firestore
- Scheduled cleanup of Verkada device names and site assignments to reflect checkout status
- User group whitelisting for permission management
- Scheduled permission granting based on checkout state
- Per-product site designations

### Other
- Cross-platform Flutter client: web, iOS, Android, macOS, Windows, Linux
- Email-based authentication with email verification (passwordless custom-token sign-in supported via SendGrid)
- Per-function rate limiting for callable functions

## Architecture

### Frontend (Flutter)
- Flutter SDK `>=3.3.0 <4.0.0` (CI builds against Flutter 3.29.3)
- State management: Provider with `ChangeNotifier`
- Authentication: `firebase_ui_auth` with the email provider enabled. The Google and Apple sign-in packages are present in `pubspec.yaml` but are not currently wired into the auth provider list — see `flutter/lib/src/shared/authentication_provider_list.dart` if you want to enable them.
- Navigation: `Navigator` with named routes (the `go_router` dependency is listed in `pubspec.yaml` but not currently used)
- Firebase: `firebase_core`, `cloud_firestore`, `firebase_auth`, `cloud_functions`

### Backend (Firebase)
- **Firestore** for real-time data, with security rules in `firestore.rules`
- **Firebase Auth** with custom claims of the form `org_admin_{orgId}`, `org_deskstation_{orgId}`, `org_member_{orgId}`
- **Cloud Functions for Firebase (Python)** for callable, scheduled, and Firestore-triggered server logic
- **Firebase Hosting** for the Flutter web build

### Cloud Functions layout
Entry points are wired up in `functions/main.py`. Functions are grouped by trigger type:

- **Callable functions** under `functions/src/callable_functions/`
  - `org_admin_callables/` — organization, user, device, and Verkada admin operations
  - `org_member_callables/` — device creation, checkout status updates
  - `global_user_callables/` — global user profile and organization creation
- **Firestore-triggered functions** under `functions/src/firestore_triggered_functions/`
  - `monitor_for_user_changes` — propagates user changes
- **Scheduled functions** under `functions/src/scheduled_functions/verkada_integration/`
  - Syncers: device IDs, site IDs, permissions
  - Cleaners: device names, device sites, user list, user groups

Rate limits per callable function are configured in `functions/src/rate_limit_config.py` — see that file to tune buckets per function group.

### Firestore data model
- `users/{userId}` — global user profile (read-only from clients)
- `usersMetadata/{userId}` — token revocation tracking (read-only from clients)
- `organizations/{orgId}` — organization document
  - `members/{userId}` — membership records
  - `devices/{deviceId}` — inventory items
  - `sensitiveConfigs/{configId}` — server-only config (e.g. `verkadaIntegrationSettings`); explicitly blocked from client reads in `firestore.rules`

All client writes are blocked at the Firestore rules layer. Mutations go through Cloud Functions, which enforce role and token-freshness checks.

## Getting started

### Prerequisites
- Flutter SDK `>=3.3.0` (CI uses 3.29.3)
- Node.js + npm (for the Firebase CLI)
- Python 3.13 (the deploy pipeline targets 3.13; older 3.x versions may work locally but are not tested)
- A Firebase project with Firestore, Authentication, Cloud Functions, and Hosting enabled
- Optional: a SendGrid account for transactional email
- Optional: Verkada Command access for the integration features

### Local setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/TW-WebbPulse/WebbPulse-Inventory-Management.git
   cd WebbPulse-Inventory-Management
   ```

2. **Install Firebase CLI and log in**
   ```bash
   npm install -g firebase-tools
   firebase login
   ```

3. **Point the project at your own Firebase project**
   - Update `.firebaserc` with your Firebase project ID
   - Re-run [FlutterFire CLI](https://firebase.google.com/docs/flutter/setup) to regenerate `flutter/lib/firebase_options.dart`, `flutter/android/app/google-services.json`, and `flutter/ios/Runner/GoogleService-Info.plist` for your project

4. **Provide service-account credentials for local Cloud Functions**
   - Download a service-account key from the Firebase / GCP console
   - Place it at `functions/gcp_key.json` (already gitignored)
   - This file is only needed for local emulator runs; deployed functions use the default service account

5. **(Optional) SendGrid**
   - Place your SendGrid API key at `functions/sendgrid_api_key.txt` (gitignored), or set `SENDGRID_API_KEY` in your environment

6. **Install Flutter dependencies**
   ```bash
   cd flutter
   flutter pub get
   ```

7. **Run the Firebase emulators**
   ```bash
   firebase emulators:start
   ```
   The emulator suite runs Auth (9099), Functions (5001), Firestore (8080), and Pub/Sub (8085). The Flutter app automatically connects to the emulators in debug mode.

8. **Run the app**
   ```bash
   cd flutter
   flutter run               # mobile / desktop
   flutter run -d chrome     # web
   ```

### Manual deployment

If you want to deploy your own instance:

```bash
# Functions
firebase deploy --only functions

# Firestore rules and indexes
firebase deploy --only firestore:rules,firestore:indexes

# Web build + hosting
cd flutter
flutter build web
cd ..
firebase deploy --only hosting
```

### CI/CD pipeline (reference only)

`.github/workflows/main-merge.yml` is included as a reference for the deploy pipeline used for the original `inventory.webbpulse.com` instance. It builds the web app, the Android app (Play Store internal track), and the iOS app (TestFlight), then deploys functions, rules, and hosting.

The workflow's `push` trigger has been removed — it now only runs via `workflow_dispatch`. It depends on org-specific secrets that forks will not have:
- `FIREBASE_APPLICATION_CREDENTIALS` — service-account JSON
- `SENDGRID_API_KEY`
- Android signing: `KEYSTORE_FILE`, `KEYSTORE_PASSWORD`, `KEY_ALIAS`, `KEY_PASSWORD`, `PLAY_STORE_CONFIG_JSON`
- Apple signing: `BUILD_CERTIFICATE_BASE64`, `P12_PASSWORD`, `BUILD_PROVISION_PROFILE_BASE64`, `KEYCHAIN_PASSWORD`, `APP_STORE_CONNECT_API_KEY_ID`, `APP_STORE_CONNECT_API_ISSUER_ID`, `APP_STORE_CONNECT_API_KEY_BASE64`

To re-use this workflow as your own deploy pipeline, restore the push trigger and supply the secrets above.

## Verkada integration setup

The Verkada integration is opt-in per organization. Once an org enables it:

1. Org admin enables Verkada integration in the org settings UI
2. The org provides Verkada bot credentials (org short name, org ID, bot user ID, bot v2 token), stored in `organizations/{orgId}/sensitiveConfigs/verkadaIntegrationSettings`. This document is read-only from clients and only accessible to Cloud Functions.
3. Site designations and user-group whitelists can be configured via the admin UI
4. Scheduled functions then sync devices and clean up Verkada state every 24 hours

See `functions/src/helper_functions/verkada_integration/` and `functions/src/scheduled_functions/verkada_integration/` for the implementation details.

## Security model

- **Authentication.** Firebase Auth, with email verification required by Firestore rules. Custom claims encode org membership and role.
- **Authorization.** Firestore rules block all client writes; reads are gated on authentication, email verification, recent token issuance, and an org-scoped custom claim. Server-side, callable functions re-check role and token freshness.
- **Token revocation.** When a user's role changes or they're removed from an org, their refresh tokens are revoked and the new token-issuance time is recorded in `usersMetadata/{userId}`. Firestore rules reject reads using stale tokens.
- **Sensitive config.** Per-org sensitive data (Verkada credentials, etc.) lives under `organizations/{orgId}/sensitiveConfigs/` which is explicitly excluded from the client-readable subcollection rule.
- **Rate limiting.** Per-user and per-global buckets on callable functions, configured in `functions/src/rate_limit_config.py`.
- **Public Firebase identifiers.** `firebase_options.dart`, `google-services.json`, and the web API key in those files are not secrets — they're public client identifiers protected by the auth and rules layers above. If you fork, you should still regenerate these for your own Firebase project.

## Testing

Flutter:
```bash
cd flutter
flutter test
```

Cloud Functions: there is currently no Python test suite in `functions/`. PRs adding tests are welcome.

End-to-end testing is best done against the Firebase emulators (see local setup, step 7).

## Contributing

Contributions are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for setup, coding conventions, and PR process.

For bug reports and feature requests, please use the GitHub issue templates.

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

## Project status

This repository was open-sourced from a working production codebase. It's provided as-is — issues and PRs will be reviewed on a best-effort basis.
