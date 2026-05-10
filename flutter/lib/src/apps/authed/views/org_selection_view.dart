import 'package:provider/provider.dart';
import 'package:flutter/material.dart';
import 'package:webbpulse_inventory_management/src/shared/providers/firestore_read_service.dart';
import 'org_create_view.dart';
import 'package:webbpulse_inventory_management/src/shared/widgets/styling/styling_widgets.dart';
import 'package:webbpulse_inventory_management/src/shared/providers/org_selector_change_notifier.dart';
import 'package:webbpulse_inventory_management/src/shared/providers/authentication_change_notifier.dart';
import 'org_selected/org_device_list_view.dart';
import 'package:webbpulse_inventory_management/src/shared/widgets/users/user_widgets.dart';

/// OrgSelectionView provides the screen for selecting an organization.
/// Users can choose an organization they are part of or create a new one.
class OrgSelectionView extends StatelessWidget {
  const OrgSelectionView({super.key});

  /// Route name for navigation to this view
  static const routeName = '/select-organization';

  @override
  Widget build(BuildContext context) {
    ThemeData theme = Theme.of(context);

    return Consumer2<AuthenticationChangeNotifier, FirestoreReadService>(
      builder:
          (context, authenticationChangeNotifier, firestoreService, child) =>
              AuthClaimChecker(builder: (context, userClaims) {
        final List<String> userOrgIds = extractOrgIdsFromClaims(userClaims);

        return Scaffold(
          appBar: AppBar(
            automaticallyImplyLeading: false,
            title: const Text('My Organizations'),
            actions: [
              if (Provider.of<OrgSelectorChangeNotifier>(context).orgId == '')
                ElevatedButton.icon(
                  icon: const Icon(Icons.logout),
                  label: const Text('Sign Out'),
                  onPressed: () {
                    authenticationChangeNotifier.signOutUser();
                  },
                  style: ElevatedButton.styleFrom(
                    backgroundColor:
                        theme.colorScheme.surface.withOpacity(0.95),
                    side: BorderSide(
                      color: theme.colorScheme.primary.withOpacity(0.5),
                      width: 1.5,
                    ),
                    padding: const EdgeInsets.all(16.0),
                  ),
                ),
            ],
          ),
          body: LayoutBuilder(
            builder: (context, constraints) {
              return Center(
                child: Column(
                  children: [
                    if (constraints.maxWidth > 600)
                      Text(
                        'Select an Organization',
                        style: theme.textTheme.headlineSmall,
                      ),
                    Expanded(
                      child: userOrgIds.isNotEmpty
                          ? SmallLayoutBuilder(
                              childWidget: ListView.builder(
                                physics: const BouncingScrollPhysics(),
                                itemCount: userOrgIds.length +
                                    (userOrgIds.length < 10 ? 1 : 0),
                                itemBuilder: (context, index) {
                                  if (index == userOrgIds.length &&
                                      userOrgIds.length < 10) {
                                    return Padding(
                                      padding: const EdgeInsets.symmetric(
                                          vertical: 8.0),
                                      child: ElevatedButton(
                                        onPressed: () {
                                          Navigator.pushNamed(
                                              context, OrgCreateView.routeName);
                                        },
                                        style: ElevatedButton.styleFrom(
                                          backgroundColor: theme
                                              .colorScheme.surface
                                              .withOpacity(0.95),
                                          side: BorderSide(
                                            color: theme.colorScheme.primary
                                                .withOpacity(0.5),
                                            width: 1.5,
                                          ),
                                          padding: const EdgeInsets.all(16.0),
                                        ),
                                        child: const Text(
                                            'Create New Organization'),
                                      ),
                                    );
                                  }
                                  final orgId = userOrgIds[index];
                                  return OrgCard(orgId: orgId);
                                },
                              ),
                            )
                          : Column(
                              children: [
                                const Text('No organizations found'),
                                ElevatedButton(
                                  onPressed: () {
                                    Navigator.pushNamed(
                                        context, OrgCreateView.routeName);
                                  },
                                  style: ElevatedButton.styleFrom(
                                    backgroundColor: theme.colorScheme.surface
                                        .withOpacity(0.95),
                                    side: BorderSide(
                                      color: theme.colorScheme.primary
                                          .withOpacity(0.5),
                                      width: 1.5,
                                    ),
                                  ),
                                  child: const Text('Create New Organization'),
                                ),
                              ],
                            ),
                    ),
                  ],
                ),
              );
            },
          ),
        );
      }),
    );
  }
}

/// OrgCard is a widget that represents an organization in the organization list.
class OrgCard extends StatelessWidget {
  const OrgCard({
    super.key,
    required this.orgId,
  });

  final String orgId;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Consumer2<OrgSelectorChangeNotifier, FirestoreReadService>(
      builder: (context, orgSelectorProvider, firestoreService, child) {
        return StreamBuilder(
          stream: firestoreService.getOrgDocument(orgId),
          builder: (context, snapshot) {
            if (snapshot.connectionState == ConnectionState.waiting) {
              return const Center(child: CircularProgressIndicator());
            } else if (snapshot.hasError) {
              return const Center(child: Text('Error loading organizations'));
            }

            final String orgName = snapshot.data?['orgName'] ?? '';
            final bool orgDeleted = snapshot.data?['orgDeleted'] ?? false;

            if (orgDeleted) {
              return const SizedBox.shrink();
            }

            return CustomCard(
              theme: theme,
              customCardLeading:
                  Icon(Icons.home, color: theme.colorScheme.secondary),
              customCardTitle: Text(orgName),
              customCardTrailing: null,
              onTapAction: () {
                orgSelectorProvider.selectOrg(orgId);
                Navigator.pushNamed(context, OrgDeviceListView.routeName);
              },
            );
          },
        );
      },
    );
  }
}

/// Extracts organization IDs from the user's authentication claims.
List<String> extractOrgIdsFromClaims(Map<String, dynamic> claims) {
  final RegExp orgIdPattern = RegExp(r'^org_(member|admin|deskstation)_(\w+)$');
  List<String> orgIds = [];

  claims.forEach((key, value) {
    final match = orgIdPattern.firstMatch(key);
    if (match != null) {
      final orgId = match.group(2);
      if (orgId != null) {
        orgIds.add(orgId);
      }
    }
  });

  return orgIds;
}
