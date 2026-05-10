import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:webbpulse_inventory_management/src/shared/providers/authentication_change_notifier.dart';
import 'package:webbpulse_inventory_management/src/shared/widgets/styling/styling_widgets.dart';
import 'package:cloud_functions/cloud_functions.dart';

// OrgNameEditor provides a text field to edit the organization's name.
class OrgNameEditor extends StatefulWidget {
  final Map<String, dynamic> orgData;

  const OrgNameEditor({super.key, required this.orgData});

  @override
  _OrgNameEditorState createState() => _OrgNameEditorState();
}

class _OrgNameEditorState extends State<OrgNameEditor> {
  late TextEditingController orgNameController;
  var _isLoading = false;

  @override
  void initState() {
    super.initState();
    orgNameController =
        TextEditingController(text: widget.orgData['orgName'] as String? ?? '');
  }

  @override
  void dispose() {
    orgNameController.dispose();
    super.dispose();
  }

  /// Handles the submission of the new organization name.
  void _onSubmit() async {
    final newName = orgNameController.text;
    final firebaseFunctions =
        Provider.of<FirebaseFunctions>(context, listen: false);

    setState(() {
      _isLoading = true;
    });
    try {
      await firebaseFunctions.httpsCallable('update_org_name_callable').call({
        'orgId': widget.orgData['orgId'],
        'orgName': newName,
      });

      await AsyncContextHelpers.showSnackBarIfMounted(
          context, 'Org name changed successfully');
    } catch (e) {
      await AsyncContextHelpers.showSnackBarIfMounted(
          context, 'Failed to change Org name: $e');
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return TextField(
      controller: orgNameController,
      decoration: InputDecoration(
        labelText: 'Organization Name',
        border: const OutlineInputBorder(),
        prefixIcon: const Icon(Icons.edit),
        suffixIcon: IconButton(
          icon: _isLoading
              ? const CircularProgressIndicator()
              : const Icon(Icons.check),
          onPressed: _isLoading ? null : _onSubmit,
        ),
      ),
    );
  }
}

//
class OrgDeviceRegexEditor extends StatefulWidget {
  final Map<String, dynamic> orgData;

  const OrgDeviceRegexEditor({super.key, required this.orgData});

  @override
  _OrgDeviceRegexEditorState createState() => _OrgDeviceRegexEditorState();
}

class _OrgDeviceRegexEditorState extends State<OrgDeviceRegexEditor> {
  late TextEditingController regexStringController;
  var _isLoading = false;

  @override
  void initState() {
    super.initState();
    regexStringController = TextEditingController(
        text: widget.orgData['orgDeviceRegexString'] as String? ?? '');
  }

  @override
  void dispose() {
    regexStringController.dispose();
    super.dispose();
  }

  /// Handles the submission of the new organization name.
  void _onSubmit() async {
    final newRegexString = regexStringController.text;
    final firebaseFunctions =
        Provider.of<FirebaseFunctions>(context, listen: false);

    setState(() {
      _isLoading = true;
    });
    try {
      await firebaseFunctions
          .httpsCallable('update_org_device_regex_callable')
          .call({
        'orgId': widget.orgData['orgId'],
        'orgDeviceRegexString': newRegexString,
      });

      await AsyncContextHelpers.showSnackBarIfMounted(
          context, 'Device regex configuration changed');
    } catch (e) {
      await AsyncContextHelpers.showSnackBarIfMounted(
          context, 'Failed to change device regex configuration: $e');
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return TextField(
      controller: regexStringController,
      decoration: InputDecoration(
        labelText: 'Device Regex Filter',
        border: const OutlineInputBorder(),
        prefixIcon: const Icon(Icons.edit),
        suffixIcon: IconButton(
          icon: _isLoading
              ? const CircularProgressIndicator()
              : const Icon(Icons.check),
          onPressed: _isLoading ? null : _onSubmit,
        ),
      ),
    );
  }
}

class OrgImageEditorAlertDialog extends StatefulWidget {
  final Map<String, dynamic> orgData;

