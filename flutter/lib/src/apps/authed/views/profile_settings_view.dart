import 'package:cloud_functions/cloud_functions.dart';
import 'package:flutter/material.dart';
import 'package:firebase_ui_auth/firebase_ui_auth.dart';
import 'package:provider/provider.dart';
import 'package:webbpulse_inventory_management/src/shared/providers/authentication_change_notifier.dart';
import 'package:webbpulse_inventory_management/src/shared/providers/firestore_read_service.dart';
import 'package:webbpulse_inventory_management/src/shared/widgets/styling/styling_widgets.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:webbpulse_inventory_management/src/shared/providers/settings_change_notifier.dart';
import 'package:webbpulse_inventory_management/src/shared/widgets/users/user_widgets.dart';

/// ProfileSettingsView allows users to manage their profile settings, such as changing
/// their profile picture, display name, and theme preferences.
class ProfileSettingsView extends StatelessWidget {
  const ProfileSettingsView({super.key});

  /// Route name for navigation to this view
  static const routeName = '/profile';

  @override
  Widget build(BuildContext context) {
    ThemeData theme = Theme.of(context);

    return Consumer4<FirebaseFunctions, AuthenticationChangeNotifier,
            FirestoreReadService, SettingsChangeNotifier>(
        builder: (context, firebaseFunctions, authenticationChangeNotifier,
            firestoreService, settingsChangeNotifier, child) {
      return Scaffold(
        appBar: AppBar(
          title: const Text('Profile'),
        ),
        drawer: const AuthedDrawer(),
        body: StreamBuilder<DocumentSnapshot>(
            stream: firestoreService
                .getGlobalUserDocument(authenticationChangeNotifier.user!.uid),
            builder: (context, snapshot) {
              if (snapshot.connectionState == ConnectionState.waiting) {
                return const Center(child: CircularProgressIndicator());
              } else if (snapshot.hasError) {
                return const Center(child: Text('Error loading user data'));
              }
              if (!snapshot.hasData || !snapshot.data!.exists) {
                return const Center(child: Text('User not found'));
              }

              final DocumentSnapshot userDocument = snapshot.data!;
              final bool hasPhoto = userDocument['userPhotoURL'] != '';

              return ProfileScreen(
                avatar: hasPhoto
                    ? ProfileAvatar(
                        photoUrl: userDocument['userPhotoURL'],
                      )
                    : CircleAvatar(
                        radius: 75,
                        child: Icon(
                          Icons.person,
                          size: 50,
                          color: Theme.of(context).colorScheme.secondary,
                        ),
                      ),
                actions: [
                  AccountDeletedAction((context, user) async {
                    await firebaseFunctions
                        .httpsCallable('delete_global_user_callable')
                        .call();
                  }),
                  DisplayNameChangedAction(
                    (context, user, userDisplayName) async {
                      await firebaseFunctions
                          .httpsCallable(
                              'update_global_user_display_name_callable')
                          .call({
                        'userDisplayName': userDisplayName,
                      });
                    },
                  ),
                  SignedOutAction((context) {
                    authenticationChangeNotifier.setUserWasLoggedIn(false);
                  }),
                ],
                providers: [
                  EmailAuthProvider(),
                ],
                children: [
                  const SizedBox(height: 16),

                  // Theme mode dropdown
                  DropdownButton<ThemeMode>(
                    value: settingsChangeNotifier.themeMode,
                    onChanged: settingsChangeNotifier.updateThemeMode,
                    items: const [
                      DropdownMenuItem(
                        value: ThemeMode.system,
                        child: Text('System Theme'),
                      ),
                      DropdownMenuItem(
                        value: ThemeMode.light,
                        child: Text('Light Theme'),
                      ),
                      DropdownMenuItem(
                        value: ThemeMode.dark,
                        child: Text('Dark Theme'),
                      ),
                    ],
                  ),
                  const SizedBox(height: 16),

                  ElevatedButton(
                    onPressed: () {
                      showDialog(
                          context: context,
                          builder: (BuildContext context) {
                            return const ChangeProfilePictureAlertDialog();
                          });
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
                    child: const Text('Change Profile Picture'),
                  ),
                ],
              );
            }),
      );
    });
  }
}

/// Dialog for changing the user's profile picture.
class ChangeProfilePictureAlertDialog extends StatefulWidget {
  const ChangeProfilePictureAlertDialog({super.key});

  @override
  ChangeProfilePictureAlertDialogState createState() =>
      ChangeProfilePictureAlertDialogState();
}

class ChangeProfilePictureAlertDialogState
    extends State<ChangeProfilePictureAlertDialog> {
  late TextEditingController _userPhotoURLController;
  var _isLoading = false;

  @override
  void initState() {
    super.initState();
    _userPhotoURLController = TextEditingController();
  }

  @override
  void dispose() {
    _userPhotoURLController.dispose();
    super.dispose();
  }

  /// Handles submission of the new profile picture URL
  void _onSubmit() async {
    final userPhotoURL = _userPhotoURLController.text;
    final firebaseFunctions =
        Provider.of<FirebaseFunctions>(context, listen: false);

    setState(() {
      _isLoading = true;
    });
    try {
      await firebaseFunctions
          .httpsCallable('update_global_user_photo_url_callable')
          .call({
        'userPhotoURL': userPhotoURL,
      });

      await AsyncContextHelpers.showSnackBarIfMounted(
          context, 'Profile picture changed successfully');
      AsyncContextHelpers.popContextIfMounted(context);
    } catch (e) {
      await AsyncContextHelpers.showSnackBarIfMounted(
          context, 'Failed to change profile picture: $e');
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return AlertDialog(
      title: const Text('Change Profile Picture'),
      content: SingleChildScrollView(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 500),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Text(
                  'Enter the URL of a picture to use as your profile picture.'),
              const SizedBox(height: 16.0),
              TextField(
                controller: _userPhotoURLController,
                decoration: const InputDecoration(
                  labelText: 'URL',
                ),
              ),
            ],
          ),
        ),
      ),
      actions: <Widget>[
        ElevatedButton.icon(
          style: ElevatedButton.styleFrom(
            backgroundColor: theme.colorScheme.surface.withOpacity(0.95),
            side: BorderSide(
              color: theme.colorScheme.primary.withOpacity(0.5),
              width: 1.5,
            ),
            padding: const EdgeInsets.all(16.0),
          ),
          onPressed: _isLoading ? null : _onSubmit,
          icon: _isLoading
              ? const CircularProgressIndicator()
              : const Icon(Icons.photo),
          label: const Text('Change Profile Picture'),
        ),
        const SizedBox(height: 16.0),
        ElevatedButton.icon(
          onPressed: () {
            Navigator.of(context).pop();
          },
          style: ElevatedButton.styleFrom(
            backgroundColor: theme.colorScheme.surface.withOpacity(0.95),
            side: BorderSide(
              color: theme.colorScheme.primary.withOpacity(0.5),
              width: 1.5,
            ),
            padding: const EdgeInsets.all(16.0),
          ),
          icon: const Icon(Icons.arrow_back),
          label: const Text('Go Back'),
        ),
      ],
    );
  }
}
