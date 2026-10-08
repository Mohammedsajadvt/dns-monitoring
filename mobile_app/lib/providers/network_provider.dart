import 'package:flutter/foundation.dart';
import '../models/models.dart';
import '../services/api_service.dart';

class NetworkProvider with ChangeNotifier {
  final ApiService _apiService;

  String _activeNetworkId = 'all';
  List<NetworkModel> _networks = [];
  bool _isLoading = false;

  NetworkProvider({ApiService? apiService})
      : _apiService = apiService ?? ApiService();

  String get activeNetworkId => _activeNetworkId;
  List<NetworkModel> get networks => _networks;
  bool get isLoading => _isLoading;

  void setActiveNetworkId(String networkId) {
    if (_activeNetworkId != networkId) {
      _activeNetworkId = networkId;
      _apiService.connectWebSocket(networkId);
      notifyListeners();
    }
  }

  Future<void> fetchNetworks() async {
    _isLoading = true;
    notifyListeners();

    try {
      final list = await _apiService.getNetworks();
      _networks = list;
    } catch (e) {
      debugPrint('[NetworkProvider] fetchNetworks error: $e');
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> autoDetectCurrentWifi() async {
    _isLoading = true;
    notifyListeners();

    try {
      final detected = await _apiService.autoDetectNetwork();
      if (detected != null) {
        final idx = _networks.indexWhere((n) => n.networkId == detected.networkId);
        if (idx >= 0) {
          _networks[idx] = detected;
        } else {
          _networks.insert(0, detected);
        }
        _activeNetworkId = detected.networkId;
        _apiService.connectWebSocket(detected.networkId);
      }
    } catch (e) {
      debugPrint('[NetworkProvider] autoDetectCurrentWifi error: $e');
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }
}
