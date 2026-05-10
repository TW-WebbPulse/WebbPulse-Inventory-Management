import 'package:cloud_firestore/cloud_firestore.dart';

/// A service class that provides various Firestore read operations
class FirestoreReadService {
  final FirebaseFirestore _db = FirebaseFirestore.instance;

  /// Stream that returns a DocumentSnapshot for an organization document
  Stream<DocumentSnapshot> getOrgDocument(String orgId) {
    try {
      DocumentReference documentRef =
          _db.collection('organizations').doc(orgId);
      return documentRef.snapshots();
    } catch (e) {
      return Stream.error('Failed to get organization');
    }
  }

  Stream<DocumentSnapshot> getOrgVerkadaIntegrationDocument(String orgId) {
    try {
      DocumentReference documentRef = _db
          .collection('organizations')
          .doc(orgId)
          .collection('sensitiveConfigs')
          .doc('verkadaIntegrationSettings');
      return documentRef.snapshots();
    } catch (e) {
      return Stream.error(
          'Failed to get organization verkada integration info');
    }
  }

  /// Stream that returns a list of organization IDs that the user is a part of
  Stream<List<String>> getUserOrgsIds(String? uid) {
    if (uid == null) {
      return Stream.value([]);
    }

    return _db.collection('users').doc(uid).snapshots().map((snapshot) {
      return List<String>.from(snapshot.data()?['userOrgIds'] ?? []);
    }).handleError((error) {
      return Stream.value([]);
    });
  }

  /// Check if a device exists in Firestore based on its serial number and organization ID
  Future<bool> doesDeviceExistInFirestore(
      String? deviceSerialNumber, String? orgId) async {
    try {
      final querySnapshot = await _db
          .collection('organizations')
          .doc(orgId)
          .collection('devices')
          .where('deviceSerialNumber', isEqualTo: deviceSerialNumber)
          .get();
      return querySnapshot.docs.isNotEmpty;
    } catch (e) {
      return false;
    }
  }

  /// Check if a device is checked out in Firestore based on its serial number and organization ID
  Future<bool> isDeviceCheckedOutInFirestore(
      String? serial, String? orgId) async {
    try {
      final querySnapshot = await _db
          .collection('organizations')
          .doc(orgId)
          .collection('devices')
          .where('deviceSerialNumber', isEqualTo: serial)
          .get();
      return querySnapshot.docs.first.data()['isDeviceCheckedOut'];
    } catch (e) {
      return false;
    }
  }

  /// Stream that checks if a device is checked out in Firestore based on its serial number and organization ID
  Stream<bool> isDeviceCheckedOutInFirestoreStream(
      String? serial, String? orgId) {
    try {
      return _db
          .collection('organizations')
          .doc(orgId)
          .collection('devices')
          .where('deviceSerialNumber', isEqualTo: serial)
          .snapshots()
          .map((querySnapshot) {
        if (querySnapshot.docs.isNotEmpty) {
          return querySnapshot.docs.first.data()['isDeviceCheckedOut'];
        }
        return false;
      });
    } catch (e) {
      return Stream.value(false);
    }
  }

  /// Stream that returns a DocumentSnapshot for a device document in an organization
  Stream<DocumentSnapshot> getOrgDeviceDocument(
      String? deviceId, String? orgId) {
    try {
      DocumentReference documentRef = _db
          .collection('organizations')
          .doc(orgId)
          .collection('devices')
          .doc(deviceId);
      return documentRef.snapshots();
    } catch (e) {
      return Stream.error('Failed to get organization');
    }
  }

  /// Stream that returns a list of all device documents in an organization
  Stream<List<DocumentSnapshot>> getOrgDevicesDocuments(
      String orgId, String? orgMemberId) {
    CollectionReference collectionRef =
        _db.collection('organizations').doc(orgId).collection('devices');

    if (orgMemberId != null) {
      return collectionRef
          .where('deviceCheckedOutBy', isEqualTo: orgMemberId)
          .snapshots()
          .map((querySnapshot) => querySnapshot.docs)
          .handleError((error) {
        return <DocumentSnapshot>[];
      });
    } else {
      return collectionRef.snapshots().map((querySnapshot) {
        return querySnapshot.docs;
      }).handleError((error) {
        return <DocumentSnapshot>[];
      });
    }
  }

  /// Stream that returns a list of member documents in an organization
  Stream<List<DocumentSnapshot>> getOrgMembersDocuments(String orgId) {
    try {
      CollectionReference collectionRef =
          _db.collection('organizations').doc(orgId).collection('members');
      return collectionRef.snapshots().map((querySnapshot) {
        return querySnapshot.docs;
      });
    } catch (e) {
      return Stream.value(<DocumentSnapshot>[]);
    }
  }

  /// Stream that returns a single member document from an organization based on the member ID
  Stream<DocumentSnapshot?> getOrgMemberDocument(
      String orgId, String orgMemberId) {
    if (orgMemberId.isEmpty) {
      return Stream.value(null);
    }

    try {
      DocumentReference documentRef = _db
          .collection('organizations')
          .doc(orgId)
          .collection('members')
          .doc(orgMemberId);
      return documentRef.snapshots();
    } catch (e) {
      return Stream.error('Failed to get org member');
    }
  }

  /// Stream that returns a global user document based on the user ID (UID)
  Stream<DocumentSnapshot> getGlobalUserDocument(String? uid) {
    try {
      DocumentReference documentRef = _db.collection('users').doc(uid);
      return documentRef.snapshots();
    } catch (e) {
      return Stream.error('Failed to get user');
    }
  }

  /// Stream that checks if a global user exists in Firestore based on the user ID (UID)
  Stream<bool> doesGlobalUserExistInFirestore(String uid) {
    try {
      return _db
          .collection('usersMetadata')
          .doc(uid)
          .snapshots()
          .map((docSnapshot) {
        return docSnapshot.exists;
      });
    } catch (e) {
      return Stream.value(false);
    }
  }
}
