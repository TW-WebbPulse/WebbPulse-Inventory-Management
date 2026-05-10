import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:cloud_functions/cloud_functions.dart';
import 'package:universal_html/html.dart' as html;
import 'package:path_provider/path_provider.dart';
import 'dart:io' as io;
import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:permission_handler/permission_handler.dart';
import 'dart:convert';
import 'package:file_picker/file_picker.dart';

import '../../providers/org_selector_change_notifier.dart';

import 'package:webbpulse_inventory_management/src/shared/widgets/styling/styling_widgets.dart';

class AddDeviceAlertDialog extends StatefulWidget {
  const AddDeviceAlertDialog({super.key});

  @override
  AddDeviceAlertDialogState createState() => AddDeviceAlertDialogState();
}

class AddDeviceAlertDialogState extends State<AddDeviceAlertDialog> {
  late TextEditingController _deviceSerialNumberController;
  var _isLoading = false;
  final String csvTemplate =
      "Device Serial Number\nAAAA-AAAA-AAAA\nBBBB-BBBB-BBBB";

  @override
  void initState() {
    super.initState();
    _deviceSerialNumberController = TextEditingController();
  }

  @override
  void dispose() {
    _deviceSerialNumberController.dispose();
    super.dispose();
  }

  Future<void> downloadCSV() async {
    if (kIsWeb) {
      downloadCSVForWeb();
    } else {
      await downloadCSVForMobile();
    }
  }

  void downloadCSVForWeb() {
    final bytes = utf8.encode(csvTemplate);
    final blob = html.Blob([bytes], 'text/csv');

    final url = html.Url.createObjectUrlFromBlob(blob);
    html.AnchorElement(href: url)
      ..setAttribute("download", "device_template.csv")
      ..click();
    html.Url.revokeObjectUrl(url);
  }

  Future<void> downloadCSVForMobile() async {
    var status = await Permission.storage.request();
    if (status.isGranted) {
      final directory = await getExternalStorageDirectory();
      if (directory != null) {
        String filePath = '${directory.path}/user_template.csv';

        io.File file = io.File(filePath);
        await file.writeAsString(csvTemplate);

        await AsyncContextHelpers.showSnackBarIfMounted(
            context, 'CSV Template saved to $filePath');
      } else {
        await AsyncContextHelpers.showSnackBarIfMounted(
            context, 'Failed to get storage directory');
      }
    } else {
      await AsyncContextHelpers.showSnackBarIfMounted(
          context, 'Permission denied');
    }
  }

  Future<void> _submitDeviceSerialNumbers(
      List<String> deviceSerialNumbers) async {
    final orgSelectorProvider =
        Provider.of<OrgSelectorChangeNotifier>(context, listen: false);
    final firebaseFunctions =
        Provider.of<FirebaseFunctions>(context, listen: false);
    setState(() {
      _isLoading = true;
    });

    try {
      final HttpsCallableResult createDevicesResult = await firebaseFunctions
          .httpsCallable('create_devices_callable')
          .call({
        "deviceSerialNumbers": deviceSerialNumbers,
        "orgId": orgSelectorProvider.orgId,
      });
      final responseData = createDevicesResult.data;

      int successCount = 0;
      int failureCount = 0;
      if (responseData is Map<String, dynamic>) {
        Map<String, dynamic>? successes = responseData['success'];
        Map<String, dynamic>? failures = responseData['failure'];
        if (successes != null) {
          successCount = successes.length;
        }
        if (failures != null) {
          failureCount = failures.length;
        }
      }
      await AsyncContextHelpers.showSnackBarIfMounted(context,
          'Devices Creation Processed. Success Count: $successCount, Failure Count:$failureCount');
      AsyncContextHelpers.popContextIfMounted(context);
    } catch (e) {
      await AsyncContextHelpers.showSnackBarIfMounted(
          context, 'Failed to create Devices: $e');
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  void _onSubmitSingleEmail() async {
    final deviceSerialNumber = _deviceSerialNumberController.text;
    if (deviceSerialNumber.isNotEmpty) {
      await _submitDeviceSerialNumbers([deviceSerialNumber]);
    }
  }

  void _onCsvFileSelected() async {
    final result = await FilePicker.platform.pickFiles(
      type: FileType.custom,
      allowedExtensions: ['csv'],
    );

    if (result != null) {
      String content = '';

      if (kIsWeb) {
        final file = result.files.first;
        content = utf8.decode(file.bytes!);
      } else {
        final path = result.files.single.path;
        if (path != null) {
          final file = io.File(path);
          content = await file.readAsString();
        }
      }

      List<String> lines = content.split(RegExp(r'[\r\n]+'));

      if (lines.isNotEmpty) {
        lines = lines.sublist(1);
      }

      List<String> deviceSerialNumbers = lines
          .map((line) => line.trim())
          .where((line) => line.isNotEmpty)
          .toList();

      if (deviceSerialNumbers.isNotEmpty) {
        await _submitDeviceSerialNumbers(deviceSerialNumbers);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    ThemeData theme = Theme.of(context);
    return AlertDialog(
      title: const Text('Add New Device'),
      content: SingleChildScrollView(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 500),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Column(
                children: [
                  const Text(
                    'Add a new device to this organization',
                  ),
                  TextField(
                    controller: _deviceSerialNumberController,
                    decoration: const InputDecoration(
                      labelText: 'Device Serial Number',
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
      actions: <Widget>[
        ElevatedButton.icon(
          onPressed: _isLoading ? null : _onSubmitSingleEmail,
          style: ElevatedButton.styleFrom(
            backgroundColor: theme.colorScheme.surface.withOpacity(0.95),
            side: BorderSide(
              color: theme.colorScheme.primary.withOpacity(0.5),
              width: 1.5,
            ),
            padding: const EdgeInsets.all(16.0),
          ),
          icon: _isLoading
              ? const CircularProgressIndicator()
              : const Icon(Icons.add),
          label: const Text('Add Device'),
        ),
        const SizedBox(height: 16.0),
        ElevatedButton.icon(
          onPressed: _isLoading ? null : _onCsvFileSelected,
          style: ElevatedButton.styleFrom(
            backgroundColor: theme.colorScheme.surface.withOpacity(0.95),
            side: BorderSide(
              color: theme.colorScheme.primary.withOpacity(0.5),
              width: 1.5,
            ),
            padding: const EdgeInsets.all(16.0),
          ),
          icon: _isLoading
              ? const CircularProgressIndicator()
              : const Icon(Icons.upload_file),
          label: const Text('Add Devices from CSV'),
        ),
        const SizedBox(height: 16.0),
        ElevatedButton.icon(
          onPressed: () async {
            await downloadCSV();
          },
          style: ElevatedButton.styleFrom(
            backgroundColor: theme.colorScheme.surface.withOpacity(0.95),
            side: BorderSide(
              color: theme.colorScheme.primary.withOpacity(0.5),
              width: 1.5,
            ),
            padding: const EdgeInsets.all(16.0),
          ),
          icon: const Icon(Icons.download),
          label: const Text('Download CSV Template'),
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