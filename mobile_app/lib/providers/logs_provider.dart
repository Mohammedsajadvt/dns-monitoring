import 'dart:async';
import 'package:flutter/foundation.dart';
import '../models/models.dart';
import '../services/api_service.dart';

class LogsProvider with ChangeNotifier {
  final ApiService _apiService;
  StreamSubscription<DNSLogModel>? _logSub;

  List<DNSLogModel> _logs = [];
  bool _isLoading = true;
  String _selectedCategory = 'all';
  String _searchQuery = '';

  final List<String> categories = const [
    'all',
    'Video Streaming',
    'Social Media',
    'Developer',
    'Search & Cloud',
    'Ads & Tracking',
    'Cryptomining',
    'Phishing',
    'Suspicious DGA',
  ];

  LogsProvider({ApiService? apiService})
      : _apiService = apiService ?? ApiService() {
    _initLiveListener();
  }

  List<DNSLogModel> get logs => _logs;
  bool get isLoading => _isLoading;
  String get selectedCategory => _selectedCategory;
  String get searchQuery => _searchQuery;

  void _initLiveListener() {
    _logSub = _apiService.liveLogStream.listen((log) {
      final matchesCat =
          _selectedCategory == 'all' || log.category == _selectedCategory;
      final q = _searchQuery.trim().toLowerCase();
      final matchesSearch = q.isEmpty ||
          log.domain.toLowerCase().contains(q) ||
          log.clientIp.toLowerCase().contains(q) ||
          log.clientName.toLowerCase().contains(q);

      if (matchesCat && matchesSearch) {
        _logs.insert(0, log);
        if (_logs.length > 200) {
          _logs.removeLast();
        }
        notifyListeners();
      }
    });
  }

  Future<void> fetchLogs({
    required String networkId,
    String? category,
    String? domain,
    bool showLoading = true,
  }) async {
    if (category != null) _selectedCategory = category;
    if (domain != null) _searchQuery = domain;

    if (showLoading) {
      _isLoading = true;
      notifyListeners();
    }

    try {
      final list = await _apiService.getLogs(
        networkId: networkId,
        limit: 100,
        category: _selectedCategory,
        domain: _searchQuery.isNotEmpty ? _searchQuery : null,
      );
      _logs = list;
    } catch (e) {
      debugPrint('[LogsProvider] fetchLogs error: $e');
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  void setCategory(String category, String networkId) {
    _selectedCategory = category;
    fetchLogs(networkId: networkId, category: category);
  }

  void setSearchQuery(String query, String networkId) {
    _searchQuery = query;
    fetchLogs(networkId: networkId, domain: query);
  }

  @override
  void dispose() {
    _logSub?.cancel();
    super.dispose();
  }
}
