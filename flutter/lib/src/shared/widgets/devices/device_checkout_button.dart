import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../providers/device_checkout_service.dart';
import '../../providers/org_selector_change_notifier.dart';
import '../../providers/firestore_read_service.dart';
import '../../providers/authentication_change_notifier.dart';
import '../../providers/device_selector_change_notifier.dart';
import 'package:webbpulse_inventory_management/src/apps/authed/views/org_selected/device_checkout_note_view.dart';

class DeviceCheckoutButton extends StatefulWidget {
  final String deviceSerialNumber;

  const DeviceCheckoutButton({
    super.key,
    required this.deviceSerialNumber,
  });

  @override
  DeviceCheckoutButtonState createState() => DeviceCheckoutButtonState();
}

class DeviceCheckoutButtonState extends State<DeviceCheckoutButton> {
  var _isLoading = false;

  @override
  void initState() {
    super.initState();
  }

  @override
  void dispose() {
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    ThemeData theme = Theme.of(context);
    return Consumer3<OrgSelectorChangeNotifier, FirestoreReadService,
            DeviceSelectorChangeNotifier>(
        builder: (context, orgSelectorChangeNotifier, firestoreReadService,
            deviceSelectorChangeNotifier, child) {
      return StreamBuilder<bool>(
          stream: firestoreReadService.isDeviceCheckedOutInFirestoreStream(
              widget.deviceSerialNumber, orgSelectorChangeNotifier.orgId),
          builder: (context, snapshot) {
            if (snapshot.connectionState == ConnectionState.waiting) {
              return const CircularProgressIndicator();
            }
            final bool isDeviceCurrentlyCheckedOut = snapshot.data ?? false;
            return ElevatedButton.icon(
                onPressed: widget.deviceSerialNumber == ''
                    ? null
                    : _isLoading
                        ? null
                        : () {
                            if (isDeviceCurrentlyCheckedOut == true) {
                              _checkinDevice();
                            } else {
                              deviceSelectorChangeNotifier
                                  .selectDevice(widget.deviceSerialNumber);
                              Navigator.pushNamed(
                                context,
                                DeviceCheckoutNoteView.routeName,
                              );
                            }
                          },
                icon: Icon(
                    isDeviceCurrentlyCheckedOut ? Icons.login : Icons.logout),
                label: Text(widget.deviceSerialNumber == ''
                    ? 'Please enter a serial number'
                    : isDeviceCurrentlyCheckedOut
                        ? 'Check-in Device'
                        : 'Check-out Device'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: theme.colorScheme.surface.withOpacity(0.95),
                  side: BorderSide(
                    color: theme.colorScheme.primary.withOpacity(0.5),
                    width: 1.5,
                  ),
                  padding: const EdgeInsets.all(16.0),
                ));
          });
    });
  }

  /// Handles the submission of the check-in or check-out operation
  Future<void> _checkinDevice() async {
    setState(() => _isLoading = true);
    final deviceCheckoutService =
        Provider.of<DeviceCheckoutService>(context, listen: false);
    final orgId =
        Provider.of<OrgSelectorChangeNotifier>(context, listen: false).orgId;
    final deviceCheckedOutBy =
        Provider.of<AuthenticationChangeNotifier>(context, listen: false)
            .user!
            .uid;
    try {
      await deviceCheckoutService.handleDeviceCheckout(
        context,
        widget.deviceSerialNumber,
        orgId,
        deviceCheckedOutBy,
        false,
        '',
      );
    } finally {
      setState(() => _isLoading = false);
    }
  }
}
