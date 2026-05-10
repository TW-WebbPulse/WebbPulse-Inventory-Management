import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:cloud_functions/cloud_functions.dart';
import 'package:webbpulse_inventory_management/src/shared/providers/authentication_change_notifier.dart';
import 'package:webbpulse_inventory_management/src/shared/providers/firestore_read_service.dart';
import 'package:webbpulse_inventory_management/src/shared/providers/org_member_selector_change_notifier.dart';
import 'package:webbpulse_inventory_management/src/shared/providers/org_selector_change_notifier.dart';
import 'package:webbpulse_inventory_management/src/shared/widgets/styling/styling_widgets.dart';
import 'package:webbpulse_inventory_management/src/shared/widgets/devices/device_list.dart';
import 'package:webbpulse_inventory_management/src/shared/widgets/users/user_widgets.dart';

/// OrgMemberView is the screen where an admin can manage a selected organization member.
/// It displays the member's profile, roles, and their checked-out devices.
class OrgMemberView extends StatelessWidget {
  OrgMemberView({super.key});
  static const routeName = '/manage-user';
  final ValueNotifier<String> searchQuery = ValueNotifier<String>('');

  @override
  Widget build(BuildContext context) {
    return Consumer5<
            OrgSelectorChangeNotifier,
            OrgMemberSelectorChangeNotifier,
            FirestoreReadService,
            FirebaseFunctions,
            AuthenticationChangeNotifier>(
        builder: (context,
            orgSelectorChangeNotifier,
            orgMemberSelectorProvider,
            firestoreService,
            firebaseFunctions,
            authenticationChangeNotifier,
            child) {
      // Checking the authentication state and user claims for authorization
      return AuthClaimChecker(
        builder: (context, userClaims) {
          return Scaffold(
            appBar: AppBar(
              title: const Text('Manage User'), // App bar title
              leading: IconButton(
                icon: const Icon(Icons.arrow_back), // Back button
                onPressed: () {
                  // Clear the selected organization member when the user navigates back
                  orgMemberSelectorProvider.clearSelectedOrgMember();
                  Navigator.pop(context); // Navigate back
                },
              ),
            ),
            body: orgSelectorChangeNotifier.orgId.isNotEmpty &&
                    orgMemberSelectorProvider.orgMemberId.isNotEmpty
                // If organization and member are selected, load member's data
                ? StreamBuilder<DocumentSnapshot?>(
                    stream: firestoreService.getOrgMemberDocument(
                        orgSelectorChangeNotifier.orgId,
                        orgMemberSelectorProvider.orgMemberId),
                    builder: (context, snapshot) {
                      if (snapshot.connectionState == ConnectionState.waiting) {
                        return const Center(
                            child:
                                CircularProgressIndicator()); // Show loading indicator
                      } else if (snapshot.hasError) {
                        return const Center(
                            child: Text(
                                'Error loading user data')); // Show error message
                      }
                      if (!snapshot.hasData || !snapshot.data!.exists) {
                        return const Center(
                            child: Text(
                                'User not found')); // Show message if user not found
                      }
                      final DocumentSnapshot orgMemberData = snapshot.data!;
                      if (orgMemberData['orgMemberDeleted'] == true) {
                        return const Center(
                            child: Text(
                                'User not found')); // Handle deleted user case
                      }

                      // Layout builder to adjust the view based on screen size
                      return LayoutBuilder(builder: (context, constraints) {
                        double containerWidth;

                        // Adjust the width of the side column based on screen size
                        if (constraints.maxWidth < 600) {
                          containerWidth =
                              constraints.maxWidth * 0.35; // Mobile width
                        } else if (constraints.maxWidth < 1200) {
                          containerWidth =
                              constraints.maxWidth * 0.25; // Tablet width
                        } else {
                          containerWidth = constraints.maxWidth *
                              0.15; // Larger screen width
                        }

                        return Row(
                          children: [
                            // Right-side column for displaying user details
                            Container(
                              width: containerWidth,
                              color: Theme.of(context).colorScheme.secondary,
                              padding: const EdgeInsets.all(8.0),
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.center,
                                children: [
                                  // Display user's name
                                  Text(
                                    '${orgMemberData['orgMemberDisplayName']}',
                                    style: Theme.of(context)
                                        .textTheme
                                        .titleLarge
                                        ?.copyWith(
                                            color: Theme.of(context)
                                                .colorScheme
                                                .onSecondary,
                                            fontWeight: FontWeight.bold),
                                  ),
                                  const SizedBox(height: 8),
                                  // Display user's email
                                  Text(
                                    '${orgMemberData['orgMemberEmail']}',
                                    style: Theme.of(context)
                                        .textTheme
                                        .titleMedium
                                        ?.copyWith(
                                            color: Theme.of(context)
                                                .colorScheme
                                                .onSecondary,
                                            fontWeight: FontWeight.bold),
                                  ),
                                  const SizedBox(height: 16),
                                  // Display user's profile picture or default avatar
                                  if (orgMemberData['orgMemberPhotoURL'] !=
                                          '' &&
                                      orgMemberData['orgMemberPhotoURL'] !=
                                          null)
                                    ProfileAvatar(
                                        photoUrl:
                                            orgMemberData['orgMemberPhotoURL'])
                                  else
                                    CircleAvatar(
                                      radius: 75,
                                      backgroundColor: Theme.of(context)
                                          .colorScheme
                                          .onSecondary,
                                      child: Icon(
                                        Icons.person,
                                        size: 50,
                                        color: Theme.of(context)
                                            .colorScheme
                                            .secondary,
                                      ),
                                    ),
                                  const SizedBox(height: 16),
                                  // If the user is an admin, display role management and delete options
                                  if (userClaims[
                                          'org_admin_${orgSelectorChangeNotifier.orgId}'] ==
                                      true)
                                    Column(
                                      children: [
                                        UserRoleDropdownButton(
                                            orgMemberData: orgMemberData),
                                        const SizedBox(height: 8),
                                        DeleteUserButton(
                                            orgMemberData: orgMemberData),
                                      ],
                                    )
                                  else
                                    // Display current user's role if not an admin
                                    UserRoleCard(orgMemberData: orgMemberData),
                                ],
                              ),
                            ),
                            // Expanded section to show user's checked-out devices
                            Expanded(
                              child: Padding(
                                padding: const EdgeInsets.all(16.0),
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    // Section title for checked-out devices
                                    Text(
                                      'Checked Out Devices',
                                      style: Theme.of(context)
                                          .textTheme
                                          .titleLarge
                                          ?.copyWith(
                                              fontWeight: FontWeight.bold),
                                    ),

                                    Expanded(
                                      // Display a list of checked-out devices
                                      child: DeviceList(
                                        orgMemberId:
                                            orgMemberData['orgMemberId'],
                                        searchQuery: searchQuery,
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                            ),
                          ],
                        );
                      });
                    },
                  )
                : const Center(
                    child:
                        CircularProgressIndicator()), // Show loading screen if no org or member is selected
          );
        },
      );
    });
  }
}

/// DeleteUserButton provides functionality to delete a user from an organization.
class DeleteUserButton extends StatefulWidget {
  const DeleteUserButton({super.key, required this.orgMemberData});

  final DocumentSnapshot<Object?> orgMemberData;

  @override
  State<DeleteUserButton> createState() => _DeleteUserButtonState();
}

class _DeleteUserButtonState extends State<DeleteUserButton> {
  var _isLoading = false;

  @override
  void initState() {
    super.initState();
  }

  @override
  void dispose() {
    super.dispose();
  }

  /// Handles the process of deleting a user.
  void _onPressed() async {
    final orgSelectorProvider =
        Provider.of<OrgSelectorChangeNotifier>(context, listen: false);
    final firebaseFunctions =
        Provider.of<FirebaseFunctions>(context, listen: false);
    final authenticationChangeNotifier =
        Provider.of<AuthenticationChangeNotifier>(context, listen: false);

    setState(() {
      _isLoading = true;
    });

    try {
      String orgMemberId = widget.orgMemberData['orgMemberId'];
      await firebaseFunctions.httpsCallable('delete_org_member_callable').call({
        'orgId': orgSelectorProvider.orgId,
        'orgMemberId': widget.orgMemberData.id,
      });
      // Sign out the user if they delete themselves
      if (orgMemberId == authenticationChangeNotifier.user?.uid) {
        authenticationChangeNotifier.signOutUser();
      }
      await AsyncContextHelpers.showSnackBarIfMounted(
          context, 'User deleted successfully');
    } catch (e) {
      await AsyncContextHelpers.showSnackBarIfMounted(
          context, 'Failed to delete user: $e');
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Consumer3<FirebaseFunctions, OrgSelectorChangeNotifier,
            AuthenticationChangeNotifier>(
        builder: (context, firebaseFunctions, orgSelectorChangeNotifier,
            authenticationChangeNotifier, child) {
      return ElevatedButton.icon(
        onPressed:
            _isLoading ? null : _onPressed, // Disable button while loading
        icon: _isLoading
            ? const CircularProgressIndicator()
            : const Icon(Icons.delete),
        label: Wrap(
          children: [
            Text(
              'Delete User',
              style: Theme.of(context)
                  .textTheme
                  .labelSmall
                  ?.copyWith(fontWeight: FontWeight.bold),
            ),
          ],
        ),
        style: ElevatedButton.styleFrom(
          disabledBackgroundColor: Colors.red,
          backgroundColor: Colors.red,
          padding: const EdgeInsets.all(16.0),
        ),
      );
    });
  }
}

/// UserRoleCard displays the current role of a user (e.g., Org Admin, Org Member, Desk Station).
class UserRoleCard extends StatelessWidget {
  final DocumentSnapshot orgMemberData;

  const UserRoleCard({required this.orgMemberData, super.key});

  @override
  Widget build(BuildContext context) {
    // Mapping for role display names
    final roleDisplayNames = {
      'admin': 'Org Admin',
      'member': 'Org Member',
      'deskstation': 'Desk Station',
    };

    // Fetch the role name or fallback to 'Unknown Role'
    final role = orgMemberData['orgMemberRole'];
    final displayName = roleDisplayNames[role] ?? 'Unknown Role';

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            Text(
              displayName,
              style: Theme.of(context)
                  .textTheme
                  .labelSmall
                  ?.copyWith(fontWeight: FontWeight.bold),
            ),
          ],
        ),
      ),
    );
  }
}

