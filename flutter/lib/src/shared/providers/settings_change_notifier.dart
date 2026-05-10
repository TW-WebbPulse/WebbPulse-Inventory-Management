import 'package:flutter/material.dart';
import '../non_provider_services/settings_service.dart';

/// A ChangeNotifier that manages the app's settings, such as the theme mode
class SettingsChangeNotifier with ChangeNotifier {
  SettingsChangeNotifier(this._settingsService);

  final SettingsService _settingsService;

  late ThemeMode _themeMode;

  ThemeMode get themeMode => _themeMode;

  Future<void> loadSettings() async {
    _themeMode = await _settingsService.themeMode();
    notifyListeners();
  }

  Future<void> updateThemeMode(ThemeMode? newThemeMode) async {
    if (newThemeMode == null) return;

    if (newThemeMode == _themeMode) return;

    _themeMode = newThemeMode;

    notifyListeners();
  }
}
