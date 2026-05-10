import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:cloud_functions/cloud_functions.dart';
import 'package:webbpulse_inventory_management/src/shared/widgets/styling/styling_widgets.dart';
import '../../providers/org_selector_change_notifier.dart';

import '../../providers/authentication_change_notifier.dart';

class DeleteDeviceButton extends StatefulWidget {
  const DeleteDeviceButton({
    super.key,
    required this.deviceId,
  });

  final String deviceId;

  @override
  State<DeleteDeviceButton> createState() => _DeleteDeviceButtonState();
}

class _DeleteDeviceButtonState extends State<DeleteDeviceButton> {
  var _isLoading = false;

  @override
  void initState() {
    super.initState();
  }

  @override
  void dispose() {
    super.dispose();
  }

  void _onPressed() async {
    final orgSelectorProvider = Provider.of<OrgSelectorChangeNotifier>(context,
        listen: false);
    final firebaseFunctions = Provider.of<FirebaseFunctions>(context,
        listen: false);

    setState(() {
      _isLoading = true;
    });

    try {
      await firebaseFunctions.httpsCallable('delete_device_callable').call({
        'orgId': orgSelectorProvider.orgId,
        'deviceId': widget.deviceId,
      });

      await AsyncContextHelpers.showSnackBarIfMounted(
          context, 'Device deleted successfully');
    } catch (e) {

      await AsyncContextHelpers.showSnackBarIfMounted(
          context, 'Failed to delete device: $e');
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
            _isLoading ? null : _onPressed,
        icon: _isLoading
            ? const CircularProgressIndicator()
            : const Icon(Icons.delete),
        label: Wrap(children: [
          Text(
            'Delete Device',
            style: Theme.of(context)
                .textTheme
                .labelSmall
                ?.copyWith(fontWeight: FontWeight.bold),
          ),
        ]),
        style: ElevatedButton.styleFrom(
          disabledBackgroundColor: Colors.red,
          backgroundColor: Colors.red,
          padding: const EdgeInsets.all(16.0),
        ),
      );
    });
  }
}
