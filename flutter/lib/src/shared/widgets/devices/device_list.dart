import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:webbpulse_inventory_management/src/shared/widgets/devices/device_cards.dart';
import '../../providers/org_selector_change_notifier.dart';
import '../../providers/firestore_read_service.dart';

/// Widget that displays a list of devices and allows filtering by serial number or status
class DeviceList extends StatefulWidget {
  final ValueNotifier<String> searchQuery;
  const DeviceList({super.key, this.orgMemberId, required this.searchQuery});
  final String? orgMemberId;

  @override
  State<DeviceList> createState() => _DeviceListState();
}

class _DeviceListState extends State<DeviceList> {
  String _sortCriteria = 'Checked Out';
  String _statusFilterCriteria = 'All';

  @override
  Widget build(BuildContext context) {
    return Consumer2<OrgSelectorChangeNotifier, FirestoreReadService>(
      builder: (context, orgSelectorProvider, firestoreReadService, child) {
        return StreamBuilder<List<DocumentSnapshot>>(
            stream: firestoreReadService.getOrgDevicesDocuments(
                orgSelectorProvider.orgId, widget.orgMemberId),
            builder: (context, snapshot) {
              if (snapshot.connectionState == ConnectionState.waiting) {
                return const Center(child: CircularProgressIndicator());
              } else if (snapshot.hasError) {
                return const Center(child: Text('Error loading devices'));
              }

              final List<DocumentSnapshot> devicesDocs = snapshot.data!;

              return Column(
                children: [
                  /// Search field for filtering devices
                  SerialSearchTextField(searchQuery: widget.searchQuery),

                  // Sort and filter controls
                  Padding(
                      padding: const EdgeInsets.symmetric(
                          horizontal: 16.0, vertical: 8.0),
                      child: Align(
                        alignment: Alignment.centerLeft,
                        child: Wrap(
                          spacing: 16.0,
                          children: [
                            Row(
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                const Text('Sort by:'),
                                const SizedBox(width: 8.0),
                                DropdownButton<String>(
                                  value: _sortCriteria,
                                  items: <String>[
                                    'Checked Out',
                                    'Checked In',
                                    'Alphanumeric'
                                  ].map((String value) {
                                    return DropdownMenuItem<String>(
                                      value: value,
                                      child: Text(value),
                                    );
                                  }).toList(),
                                  onChanged: (String? newValue) {
                                    if (newValue != null) {
                                      setState(() {
                                        _sortCriteria = newValue;
                                      });
                                    }
                                  },
                                ),
                              ],
                            ),
                            Row(
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                const Text('Filter by Status:'),
                                const SizedBox(width: 8.0),
                                DropdownButton<String>(
                                  value: _statusFilterCriteria,
                                  items: <String>[
                                    'All',
                                    'Checked Out',
                                    'Checked In',
                                  ].map((String value) {
                                    return DropdownMenuItem<String>(
                                      value: value,
                                      child: Text(value),
                                    );
                                  }).toList(),
                                  onChanged: (String? newValue) {
                                    if (newValue != null) {
                                      setState(() {
                                        _statusFilterCriteria = newValue;
                                      });
                                    }
                                  },
                                ),
                              ],
                            ),
                          ],
                        ),
                      )),

                  Expanded(
                    child: ValueListenableBuilder<String>(
                      valueListenable: widget.searchQuery,
                      builder: (context, query, child) {
                        final lowerCaseQuery = query.toLowerCase();

                        // Filter devices based on serial number or check-out status
                        final searchedDevicesDocs = devicesDocs.where((doc) {
                          final data = doc.data() as Map<String, dynamic>;

                          final isDeviceCheckedOut =
                              (data['isDeviceCheckedOut'] == true
                                      ? 'Checked Out'
                                      : 'Checked In')
                                  .toString()
                                  .toLowerCase();
                          final deviceSerialNumber =
                              (data['deviceSerialNumber'] ?? '')
                                  .toString()
                                  .toLowerCase();

                          return deviceSerialNumber.contains(lowerCaseQuery) ||
                              isDeviceCheckedOut.contains(lowerCaseQuery);
                        }).toList();

                        searchedDevicesDocs.retainWhere((doc) {
                          final data = doc.data() as Map<String, dynamic>;
                          final isDeviceCheckedOut =
                              (data['isDeviceCheckedOut'] == true
                                  ? 'Checked Out'
                                  : 'Checked In');

                          if (_statusFilterCriteria == 'All') {
                            return true;
                          } else if (_statusFilterCriteria == 'Checked Out') {
                            return isDeviceCheckedOut == 'Checked Out';
                          } else {
                            return isDeviceCheckedOut == 'Checked In';
                          }
                        });

                        // Sort based on the selected criteria
                        searchedDevicesDocs.sort((a, b) {
                          final deviceDataA = a.data() as Map<String, dynamic>;
                          final deviceDataB = b.data() as Map<String, dynamic>;

                          final isCheckedOutA =
                              deviceDataA['isDeviceCheckedOut'] ?? false;
                          final isCheckedOutB =
                              deviceDataB['isDeviceCheckedOut'] ?? false;
                          final serialNumberA =
                              deviceDataA['deviceSerialNumber'] ?? '';
                          final serialNumberB =
                              deviceDataB['deviceSerialNumber'] ?? '';

                          if (_sortCriteria == 'Checked Out') {
                            // Sort to have checked-out devices first
                            return (isCheckedOutB ? 1 : 0)
                                .compareTo(isCheckedOutA ? 1 : 0);
                          } else if (_sortCriteria == 'Checked In') {
                            // Sort to have checked-in devices first
                            return (isCheckedOutA ? 1 : 0)
                                .compareTo(isCheckedOutB ? 1 : 0);
                          } else {
                            // Sort by serial number alphabetically
                            return serialNumberA.compareTo(serialNumberB);
                          }
                        });

                        // Display the filtered devices
                        return searchedDevicesDocs.isNotEmpty
                            ? LayoutBuilder(builder: (context, constraints) {
                                return SizedBox(
                                  width: constraints.maxWidth * 0.95,
                                  child: ListView.builder(
                                    physics: const BouncingScrollPhysics(),
                                    itemCount: searchedDevicesDocs.length,
                                    itemBuilder: (context, index) {
                                      Map<String, dynamic> deviceData =
                                          searchedDevicesDocs[index].data()
                                              as Map<String, dynamic>;
                                      if (constraints.maxWidth < 600) {
                                        return DeviceCardMobile(
                                          deviceData: deviceData,
                                        );
                                      }
                                      return DeviceCardDesktop(
                                        deviceData: deviceData,
                                      );
                                    },
                                  ),
                                );
                              })
                            : const Center(child: Text('No devices found'));
                      },
                    ),
                  ),
                ],
              );
            });
      },
    );
  }
}

