import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:provider/provider.dart';
import 'package:cloud_functions/cloud_functions.dart';
import 'package:intl/intl.dart';

import 'package:cloud_firestore/cloud_firestore.dart';

import '../../providers/device_checkout_service.dart';
import '../../providers/org_selector_change_notifier.dart';
import '../../providers/firestore_read_service.dart';
import 'package:webbpulse_inventory_management/src/shared/widgets/devices/device_checkout_button.dart';
import 'package:webbpulse_inventory_management/src/shared/widgets/devices/device_delete_button.dart';
import 'package:webbpulse_inventory_management/src/shared/widgets/org/org_widgets.dart';

import 'package:webbpulse_inventory_management/src/shared/widgets/styling/styling_widgets.dart';
import 'package:webbpulse_inventory_management/src/shared/widgets/users/user_widgets.dart';

/// A widget that displays a device serial number with a copy button
class CopyableSerialNumber extends StatelessWidget {
  const CopyableSerialNumber({
    super.key,
    required this.serialNumber,
    this.style,
  });

  final String serialNumber;
  final TextStyle? style;

  Future<void> _copyToClipboard(BuildContext context) async {
    await Clipboard.setData(ClipboardData(text: serialNumber));
    if (context.mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Serial number "$serialNumber" copied to clipboard'),
          duration: const Duration(seconds: 2),
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Text(serialNumber, style: style),
        const SizedBox(width: 4),
        IconButton(
          icon: const Icon(Icons.copy, size: 16),
          onPressed: () => _copyToClipboard(context),
          tooltip: 'Copy serial number',
          padding: EdgeInsets.zero,
          constraints: const BoxConstraints(),
          style: IconButton.styleFrom(
            foregroundColor: Theme.of(context).colorScheme.secondary,
          ),
        ),
      ],
    );
  }
}

class DeviceCardDesktop extends StatelessWidget {
  const DeviceCardDesktop({
    super.key,
    required this.deviceData,
  });

  final Map<String, dynamic> deviceData;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final String deviceId = deviceData['deviceId'];
    final String deviceSerialNumber = deviceData['deviceSerialNumber'];
    final bool deviceDeleted = deviceData['deviceDeleted'] ?? false;
    final String orgMemberId = deviceData['deviceCheckedOutBy'];
    final bool isDeviceCheckedOut = deviceData['isDeviceCheckedOut'];
    final String deviceCheckedOutNote =
        deviceData['deviceCheckedOutNote'] ?? '';
    final String verkadaDeviceType =
        deviceData['deviceVerkadaDeviceType'] ?? '';

    // Timestamp related
    final Timestamp deviceCheckedOutAtTimestamp =
        deviceData['deviceCheckedOutAt'] ?? Timestamp.now();
    final DateTime deviceCheckedOutAt = deviceCheckedOutAtTimestamp.toDate();
    final String deviceCheckedOutAtFormatted =
        DateFormat('yyyy-MM-dd kk:mm a').format(deviceCheckedOutAt);

    // Skip rendering if the device has been marked as deleted
    if (deviceDeleted) {
      return const SizedBox.shrink();
    } else {
      return Consumer4<FirestoreReadService, DeviceCheckoutService,
              OrgSelectorChangeNotifier, FirebaseFunctions>(
          builder: (context, firestoreService, deviceCheckoutService,
              orgSelectorChangeNotifier, firebaseFunctions, child) {
        return OrgDocumentStreamBuilder(builder: (context, orgDocument) {
          final orgData = orgDocument.data() as Map<String, dynamic>;
          return StreamBuilder<DocumentSnapshot?>(
              stream: firestoreService.getOrgMemberDocument(
                  orgSelectorChangeNotifier.orgId, orgMemberId),
              builder: (context, snapshot) {
                if (snapshot.connectionState == ConnectionState.waiting) {
                  return const Center(child: CircularProgressIndicator());
                } else if (snapshot.hasError) {
                  return const Text('Error loading org member data');
                } else {
                  // Fetch the organization member data
                  Map<String, dynamic> orgMemberData =
                      snapshot.data?.data() as Map<String, dynamic>? ?? {};
                  return AuthClaimChecker(
                    builder: (context, userClaims) {
                      return CustomCard(
                        theme: theme,
                        customCardLeading: Icon(Icons.devices,
                            color: theme.colorScheme.secondary),
                        customCardTitle: Row(
                          children: [
                            Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Wrap(
                                    children: [
                                      CopyableSerialNumber(
                                        serialNumber: deviceSerialNumber,
                                        style: const TextStyle(
                                            fontWeight: FontWeight.bold),
                                      ),
                                    ],
                                  ),
                                  if (orgData['orgVerkadaIntegrationEnabled'] ==
                                      true) ...[
                                    Wrap(
                                      children: [
                                        Text('Verkada Device Category: ',
                                            style: theme.textTheme.labelSmall
                                                ?.copyWith(
                                                    fontWeight:
                                                        FontWeight.bold)),
                                        Text(verkadaDeviceType,
                                            style: theme.textTheme.labelSmall),
                                      ],
                                    ),
                                  ],
                                  if (isDeviceCheckedOut) ...[
                                    Wrap(
                                      children: [
                                        Text('Checked Out By: ',
                                            style: theme.textTheme.labelSmall
                                                ?.copyWith(
                                                    fontWeight:
                                                        FontWeight.bold)),
                                        Text(
                                            orgMemberData[
                                                'orgMemberDisplayName'],
                                            style: theme.textTheme.labelSmall),
                                      ],
                                    ),
                                    Wrap(
                                      children: [
                                        Text('Checked Out On: ',
                                            style: theme.textTheme.labelSmall
                                                ?.copyWith(
                                                    fontWeight:
                                                        FontWeight.bold)),
                                        Text(deviceCheckedOutAtFormatted,
                                            style: theme.textTheme.labelSmall),
                                      ],
                                    ),
                                    Wrap(
                                      children: [
                                        Text('Checkout Note: ',
                                            style: theme.textTheme.labelSmall
                                                ?.copyWith(
                                                    fontWeight:
                                                        FontWeight.bold)),
                                        Text(deviceCheckedOutNote,
                                            style: theme.textTheme.labelSmall),
                                      ],
                                    ),
                                  ],
                                ],
                              ),
                            ),
                            Column(
                              crossAxisAlignment: CrossAxisAlignment.end,
                              children: [
                                Row(
                                  children: [
                                    DeviceCheckoutButton(
                                      key: ValueKey(deviceSerialNumber),
                                      deviceSerialNumber: deviceSerialNumber,
                                    ),
                                    const SizedBox(width: 8),
                                    if (userClaims[
                                            'org_admin_${orgSelectorChangeNotifier.orgId}'] ==
                                        true)
                                      DeleteDeviceButton(deviceId: deviceId),
                                  ],
                                ),
                              ],
                            ),
                          ],
                        ),
                        customCardTrailing: null,
                        onTapAction: () {},
                      );
                    },
                  );
                }
              });
        });
      });
    }
  }
}

