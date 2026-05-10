import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:cloud_functions/cloud_functions.dart';
import 'package:webbpulse_inventory_management/src/shared/providers/authentication_change_notifier.dart';

import 'org_selection_view.dart';
import 'package:webbpulse_inventory_management/src/shared/widgets/styling/styling_widgets.dart';

/// OrgCreateView provides the UI for creating a new organization.
/// Users can enter a name for their organization and submit the form to create it.
class OrgCreateView extends StatelessWidget {
  const OrgCreateView({super.key});

  /// Route name for navigation to this view
  static const routeName = '/create-organization';

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Create Organization'),
      ),
      body: const Padding(
        padding: EdgeInsets.all(16.0),
        child: CreateOrganizationForm(),
      ),
    );
  }
}

/// Stateful widget that holds the form for creating a new organization.
class CreateOrganizationForm extends StatefulWidget {
  const CreateOrganizationForm({super.key});

  @override
  CreateOrganizationFormState createState() => CreateOrganizationFormState();
}

class CreateOrganizationFormState extends State<CreateOrganizationForm> {
  late TextEditingController _controller;
  var _isLoading = false;

  @override
  void initState() {
    super.initState();
    _controller = TextEditingController();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  /// Handles the submission of the organization creation form.
  void _onSubmit() async {
    final orgName = _controller.text;
    final firebaseFunctions =
        Provider.of<FirebaseFunctions>(context, listen: false);
    final authenticationChangeNotifier =
        Provider.of<AuthenticationChangeNotifier>(context, listen: false);

    if (orgName.isNotEmpty) {
      try {
        setState(() => _isLoading = true);
        await firebaseFunctions
            .httpsCallable('create_organization_callable')
            .call({
          "orgName": orgName,
        });

        /// Refresh the user's ID token to get the roles for the newly created organization
        await authenticationChangeNotifier.user!.getIdToken(true);

        await AsyncContextHelpers.showSnackBarIfMounted(
            context, 'Organization created!');
        Navigator.pushNamed(context, OrgSelectionView.routeName);
      } catch (e) {
        await AsyncContextHelpers.showSnackBarIfMounted(
            context, 'Failed to create organization: $e');
      } finally {
        setState(() => _isLoading = false);
      }
    } else {
      await AsyncContextHelpers.showSnackBarIfMounted(
          context, 'Please enter an organization name');
    }
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        TextField(
          controller: _controller,
          decoration: const InputDecoration(
            labelText: 'Organization Name',
          ),
        ),
        const SizedBox(height: 16.0),
        ElevatedButton.icon(
          onPressed: _isLoading ? null : _onSubmit,
          style: ElevatedButton.styleFrom(padding: const EdgeInsets.all(16.0)),
          icon: _isLoading
              ? const CircularProgressIndicator()
              : const Icon(Icons.add),
          label: const Text('Create Organization'),
        ),
      ],
    );
  }
}
