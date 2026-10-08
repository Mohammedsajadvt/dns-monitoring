import 'dart:async';
import 'dart:convert';
import 'dart:io' show Platform;
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import 'package:web_socket_channel/web_socket_channel.dart';
import '../models/models.dart';

class ApiService {
  static final ApiService _instance = ApiService._internal();
  factory ApiService() => _instance;

  String _baseUrl = 'http://127.0.0.1:8000';
  String get baseUrl => _baseUrl;

  set baseUrl(String url) {
    _baseUrl = url.trim().replaceAll(RegExp(r'/+$'), '');
    if (_activeNetworkId != null) {
      connectWebSocket(_activeNetworkId!);
    }
  }

  String? _token;
  UserModel? _currentUser;
  bool _isGuest = false;

  String? get token => _token;
  UserModel? get currentUser => _currentUser;
  bool get isAuthenticated => _token != null || _isGuest;
  bool get isGuest => _isGuest;

  WebSocketChannel? _wsChannel;
  String? _activeNetworkId;
  Timer? _reconnectTimer;
  Timer? _keepAliveTimer;

  final StreamController<DNSLogModel> _liveLogStream =
      StreamController<DNSLogModel>.broadcast();
  final StreamController<ThreatAlertModel> _liveThreatStream =
      StreamController<ThreatAlertModel>.broadcast();
  final StreamController<DeviceModel> _liveDeviceStream =
      StreamController<DeviceModel>.broadcast();
  final StreamController<bool> _connectionStatusStream =
      StreamController<bool>.broadcast();
  final StreamController<UserModel?> _authStateStream =
      StreamController<UserModel?>.broadcast();

  Stream<DNSLogModel> get liveLogStream => _liveLogStream.stream;
  Stream<ThreatAlertModel> get liveThreatStream => _liveThreatStream.stream;
  Stream<DeviceModel> get liveDeviceStream => _liveDeviceStream.stream;
  Stream<bool> get connectionStatusStream => _connectionStatusStream.stream;
  Stream<UserModel?> get authStateStream => _authStateStream.stream;

  ApiService._internal() {
    _initDefaultBaseUrl();
  }

  void _initDefaultBaseUrl() {
    if (kIsWeb) {
      _baseUrl = 'http://[IP_ADDRESS]';
    } else {
      try {
        if (Platform.isAndroid) {
          _baseUrl = 'http://[IP_ADDRESS]';
        } else {
          _baseUrl = 'http://[IP_ADDRESS]';
        }
      } catch (_) {
        _baseUrl = 'http://127.0.0.1:8000';
      }
    }
  }

  Map<String, String> _getHeaders() {
    final headers = {'Content-Type': 'application/json'};
    if (_token != null && _token!.isNotEmpty) {
      headers['Authorization'] = 'Bearer $_token';
    }
    return headers;
  }

  // --- Authentication Options (Option 1: Login, Option 2: Register, Option 3: Guest/Demo) ---

  Future<Map<String, dynamic>> login(String email, String password) async {
    try {
      final response = await http
          .post(
            Uri.parse('$_baseUrl/api/auth/login'),
            headers: {'Content-Type': 'application/json'},
            body: jsonEncode({
              'email': email.trim().toLowerCase(),
              'password': password,
            }),
          )
          .timeout(const Duration(seconds: 8));

      final data = jsonDecode(response.body);
      if (response.statusCode == 200) {
        final authResp = AuthResponse.fromJson(data);
        _token = authResp.accessToken;
        _currentUser = authResp.user;
        _isGuest = false;
        _authStateStream.add(_currentUser);
        return {'success': true, 'user': _currentUser};
      } else {
        return {
          'success': false,
          'message': data['detail'] ?? 'Invalid credentials'
        };
      }
    } catch (e) {
      return {
        'success': false,
        'message': 'Network error connecting to backend: $e'
      };
    }
  }

  Future<Map<String, dynamic>> register(
      String fullName, String email, String password) async {
    try {
      final response = await http
          .post(
            Uri.parse('$_baseUrl/api/auth/register'),
            headers: {'Content-Type': 'application/json'},
            body: jsonEncode({
              'full_name': fullName.trim(),
              'email': email.trim().toLowerCase(),
              'password': password,
              'role': 'admin'
            }),
          )
          .timeout(const Duration(seconds: 8));

      final data = jsonDecode(response.body);
      if (response.statusCode == 200) {
        final authResp = AuthResponse.fromJson(data);
        _token = authResp.accessToken;
        _currentUser = authResp.user;
        _isGuest = false;
        _authStateStream.add(_currentUser);
        return {'success': true, 'user': _currentUser};
      } else {
        return {
          'success': false,
          'message': data['detail'] ?? 'Registration failed'
        };
      }
    } catch (e) {
      return {
        'success': false,
        'message': 'Network error connecting to backend: $e'
      };
    }
  }

