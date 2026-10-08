import 'dart:async';
import 'package:flutter/foundation.dart';
import '../models/models.dart';
import '../services/api_service.dart';

class DevicesProvider with ChangeNotifier {
  final ApiService _apiService;
  StreamSubscription<DeviceModel>? _deviceSub;

  List<DeviceModel> _devices = [];
  bool _isLoading = true;

  DevicesProvider({ApiService? apiService})
      : _apiService = apiService ?? ApiService() {
    _initLiveListener();
  }

  List<DeviceModel> get devices => _devices;
  bool get isLoading => _isLoading;

  void _initLiveListener() {
    _deviceSub = _apiService.liveDeviceStream.listen((dev) {
      final idx = _devices.indexWhere((d) => d.ip == dev.ip);
      if (idx >= 0) {
        _devices[idx] = dev;
      } else {
        _devices.insert(0, dev);
      }
      notifyListeners();
    });
  }

  Future<void> fetchDevices(String networkId, {bool showLoading = true}) async {
    if (showLoading) {
      _isLoading = true;
      notifyListeners();
    }

    try {
      final list = await _apiService.getDevices(networkId: networkId);
      _devices = list;
    } catch (e) {
      debugPrint('[DevicesProvider] fetchDevices error: $e');
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<bool> updateDeviceAlias({
    required String networkId,
    required String ip,
    required String friendlyName,
    required String deviceType,
  }) async {
    final success = await _apiService.updateDevice(
      networkId == 'all' ? 'net_home_01' : networkId,
      ip,
      friendlyName,
      deviceType,
    );

    if (success) {
      final idx = _devices.indexWhere((d) => d.ip == ip);
      if (idx >= 0) {
        _devices[idx] = _devices[idx].copyWith(
          friendlyName: friendlyName,
          deviceType: deviceType,
        );
        notifyListeners();
      }
    }
    return success;
  }

  @override
  void dispose() {
    _deviceSub?.cancel();
    super.dispose();
  }
}
