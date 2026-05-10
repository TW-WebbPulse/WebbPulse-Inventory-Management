import 'package:flutter/material.dart';

/// A ChangeNotifier that manages the selection of an organization (orgId)
class OrgSelectorChangeNotifier extends ChangeNotifier {
  OrgSelectorChangeNotifier() {
    init();
  }

  String _orgId = '';

  String get orgId => _orgId;

  void init() {
    _orgId = '';
  }

  void selectOrg(String orgId) {
    if (_orgId != orgId) {
      _orgId = orgId;
      notifyListeners();
    }
  }

  void clearSelectedOrg() {
    if (_orgId.isNotEmpty) {
      _orgId = '';
      notifyListeners();
    }
  }
}
