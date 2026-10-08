import 'package:flutter_test/flutter_test.dart';
import 'package:mobile_app/main.dart';
import 'package:mobile_app/providers/providers.dart';
import 'package:provider/provider.dart';

void main() {
  testWidgets('NetSentryApp loads AuthGate and displays branding', (WidgetTester tester) async {
    await tester.pumpWidget(
      MultiProvider(
        providers: [
          ChangeNotifierProvider(create: (_) => AuthProvider()),
          ChangeNotifierProvider(create: (_) => NetworkProvider()),
          ChangeNotifierProvider(create: (_) => DashboardProvider()),
          ChangeNotifierProvider(create: (_) => DevicesProvider()),
          ChangeNotifierProvider(create: (_) => LogsProvider()),
          ChangeNotifierProvider(create: (_) => ThreatsProvider()),
        ],
        child: const NetSentryApp(),
      ),
    );

    expect(find.text('NetSentry'), findsWidgets);
  });
}
