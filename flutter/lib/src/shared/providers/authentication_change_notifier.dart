import 'package:flutter/material.dart';
import 'package:firebase_auth/firebase_auth.dart'
    hide EmailAuthProvider, PhoneAuthProvider;
import 'package:firebase_ui_auth/firebase_ui_auth.dart';
import 'package:webbpulse_inventory_management/src/shared/authentication_provider_list.dart';

class AuthenticationChangeNotifier extends ChangeNotifier {
  AuthenticationChangeNotifier() {
    init();
  }

  User? _user;
  bool _userWasLoggedIn = false;
  bool _userEmailVerified = false;
  bool _userLoggedIn = false;
  bool _noPasswordConfigured = false;

  User? get user => _user;
  bool get userWasLoggedIn => _userWasLoggedIn;
  bool get userEmailVerified => _userEmailVerified;
  bool get userLoggedIn => _userLoggedIn;
  bool get noPasswordConfigured => _noPasswordConfigured;

  Future<void> init() async {
    FirebaseUIAuth.configureProviders(authenticationProviderList);

    FirebaseAuth.instance.authStateChanges().listen((user) {
      if (user != null) {
        user.getIdToken(true);
        _user = user;
        _userLoggedIn = true;
        _userWasLoggedIn = true;
        _userEmailVerified = user.emailVerified;
      } else {
        _user = null;
        _userLoggedIn = false;
      }
      notifyListeners();
    });
  }

  Future<void> signInWithCustomToken(String token) async {
    try {
      // Try signing in with the provided custom token
      await FirebaseAuth.instance.signInWithCustomToken(token);
      notifyListeners();
    } on FirebaseAuthException catch (e) {
      if (e.code == 'user-token-expired' || e.code == 'invalid-custom-token') {
        // Handle token expiration or invalid token here
        _authError = 'The provided token is invalid or has expired.';
      } else {
        _authError = 'An unexpected error occurred: ${e.message}';
      }
      notifyListeners();
    }
  }

  String? _authError;
  String? get authError => _authError;

  void clearError() {
    _authError = null;
    notifyListeners();
  }

  Future<void> setNewPassword(String newPassword) async {
  if (_user == null) {
    throw FirebaseAuthException(
      code: 'user-not-signed-in',
      message: 'No user is currently signed in.',
    );
  }
  
  try {
    await _user!.updatePassword(newPassword);
    _noPasswordConfigured = false;
    notifyListeners();
  } on FirebaseAuthException catch (e) {
    // Handle specific Firebase errors, e.g., reauthentication required
    if (e.code == 'requires-recent-login') {
      // Trigger reauthentication in the UI as needed
      print('Reauthentication required');
    }
    rethrow; // Allows UI to handle specific error messages
  }
}


  void setNoPasswordConfigured(bool value) {
    _userLoggedIn = value;
    notifyListeners();
  }

  void setUserWasLoggedIn(bool value) {
    _userWasLoggedIn = value;
    notifyListeners();
  }

  void setUserEmailVerified(bool value) {
    _userEmailVerified = value;
    notifyListeners();
  }

  Future<void> signOutUser() async {
    await FirebaseAuth.instance.signOut();
    _user = null;
    _userLoggedIn = false;
    notifyListeners();
  }
}
