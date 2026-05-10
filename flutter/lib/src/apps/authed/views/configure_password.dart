import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:webbpulse_inventory_management/src/shared/providers/authentication_change_notifier.dart';
import 'package:webbpulse_inventory_management/src/shared/widgets/styling/styling_widgets.dart';
import 'package:webbpulse_inventory_management/src/apps/authed/views/org_selection_view.dart';
import 'dart:io';



class ConfigurePasswordView extends StatelessWidget {
  const ConfigurePasswordView({super.key});

  /// Route name for navigation to this view
  static const routeName = '/configure-password';

  @override
  Widget build(BuildContext context) {
    // Retrieve the current theme to style widgets accordingly

    return Consumer<AuthenticationChangeNotifier>(
        builder: (context, authenticationChangeNotifier, child) {
        return Scaffold(
          appBar: AppBar(
            title: const Text('Configure Password'),
            actions: const [
              
            ],
          ),
          body: LayoutBuilder(
            builder: (context, constraints) {
              // Calculate isIPad based on the width constraints
              final bool isIPad = !kIsWeb && Platform.isIOS && constraints.maxWidth >= 600;
              return SafeArea(
                child: SizedBox.expand(
                  child: isIPad
                      ? const Center(child: ConfigurePasswordForm())
                      : const ConfigurePasswordForm(),
                ),
              );
            },
          ),
        );
      },
    );
  }
}

/// CheckoutForm handles the form input and logic for device checkout and check-in
class ConfigurePasswordForm extends StatefulWidget {
  const ConfigurePasswordForm({super.key});

  @override
  ConfigurePasswordFormState createState() => ConfigurePasswordFormState();
}

class ConfigurePasswordFormState extends State<ConfigurePasswordForm> {
  var _isLoading = false; // Loading indicator for async operations
  late TextEditingController
      _newPasswordController; // Controller for the device serial input
  late TextEditingController
      _confirmPasswordController; // Controller for user search input
  bool _newPasswordIsObscured = true;
  bool _confirmPasswordIsObscured = true;
  
  @override
  void initState() {
    super.initState();
    _newPasswordController =
        TextEditingController(); // Initialize controller for device serial
    _confirmPasswordController =
        TextEditingController(); // Initialize controller for user search
  }
  @override
  void dispose() {
    _newPasswordController
        .dispose(); // Dispose controller when widget is destroyed
    _confirmPasswordController.dispose();
    super.dispose();
  }

  // Function to handle device checkout or check-in
  Future<void> _onSubmit(bool checkOut) async {
    setState(() => _isLoading = true); // Show loading indicator
    try {
      String newPassword = _newPasswordController.text;
      String confirmPassword = _confirmPasswordController.text;
      AuthenticationChangeNotifier authenticationChangeNotifier = Provider.of<AuthenticationChangeNotifier>(context, listen: false);
      if (newPassword != confirmPassword) {
        // Show error message if passwords do not match
        await AsyncContextHelpers.showSnackBarIfMounted(
            context, 'Passwords do not match'); // Show success message
        return;
      }
      if (newPassword.isEmpty || newPassword.length < 6) {
      await AsyncContextHelpers.showSnackBarIfMounted(
          context, 'Password must be at least 6 characters');
      return;
    }
      await authenticationChangeNotifier.setNewPassword(newPassword);
      Navigator.pushNamed(
            context,
            OrgSelectionView
                .routeName); // Navigate to the organization selection view
    } catch (e) {
      // Show error message if an error occurs
      await AsyncContextHelpers.showSnackBarIfMounted(
          context, 'An error occurred: $e'); // Show error message
    } finally {
      setState(() => _isLoading = false); // Hide loading indicator
    }
  }

  @override
  Widget build(BuildContext context) {
    ThemeData theme = Theme.of(context); // Get the current theme
    AuthenticationChangeNotifier authenticationChangeNotifier = Provider.of<AuthenticationChangeNotifier>(context, listen: false);
    return SingleChildScrollView(
      child: Center(
        child: LayoutBuilder(
          builder: (context, constraints) {
            // Set maximum width constraints based on screen size
            double maxWidth;
            if (constraints.maxWidth < 600) {
              maxWidth = constraints.maxWidth * 0.95;
            } else if (constraints.maxWidth < 1200) {
              maxWidth = constraints.maxWidth * 0.6;
            } else {
              maxWidth = constraints.maxWidth * 0.4;
            }

            return ConstrainedBox(
              constraints: BoxConstraints(
                maxWidth: maxWidth,
              ),
              child: Card(
                elevation: 4.0,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Column(
                    children: [
                      // Serial Number Input Field
                      TextField(
                        controller: _newPasswordController,
                        decoration: InputDecoration(
                          labelText: 'New Password',
                          suffixIcon: IconButton(
                            icon: Icon(
                              _newPasswordIsObscured ? Icons.visibility : Icons.visibility_off,
                            ),
                            onPressed: () {
                              setState(() {
                                _newPasswordIsObscured = !_newPasswordIsObscured;});
                            },
                          ),
                        ),
                        obscureText: _newPasswordIsObscured,
                        
                      ),
                      TextField(
                        controller: _confirmPasswordController,
                        decoration: InputDecoration(
                          labelText: 'Confirm Password',
                          suffixIcon: IconButton(
                            icon: Icon(
                              _confirmPasswordIsObscured ? Icons.visibility : Icons.visibility_off,
                            ),
                            onPressed: () {
                              setState(() {
                                _confirmPasswordIsObscured = !_confirmPasswordIsObscured;});
                            },
                          ),
                        ),
                        obscureText: _confirmPasswordIsObscured,
                      ),
                      const SizedBox(height: 16.0),
                      Wrap(
                        spacing: 8.0,
                        runSpacing: 8.0,
                        children: [
                          // Check-out Button
                          ElevatedButton.icon(
                            onPressed: _isLoading
                                ? null
                                : () {
                                      _onSubmit(true);
                                  },
                            style: ElevatedButton.styleFrom(
                              backgroundColor:
                                  theme.colorScheme.surface.withOpacity(0.95),
                              side: BorderSide(
                                color: theme.colorScheme.primary
                                    .withOpacity(0.5),
                                width: 1.5,
                              ),
                              padding: const EdgeInsets.all(16.0),
                            ),
                            icon: _isLoading
                                ? const CircularProgressIndicator()
                                : const Icon(Icons.check),
                            label: const Text('Set New Password'),
                          ),
                          ElevatedButton.icon(
                            onPressed: () {
                            authenticationChangeNotifier.signOutUser();           
                            },
                            style: ElevatedButton.styleFrom(
                              backgroundColor:
                                  theme.colorScheme.surface.withOpacity(0.95),
                              side: BorderSide(
                                color: theme.colorScheme.primary.withOpacity(0.5),
                                width: 1.5,
                              ),
                              padding: const EdgeInsets.all(16.0),
                            ),
                            label: const Text('Sign Out'),
                            icon: const Icon(Icons.logout),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              ),
            );
          },
        ),
      ),
    );
  }
}
