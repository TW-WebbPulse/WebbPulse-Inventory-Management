# WebbPulse Inventory Management

A comprehensive full-stack inventory management system built with Flutter and Firebase, designed for tracking device checkout status with advanced Verkada integration capabilities.

## 🌟 Features

### Core Inventory Management
- **Device Check-in/Check-out**: Track device availability with real-time status updates
- **Serial Number Tracking**: Manage devices by unique serial numbers
- **Checkout Notes**: Add contextual notes when checking out devices
- **Real-time Updates**: Live synchronization across all users
- **Device History**: Track who checked out devices and when

### Organization Management
- **Multi-Organization Support**: Users can belong to multiple organizations
- **Role-Based Access Control**: Three distinct user roles:
  - **Org Admin**: Full administrative privileges
  - **Desk Station**: Can check out devices for other users
  - **Org Member**: Standard user with basic checkout permissions
- **User Management**: Add, remove, and manage organization members
- **Organization Settings**: Customize device regex patterns and background images

### Verkada Integration
- **Seamless Integration**: Connect with Verkada Command platform
- **Device Synchronization**: Auto-sync Verkada devices (cameras, access controllers, sensors, etc.)
- **Site Management**: Organize devices by Verkada sites
- **User Group Whitelisting**: Control access through Verkada user groups
- **Automated Cleanup**: Scheduled maintenance of Verkada device names and sites
- **Permission Management**: Automated Verkada permission granting

### User Experience
- **Cross-Platform**: Works on web, mobile, and desktop
- **Responsive Design**: Optimized for all screen sizes
- **Modern UI**: Material Design with custom styling
- **Search & Filter**: Find devices and users quickly
- **Export Capabilities**: CSV export functionality

## 🏗️ Architecture

### Frontend (Flutter)
- **Framework**: Flutter 3.3.0+
- **State Management**: Provider pattern with ChangeNotifier
- **Navigation**: Go Router for declarative routing
- **Authentication**: Firebase Auth with Google/Apple sign-in
- **UI Components**: Custom Material Design widgets

### Backend (Firebase)
- **Database**: Cloud Firestore for real-time data
- **Authentication**: Firebase Auth with custom claims
- **Functions**: Cloud Functions for server-side logic
- **Security**: Firestore security rules with role-based access

### Key Dependencies
```yaml
# Core
flutter: ^3.3.0
firebase_core: ^3.8.0
cloud_firestore: ^5.5.0
firebase_auth: ^5.3.3

# UI & Navigation
go_router: ^14.2.0
google_fonts: ^6.1.0
provider: ^6.1.1

# Authentication
firebase_ui_auth: ^1.13.0
google_sign_in: ^6.2.1
sign_in_with_apple: ^6.1.2

# Utilities
rxdart: ^0.28.0
intl: ^0.19.0
csv: ^6.0.0
```

## 🚀 Getting Started

### Prerequisites
- Flutter SDK 3.3.0 or higher
- Firebase project with Firestore, Auth, and Functions enabled
- Node.js and npm (for Firebase CLI)
- Python 3.8+ (for Cloud Functions)

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd WebbPulse-Inventory-Management
   ```

2. **Install Flutter dependencies**
   ```bash
   cd flutter
   flutter pub get
   ```

3. **Configure Firebase**
   ```bash
   # Install Firebase CLI
   npm install -g firebase-tools
   
   # Login to Firebase
   firebase login
   
   # Initialize Firebase (if not already done)
   firebase init
   ```

4. **Set up Firebase emulators**
   ```bash
   # Start Firebase emulators
   firebase emulators:start
   ```

5. **Configure environment variables**
   - Place your Firebase service account key JSON in `functions/`
   - Add SendGrid API key for email functionality

6. **Run the application**
   ```bash
   # In debug mode, the app will automatically use emulators
   flutter run
   ```

### Production Deployment

1. **Deploy Firebase Functions**
   ```bash
   cd functions
   firebase deploy --only functions
   ```

2. **Deploy Firestore Rules**
   ```bash
   firebase deploy --only firestore:rules
   ```

3. **Build and deploy Flutter app**
   ```bash
   cd flutter
   flutter build web
   # Deploy to your hosting platform
   ```

## 📱 Usage

### For Organization Admins
1. **Create Organization**: Set up your organization with custom settings
2. **Invite Members**: Add users via email invitations
3. **Manage Roles**: Assign admin, desk station, or member roles
4. **Configure Verkada**: Set up Verkada integration if needed
5. **Monitor Activity**: Track device usage and user activity

### For Desk Station Users
1. **Check Out for Others**: Use the checkout interface to assign devices to users
2. **Manage Inventory**: Add new devices and update existing ones
3. **View Reports**: Access device status and usage reports

### For Organization Members
1. **Check Out Devices**: Self-service device checkout
2. **Add Notes**: Include context when checking out devices
3. **View History**: See your checkout history and current devices

## 🔧 Configuration

### Verkada Integration Setup
1. Enable Verkada integration in organization settings
2. Provide Verkada credentials:
   - Organization Short Name
   - Organization ID
   - Bot User ID
   - Bot V2 Token
3. Configure site designations for different device types
4. Set up user group whitelisting

### Device Management
- Configure device serial number regex patterns
- Set up automatic device categorization
- Enable/disable Verkada device synchronization

## 🔒 Security

### Authentication
- Email verification required
- Google/Apple OAuth support
- Custom Firebase Auth claims for role management

### Authorization
- Role-based access control (RBAC)
- Organization-scoped permissions
- Firestore security rules enforcement

### Data Protection
- Sensitive configuration stored separately
- Encrypted API keys and tokens
- Audit logging for administrative actions

## 🧪 Testing

### Local Testing
```bash
# Run Flutter tests
cd flutter
flutter test

# Test Firebase Functions
cd functions
python -m pytest
```

### Emulator Testing
- Use Firebase emulators for local development
- Test all functionality without affecting production data
- Debug authentication and database operations

## 📊 Monitoring

### Firebase Console
- Monitor function execution and errors
- Track Firestore usage and performance
- View authentication logs

### Application Metrics
- Device checkout frequency
- User activity patterns
- Verkada integration status

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is proprietary software. All rights reserved.

## 🆘 Support

For support and questions:
- Check the Firebase console for error logs
- Review the application logs in the browser console
- Contact the development team for assistance

## 🔄 Version History

- **v1.1.0**: Current version with Verkada integration
- **v1.0.0**: Initial release with basic inventory management

---

**Live Demo**: [webbpulse.com](https://webbpulse.com)