class DeviceCardMobile extends StatelessWidget {
  const DeviceCardMobile({
    super.key,
    required this.deviceData,
  });

  final Map<String, dynamic> deviceData;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final String deviceId = deviceData['deviceId'];
    final String deviceSerialNumber = deviceData['deviceSerialNumber'];
    final bool deviceDeleted = deviceData['deviceDeleted'] ?? false;
    final String orgMemberId = deviceData['deviceCheckedOutBy'];
    final bool isDeviceCheckedOut = deviceData['isDeviceCheckedOut'];
    final String deviceCheckedOutNote =
        deviceData['deviceCheckedOutNote'] ?? '';

    final Timestamp deviceCheckedOutAtTimestamp =
        deviceData['deviceCheckedOutAt'] ?? Timestamp.now();
    final DateTime deviceCheckedOutAt = deviceCheckedOutAtTimestamp.toDate();
    final String deviceCheckedOutAtFormatted =
        DateFormat('yyyy-MM-dd kk:mm a').format(deviceCheckedOutAt);

    // Skip rendering if the device has been marked as deleted
    if (deviceDeleted) {
      return const SizedBox.shrink();
    }
    return Consumer4<FirestoreReadService, DeviceCheckoutService,
            OrgSelectorChangeNotifier, FirebaseFunctions>(
        builder: (context, firestoreService, deviceCheckoutService,
            orgSelectorChangeNotifier, firebaseFunctions, child) {
      return StreamBuilder<DocumentSnapshot?>(
          stream: firestoreService.getOrgMemberDocument(
              orgSelectorChangeNotifier.orgId, orgMemberId),
          builder: (context, snapshot) {
            if (snapshot.connectionState == ConnectionState.waiting) {
              return const Center(child: CircularProgressIndicator());
            } else if (snapshot.hasError) {
              return const Text('Error loading org member data');
            } else {
              // Fetch the organization member data
              Map<String, dynamic> orgMemberData =
                  snapshot.data?.data() as Map<String, dynamic>? ?? {};
              return AuthClaimChecker(
                builder: (context, userClaims) {
                  return CustomCard(
                    theme: theme,
                    customCardLeading: null,
                    customCardTitle: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Icon(Icons.devices, color: theme.colorScheme.secondary),
                        Wrap(
                          children: [
                            CopyableSerialNumber(
                              serialNumber: deviceSerialNumber,
                              style: const TextStyle(
                                  fontWeight: FontWeight.bold),
                            ),
                          ],
                        ),
                        if (isDeviceCheckedOut) ...[
                          Wrap(
                            children: [
                              Text('Checked Out By: ',
                                  style: theme.textTheme.labelSmall
                                      ?.copyWith(fontWeight: FontWeight.bold)),
                              Text(orgMemberData['orgMemberDisplayName'],
                                  style: theme.textTheme.labelSmall),
                            ],
                          ),
                          Wrap(
                            children: [
                              Text('Checked Out On: ',
                                  style: theme.textTheme.labelSmall
                                      ?.copyWith(fontWeight: FontWeight.bold)),
                              Text(deviceCheckedOutAtFormatted,
                                  style: theme.textTheme.labelSmall),
                            ],
                          ),
                          Wrap(
                            children: [
                              Text('Checkout Note: ',
                                  style: theme.textTheme.labelSmall
                                      ?.copyWith(fontWeight: FontWeight.bold)),
                              Text(deviceCheckedOutNote,
                                  style: theme.textTheme.labelSmall),
                            ],
                          ),
                        ],
                        const SizedBox(height: 8),
                        Wrap(
                          alignment: WrapAlignment.start,
                          runSpacing: 8,
                          children: [
                            DeviceCheckoutButton(
                              key: ValueKey(deviceSerialNumber),
                              deviceSerialNumber: deviceSerialNumber,
                            ),
                            const SizedBox(width: 8),
                            if (userClaims[
                                    'org_admin_${orgSelectorChangeNotifier.orgId}'] ==
                                true)
                              DeleteDeviceButton(deviceId: deviceId),
                          ],
                        ),
                      ],
                    ),
                    customCardTrailing: null,
                    onTapAction: () {},
                  );
                },
              );
            }
          });
    });
  }
}
