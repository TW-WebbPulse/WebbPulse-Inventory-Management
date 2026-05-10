import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:webbpulse_inventory_management/src/shared/providers/authentication_change_notifier.dart';
import 'landing_view.dart';

class CustomSignInView extends StatelessWidget {
  final String? token;

  const CustomSignInView({super.key, this.token});

  static const routeName = '/custom-signin';

  @override
  Widget build(BuildContext context) {
    final authProvider = Provider.of<AuthenticationChangeNotifier>(context);

    // Trigger sign-in only if the token exists and there's no error
    if (token != null && authProvider.authError == null) {
      WidgetsBinding.instance.addPostFrameCallback((_) {
        authProvider.signInWithCustomToken(token!);
      });
    }

    return Scaffold(
      appBar: AppBar(
        title:const Text("Custom Sign-In"),
        actions: [
          ElevatedButton.icon(
            label: const Text("Sign In"),
            icon: const Icon(Icons.login),
            onPressed: () {
              Navigator.pushNamed(context, LandingView.routeName);
            },
          ),
        ],
        ),
      body: Center(
        child: authProvider.authError != null
            ? Text(authProvider.authError!) // Display error message if token is invalid
            : token != null
                ? const CircularProgressIndicator() // Show loading if token is valid and signing in
                : const Text("No token found in the URL"), // No token present in the URL
      ),
    );
  }
}

