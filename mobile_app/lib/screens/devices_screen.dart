import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:provider/provider.dart';
import '../models/models.dart';
import '../providers/devices_provider.dart';
import '../providers/network_provider.dart';

class DevicesScreen extends StatefulWidget {
  const DevicesScreen({super.key});

  @override
  State<DevicesScreen> createState() => _DevicesScreenState();
}

class _DevicesScreenState extends State<DevicesScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final activeNet = context.read<NetworkProvider>().activeNetworkId;
      context.read<DevicesProvider>().fetchDevices(activeNet);
    });
  }

  void _showEditDeviceModal(DeviceModel device) {
    final nameController = TextEditingController(text: device.friendlyName);
    String selectedType = device.deviceType;

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: const Color(0xFF0F1422),
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (ctx) => StatefulBuilder(
        builder: (ctx, setModalState) => Padding(
          padding: EdgeInsets.only(
            left: 20,
            right: 20,
            top: 20,
            bottom: MediaQuery.of(ctx).viewInsets.bottom + 20,
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text(
                    'Edit Device Alias',
                    style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                        color: Colors.white),
                  ),
                  IconButton(
                    icon: const Icon(Icons.close, color: Colors.grey),
                    onPressed: () => Navigator.pop(ctx),
                  )
                ],
              ),
              const SizedBox(height: 12),
              Text(
                'IP: ${device.ip}  •  MAC: ${device.mac}',
                style: const TextStyle(
                    color: Color(0xFF94A3B8),
                    fontSize: 13,
                    fontFamily: 'monospace'),
              ),
              const SizedBox(height: 16),
              const Text('Friendly Device Name',
                  style: TextStyle(color: Color(0xFF64748B), fontSize: 12)),
              const SizedBox(height: 6),
              TextField(
                controller: nameController,
                style: const TextStyle(color: Colors.white),
                decoration: InputDecoration(
                  filled: true,
                  fillColor: const Color(0xFF161D30),
                  border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(10),
                      borderSide: BorderSide.none),
                ),
              ),
              const SizedBox(height: 16),
              const Text('Device Type',
                  style: TextStyle(color: Color(0xFF64748B), fontSize: 12)),
              const SizedBox(height: 6),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 12),
                decoration: BoxDecoration(
                  color: const Color(0xFF161D30),
                  borderRadius: BorderRadius.circular(10),
                ),
                child: DropdownButtonHideUnderline(
                  child: DropdownButton<String>(
                    value: selectedType,
                    isExpanded: true,
                    dropdownColor: const Color(0xFF161D30),
                    style: const TextStyle(color: Colors.white),
                    items: const [
                      DropdownMenuItem(
                          value: 'phone', child: Text('Phone / Mobile')),
                      DropdownMenuItem(
                          value: 'laptop',
                          child: Text('Laptop / Workstation')),
                      DropdownMenuItem(
                          value: 'smart_tv',
                          child: Text('Smart TV / Streaming')),
                      DropdownMenuItem(
                          value: 'iot', child: Text('Smart Home IoT')),
                      DropdownMenuItem(
                          value: 'router', child: Text('Router / Gateway')),
                      DropdownMenuItem(
                          value: 'unknown', child: Text('Unknown Device')),
                    ],
                    onChanged: (val) {
                      if (val != null) {
                        setModalState(() => selectedType = val);
                      }
                    },
                  ),
                ),
              ),
              const SizedBox(height: 24),
              ElevatedButton(
                onPressed: () async {
                  final devProv = context.read<DevicesProvider>();
                  final success = await devProv.updateDeviceAlias(
                    networkId: device.networkId,
                    ip: device.ip,
                    friendlyName: nameController.text.trim(),
                    deviceType: selectedType,
                  );

                  if (ctx.mounted) Navigator.pop(ctx);
                  if (mounted && success) {
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(
                          content: Text('Device updated successfully')),
                    );
                  }
                },
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF06B6D4),
                  foregroundColor: Colors.black,
                  minimumSize: const Size(double.infinity, 48),
                  shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(10)),
                ),
                child: const Text('Save Changes',
                    style: TextStyle(fontWeight: FontWeight.bold)),
              ),
            ],
          ),
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final devProv = context.watch<DevicesProvider>();
    final activeNet = context.watch<NetworkProvider>().activeNetworkId;

    return Scaffold(
      backgroundColor: const Color(0xFF07090E),
      body: devProv.isLoading
          ? const Center(
              child: CircularProgressIndicator(color: Color(0xFF06B6D4)))
          : devProv.devices.isEmpty
              ? const Center(
                  child: Text('No devices discovered on network.',
                      style: TextStyle(color: Color(0xFF64748B))),
                )
              : RefreshIndicator(
                  onRefresh: () =>
                      devProv.fetchDevices(activeNet, showLoading: false),
                  color: const Color(0xFF06B6D4),
                  child: ListView.builder(
                    padding: const EdgeInsets.all(16),
                    itemCount: devProv.devices.length,
                    itemBuilder: (context, index) {
                      final dev = devProv.devices[index];
                      final lastSeenStr =
                          DateFormat('MMM dd, HH:mm').format(dev.lastSeen);

                      IconData devIcon = Icons.laptop;
                      if (dev.deviceType == 'phone') devIcon = Icons.smartphone;
                      if (dev.deviceType == 'smart_tv') devIcon = Icons.tv;
                      if (dev.deviceType == 'iot') {
                        devIcon = Icons.devices_other;
                      }
                      if (dev.deviceType == 'router') devIcon = Icons.router;

                      return Container(
                        margin: const EdgeInsets.only(bottom: 12),
                        padding: const EdgeInsets.all(16),
                        decoration: BoxDecoration(
                          color: const Color(0xFF131A2B),
                          borderRadius: BorderRadius.circular(16),
                          border: Border.all(
                              color: Colors.white.withOpacity(0.06)),
                        ),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: [
                                Row(
                                  children: [
                                    Container(
                                      padding: const EdgeInsets.all(8),
                                      decoration: BoxDecoration(
                                        color: const Color(0xFF06B6D4)
                                            .withOpacity(0.12),
                                        borderRadius:
                                            BorderRadius.circular(10),
                                      ),
                                      child: Icon(devIcon,
                                          color: const Color(0xFF06B6D4),
                                          size: 22),
                                    ),
                                    const SizedBox(width: 12),
                                    Column(
                                      crossAxisAlignment:
                                          CrossAxisAlignment.start,
                                      children: [
                                        Text(
                                          dev.friendlyName,
                                          style: const TextStyle(
                                            color: Colors.white,
                                            fontWeight: FontWeight.bold,
                                            fontSize: 15,
                                          ),
                                        ),
                                        Text(
                                          '${dev.hostname} • Last active $lastSeenStr',
                                          style: const TextStyle(
                                              color: Color(0xFF64748B),
                                              fontSize: 11),
                                        ),
                                      ],
                                    ),
                                  ],
                                ),
                                Container(
                                  padding: const EdgeInsets.symmetric(
                                      horizontal: 8, vertical: 2),
                                  decoration: BoxDecoration(
                                    color: dev.isOnline
                                        ? const Color(0xFF10B981)
                                            .withOpacity(0.2)
                                        : Colors.grey.withOpacity(0.2),
                                    borderRadius: BorderRadius.circular(6),
                                  ),
                                  child: Text(
                                    dev.isOnline ? 'ONLINE' : 'OFFLINE',
                                    style: TextStyle(
                                      color: dev.isOnline
                                          ? const Color(0xFF10B981)
                                          : Colors.grey,
                                      fontSize: 10,
                                      fontWeight: FontWeight.bold,
                                    ),
                                  ),
                                ),
                              ],
                            ),
                            const Divider(color: Color(0xFF1E293B), height: 24),
                            Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: [
                                Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    const Text('IP ADDRESS',
                                        style: TextStyle(
                                            fontSize: 10,
                                            color: Color(0xFF64748B))),
                                    Text(dev.ip,
                                        style: const TextStyle(
                                            color: Colors.white,
                                            fontFamily: 'monospace',
                                            fontSize: 12)),
                                  ],
                                ),
                                Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    const Text('MAC ADDRESS',
                                        style: TextStyle(
                                            fontSize: 10,
                                            color: Color(0xFF64748B))),
                                    Text(dev.mac,
                                        style: const TextStyle(
                                            color: Colors.white,
                                            fontFamily: 'monospace',
                                            fontSize: 12)),
                                  ],
                                ),
                                Column(
                                  crossAxisAlignment: CrossAxisAlignment.end,
                                  children: [
                                    const Text('QUERIES',
                                        style: TextStyle(
                                            fontSize: 10,
                                            color: Color(0xFF64748B))),
                                    Text(
                                        NumberFormat.compact()
                                            .format(dev.totalQueries),
                                        style: const TextStyle(
                                            color: Color(0xFF06B6D4),
                                            fontWeight: FontWeight.bold,
                                            fontSize: 12)),
                                  ],
                                ),
                              ],
                            ),
                            const SizedBox(height: 12),
                            OutlinedButton.icon(
                              onPressed: () => _showEditDeviceModal(dev),
                              icon: const Icon(Icons.edit,
                                  size: 14, color: Color(0xFF06B6D4)),
                              label: const Text('Edit Name & Type',
                                  style: TextStyle(
                                      color: Color(0xFF06B6D4), fontSize: 12)),
                              style: OutlinedButton.styleFrom(
                                side: BorderSide(
                                    color: const Color(0xFF06B6D4)
                                        .withOpacity(0.3)),
                                shape: RoundedRectangleBorder(
                                    borderRadius: BorderRadius.circular(8)),
                                minimumSize: const Size(double.infinity, 36),
                              ),
                            ),
                          ],
                        ),
                      );
                    },
                  ),
                ),
    );
  }
}
