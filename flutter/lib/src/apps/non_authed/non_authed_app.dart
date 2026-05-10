import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:webbpulse_inventory_management/src/shared/providers/authentication_change_notifier.dart';
import 'package:webbpulse_inventory_management/src/shared/providers/settings_change_notifier.dart';
import 'views/user_session_expired_view.dart';
import 'views/landing_view.dart';
import 'views/register_view.dart';
import 'views/signin_view.dart';
import 'views/forgot_password_view.dart';
import 'views/custom_signin.dart';

/// Main app widget for non-authenticated users
/// Handles routing for login, registration, password reset, and session expiration views
class NonAuthedApp extends StatelessWidget {
  const NonAuthedApp({super.key});

  @override
  Widget build(BuildContext context) {
    return Consumer2<AuthenticationChangeNotifier, SettingsChangeNotifier>(
      builder:
          (context, authenticationChangeNotifier, settingsProvider, child) =>
              MaterialApp(
        restorationScopeId: 'nonauthedapp',
        title: 'WebbPulse Inventory Management',
        theme: ThemeData(),
        darkTheme: ThemeData.dark(),
        themeMode: settingsProvider.themeMode,
        onGenerateRoute: (RouteSettings routeSettings) {
          if (authenticationChangeNotifier.userWasLoggedIn == true) {
            // Redirect to UserSessionExpiredView if the user was logged in but their session expired
            return MaterialPageRoute<void>(
              builder: (context) => const UserSessionExpiredView(),
            );
          }

          final uri = Uri.parse(routeSettings.name ?? '');

          // Handle different routes based on route name and query parameters
          switch (uri.path) {
            case RegisterView.routeName:
              return MaterialPageRoute<void>(
                builder: (context) => const RegisterView(),
              );
            case SignInView.routeName:
              return MaterialPageRoute<void>(
                builder: (context) => const SignInView(),
              );
            case ForgotPasswordView.routeName:
              return MaterialPageRoute<void>(
                builder: (context) => const ForgotPasswordView(),
              );
            case CustomSignInView.routeName:
              final token = uri.queryParameters['token'];
              return MaterialPageRoute<void>(
                builder: (context) => CustomSignInView(token: token),
              );
            default:
              return MaterialPageRoute<void>(
                builder: (context) => const LandingView(),
              );
          }
        },
      ),
    );
  }
}
