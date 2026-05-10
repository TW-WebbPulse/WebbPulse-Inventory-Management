import 'package:flutter/material.dart';
import 'package:webbpulse_inventory_management/src/shared/providers/authentication_change_notifier.dart';

import 'firestore_read_service.dart';
import 'package:cloud_functions/cloud_functions.dart';
import 'package:provider/provider.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:webbpulse_inventory_management/src/shared/widgets/styling/styling_widgets.dart';

/// Service class for handling the check-in and check-out logic of devices
class DeviceCheckoutService {
  final FirestoreReadService firestoreService;
  final FirebaseFunctions firebaseFunctions;

  DeviceCheckoutService(
      {required this.firestoreService, required this.firebaseFunctions});

  /// Main method to handle device check-in and check-out
  Future<void> handleDeviceCheckout(
      BuildContext context,
      String deviceSerialNumber,
      String orgId,
      String deviceBeingCheckedBy,
      bool isDeviceBeingCheckedOut,
      String deviceCheckedOutNote) async {
    if (deviceSerialNumber.isNotEmpty) {
      try {
        final authenticationChangeNotifier =
            Provider.of<AuthenticationChangeNotifier>(context, listen: false);

        // Verify permissions if checking out for another user
        if (deviceBeingCheckedBy != authenticationChangeNotifier.user!.uid) {
          IdTokenResult userIdTokenResult =
              await authenticationChangeNotifier.user!.getIdTokenResult();
          final userClaims = userIdTokenResult.claims;

          if (userClaims!['org_admin_$orgId'] == false &&
              userClaims['org_deskstation_$orgId'] == false) {
            await AsyncContextHelpers.showSnackBarIfMounted(context,
                'You do not have permission to check out devices for other users in this organization');
            return;
          }
        }

        // Create device if it doesn't exist in Firestore
        if (!await firestoreService.doesDeviceExistInFirestore(
            deviceSerialNumber, orgId)) {
          await firebaseFunctions
              .httpsCallable('create_devices_callable')
              .call({
            "deviceSerialNumbers": [deviceSerialNumber],
            "orgId": orgId,
            "isDeviceCheckedOut": false,
          });

          await firebaseFunctions
              .httpsCallable('update_device_checkout_status_callable')
              .call({
            "deviceSerialNumber": deviceSerialNumber,
            "orgId": orgId,
            "isDeviceBeingCheckedOut": isDeviceBeingCheckedOut,
            "deviceBeingCheckedBy": deviceBeingCheckedBy,
            "deviceCheckedOutNote": deviceCheckedOutNote
          });

          String snackBarMessage = isDeviceBeingCheckedOut
              ? 'Device added to organization and checked out!'
              : 'Device added to organization and checked in!';

          await AsyncContextHelpers.showSnackBarIfMounted(
              context, snackBarMessage);
        } else {
          // Handle existing device checkout status
          bool isDeviceCheckedOut = await firestoreService
              .isDeviceCheckedOutInFirestore(deviceSerialNumber, orgId);

          if (isDeviceBeingCheckedOut && isDeviceCheckedOut) {
            await AsyncContextHelpers.showSnackBarIfMounted(
                context, 'Device is already checked out!');
          } else if (!isDeviceBeingCheckedOut && !isDeviceCheckedOut) {
            await AsyncContextHelpers.showSnackBarIfMounted(
                context, 'Device is already checked in!');
          } else {
            await firebaseFunctions
                .httpsCallable('update_device_checkout_status_callable')
                .call({
              "deviceSerialNumber": deviceSerialNumber,
              "orgId": orgId,
              "isDeviceBeingCheckedOut": isDeviceBeingCheckedOut,
              "deviceBeingCheckedBy": deviceBeingCheckedBy,
              "deviceCheckedOutNote": deviceCheckedOutNote
            });

            await AsyncContextHelpers.showSnackBarIfMounted(
                context,
                isDeviceBeingCheckedOut
                    ? 'Device checked out successfully!'
                    : 'Device checked in successfully!');
          }
        }
      } catch (e) {
        await AsyncContextHelpers.showSnackBarIfMounted(
            context, 'Failed to check in/out device: $e');
      }
    } else {
      await AsyncContextHelpers.showSnackBarIfMounted(
          context, 'Please enter a serial number');
    }
  }
}
