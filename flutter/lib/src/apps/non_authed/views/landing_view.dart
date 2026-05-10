import 'package:flutter/material.dart';
import 'register_view.dart';
import 'signin_view.dart';
import 'package:webbpulse_inventory_management/src/shared/widgets/styling/styling_widgets.dart';

/// LandingView provides the initial landing screen for the app.
/// It offers options for users to either register or sign in.
class LandingView extends StatelessWidget {
  const LandingView({super.key});

  /// Route name for navigation to this view
  static const routeName = '/';

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

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
              return ConstrainedBox(
                constraints: BoxConstraints(maxHeight: constraints.maxHeight),
                child: Center(
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
                                  'WebbPulse Inventory Management',
                                  style: theme.textTheme.titleLarge,
                                ),
                              ),
                            ),
                            // Register option
                            CustomCard(
                              theme: theme,
                              customCardLeading: Icon(Icons.person_add,
                                  color: theme.colorScheme.secondary),
                              customCardTitle: const Text('Register'),
                              customCardTrailing: null,
                              onTapAction: () {
                                Navigator.pushNamed(
                                    context, RegisterView.routeName);
                              },
                            ),
                            // Sign In option
                            CustomCard(
                              theme: theme,
                              customCardLeading: Icon(Icons.login,
                                  color: theme.colorScheme.secondary),
                              customCardTitle: const Text('Sign In'),
                              customCardTrailing: null,
                              onTapAction: () {
                                Navigator.pushNamed(
                                    context, SignInView.routeName);
                              },
                            ),
                          ],
                        ),
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
  }
}
