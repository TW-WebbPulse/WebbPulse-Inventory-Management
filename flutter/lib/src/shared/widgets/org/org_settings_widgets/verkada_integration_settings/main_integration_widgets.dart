import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:webbpulse_inventory_management/src/shared/widgets/styling/styling_widgets.dart';
import 'package:webbpulse_inventory_management/src/shared/widgets/org/org_settings_widgets/verkada_integration_settings/whitelisting/user_group_whitelisting.dart';
import 'package:webbpulse_inventory_management/src/shared/widgets/org/org_settings_widgets/verkada_integration_settings/whitelisting/product_site_linking.dart';
import 'package:cloud_functions/cloud_functions.dart';

class VerkadaIntegrationToggle extends StatefulWidget {
  final Map<String, dynamic> orgData;

  const VerkadaIntegrationToggle({super.key, required this.orgData});

  @override
  _VerkadaIntegrationToggleState createState() =>
      _VerkadaIntegrationToggleState();
}

class _VerkadaIntegrationToggleState extends State<VerkadaIntegrationToggle> {
  var _isLoading = false;

  @override
  void initState() {
    super.initState();
  }

  void _onToggleChanged(bool newValue) async {
    final firebaseFunctions =
        Provider.of<FirebaseFunctions>(context, listen: false);

    setState(() {
      _isLoading = true;
    });

    try {
      await firebaseFunctions
          .httpsCallable('update_verkada_integration_status_callable')
          .call({
        'orgId': widget.orgData['orgId'],
        'enabled': newValue,
      });

      await AsyncContextHelpers.showSnackBarIfMounted(
          context, 'Verkada integration status updated successfully');
    } catch (e) {
      await AsyncContextHelpers.showSnackBarIfMounted(
          context, 'Failed to update Verkada integration status: $e');
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final currentEnabledState =
        widget.orgData['orgVerkadaIntegrationEnabled'] as bool? ?? false;

    return SwitchListTile(
      title: const Text('Verkada Command Integration'),
      value: currentEnabledState,
      onChanged: _isLoading ? null : _onToggleChanged,
      secondary: _isLoading
          ? const CircularProgressIndicator()
          : const Icon(Icons.integration_instructions),
      activeColor: Theme.of(context).colorScheme.primary,
    );
  }
}

// Combined widget for Verkada Credentials
class VerkadaCredentialsEditor extends StatefulWidget {
  final Map<String, dynamic> orgData;
  const VerkadaCredentialsEditor(
      {super.key,
      required this.orgData,});

  @override
  _VerkadaCredentialsEditorState createState() =>
      _VerkadaCredentialsEditorState();
}

class _VerkadaCredentialsEditorState extends State<VerkadaCredentialsEditor> {
  late TextEditingController verkadaOrgShortNameController;
  late TextEditingController verkadaOrgBotUserIdController;
  late TextEditingController verkadaOrgBotV2Controller;
  late TextEditingController verkadaOrgIdController;

  var _isLoading = false;
  bool _obscureText = true;
  @override
  void initState() {
    super.initState();
    // Use null-aware access on the potentially null map
    verkadaOrgShortNameController = TextEditingController(
        text: "", // Default to empty string if null
        );
    verkadaOrgBotUserIdController = TextEditingController(
        text: "");
    verkadaOrgBotV2Controller = TextEditingController(
        text: "");
    verkadaOrgIdController = TextEditingController(
        text: "");
  }

  @override
  void dispose() {
    verkadaOrgShortNameController.dispose();
    verkadaOrgBotUserIdController.dispose();
    verkadaOrgBotV2Controller.dispose();
    verkadaOrgIdController.dispose();

    super.dispose();
  }

