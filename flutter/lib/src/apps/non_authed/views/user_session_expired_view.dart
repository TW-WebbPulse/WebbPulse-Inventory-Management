import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:webbpulse_inventory_management/src/apps/non_authed/views/landing_view.dart';
import 'package:webbpulse_inventory_management/src/shared/providers/authentication_change_notifier.dart';

/// View displayed when the user's session has expired.
/// It informs the user and provides an option to sign in again.
class UserSessionExpiredView extends StatelessWidget {
  const UserSessionExpiredView({super.key});

  /// Route name to navigate to this view
  static const routeName = '/user_session_expired';

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: Consumer<AuthenticationChangeNotifier>(
          builder: (context, authenticationChangeNotifier, child) => Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: <Widget>[
                const Text('User Session Expired'),
                ElevatedButton(
                  onPressed: () {
                    // Reset the session state and navigate back to the sign-in screen
                    authenticationChangeNotifier.setUserWasLoggedIn(false);
                    Navigator.pop(context);
                    Navigator.pushNamed(context, LandingView.routeName);
                  },
                  child: const Text('Please Sign In Again'),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
