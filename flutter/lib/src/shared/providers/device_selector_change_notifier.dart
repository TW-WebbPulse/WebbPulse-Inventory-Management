import 'package:flutter/material.dart';

class DeviceSelectorChangeNotifier extends ChangeNotifier {
  String _deviceSerialNumber = '';

  String get deviceSerialNumber => _deviceSerialNumber;

  void selectDevice(String deviceSerialNumber) {
    _deviceSerialNumber = deviceSerialNumber;
    notifyListeners();
  }

  void clearSelectedOrgMember() {
    _deviceSerialNumber = '';
    notifyListeners();
  }
}
