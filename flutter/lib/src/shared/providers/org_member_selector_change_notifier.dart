import 'package:flutter/material.dart';

/// A ChangeNotifier that manages the selection of an organization member (orgMemberId)
class OrgMemberSelectorChangeNotifier extends ChangeNotifier {
  String _orgMemberId = '';

  String get orgMemberId => _orgMemberId;

  void selectOrgMember(String orgMemberId) {
    _orgMemberId = orgMemberId;
    notifyListeners();
  }

  void clearSelectedOrgMember() {
    _orgMemberId = '';
    notifyListeners();
  }
}
