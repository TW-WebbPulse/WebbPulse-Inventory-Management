import 'package:flutter/material.dart';

import 'package:firebase_ui_auth/firebase_ui_auth.dart'; // Firebase UI for authentication
import 'package:provider/provider.dart';
import 'package:webbpulse_inventory_management/src/shared/authentication_provider_list.dart';

import 'package:webbpulse_inventory_management/src/shared/providers/authentication_change_notifier.dart';
import 'package:webbpulse_inventory_management/src/apps/authed/views/org_selected/org_device_list_view.dart';

/// SignInView is the screen where users can sign in using Firebase UI.
class SignInView extends StatelessWidget {
  const SignInView({super.key});

  static const routeName = '/signin';

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Sign In'),
      ),
      body: Center(
        child: Consumer<AuthenticationChangeNotifier>(
          builder: (context, authProvider, child) => SignInScreen(
            providers: authenticationProviderList,
            actions: [
              AuthStateChangeAction<SignedIn>((context, state) {
                // If the user signs in successfully, navigate to DeviceCheckoutView
                Navigator.pushNamed(context, OrgDeviceListView.routeName);
              }),
            ],
          ),
        ),
      ),
    );
  }
}
