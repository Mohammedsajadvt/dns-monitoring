import 'dart:async';
import 'package:flutter/foundation.dart';
import '../models/models.dart';
import '../services/api_service.dart';

class ThreatsProvider with ChangeNotifier {
  final ApiService _apiService;
  StreamSubscription<ThreatAlertModel>? _threatSub;

  List<ThreatAlertModel> _alerts = [];
  bool _isLoading = true;

  ThreatsProvider({ApiService? apiService})
      : _apiService = apiService ?? ApiService() {
    _initLiveListener();
  }

  List<ThreatAlertModel> get alerts => _alerts;
  bool get isLoading => _isLoading;
  int get activeThreatCount => _alerts.where((a) => !a.isResolved).length;

  void _initLiveListener() {
    _threatSub = _apiService.liveThreatStream.listen((alert) {
      _alerts.insert(0, alert);
      notifyListeners();
    });
  }

  Future<void> fetchThreats(String networkId, {bool showLoading = true}) async {
    if (showLoading) {
      _isLoading = true;
      notifyListeners();
    }

    try {
      final list = await _apiService.getThreatAlerts(networkId: networkId);
      _alerts = list;
    } catch (e) {
      debugPrint('[ThreatsProvider] fetchThreats error: $e');
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<bool> resolveThreat(String alertId, String networkId) async {
    final success = await _apiService.resolveThreat(alertId);
    if (success) {
      final idx = _alerts.indexWhere((a) => a.id == alertId);
      if (idx >= 0) {
        _alerts[idx] = _alerts[idx].copyWith(isResolved: true);
        notifyListeners();
      }
    }
    return success;
  }

  @override
  void dispose() {
    _threatSub?.cancel();
    super.dispose();
  }
}
