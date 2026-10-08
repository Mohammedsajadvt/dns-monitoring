import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:provider/provider.dart';
import '../providers/logs_provider.dart';
import '../providers/network_provider.dart';

class LogsScreen extends StatefulWidget {
  const LogsScreen({super.key});

  @override
  State<LogsScreen> createState() => _LogsScreenState();
}

class _LogsScreenState extends State<LogsScreen> {
  final TextEditingController _searchController = TextEditingController();

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final activeNet = context.read<NetworkProvider>().activeNetworkId;
      context.read<LogsProvider>().fetchLogs(networkId: activeNet);
    });
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final logsProv = context.watch<LogsProvider>();
    final activeNet = context.watch<NetworkProvider>().activeNetworkId;

    return Scaffold(
      backgroundColor: const Color(0xFF07090E),
      body: Column(
        children: [
          // Search & Filter Box
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: const Color(0xFF0F1422),
              border: Border(
                  bottom: BorderSide(color: Colors.white.withOpacity(0.08))),
            ),
            child: Column(
              children: [
                TextField(
                  controller: _searchController,
                  style: const TextStyle(color: Colors.white, fontSize: 14),
                  decoration: InputDecoration(
                    hintText: 'Search domain, IP or client...',
                    hintStyle:
                        const TextStyle(color: Color(0xFF64748B), fontSize: 14),
                    prefixIcon: const Icon(Icons.search,
                        color: Color(0xFF06B6D4), size: 20),
                    suffixIcon: _searchController.text.isNotEmpty
                        ? IconButton(
                            icon: const Icon(Icons.clear,
                                color: Colors.grey, size: 18),
                            onPressed: () {
                              _searchController.clear();
                              logsProv.setSearchQuery('', activeNet);
                            },
                          )
                        : null,
                    filled: true,
                    fillColor: const Color(0xFF161D30),
                    contentPadding: const EdgeInsets.symmetric(
                        horizontal: 16, vertical: 10),
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                      borderSide: BorderSide.none,
                    ),
                  ),
                  onSubmitted: (val) =>
                      logsProv.setSearchQuery(val.trim(), activeNet),
                ),
                const SizedBox(height: 12),
                SingleChildScrollView(
                  scrollDirection: Axis.horizontal,
                  child: Row(
                    children: logsProv.categories.map((cat) {
                      final isSelected = logsProv.selectedCategory == cat;
                      return Padding(
                        padding: const EdgeInsets.only(right: 8),
                        child: ChoiceChip(
                          label: Text(cat == 'all' ? 'All' : cat),
                          selected: isSelected,
                          selectedColor: const Color(0xFF06B6D4),
                          backgroundColor: const Color(0xFF161D30),
                          labelStyle: TextStyle(
                            color: isSelected
                                ? Colors.black
                                : const Color(0xFF94A3B8),
                            fontSize: 12,
                            fontWeight: isSelected
                                ? FontWeight.bold
                                : FontWeight.normal,
                          ),
                          onSelected: (selected) {
                            if (selected) {
                              logsProv.setCategory(cat, activeNet);
                            }
                          },
                        ),
                      );
                    }).toList(),
                  ),
                ),
              ],
            ),
          ),

          // Logs List View
          Expanded(
            child: logsProv.isLoading
                ? const Center(
                    child: CircularProgressIndicator(color: Color(0xFF06B6D4)))
                : logsProv.logs.isEmpty
                    ? const Center(
                        child: Text(
                          'No DNS logs found matching criteria.',
                          style: TextStyle(color: Color(0xFF64748B)),
                        ),
                      )
                    : RefreshIndicator(
                        onRefresh: () => logsProv.fetchLogs(
                          networkId: activeNet,
                          showLoading: false,
                        ),
                        color: const Color(0xFF06B6D4),
                        child: ListView.builder(
                          padding: const EdgeInsets.all(16),
                          itemCount: logsProv.logs.length,
                          itemBuilder: (context, index) {
                            final log = logsProv.logs[index];
                            final timeStr = DateFormat('MMM dd, HH:mm:ss')
                                .format(log.timestamp);
                            final isThreat = log.isThreat;

                            return Container(
                              margin: const EdgeInsets.only(bottom: 10),
                              padding: const EdgeInsets.all(14),
                              decoration: BoxDecoration(
                                color: isThreat
                                    ? const Color(0xFFEF4444).withOpacity(0.08)
                                    : const Color(0xFF131A2B),
                                borderRadius: BorderRadius.circular(14),
                                border: Border.all(
                                  color: isThreat
                                      ? const Color(0xFFEF4444).withOpacity(0.3)
                                      : Colors.white.withOpacity(0.06),
                                ),
                              ),
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Row(
                                    mainAxisAlignment:
                                        MainAxisAlignment.spaceBetween,
                                    children: [
                                      Expanded(
                                        child: Text(
                                          log.domain,
                                          style: TextStyle(
                                            fontFamily: 'monospace',
                                            fontWeight: FontWeight.bold,
                                            fontSize: 14,
                                            color: isThreat
                                                ? const Color(0xFFFCA5A5)
                                                : Colors.white,
                                          ),
                                          overflow: TextOverflow.ellipsis,
                                        ),
                                      ),
                                      Container(
                                        padding: const EdgeInsets.symmetric(
                                            horizontal: 8, vertical: 2),
                                        decoration: BoxDecoration(
                                          color: isThreat
                                              ? const Color(0xFFEF4444)
                                                  .withOpacity(0.2)
                                              : const Color(0xFF10B981)
                                                  .withOpacity(0.2),
                                          borderRadius:
                                              BorderRadius.circular(6),
                                        ),
                                        child: Text(
                                          log.action,
                                          style: TextStyle(
                                            color: isThreat
                                                ? const Color(0xFFEF4444)
                                                : const Color(0xFF10B981),
                                            fontSize: 10,
                                            fontWeight: FontWeight.bold,
                                          ),
                                        ),
                                      ),
                                    ],
                                  ),
                                  const SizedBox(height: 6),
                                  Row(
                                    children: [
                                      const Icon(Icons.person_pin,
                                          size: 14, color: Color(0xFF94A3B8)),
                                      const SizedBox(width: 4),
                                      Text(
                                        '${log.clientName} (${log.clientIp})',
                                        style: const TextStyle(
                                            color: Color(0xFF94A3B8),
                                            fontSize: 12),
                                      ),
                                    ],
                                  ),
                                  const SizedBox(height: 4),
                                  Row(
                                    mainAxisAlignment:
                                        MainAxisAlignment.spaceBetween,
                                    children: [
                                      Text(
                                        '${log.category} • ${log.queryType} • ${log.responseTimeMs.toStringAsFixed(1)} ms',
                                        style: const TextStyle(
                                            color: Color(0xFF64748B),
                                            fontSize: 11),
                                      ),
                                      Text(
                                        timeStr,
                                        style: const TextStyle(
                                          color: Color(0xFF64748B),
                                          fontSize: 11,
                                          fontFamily: 'monospace',
                                        ),
                                      ),
                                    ],
                                  )
                                ],
                              ),
                            );
                          },
                        ),
                      ),
          ),
        ],
      ),
    );
  }
}
