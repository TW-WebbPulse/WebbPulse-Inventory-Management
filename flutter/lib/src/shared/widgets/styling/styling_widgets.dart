import 'package:flutter/material.dart';

/// A simple widget for displaying a heading with some padding
class Header extends StatelessWidget {
  const Header(this.heading, {super.key});
  final String heading;

  @override
  Widget build(BuildContext context) => Padding(
        padding: const EdgeInsets.all(8.0),
        child: Text(
          heading,
          style: const TextStyle(fontSize: 24),
        ),
      );
}

/// A widget for displaying a paragraph with some padding and a larger font size
class Paragraph extends StatelessWidget {
  const Paragraph(this.content, {super.key});
  final String content;

  @override
  Widget build(BuildContext context) => Padding(
        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
        child: Text(
          content,
          style: const TextStyle(fontSize: 18),
        ),
      );
}

/// A widget that displays an icon followed by some text in a row
class IconAndDetail extends StatelessWidget {
  const IconAndDetail(this.icon, this.detail, {super.key});
  final IconData icon;
  final String detail;

  @override
  Widget build(BuildContext context) => Padding(
        padding: const EdgeInsets.all(8.0),
        child: Row(
          children: [
            Icon(icon),
            const SizedBox(width: 8),
            Text(
              detail,
              style: const TextStyle(fontSize: 18),
            )
          ],
        ),
      );
}

/// A customizable card widget that allows setting a leading icon, title, trailing widget, and tap action
class CustomCard extends StatelessWidget {
  const CustomCard({
    super.key,
    required this.theme,
    required this.customCardLeading,
    required this.customCardTitle,
    required this.customCardTrailing,
    required this.onTapAction,
  });

  final ThemeData theme;
  final dynamic customCardLeading;
  final dynamic customCardTitle;
  final dynamic customCardTrailing;
  final dynamic onTapAction;

  @override
  Widget build(BuildContext context) => Card(
        margin: const EdgeInsets.symmetric(vertical: 8.0),
        child: ListTile(
          contentPadding:
              const EdgeInsets.symmetric(horizontal: 16.0, vertical: 8.0),
          tileColor: theme.colorScheme.secondary.withOpacity(0),
          leading: customCardLeading,
          title: customCardTitle,
          trailing: customCardTrailing,
          onTap: onTapAction,
        ),
      );
}

/// A layout builder that adjusts the width of the child widget based on screen size
class SmallLayoutBuilder extends StatelessWidget {
  const SmallLayoutBuilder({super.key, required this.childWidget});

  final Widget childWidget;

  @override
  Widget build(BuildContext context) {
    return Center(
      child: LayoutBuilder(
        builder: (context, constraints) {
          double widthFactor;
          if (constraints.maxWidth < 600) {
            widthFactor = 0.95; // 95% width for narrow screens
          } else if (constraints.maxWidth < 1200) {
            widthFactor = 0.5; // 50% width for medium screens
          } else {
            widthFactor = 0.2; // 20% width for large screens
          }
          return SizedBox(
            width: constraints.maxWidth * widthFactor,
            child: childWidget,
          );
        },
      ),
    );
  }
}

/// Helper class for managing context-related asynchronous tasks
class AsyncContextHelpers {
  /// Display a SnackBar with a message
  static void showSnackBar(BuildContext context, String message) {
    ScaffoldMessenger.of(context)
        .showSnackBar(SnackBar(content: Text(message)));
  }

  /// Display a SnackBar only if the context is mounted (i.e., still valid)
  static Future<void> showSnackBarIfMounted(
      BuildContext context, String message) async {
    while (!context.mounted) {
      await Future.delayed(const Duration(milliseconds: 100));
    }
    if (context.mounted) {
      showSnackBar(context, message);
    }
  }

  /// Pop the current context (e.g., close a dialog) only if the context is mounted
  static Future<void> popContextIfMounted(BuildContext context) async {
    while (!context.mounted) {
      await Future.delayed(const Duration(milliseconds: 100));
    }
    if (context.mounted) {
      Navigator.of(context).pop();
    }
  }
}