/// UserRoleDropdownButton allows admins to change the role of an organization member.
class UserRoleDropdownButton extends StatefulWidget {
  final DocumentSnapshot orgMemberData;

  const UserRoleDropdownButton({required this.orgMemberData, super.key});

  @override
  UserRoleDropdownButtonState createState() => UserRoleDropdownButtonState();
}

class UserRoleDropdownButtonState extends State<UserRoleDropdownButton> {
  String? selectedValue;
  bool _isLoading = false;

  final List<Map<String, String>> items = [
    {'value': 'admin', 'display': 'Org Admin'},
    {'value': 'member', 'display': 'Org Member'},
    {'value': 'deskstation', 'display': 'Desk Station'},
  ];

  @override
  void initState() {
    super.initState();
    selectedValue = widget
        .orgMemberData['orgMemberRole']; // Initialize with current user role
  }

  /// Handles updating the user's role.
  void _onChanged() async {
    final orgSelectorProvider =
        Provider.of<OrgSelectorChangeNotifier>(context, listen: false);
    final firebaseFunctions =
        Provider.of<FirebaseFunctions>(context, listen: false);

    setState(() {
      _isLoading = true;
    });

    try {
      await firebaseFunctions.httpsCallable('update_user_role_callable').call({
        "orgMemberRole": selectedValue,
        "orgMemberId": widget.orgMemberData.id,
        "orgId": orgSelectorProvider.orgId,
      });

      await AsyncContextHelpers.showSnackBarIfMounted(
          context, 'User role updated successfully');
    } catch (e) {
      await AsyncContextHelpers.showSnackBarIfMounted(
          context, 'Failed to update user role: $e');
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(8.0),
        child: DropdownButton<String>(
          value: selectedValue,
          hint: const Text('Role'),
          elevation: 16,
          style: Theme.of(context)
              .textTheme
              .labelSmall
              ?.copyWith(fontWeight: FontWeight.bold),
          icon: _isLoading
              ? const CircularProgressIndicator()
              : const Icon(Icons.arrow_drop_down),
          onChanged: (String? newValue) {
            setState(() {
              selectedValue = newValue; // Update selected value when changed
            });
            _isLoading
                ? null
                : _onChanged(); // Only call _onChanged if not loading
          },
          items:
              items.map<DropdownMenuItem<String>>((Map<String, String> item) {
            return DropdownMenuItem<String>(
              value: item['value'],
              child: Text(item['display']!),
            );
          }).toList(),
        ),
      ),
    );
  }
}
