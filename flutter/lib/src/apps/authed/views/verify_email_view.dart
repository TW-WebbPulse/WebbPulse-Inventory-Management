import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:firebase_ui_auth/firebase_ui_auth.dart';
import 'package:webbpulse_inventory_management/src/shared/providers/authentication_change_notifier.dart';

/// VerifyEmailView provides the screen for email verification using Firebase UI.
class VerifyEmailView extends StatelessWidget {
  const VerifyEmailView({super.key});

  static const routeName = '/verify-email';

  @override
  Widget build(BuildContext context) {
    return Consumer<AuthenticationChangeNotifier>(
        builder: (context, authenticationChangeNotifier, child) {
      return Scaffold(
        appBar: AppBar(
          title: const Text('Verify Email'),
        ),
        body: EmailVerificationScreen(actions: [
          EmailVerifiedAction(() async {
            await authenticationChangeNotifier.user!.getIdToken(true);
            authenticationChangeNotifier.setUserEmailVerified(true);
          }),
          AuthCancelledAction((context) {
            Navigator.of(context).pop(); // Close dialog
          }),
        ]),
      );
    });
  }
}