/// Widget for the search input field, used to filter devices by serial number
class SerialSearchTextField extends StatefulWidget {
  final ValueNotifier<String> searchQuery;

  const SerialSearchTextField({super.key, required this.searchQuery});

  @override
  SerialSearchTextFieldState createState() => SerialSearchTextFieldState();
}

class SerialSearchTextFieldState extends State<SerialSearchTextField> {
  late TextEditingController _searchController;
  late VoidCallback _listener;

  @override
  void initState() {
    super.initState();
    _searchController = TextEditingController(text: widget.searchQuery.value);

    _listener = () {
      if (_searchController.text != widget.searchQuery.value) {
        _searchController.text = widget.searchQuery.value;
      }
    };

    widget.searchQuery.addListener(_listener);
  }

  @override
  void dispose() {
    widget.searchQuery.removeListener(_listener);
    _searchController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(8.0),
      child: TextField(
        controller: _searchController,
        decoration: InputDecoration(
          labelText: 'Search by Serial',
          border: const OutlineInputBorder(),
          suffixIcon: IconButton(
            icon: const Icon(Icons.clear),
            onPressed: () {
              _searchController.clear();
              widget.searchQuery.value = '';
            },
          ),
        ),
        onChanged: (value) {
          widget.searchQuery.value = value;
        },
      ),
    );
  }
}
