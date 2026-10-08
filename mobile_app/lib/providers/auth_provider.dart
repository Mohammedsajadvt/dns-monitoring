import 'dart:async';
import 'package:flutter/foundation.dart';
import '../models/models.dart';
import '../services/api_service.dart';

class AuthProvider with ChangeNotifier {
  final ApiService _apiService;
  StreamSubscription<bool>? _connectionSub;
  StreamSubscription<UserModel?>? _authSub;

  bool _isLoading = false;
  String? _errorMessage;
  bool _isOnline = true;

  AuthProvider({ApiService? apiService})
      : _apiService = apiService ?? ApiService() {
    _initListeners();
  }

  void _initListeners() {
    _isOnline = true;
    _connectionSub = _apiService.connectionStatusStream.listen((online) {
      if (_isOnline != online) {
        _isOnline = online;
        notifyListeners();
      }
    });

    _authSub = _apiService.authStateStream.listen((user) {
      notifyListeners();
    });
  }

  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;
  bool get isOnline => _isOnline;
  UserModel? get currentUser => _apiService.currentUser;
  bool get isAuthenticated => _apiService.isAuthenticated;
  bool get isGuest => _apiService.isGuest;
  String get baseUrl => _apiService.baseUrl;
  ApiService get apiService => _apiService;

  void clearError() {
    _errorMessage = null;
    notifyListeners();
  }

  void updateBaseUrl(String newUrl, {String activeNetworkId = 'all'}) {
    _apiService.baseUrl = newUrl;
    _apiService.connectWebSocket(activeNetworkId);
    notifyListeners();
  }

  Future<bool> login(String email, String password) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      final res = await _apiService.login(email, password);
      _isLoading = false;
      if (res['success'] == true) {
        notifyListeners();
        return true;
      } else {
        _errorMessage = res['message'] ?? 'Login failed';
        notifyListeners();
        return false;
      }
    } catch (e) {
      _isLoading = false;
      _errorMessage = 'An unexpected error occurred: $e';
      notifyListeners();
      return false;
    }
  }

  Future<bool> register(String fullName, String email, String password) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      final res = await _apiService.register(fullName, email, password);
      _isLoading = false;
      if (res['success'] == true) {
        notifyListeners();
        return true;
      } else {
        _errorMessage = res['message'] ?? 'Registration failed';
        notifyListeners();
        return false;
      }
    } catch (e) {
      _isLoading = false;
      _errorMessage = 'An unexpected error occurred: $e';
      notifyListeners();
      return false;
    }
  }

  void loginAsGuest() {
    _apiService.loginAsGuest();
    notifyListeners();
  }

  void logout() {
    _apiService.logout();
    notifyListeners();
  }

  @override
  void dispose() {
    _connectionSub?.cancel();
    _authSub?.cancel();
    super.dispose();
  }
}
