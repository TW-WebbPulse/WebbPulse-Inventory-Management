import 'package:flutter/material.dart';
import 'package:webbpulse_inventory_management/src/shared/widgets/users/user_widgets.dart'; // Importing user-related widgets
import 'package:webbpulse_inventory_management/src/shared/widgets/org/org_widgets.dart'; // Importing organization-related widgets
import 'package:webbpulse_inventory_management/src/shared/widgets/devices/device_list.dart'; // Importing device-related widgets
import 'package:webbpulse_inventory_management/src/shared/widgets/devices/add_device_alert_dialog.dart';

/// OrgDeviceListView displays a list of devices for a selected organization.
/// It also provides functionality for adding new devices to the organization.
class OrgDeviceListView extends StatelessWidget {
  OrgDeviceListView({super.key});

  static const routeName = '/devices';
  final ValueNotifier<String> searchQuery = ValueNotifier<String>('');

  @override
  Widget build(BuildContext context) {
    ThemeData theme = Theme.of(context);

    return Scaffold(
        appBar: OrgNameAppBar(
          titleSuffix: 'Devices',
          actions: [
            ElevatedButton.icon(
              onPressed: () {
                showDialog(
                  context: context,
                  builder: (BuildContext context) {
                    return const AddDeviceAlertDialog();
                  },
                );
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: theme.colorScheme.surface.withOpacity(0.95),
                side: BorderSide(
                  color: theme.colorScheme.primary.withOpacity(0.5),
                  width: 1.5,
                ),
                padding: const EdgeInsets.all(16.0),
              ),
              label: const Text('Add New Device'),
              icon: const Icon(Icons.add),
            )
          ],
        ),

        // Drawer for navigation
        drawer: const AuthedDrawer(),

        // Main content displaying the list of devices in the organization
        body: DeviceList(orgMemberId: null, searchQuery: searchQuery));
  }
}