  void _onSubmit() async {
    final verkadaShortName = verkadaOrgShortNameController.text;
    final verkadaBotUserId = verkadaOrgBotUserIdController.text;
    final verkadaBotV2 = verkadaOrgBotV2Controller.text;
    final verkadaOrgId = verkadaOrgIdController.text;
    // Add null check for orgId access
    final orgId = widget.orgData['orgId'] as String?;

    if (orgId == null) {
      await AsyncContextHelpers.showSnackBarIfMounted(
          context,
          'Organization ID is missing.' // Specific message if orgId is null
              );
      return;
    }

    final firebaseFunctions =
        Provider.of<FirebaseFunctions>(context, listen: false);

    setState(() {
      _isLoading = true;
    });
    try {
      await firebaseFunctions
          .httpsCallable('sync_with_verkada_callable')
          .call({
        'orgId': orgId,
        'orgVerkadaBotUserId': verkadaBotUserId,
        'orgVerkadaBotUserV2': verkadaBotV2,
        'orgVerkadaOrgShortName': verkadaShortName,
        'orgVerkadaOrgId': verkadaOrgId,
        
      });

      await AsyncContextHelpers.showSnackBarIfMounted(
          context, 'Verkada credentials synced successfully');
    } catch (e) {
      await AsyncContextHelpers.showSnackBarIfMounted(
          context, 'Failed to sync Verkada credentials: $e');
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Padding(
          padding: const EdgeInsets.only(bottom: 16.0),
          child: Text(
            'If you have not configured credentials in the past or if they have expired and are creating errors, please provide them below. For security these fields are not pre-filled.',
            style: theme.textTheme.bodySmall?.copyWith(fontStyle: FontStyle.italic),
            textAlign: TextAlign.center,
          ),
        ),
        TextField(
          controller: verkadaOrgShortNameController,
          decoration: const InputDecoration(
            labelText: 'Verkada Org Short Name',
            border: OutlineInputBorder(),
            prefixIcon: Icon(Icons.business),
          ),
        ),
        const SizedBox(height: 16.0),
        TextField(
          controller: verkadaOrgIdController,
          decoration: const InputDecoration(
            labelText: 'Verkada Org ID',
            border: OutlineInputBorder(),
            prefixIcon: Icon(Icons.business_center),
          ),
        ),
        const SizedBox(height: 16.0),
        TextField(
          controller: verkadaOrgBotUserIdController,
          decoration: const InputDecoration(
            labelText: 'Verkada Bot User ID',
            border: OutlineInputBorder(),
            prefixIcon: Icon(Icons.email),
          ),
        ),
        const SizedBox(height: 16.0),
        TextField(
          obscureText: _obscureText,
          controller: verkadaOrgBotV2Controller,
          decoration: InputDecoration(
            labelText: 'Verkada Bot V2 Token',
            border: const OutlineInputBorder(),
            prefixIcon: const Icon(Icons.password),
            suffixIcon: IconButton(
              icon: Icon(
                _obscureText ? Icons.visibility_off : Icons.visibility,
              ),
              onPressed: () {
                setState(() {
                  _obscureText = !_obscureText;
                });
              },
            ),
          ),
        ),
        const SizedBox(height: 24.0),
        ElevatedButton.icon(
          onPressed: _isLoading ? null : _onSubmit,
          icon: _isLoading
              ? const CircularProgressIndicator(
                  valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                )
              : const Icon(Icons.sync),
          label: const Text('Sync With Verkada'),
          style: ElevatedButton.styleFrom(
            backgroundColor: theme.colorScheme.primary,
            foregroundColor: theme.colorScheme.onPrimary,
            padding: const EdgeInsets.all(16.0),
          ),
        ),
      ],
    );
  }
}

// Combined widget for Verkada Settings after Auth
class VerkadaSettingsEditor extends StatefulWidget {
  final Map<String, dynamic> orgData;
  final Map<String, dynamic>? orgVerkadaIntegrationData;
  const VerkadaSettingsEditor(
      {super.key,
      required this.orgData,
      required this.orgVerkadaIntegrationData});

  @override
  _VerkadaSettingsEditorState createState() => _VerkadaSettingsEditorState();
}

class _VerkadaSettingsEditorState extends State<VerkadaSettingsEditor> {
  bool _isSiteCleanerLoading = false;

  @override
  void initState() {
    super.initState();
  }

  @override
  void dispose() {
    super.dispose();
  }

  void _showUserWhitelistDialog(BuildContext context, String orgId,
      List<Map<String, dynamic>> currentGroups) {
    showDialog<bool>(
      // Expect a boolean result
      context: context,
      builder: (BuildContext dialogContext) {
        return VerkadaGroupWhitelistDialog(
          orgId: orgId,
          initialGroups: currentGroups,
        );
      },
    ).then((saved) {
      if (saved == true) {}
    });
  }

  void _showProductSiteDesignationDialog(BuildContext context, String orgId,
      Map<String, dynamic> verkadaProductSiteDesignations) {
    showDialog<bool>(
      // Expect a boolean result
      context: context,
      builder: (BuildContext dialogContext) {
        return VerkadaProductSiteDesignationDialog(
          orgId: orgId,
          verkadaProductSiteDesignations: verkadaProductSiteDesignations,
        );
      },
    ).then((saved) {
      if (saved == true) {}
    });
  }

