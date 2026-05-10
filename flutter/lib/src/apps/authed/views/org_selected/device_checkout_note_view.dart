import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:webbpulse_inventory_management/src/apps/authed/views/org_selected/org_device_list_view.dart';

import 'package:webbpulse_inventory_management/src/shared/providers/device_checkout_service.dart';
import 'package:webbpulse_inventory_management/src/shared/providers/org_selector_change_notifier.dart';
import 'package:webbpulse_inventory_management/src/shared/providers/authentication_change_notifier.dart';
import 'package:webbpulse_inventory_management/src/shared/providers/device_selector_change_notifier.dart';
import 'package:webbpulse_inventory_management/src/shared/widgets/devices/checkout_user_list_dialog.dart';
import 'package:webbpulse_inventory_management/src/shared/widgets/users/user_widgets.dart';

class DeviceCheckoutNoteView extends StatefulWidget {
  const DeviceCheckoutNoteView({
    super.key,
  });

  static const routeName = '/checkout-note';

  @override
  _CheckoutNoteDialogState createState() => _CheckoutNoteDialogState();
}

class _CheckoutNoteDialogState extends State<DeviceCheckoutNoteView> {
  late TextEditingController _noteController;
  var _isLoading = false; // Flag to indicate if an operation is in progress

  @override
  void initState() {
    super.initState();
    _noteController = TextEditingController();
  }

  @override
  void dispose() {
    _noteController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    ThemeData theme = Theme.of(context);
    return AuthClaimChecker(builder: (context, userClaims) {
      final orgId =
          Provider.of<OrgSelectorChangeNotifier>(context, listen: false).orgId;
      final bool isAdminOrDeskstation =
          (userClaims['org_admin_$orgId'] == true) ||
              (userClaims['org_deskstation_$orgId'] == true);

      return Scaffold(
        appBar: AppBar(
          title: const Text('Please Leave a Note'),
        ),
        body: SingleChildScrollView(
          child: Center(
            child: LayoutBuilder(builder: (context, constraints) {
              double maxWidth;
              if (constraints.maxWidth < 600) {
                maxWidth = constraints.maxWidth * 0.95;
              } else if (constraints.maxWidth < 1200) {
                maxWidth = constraints.maxWidth * 0.6;
              } else {
                maxWidth = constraints.maxWidth * 0.4;
              }

              return ConstrainedBox(
                constraints: BoxConstraints(maxWidth: maxWidth),
                child: Card(
                  elevation: 4.0,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Padding(
                    padding: const EdgeInsets.all(16.0),
                    child: Column(
                      children: [
                        Column(
                          mainAxisSize: MainAxisSize.min,
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const Text(
                              'Please describe why you are checking out this device:',
                            ),
                            TextField(
                              controller: _noteController,
                              decoration: const InputDecoration(
                                labelText: 'Leave a Note',
                                prefixIcon: Icon(Icons.note),
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 16.0),
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                          children: [
                            ElevatedButton.icon(
                              onPressed: () {
                                Navigator.of(context)
                                    .pop(); // Just close the dialog
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
                              icon: const Icon(Icons.arrow_back),
                              label: const Text('Go Back'),
                            ),
                            ElevatedButton.icon(
                              onPressed: () {
                                // Get the note from the text field
                                final note = _noteController.text;
                                if (isAdminOrDeskstation) {
                                  // For admin/deskstation users, show the user list dialog
                                  _showUserListDialog(orgId, note);
                                } else {
                                  // Otherwise, directly change the device status
                                  _checkoutDevice(true, note);
                                  Navigator.pushNamed(
                                    context,
                                    OrgDeviceListView.routeName,
                                  );
                                }
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
                                  : const Icon(Icons.logout),
                              label: const Text('Check Out Device'),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                ),
              );
            }),
          ),
        ),
      );
    });
  }

  Future<void> _showUserListDialog(
      String orgId, String deviceCheckedOutNote) async {
    return showDialog<void>(
      context: context,
      builder: (BuildContext context) {
        return CheckoutUserListDialog(
          orgId: orgId,
          onUserSelected: (selectedUserId) {
            _changeDeviceStatusAdminAndDeskstation(
                true, selectedUserId, deviceCheckedOutNote);
          },
        );
      },
    );
  }

  /// Handles the submission of the check-in or check-out operation
  Future<void> _checkoutDevice(
      bool isDeviceBeingCheckedOut, String deviceCheckedOutNote) async {
    setState(() => _isLoading = true); // Set loading state
    final deviceCheckoutService =
        Provider.of<DeviceCheckoutService>(context, listen: false);
    final orgId =
        Provider.of<OrgSelectorChangeNotifier>(context, listen: false).orgId;
    final deviceCheckedOutBy =
        Provider.of<AuthenticationChangeNotifier>(context, listen: false)
            .user!
            .uid;
    final deviceSerialNumber =
        Provider.of<DeviceSelectorChangeNotifier>(context, listen: false)
            .deviceSerialNumber;
    try {
      await deviceCheckoutService.handleDeviceCheckout(
        context,
        deviceSerialNumber,
        orgId,
        deviceCheckedOutBy,
        isDeviceBeingCheckedOut, // Pass the boolean to check-out or check-in the device
        deviceCheckedOutNote, // Pass the note for the check-out operation
      );
    } catch (e) {
      // Handle errors if needed
    } finally {
      setState(() => _isLoading = false); // Reset loading state
    }
  }

  /// Handles the submission of check-in/check-out by admins or desk stations
  Future<void> _changeDeviceStatusAdminAndDeskstation(bool isDeviceCheckedOut,
      String deviceCheckedOutBy, String deviceCheckedOutNote) async {
    setState(() => _isLoading = true); // Set loading state
    final orgId =
        Provider.of<OrgSelectorChangeNotifier>(context, listen: false).orgId;
    final deviceCheckoutService =
        Provider.of<DeviceCheckoutService>(context, listen: false);
    final deviceSerialNumber =
        Provider.of<DeviceSelectorChangeNotifier>(context, listen: false)
            .deviceSerialNumber;
    try {
      await deviceCheckoutService.handleDeviceCheckout(
        context,
        deviceSerialNumber,
        orgId,
        deviceCheckedOutBy,
        isDeviceCheckedOut, // Pass the boolean for check-in or check-out
        deviceCheckedOutNote, // Pass the note for the check-out operation
      );
    } catch (e) {
      // Handle errors if needed
    } finally {
      setState(() => _isLoading = false); // Reset loading state
    }
  }
}
