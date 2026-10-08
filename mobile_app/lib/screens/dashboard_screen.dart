import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:provider/provider.dart';
import '../models/models.dart';
import '../providers/dashboard_provider.dart';
import '../providers/network_provider.dart';

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final netProv = context.read<NetworkProvider>();
      netProv.fetchNetworks();
      context.read<DashboardProvider>().loadDashboard(netProv.activeNetworkId);
    });
  }

  Future<void> _handleRefresh() async {
    final activeId = context.read<NetworkProvider>().activeNetworkId;
    await Future.wait([
      context.read<NetworkProvider>().fetchNetworks(),
      context.read<DashboardProvider>().loadDashboard(activeId, showLoading: false),
    ]);
  }

  @override
  Widget build(BuildContext context) {
    final netProv = context.watch<NetworkProvider>();
    final dashProv = context.watch<DashboardProvider>();

    return RefreshIndicator(
      onRefresh: _handleRefresh,
      color: const Color(0xFF06B6D4),
      backgroundColor: const Color(0xFF1E293B),
      child: dashProv.isLoading
          ? const Center(
              child: CircularProgressIndicator(color: Color(0xFF06B6D4)),
            )
          : SingleChildScrollView(
              physics: const AlwaysScrollableScrollPhysics(),
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Network Selector Dropdown
                  _buildNetworkSelector(netProv, dashProv),
                  const SizedBox(height: 16),

                  // Top KPI Grid
                  _buildKpiSection(dashProv.stats),
                  const SizedBox(height: 24),

                  // Simulation Quick Actions
                  _buildQuickActionBanner(netProv.activeNetworkId, dashProv),
                  const SizedBox(height: 24),

                  // Top Queried Domains
                  _buildTopDomainsSection(dashProv.stats),
                  const SizedBox(height: 24),

                  // Live Activity Ticker Header
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Row(
                        children: [
                          Container(
                            width: 10,
                            height: 10,
                            decoration: const BoxDecoration(
                              color: Color(0xFF10B981),
                              shape: BoxShape.circle,
                            ),
                          ),
                          const SizedBox(width: 8),
                          const Text(
                            'Live DNS Query Stream',
                            style: TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.bold,
                              color: Colors.white,
                            ),
                          ),
                        ],
                      ),
                      Text(
                        '${dashProv.recentLogs.length} recent',
                        style: const TextStyle(fontSize: 12, color: Colors.grey),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),

                  // Recent Queries List
                  if (dashProv.recentLogs.isEmpty)
                    Container(
                      padding: const EdgeInsets.all(24),
                      alignment: Alignment.center,
                      child: const Column(
                        children: [
                          Icon(Icons.wifi_tethering,
                              color: Color(0xFF64748B), size: 36),
                          SizedBox(height: 8),
                          Text(
                            'No DNS queries captured yet for this network.',
                            style: TextStyle(
                                color: Color(0xFF94A3B8), fontSize: 13),
                          ),
                          SizedBox(height: 4),
                          Text(
                            'Live queries from gateway will appear here in real-time.',
                            style: TextStyle(
                                color: Color(0xFF64748B), fontSize: 11),
                          ),
                        ],
                      ),
                    )
                  else
                    ...dashProv.recentLogs.map((log) => _buildLogCard(log)),
                ],
              ),
            ),
    );
  }

  Widget _buildNetworkSelector(
      NetworkProvider netProv, DashboardProvider dashProv) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      decoration: BoxDecoration(
        color: const Color(0xFF131A2B),
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: Colors.white.withOpacity(0.08)),
      ),
      child: Row(
        children: [
          const Icon(Icons.wifi, color: Color(0xFF06B6D4), size: 20),
          const SizedBox(width: 12),
          Expanded(
            child: DropdownButtonHideUnderline(
              child: DropdownButton<String>(
                value: netProv.activeNetworkId,
                dropdownColor: const Color(0xFF131A2B),
                isExpanded: true,
                style: const TextStyle(
                    color: Colors.white,
                    fontSize: 14,
                    fontWeight: FontWeight.w600),
                icon: const Icon(Icons.arrow_drop_down, color: Color(0xFF06B6D4)),
                items: [
                  const DropdownMenuItem(
                      value: 'all', child: Text('Global (All Networks)')),
                  ...netProv.networks.map((net) => DropdownMenuItem(
                        value: net.networkId,
                        child: Text('${net.name} (${net.location})'),
                      )),
                ],
                onChanged: (val) {
                  if (val != null) {
                    netProv.setActiveNetworkId(val);
                    dashProv.loadDashboard(val);
                  }
                },
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildKpiSection(Map<String, dynamic> stats) {
    final totalQueries = stats['total_queries_today'] ?? 0;
    final activeDevs = stats['active_devices_count'] ?? 0;
    final threats = stats['threats_blocked_today'] ?? 0;

    return Row(
      children: [
        Expanded(
          child: _buildKpiTile(
            title: 'Queries Today',
            value: NumberFormat.compact().format(totalQueries),
            icon: Icons.language,
            color: const Color(0xFF06B6D4),
          ),
        ),
        const SizedBox(width: 10),
        Expanded(
          child: _buildKpiTile(
            title: 'Active Devices',
            value: activeDevs.toString(),
            icon: Icons.devices,
            color: const Color(0xFFA855F7),
          ),
        ),
        const SizedBox(width: 10),
        Expanded(
          child: _buildKpiTile(
            title: 'Blocked Threats',
            value: threats.toString(),
            icon: Icons.security,
            color: const Color(0xFFEF4444),
          ),
        ),
      ],
    );
  }

  Widget _buildKpiTile({
    required String title,
    required String value,
    required IconData icon,
    required Color color,
  }) {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: const Color(0xFF131A2B),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.white.withOpacity(0.08)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            padding: const EdgeInsets.all(6),
            decoration: BoxDecoration(
              color: color.withOpacity(0.15),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Icon(icon, color: color, size: 18),
          ),
          const SizedBox(height: 10),
          Text(
            value,
            style: const TextStyle(
                fontSize: 18, fontWeight: FontWeight.bold, color: Colors.white),
          ),
          const SizedBox(height: 2),
          Text(
            title,
            style: const TextStyle(
                fontSize: 10,
                color: Color(0xFF94A3B8),
                fontWeight: FontWeight.w500),
          ),
        ],
      ),
    );
  }

  Widget _buildQuickActionBanner(
      String activeNetworkId, DashboardProvider dashProv) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [
            const Color(0xFF06B6D4).withOpacity(0.12),
            const Color(0xFFA855F7).withOpacity(0.08)
          ],
        ),
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: const Color(0xFF06B6D4).withOpacity(0.3)),
      ),
      child: Row(
        children: [
          const Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisSize: MainAxisSize.min,
              children: [
                Text(
                  'Live Diagnostic Simulation',
                  style: TextStyle(
                      fontWeight: FontWeight.bold,
                      color: Colors.white,
                      fontSize: 13),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
                SizedBox(height: 2),
                Text(
                  'Inject benign traffic or test threat heuristics',
                  style: TextStyle(color: Color(0xFF94A3B8), fontSize: 10.5),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
              ],
            ),
          ),
          const SizedBox(width: 8),
          Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              SizedBox(
                height: 30,
                child: ElevatedButton(
                  onPressed: () =>
                      dashProv.triggerSimulation(activeNetworkId, false),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF06B6D4),
                    foregroundColor: Colors.black,
                    padding: const EdgeInsets.symmetric(horizontal: 10),
                    shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(8)),
                    textStyle: const TextStyle(
                        fontSize: 11, fontWeight: FontWeight.bold),
                  ),
                  child: const Text('Traffic'),
                ),
              ),
              const SizedBox(width: 6),
              SizedBox(
                height: 30,
                child: ElevatedButton(
                  onPressed: () =>
                      dashProv.triggerSimulation(activeNetworkId, true),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFFEF4444),
                    foregroundColor: Colors.white,
                    padding: const EdgeInsets.symmetric(horizontal: 10),
                    shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(8)),
                    textStyle: const TextStyle(
                        fontSize: 11, fontWeight: FontWeight.bold),
                  ),
                  child: const Text('Threat'),
                ),
              ),
            ],
          )
        ],
      ),
    );
  }

  Widget _buildTopDomainsSection(Map<String, dynamic> stats) {
    final List topList = stats['top_domains'] ?? [];
    if (topList.isEmpty) return const SizedBox.shrink();

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF131A2B),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.white.withOpacity(0.08)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Top Queried Domains',
            style: TextStyle(
                fontSize: 15, fontWeight: FontWeight.bold, color: Colors.white),
          ),
          const SizedBox(height: 12),
          ...topList.take(5).map((d) {
            return Padding(
              padding: const EdgeInsets.only(bottom: 10),
              child: Row(
                children: [
                  const Icon(Icons.link, size: 14, color: Color(0xFF06B6D4)),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      d['domain'] ?? '',
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 13,
                        fontFamily: 'monospace',
                        fontWeight: FontWeight.w600,
                      ),
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                  const SizedBox(width: 8),
                  Text(
                    '${d['count']} queries',
                    style:
                        const TextStyle(color: Color(0xFF94A3B8), fontSize: 12),
                  ),
                ],
              ),
            );
          }),
        ],
      ),
    );
  }

  Widget _buildLogCard(DNSLogModel log) {
    final timeStr = DateFormat('HH:mm:ss').format(log.timestamp);
    final isThreat = log.isThreat;

    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: isThreat
            ? const Color(0xFFEF4444).withOpacity(0.1)
            : const Color(0xFF131A2B),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: isThreat
              ? const Color(0xFFEF4444).withOpacity(0.4)
              : Colors.white.withOpacity(0.05),
        ),
      ),
      child: Row(
        children: [
          Icon(
            isThreat ? Icons.security : Icons.public,
            color: isThreat ? const Color(0xFFEF4444) : const Color(0xFF06B6D4),
            size: 20,
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  log.domain,
                  style: TextStyle(
                    fontFamily: 'monospace',
                    fontWeight: FontWeight.bold,
                    color: isThreat ? const Color(0xFFFCA5A5) : Colors.white,
                    fontSize: 13,
                  ),
                  overflow: TextOverflow.ellipsis,
                ),
                const SizedBox(height: 2),
                Text(
                  '${log.clientName} (${log.clientIp}) • ${log.category}',
                  style: const TextStyle(color: Color(0xFF94A3B8), fontSize: 11),
                ),
              ],
            ),
          ),
          Column(
            crossAxisAlignment: CrossAxisAlignment.end,
            children: [
              Text(
                timeStr,
                style: const TextStyle(
                    color: Color(0xFF64748B),
                    fontSize: 11,
                    fontFamily: 'monospace'),
              ),
              const SizedBox(height: 2),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                decoration: BoxDecoration(
                  color: isThreat
                      ? const Color(0xFFEF4444).withOpacity(0.2)
                      : const Color(0xFF10B981).withOpacity(0.2),
                  borderRadius: BorderRadius.circular(4),
                ),
                child: Text(
                  log.action,
                  style: TextStyle(
                    color: isThreat
                        ? const Color(0xFFEF4444)
                        : const Color(0xFF10B981),
                    fontSize: 9,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ],
          )
        ],
      ),
    );
  }
}