  void _onSiteCleanerToggleChanged(bool newValue) async {
    final firebaseFunctions =
        Provider.of<FirebaseFunctions>(context, listen: false);
    final orgId = widget.orgData['orgId'] as String?;

    if (orgId == null) {
      AsyncContextHelpers.showSnackBarIfMounted(
          context, 'Organization ID is missing.');
      return;
    }

    setState(() {
      _isSiteCleanerLoading = true;
    });

    try {
      await firebaseFunctions
          .httpsCallable('update_verkada_site_cleaner_status_callable')
          .call({
        'orgId': orgId,
        'enabled': newValue,
      });

      if (mounted) {
        AsyncContextHelpers.showSnackBarIfMounted(
            context, 'Verkada Site Cleaner status updated successfully');
      }
    } catch (e) {
      if (mounted) {
        AsyncContextHelpers.showSnackBarIfMounted(
            context, 'Failed to update Verkada Site Cleaner status: $e');
      }
    } finally {
      if (mounted) {
        setState(() {
          _isSiteCleanerLoading = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final orgId = widget.orgData['orgId'] as String;

    // Read Verkada settings from the main org document (widget.orgData)
    final List<Map<String, dynamic>> verkadaUserGroups =
        (widget.orgData['orgVerkadaUserGroups'] as List?)
                ?.map((item) {
                  if (item is Map) {
                    return Map<String, dynamic>.from(item);
                  }
                  return null;
                })
                .whereType<Map<String, dynamic>>()
                .toList() ??
            [];
    final Map<String, dynamic> verkadaProductSiteDesignations =
        (widget.orgData['orgVerkadaProductSiteDesignations']
                as Map<String, dynamic>?) ??
            {};

    final bool currentSiteCleanerEnabled =
        widget.orgData['orgVerkadaSiteCleanerEnabled'] as bool? ?? false;

    // Check if credentials are synced by looking for orgVerkadaBotUserInfo
    // in the verkadaIntegrationSettings document (widget.orgVerkadaIntegrationData)
    final bool credentialsSynced = widget.orgVerkadaIntegrationData != null &&
        widget.orgVerkadaIntegrationData!['orgVerkadaBotUserInfo'] != null &&
        (widget.orgVerkadaIntegrationData!['orgVerkadaBotUserInfo'] as Map).isNotEmpty;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        const Text('Verkada Integration Settings',
            style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
            textAlign: TextAlign.center),
        const SizedBox(height: 16.0),
        const Text('Verkada Product Designated Sites',
            style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
        const SizedBox(height: 8.0),
        if (!credentialsSynced)
          const Text(
              'Verkada credentials not synced. Sync credentials to manage sites.')
        else
          ElevatedButton.icon(
              icon: const Icon(Icons.settings),
              label: const Text('Manage Verkada Sites'),
              style: ElevatedButton.styleFrom(
                backgroundColor: theme.colorScheme.secondary,
                foregroundColor: theme.colorScheme.onSecondary,
                padding: const EdgeInsets.all(16.0),
              ),
              onPressed: () {
                _showProductSiteDesignationDialog(
                    context, orgId, verkadaProductSiteDesignations);
              }),
        const SizedBox(height: 16.0),
        const Text('Verkada User Group Whitelist',
            style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
        const SizedBox(height: 8.0),
        if (!credentialsSynced)
          const Text(
              'Verkada credentials not synced. Sync credentials to manage groups.')
        else
          ElevatedButton.icon(
              icon: const Icon(Icons.settings),
              label: const Text('Manage Verkada User Groups'),
              style: ElevatedButton.styleFrom(
                backgroundColor: theme.colorScheme.secondary,
                foregroundColor: theme.colorScheme.onSecondary,
                padding: const EdgeInsets.all(16.0),
              ),
              onPressed: () {
                _showUserWhitelistDialog(context, orgId, verkadaUserGroups);
              }),
        const SizedBox(height: 16.0),
        SwitchListTile(
          title: const Text('Verkada Site Cleaner'),
          value: currentSiteCleanerEnabled,
          onChanged: _isSiteCleanerLoading || !credentialsSynced
              ? null
              : _onSiteCleanerToggleChanged,
          secondary: _isSiteCleanerLoading
              ? const CircularProgressIndicator()
              : const Icon(Icons.integration_instructions),
          activeColor: Theme.of(context).colorScheme.primary,
        ),
        const SizedBox(height: 16.0),
      ],
    );
  }
}