  const OrgImageEditorAlertDialog({super.key, required this.orgData});

  @override
  OrgImageEditorAlertDialogState createState() =>
      OrgImageEditorAlertDialogState();
}

class OrgImageEditorAlertDialogState extends State<OrgImageEditorAlertDialog> {
  late TextEditingController urlController;
  var _isLoading = false;

  @override
  void initState() {
    super.initState();
    urlController = TextEditingController();
  }

  @override
  void dispose() {
    urlController.dispose();
    super.dispose();
  }

  void _onSubmit() async {
    final newOrgImageUrl = urlController.text;
    final firebaseFunctions =
        Provider.of<FirebaseFunctions>(context, listen: false);

    setState(() {
      _isLoading = true;
    });
    try {
      await firebaseFunctions
          .httpsCallable('update_org_background_image_callable')
          .call({
        'orgId': widget.orgData['orgId'],
        'orgBackgroundImageURL': newOrgImageUrl,
      });

      await AsyncContextHelpers.showSnackBarIfMounted(
          context, 'Org background image changed successfully');
      AsyncContextHelpers.popContextIfMounted(context);
    } catch (e) {
      await AsyncContextHelpers.showSnackBarIfMounted(
          context, 'Failed to change Org background image: $e');
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
      title: const Text('Change Organization Image URL'),
      content: SizedBox(
        height: 120,
        child: Column(
          children: [
            const Text(
              'Please enter the URL of the new image for the organization background:',
            ),
            const SizedBox(height: 16),
            TextField(
              controller: urlController,
              decoration: const InputDecoration(
                labelText: 'Image URL',
                border: OutlineInputBorder(),
              ),
            ),
          ],
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
          label: const Text('Change Organization Image'),
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

/// DeleteOrgAlertDialog confirms and handles the deletion of the organization.
class DeleteOrgAlertDialog extends StatefulWidget {
  final Map<String, dynamic> orgData;

  const DeleteOrgAlertDialog({super.key, required this.orgData});

  @override
  DeleteOrgAlertDialogState createState() => DeleteOrgAlertDialogState();
}

class DeleteOrgAlertDialogState extends State<DeleteOrgAlertDialog> {
  var _isLoading = false;

  void _onSubmit() async {
    final firebaseFunctions =
        Provider.of<FirebaseFunctions>(context, listen: false);
    final authenticationChangeNotifier =
        Provider.of<AuthenticationChangeNotifier>(context, listen: false);

    setState(() {
      _isLoading = true;
    });
    try {
      await firebaseFunctions.httpsCallable('delete_org_callable').call({
        'orgId': widget.orgData['orgId'],
      });
      authenticationChangeNotifier.signOutUser();
    } catch (e) {
      await AsyncContextHelpers.showSnackBarIfMounted(
          context, 'Failed to delete Org: $e');
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
      title: const Text('Delete Organization'),
      content: const Text(
          'Are you sure you want to delete this organization? This action cannot be undone.'),
      actions: <Widget>[
        ElevatedButton.icon(
          onPressed: _isLoading ? null : _onSubmit,
          icon: _isLoading
              ? const CircularProgressIndicator()
              : const Icon(Icons.delete),
          label: const Text('Delete Organization'),
          style: ElevatedButton.styleFrom(
            backgroundColor: Colors.red,
            padding: const EdgeInsets.all(16.0),
          ),
        ),
        const SizedBox(height: 16.0),
        ElevatedButton.icon(
          onPressed: () {
            Navigator.of(context).pop();
          },
          icon: const Icon(Icons.arrow_back),
          label: const Text('Go Back'),
          style: ElevatedButton.styleFrom(
            backgroundColor: theme.colorScheme.surface.withOpacity(0.95),
            side: BorderSide(
              color: theme.colorScheme.primary.withOpacity(0.5),
              width: 1.5,
            ),
            padding: const EdgeInsets.all(16.0),
          ),
        ),
      ],
    );
  }
}