  void loginAsGuest() {
    _token = null;
    _isGuest = true;
    _currentUser = UserModel(
      id: 'guest_user',
      email: 'guest@netsentry.io',
      fullName: 'SecOps Guest',
      role: 'viewer',
      createdAt: DateTime.now(),
    );
    _authStateStream.add(_currentUser);
  }

  void logout() {
    _token = null;
    _currentUser = null;
    _isGuest = false;
    _authStateStream.add(null);
  }

  /// WebSocket Live connection
  void connectWebSocket(String networkId) {
    _activeNetworkId = networkId;
    _reconnectTimer?.cancel();
    _keepAliveTimer?.cancel();

    try {
      _wsChannel?.sink.close();
    } catch (_) {}

    final channelId = networkId.isEmpty ? 'all' : networkId;
    final wsUrl =
        '${_baseUrl.replaceFirst(RegExp(r'^http'), 'ws')}/ws/$channelId';

    try {
      _wsChannel = WebSocketChannel.connect(Uri.parse(wsUrl));
      _connectionStatusStream.add(true);

      _wsChannel!.stream.listen(
        (message) {
          try {
            final data = jsonDecode(message);
            final event = data['event'];
            final payload = data['data'];

            if (event == 'dns_query') {
              _liveLogStream.add(DNSLogModel.fromJson(payload));
            } else if (event == 'threat_alert') {
              _liveThreatStream.add(ThreatAlertModel.fromJson(payload));
            } else if (event == 'device_update') {
              _liveDeviceStream.add(DeviceModel.fromJson(payload));
            }
          } catch (e) {
            debugPrint('[WS Decode Error]: $e');
          }
        },
        onDone: () {
          _connectionStatusStream.add(false);
          _scheduleReconnect();
        },
        onError: (err) {
          _connectionStatusStream.add(false);
          _scheduleReconnect();
        },
      );

      _keepAliveTimer = Timer.periodic(const Duration(seconds: 25), (_) {
        try {
          _wsChannel?.sink.add('ping');
        } catch (_) {}
      });
    } catch (e) {
      _connectionStatusStream.add(false);
      _scheduleReconnect();
    }
  }

  void _scheduleReconnect() {
    _reconnectTimer?.cancel();
    _reconnectTimer = Timer(const Duration(seconds: 3), () {
      if (_activeNetworkId != null) {
        connectWebSocket(_activeNetworkId!);
      }
    });
  }

  // --- RESTful Endpoints with Auth Header ---

  Future<List<NetworkModel>> getNetworks() async {
    try {
      final response = await http
          .get(Uri.parse('$_baseUrl/api/networks'), headers: _getHeaders())
          .timeout(const Duration(seconds: 6));
      if (response.statusCode == 200) {
        final List data = jsonDecode(response.body);
        return data.map((json) => NetworkModel.fromJson(json)).toList();
      }
    } catch (e) {
      debugPrint('getNetworks error: $e');
    }
    return [];
  }

