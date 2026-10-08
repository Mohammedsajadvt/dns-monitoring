import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:provider/provider.dart';
import '../providers/network_provider.dart';
import '../providers/threats_provider.dart';

class ThreatsScreen extends StatefulWidget {
  const ThreatsScreen({super.key});

  @override
  State<ThreatsScreen> createState() => _ThreatsScreenState();
}

class _ThreatsScreenState extends State<ThreatsScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final activeNet = context.read<NetworkProvider>().activeNetworkId;
      context.read<ThreatsProvider>().fetchThreats(activeNet);
    });
  }

  Future<void> _handleResolve(String alertId, String activeNet) async {
    final threatsProv = context.read<ThreatsProvider>();
    final success = await threatsProv.resolveThreat(alertId, activeNet);
    if (success && mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Threat alert marked as resolved')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final threatsProv = context.watch<ThreatsProvider>();
    final activeNet = context.watch<NetworkProvider>().activeNetworkId;

    return Scaffold(
      backgroundColor: const Color(0xFF07090E),
      body: threatsProv.isLoading
          ? const Center(
              child: CircularProgressIndicator(color: Color(0xFFEF4444)))
          : threatsProv.alerts.isEmpty
              ? Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(Icons.shield,
                          size: 64,
                          color: const Color(0xFF10B981).withOpacity(0.8)),
                      const SizedBox(height: 16),
                      const Text(
                        'No Active Threats Detected',
                        style: TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.bold,
                            color: Colors.white),
                      ),
                      const SizedBox(height: 8),
                      const Text(
                        'All DNS queries within policy.',
                        style: TextStyle(color: Color(0xFF64748B)),
                      ),
                    ],
                  ),
                )
              : RefreshIndicator(
                  onRefresh: () => threatsProv.fetchThreats(
                    activeNet,
                    showLoading: false,
                  ),
                  color: const Color(0xFFEF4444),
                  child: ListView.builder(
                    padding: const EdgeInsets.all(16),
                    itemCount: threatsProv.alerts.length,
                    itemBuilder: (context, index) {
                      final alert = threatsProv.alerts[index];
                      final timeStr = DateFormat('MMM dd, HH:mm:ss')
                          .format(alert.timestamp);

                      return Container(
                        margin: const EdgeInsets.only(bottom: 12),
                        padding: const EdgeInsets.all(16),
                        decoration: BoxDecoration(
                          color: const Color(0xFFEF4444).withOpacity(0.08),
                          borderRadius: BorderRadius.circular(16),
                          border: Border.all(
                              color: const Color(0xFFEF4444).withOpacity(0.35)),
                        ),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: [
                                Row(
                                  children: [
                                    const Icon(Icons.warning_amber_rounded,
                                        color: Color(0xFFEF4444), size: 22),
                                    const SizedBox(width: 8),
                                    Text(
                                      alert.threatType.toUpperCase(),
                                      style: const TextStyle(
                                        color: Color(0xFFEF4444),
                                        fontWeight: FontWeight.bold,
                                        fontSize: 12,
                                        letterSpacing: 0.8,
                                      ),
                                    ),
                                  ],
                                ),
                                Container(
                                  padding: const EdgeInsets.symmetric(
                                      horizontal: 8, vertical: 2),
                                  decoration: BoxDecoration(
                                    color: alert.isResolved
                                        ? const Color(0xFF10B981).withOpacity(0.2)
                                        : const Color(0xFFEF4444).withOpacity(0.2),
                                    borderRadius: BorderRadius.circular(6),
                                  ),
                                  child: Text(
                                    alert.isResolved ? 'RESOLVED' : 'BLOCKED',
                                    style: TextStyle(
                                      color: alert.isResolved
                                          ? const Color(0xFF10B981)
                                          : const Color(0xFFEF4444),
                                      fontSize: 10,
                                      fontWeight: FontWeight.bold,
                                    ),
                                  ),
                                ),
                              ],
                            ),
                            const SizedBox(height: 10),
                            Text(
                              alert.domain,
                              style: const TextStyle(
                                fontFamily: 'monospace',
                                fontWeight: FontWeight.bold,
                                fontSize: 15,
                                color: Color(0xFFFCA5A5),
                              ),
                            ),
                            const SizedBox(height: 4),
                            Text(
                              'Device: ${alert.clientName} (${alert.clientIp})',
                              style: const TextStyle(
                                  color: Color(0xFF94A3B8), fontSize: 12),
                            ),
                            const SizedBox(height: 4),
                            Text(
                              alert.details,
                              style: const TextStyle(
                                  color: Color(0xFF64748B), fontSize: 11),
                            ),
                            const Divider(color: Color(0xFF1E293B), height: 20),
                            Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: [
                                Text(
                                  timeStr,
                                  style: const TextStyle(
                                      color: Color(0xFF64748B),
                                      fontSize: 11,
                                      fontFamily: 'monospace'),
                                ),
                                if (!alert.isResolved)
                                  TextButton.icon(
                                    onPressed: () =>
                                        _handleResolve(alert.id, activeNet),
                                    icon: const Icon(Icons.check_circle_outline,
                                        size: 16, color: Color(0xFF10B981)),
                                    label: const Text('Resolve',
                                        style: TextStyle(
                                            color: Color(0xFF10B981),
                                            fontSize: 12)),
                                  ),
                              ],
                            )
                          ],
                        ),
                      );
                    },
                  ),
                ),
    );
  }
}
