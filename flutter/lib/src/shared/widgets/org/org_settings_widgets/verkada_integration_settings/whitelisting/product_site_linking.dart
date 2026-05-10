import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:webbpulse_inventory_management/src/shared/widgets/styling/styling_widgets.dart';
import 'package:cloud_functions/cloud_functions.dart';

class VerkadaProductSiteDesignationDialog extends StatefulWidget {
  final String orgId;
  // Expecting a map where keys are product names and values are current site IDs (or null/empty)
  final Map<String, dynamic> verkadaProductSiteDesignations;

  const VerkadaProductSiteDesignationDialog({
    super.key,
    required this.orgId,
    required this.verkadaProductSiteDesignations,
  });

  @override
  _VerkadaProductSiteDesignationDialogState createState() =>
      _VerkadaProductSiteDesignationDialogState();
}

class _VerkadaProductSiteDesignationDialogState
    extends State<VerkadaProductSiteDesignationDialog> {
  // Map to hold TextEditingControllers for each product
  late Map<String, TextEditingController> _siteIdControllers;
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    _siteIdControllers = {
      for (var entry in widget.verkadaProductSiteDesignations.entries)
        entry.key: TextEditingController(text: entry.value ?? ''),
    };
    // Remove entries if the product key is somehow empty
    _siteIdControllers.removeWhere((key, value) => key.isEmpty);
  }

  @override
  void dispose() {
    // Dispose all controllers
    for (var controller in _siteIdControllers.values) {
      controller.dispose();
    }
    super.dispose();
  }

  Future<void> _saveChanges() async {
    final firebaseFunctions =
        Provider.of<FirebaseFunctions>(context, listen: false);

    // Create the map to send, collecting text from controllers
    final Map<String, dynamic> productSiteDesignations = {
      for (var entry in _siteIdControllers.entries)
        entry.key: entry.value.text.trim(),
    };

    // Optional: Add validation here if needed (e.g., check if site IDs are empty)

    setState(() {
      _isLoading = true;
    });

    try {
      // Assuming the cloud function expects a map under 'productSiteDesignations' key
      await firebaseFunctions
          .httpsCallable('update_verkada_product_site_designations_callable')
          .call({
        'orgId': widget.orgId,
        'productSiteDesignations': productSiteDesignations,
      });
      await AsyncContextHelpers.showSnackBarIfMounted(
          context, 'Site designations updated successfully');
      Navigator.of(context).pop(true); // Pop dialog and indicate success
    } catch (e) {
      await AsyncContextHelpers.showSnackBarIfMounted(
          context, 'Failed to update site designations: $e');
    } finally {
      if (mounted) {
        setState(() {
          _isLoading = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final configNames = _siteIdControllers.keys.toList();
    configNames.sort();

    return AlertDialog(
      title: const Text('Configure Verkada Product Site IDs'),
      content: SizedBox(
        width: double.maxFinite, // Use available width
        child: _isLoading
            ? const Center(child: CircularProgressIndicator())
            : (configNames.isEmpty
                ? const Center(
                    child: Text(
                        'No Verkada Products found to configure. Have you synced your Verkada credentials?'))
                : ListView.builder(
                    shrinkWrap: true,
                    itemCount: configNames.length,
                    itemBuilder: (context, index) {
                      final configName = configNames[index];
                      final controller = _siteIdControllers[configName];

                      if (controller == null) {
                        return const SizedBox
                            .shrink(); // Should not happen, but safety check
                      }

                      return Padding(
                        padding: const EdgeInsets.symmetric(vertical: 8.0),
                        child: Row(
                          children: [
                            Expanded(
                              flex: 2,
                              child: Text(configName,
                                  style: theme.textTheme.titleMedium),
                            ),
                            const SizedBox(width: 16),
                            Expanded(
                              flex: 3,
                              child: TextField(
                                controller: controller,
                                decoration: const InputDecoration(
                                  labelText: 'ID',
                                  border: OutlineInputBorder(),
                                  isDense: true,
                                ),
                              ),
                            ),
                          ],
                        ),
                      );
                    },
                  )),
      ),
      actions: <Widget>[
        TextButton(
          onPressed: _isLoading
              ? null
              : () =>
                  Navigator.of(context).pop(false), // Indicate no changes saved
          child: const Text('Cancel'),
        ),
        ElevatedButton.icon(
          icon: _isLoading
              ? SizedBox(
                  width: 20,
                  height: 20,
                  child: CircularProgressIndicator(
                    strokeWidth: 2,
                    valueColor: AlwaysStoppedAnimation<Color>(
                        theme.colorScheme.onPrimary),
                  ),
                )
              : const Icon(Icons.save),
          label: const Text('Save Changes'),
          style: ElevatedButton.styleFrom(
            backgroundColor: theme.colorScheme.primary,
            foregroundColor: theme.colorScheme.onPrimary,
          ),
          onPressed: _isLoading ? null : _saveChanges,
        ),
      ],
    );
  }
}