  Future<NetworkModel?> autoDetectNetwork() async {
    try {
      final response = await http
          .post(Uri.parse('$_baseUrl/api/networks/auto-detect'),
              headers: _getHeaders())
          .timeout(const Duration(seconds: 6));
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return NetworkModel.fromJson(data);
      }
    } catch (e) {
      debugPrint('autoDetectNetwork error: $e');
    }
    return null;
  }

  Future<List<DeviceModel>> getDevices({String? networkId}) async {
    try {
      final url = networkId != null && networkId != 'all'
          ? '$_baseUrl/api/devices?network_id=$networkId'
          : '$_baseUrl/api/devices';
      final response = await http
          .get(Uri.parse(url), headers: _getHeaders())
          .timeout(const Duration(seconds: 6));
      if (response.statusCode == 200) {
        final List data = jsonDecode(response.body);
        return data.map((json) => DeviceModel.fromJson(json)).toList();
      }
    } catch (e) {
      debugPrint('getDevices error: $e');
    }
    return [];
  }

  Future<bool> updateDevice(String networkId, String ip, String friendlyName,
      String deviceType) async {
    try {
      final response = await http
          .put(
            Uri.parse('$_baseUrl/api/devices/$networkId/$ip'),
            headers: _getHeaders(),
            body: jsonEncode({
              'friendly_name': friendlyName,
              'device_type': deviceType,
            }),
          )
          .timeout(const Duration(seconds: 6));
      return response.statusCode == 200;
    } catch (e) {
      debugPrint('updateDevice error: $e');
      return false;
    }
  }

  Future<List<DNSLogModel>> getLogs({
    String? networkId,
    int limit = 100,
    String? domain,
    String? category,
  }) async {
    try {
      var url = '$_baseUrl/api/logs?limit=$limit';
      if (networkId != null && networkId != 'all') {
        url += '&network_id=$networkId';
      }
      if (domain != null && domain.isNotEmpty) url += '&domain=$domain';
      if (category != null && category != 'all') url += '&category=$category';

      final response = await http
          .get(Uri.parse(url), headers: _getHeaders())
          .timeout(const Duration(seconds: 6));
      if (response.statusCode == 200) {
        final List data = jsonDecode(response.body);
        return data.map((json) => DNSLogModel.fromJson(json)).toList();
      }
    } catch (e) {
      debugPrint('getLogs error: $e');
    }
    return [];
  }

  Future<List<ThreatAlertModel>> getThreatAlerts({String? networkId}) async {
    try {
      final url = networkId != null && networkId != 'all'
          ? '$_baseUrl/api/threats/alerts?network_id=$networkId'
          : '$_baseUrl/api/threats/alerts';
      final response = await http
          .get(Uri.parse(url), headers: _getHeaders())
          .timeout(const Duration(seconds: 6));
      if (response.statusCode == 200) {
        final List data = jsonDecode(response.body);
        return data.map((json) => ThreatAlertModel.fromJson(json)).toList();
      }
    } catch (e) {
      debugPrint('getThreatAlerts error: $e');
    }
    return [];
  }

  Future<bool> resolveThreat(String alertId) async {
    try {
      final response = await http
          .post(Uri.parse('$_baseUrl/api/threats/alerts/$alertId/resolve'),
              headers: _getHeaders())
          .timeout(const Duration(seconds: 6));
      return response.statusCode == 200;
    } catch (e) {
      debugPrint('resolveThreat error: $e');
      return false;
    }
  }

  Future<Map<String, dynamic>> getAnalyticsSummary({String? networkId}) async {
    try {
      final url = networkId != null && networkId != 'all'
          ? '$_baseUrl/api/analytics/summary?network_id=$networkId'
          : '$_baseUrl/api/analytics/summary';
      final response = await http
          .get(Uri.parse(url), headers: _getHeaders())
          .timeout(const Duration(seconds: 6));
      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      }
    } catch (e) {
      debugPrint('getAnalyticsSummary error: $e');
    }
    return {
      'total_queries_today': 0,
      'active_devices_count': 0,
      'threats_blocked_today': 0,
      'top_domains': [],
      'query_timeline': [],
      'category_distribution': [],
    };
  }

  Future<void> triggerSimulation(String networkId, bool isThreat) async {
    final sampleDomain =
        isThreat ? 'paypa1-security-verify.com' : 'youtube.com';
    try {
      var targetNetId = networkId;
      if (targetNetId == 'all' || targetNetId.isEmpty) {
        final nets = await getNetworks();
        targetNetId =
            nets.isNotEmpty ? nets.first.networkId : 'net_default_primary';
      }

      await http.post(
        Uri.parse('$_baseUrl/api/logs/ingest'),
        headers: _getHeaders(),
        body: jsonEncode({
          'network_id': targetNetId,
          'gateway_id': 'gw_mobile_client',
          'client_ip': '192.168.1.105',
          'client_mac': '3C:22:FB:4A:12:90',
          'client_hostname': 'iPhone-15-Pro',
          'domain': sampleDomain,
          'query_type': 'A',
          'response_code': 'NOERROR',
          'response_ips': ['142.250.190.46'],
          'response_time_ms': 14.5,
          'action': isThreat ? 'BLOCKED' : 'FORWARDED'
        }),
      );
    } catch (e) {
      debugPrint('triggerSimulation error: $e');
    }
  }
}
