import 'dart:async';
import 'package:flutter/foundation.dart';
import '../models/models.dart';
import '../services/api_service.dart';

class DashboardProvider with ChangeNotifier {
  final ApiService _apiService;
  StreamSubscription<DNSLogModel>? _logSub;

  bool _isLoading = true;
  Map<String, dynamic> _stats = {};
  List<DNSLogModel> _recentLogs = [];

  DashboardProvider({ApiService? apiService})
      : _apiService = apiService ?? ApiService() {
    _initLiveListener();
  }

  bool get isLoading => _isLoading;
  Map<String, dynamic> get stats => _stats;
  List<DNSLogModel> get recentLogs => _recentLogs;

  void _initLiveListener() {
    _logSub = _apiService.liveLogStream.listen((log) {
      _recentLogs.insert(0, log);
      if (_recentLogs.length > 20) {
        _recentLogs.removeLast();
      }

      final currentQueries = (_stats['total_queries_today'] ?? 0) as int;
      _stats['total_queries_today'] = currentQueries + 1;

      if (log.isThreat) {
        final currentThreats = (_stats['threats_blocked_today'] ?? 0) as int;
        _stats['threats_blocked_today'] = currentThreats + 1;
      }

      final currentDevs = (_stats['active_devices_count'] ?? 0) as int;
      if (currentDevs == 0) {
        _stats['active_devices_count'] = 1;
      }

      notifyListeners();
    });
  }

  Future<void> loadDashboard(String networkId, {bool showLoading = true}) async {
    if (showLoading) {
      _isLoading = true;
      notifyListeners();
    }

    try {
      final results = await Future.wait([
        _apiService.getAnalyticsSummary(networkId: networkId),
        _apiService.getLogs(networkId: networkId, limit: 15),
      ]);

      _stats = results[0] as Map<String, dynamic>;
      _recentLogs = results[1] as List<DNSLogModel>;
    } catch (e) {
      debugPrint('[DashboardProvider] loadDashboard error: $e');
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> triggerSimulation(String networkId, bool isThreat) async {
    await _apiService.triggerSimulation(networkId, isThreat);
  }

  @override
  void dispose() {
    _logSub?.cancel();
    super.dispose();
  }
}
