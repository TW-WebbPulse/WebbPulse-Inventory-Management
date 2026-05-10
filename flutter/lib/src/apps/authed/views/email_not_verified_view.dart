import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:webbpulse_inventory_management/src/apps/authed/views/verify_email_view.dart';
import 'package:webbpulse_inventory_management/src/shared/widgets/styling/styling_widgets.dart';
import 'package:webbpulse_inventory_management/src/shared/providers/authentication_change_notifier.dart';

/// EmailNotVerifiedView provides the screen for if a user is not currently email verified.
/// It offers options for users to either verify or log out.
class EmailNotVerifiedView extends StatelessWidget {
  const EmailNotVerifiedView({super.key});

  /// Route name for navigation to this view
  static const routeName = '/email-not-verified';

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Consumer<AuthenticationChangeNotifier>(
        builder: (context, authenticationChangeNotifier, child) {
      return Scaffold(
        body: Stack(
          children: [
            // Background image that fills the entire screen
            Positioned.fill(
              child: Image.asset(
                'assets/boxes.jpg',
                fit: BoxFit.cover,
              ),
            ),
            // Centered content with constrained size
            Center(
              child: LayoutBuilder(builder: (context, constraints) {
                return Center(
                  child: SmallLayoutBuilder(
                    childWidget: Card(
                      color: theme.colorScheme.onPrimary,
                      margin: const EdgeInsets.symmetric(vertical: 8.0),
                      child: Container(
                        padding: const EdgeInsets.symmetric(
                            horizontal: 16.0, vertical: 8.0),
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            // Title card displaying the app name
                            Card(
                              margin: const EdgeInsets.symmetric(vertical: 8.0),
                              child: Container(
                                padding: const EdgeInsets.symmetric(
                                    horizontal: 16.0, vertical: 8.0),
                                child: Text(
                                  'Please Verify Your Email Address',
                                  style: theme.textTheme.titleLarge,
                                ),
                              ),
                            ),
                            // Verify email option
                            CustomCard(
                              theme: theme,
                              customCardLeading: Icon(Icons.mail,
                                  color: theme.colorScheme.secondary),
                              customCardTitle: const Text('Verify Email'),
                              customCardTrailing: null,
                              onTapAction: () {
                                Navigator.pushNamed(
                                    context, VerifyEmailView.routeName);
                              },
                            ),
                            // Sign out option
                            CustomCard(
                              theme: theme,
                              customCardLeading: Icon(Icons.logout,
                                  color: theme.colorScheme.secondary),
                              customCardTitle: const Text('Sign Out'),
                              customCardTrailing: null,
                              onTapAction: () {
                                authenticationChangeNotifier.signOutUser();
                              },
                            ),
                          ],
                        ),
                      ),
                    ),
                  ),
                );
              }),
            ),
          ],
        ),
      );
    });
  }
}
