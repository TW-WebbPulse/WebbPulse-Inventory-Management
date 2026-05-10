import 'package:flutter/material.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:provider/provider.dart';
import 'src/shared/providers/authentication_change_notifier.dart';
import 'src/shared/providers/settings_change_notifier.dart';
import 'src/apps/authed/authed_app.dart';
import 'src/apps/non_authed/non_authed_app.dart';
import 'src/shared/non_provider_services/settings_service.dart';
import 'firebase_options.dart';
import 'package:flutter/foundation.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:cloud_functions/cloud_functions.dart';

/// Main entry point of the Flutter application
void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  final settingsChangeNotifier = SettingsChangeNotifier(SettingsService());
  await settingsChangeNotifier.loadSettings();
  await Firebase.initializeApp(options: DefaultFirebaseOptions.currentPlatform);

  // --- Start Emulator Configuration ---
  // Use emulators only in debug mode
  if (kDebugMode) {
    try {
      const String host = 'localhost'; // Or use '10.0.2.2' for Android Emulator

      FirebaseFirestore.instance.useFirestoreEmulator(host, 8080);

      await FirebaseAuth.instance.useAuthEmulator(host, 9099);

      FirebaseFunctions.instance.useFunctionsEmulator(host, 5001);

      print(
          'Using Firebase Emulators: Auth (9099), Firestore (8080), Functions (5001)');
    } catch (e) {
      // Handle exceptions, e.g., emulator not running
      print('Error configuring Firebase Emulators: $e');
    }
  }
  // --- End Emulator Configuration ---

  runApp(MultiProvider(
      providers: [
        ChangeNotifierProvider<AuthenticationChangeNotifier>(
          create: (_) => AuthenticationChangeNotifier(),
        ),
        ChangeNotifierProvider<SettingsChangeNotifier>.value(
          value: settingsChangeNotifier,
        ),
      ],
      child: Consumer<AuthenticationChangeNotifier>(
        builder: (context, authProvider, child) {
          if (authProvider.userLoggedIn) {
            return AuthedApp();
          } else {
            return const NonAuthedApp();
          }
        },
      )));
}
