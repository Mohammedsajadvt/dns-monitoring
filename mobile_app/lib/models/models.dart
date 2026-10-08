class UserModel {
  final String id;
  final String email;
  final String fullName;
  final String role;
  final DateTime createdAt;

  UserModel({
    required this.id,
    required this.email,
    required this.fullName,
    required this.role,
    required this.createdAt,
  });

  factory UserModel.fromJson(Map<String, dynamic> json) {
    return UserModel(
      id: json['id'] ?? json['user_id'] ?? '',
      email: json['email'] ?? '',
      fullName: json['full_name'] ?? 'Administrator',
      role: json['role'] ?? 'admin',
      createdAt: DateTime.tryParse(json['created_at'] ?? '') ?? DateTime.now(),
    );
  }

  Map<String, dynamic> toJson() => {
    'id': id,
    'email': email,
    'full_name': fullName,
    'role': role,
    'created_at': createdAt.toIso8601String(),
  };
}

class AuthResponse {
  final String accessToken;
  final String tokenType;
  final UserModel user;

  AuthResponse({
    required this.accessToken,
    required this.tokenType,
    required this.user,
  });

  factory AuthResponse.fromJson(Map<String, dynamic> json) {
    return AuthResponse(
      accessToken: json['access_token'] ?? '',
      tokenType: json['token_type'] ?? 'bearer',
      user: UserModel.fromJson(json['user'] ?? {}),
    );
  }
}

class NetworkModel {
  final String networkId;
  final String name;
  final String location;
  final String description;
  final String subnet;
  final int deviceCount;
  final bool gatewayOnline;

  NetworkModel({
    required this.networkId,
    required this.name,
    required this.location,
    required this.description,
    required this.subnet,
    required this.deviceCount,
    required this.gatewayOnline,
  });

  factory NetworkModel.fromJson(Map<String, dynamic> json) {
    return NetworkModel(
      networkId: json['network_id'] ?? '',
      name: json['name'] ?? 'Unnamed Network',
      location: json['location'] ?? '',
      description: json['description'] ?? '',
      subnet: json['subnet'] ?? '',
      deviceCount: json['device_count'] ?? 0,
      gatewayOnline: json['gateway_online'] ?? false,
    );
  }
}

class DeviceModel {
  final String networkId;
  final String ip;
  final String mac;
  final String hostname;
  final String friendlyName;
  final String deviceType;
  final String vendor;
  final DateTime firstSeen;
  final DateTime lastSeen;
  final bool isOnline;
  final bool isBlocked;
  final int totalQueries;

  DeviceModel({
    required this.networkId,
    required this.ip,
    required this.mac,
    required this.hostname,
    required this.friendlyName,
    required this.deviceType,
    required this.vendor,
    required this.firstSeen,
    required this.lastSeen,
    required this.isOnline,
    required this.isBlocked,
    required this.totalQueries,
  });

  factory DeviceModel.fromJson(Map<String, dynamic> json) {
    return DeviceModel(
      networkId: json['network_id'] ?? '',
      ip: json['ip'] ?? '',
      mac: json['mac'] ?? 'Unknown',
      hostname: json['hostname'] ?? 'Device',
      friendlyName: json['friendly_name'] ?? json['hostname'] ?? json['ip'] ?? 'Device',
      deviceType: json['device_type'] ?? 'unknown',
      vendor: json['vendor'] ?? 'Unknown',
      firstSeen: DateTime.tryParse(json['first_seen'] ?? '') ?? DateTime.now(),
      lastSeen: DateTime.tryParse(json['last_seen'] ?? '') ?? DateTime.now(),
      isOnline: json['is_online'] ?? false,
      isBlocked: json['is_blocked'] ?? false,
      totalQueries: json['total_queries'] ?? 0,
    );
  }

  Map<String, dynamic> toJson() => {
    'network_id': networkId,
    'ip': ip,
    'mac': mac,
    'hostname': hostname,
    'friendly_name': friendlyName,
    'device_type': deviceType,
    'vendor': vendor,
    'first_seen': firstSeen.toIso8601String(),
    'last_seen': lastSeen.toIso8601String(),
    'is_online': isOnline,
    'is_blocked': isBlocked,
    'total_queries': totalQueries,
  };

  DeviceModel copyWith({
    String? networkId,
    String? ip,
    String? mac,
    String? hostname,
    String? friendlyName,
    String? deviceType,
    String? vendor,
    DateTime? firstSeen,
    DateTime? lastSeen,
    bool? isOnline,
    bool? isBlocked,
    int? totalQueries,
  }) {
    return DeviceModel(
      networkId: networkId ?? this.networkId,
      ip: ip ?? this.ip,
      mac: mac ?? this.mac,
      hostname: hostname ?? this.hostname,
      friendlyName: friendlyName ?? this.friendlyName,
      deviceType: deviceType ?? this.deviceType,
      vendor: vendor ?? this.vendor,
      firstSeen: firstSeen ?? this.firstSeen,
      lastSeen: lastSeen ?? this.lastSeen,
      isOnline: isOnline ?? this.isOnline,
      isBlocked: isBlocked ?? this.isBlocked,
      totalQueries: totalQueries ?? this.totalQueries,
    );
  }
}

class DNSLogModel {
  final String id;
  final DateTime timestamp;
  final String networkId;
  final String clientIp;
  final String clientMac;
  final String clientName;
  final String domain;
  final String category;
  final String queryType;
  final String responseCode;
  final double responseTimeMs;
  final String action;
  final bool isThreat;
  final String? threatType;
  final String? threatSeverity;

  DNSLogModel({
    required this.id,
    required this.timestamp,
    required this.networkId,
    required this.clientIp,
    required this.clientMac,
    required this.clientName,
    required this.domain,
    required this.category,
    required this.queryType,
    required this.responseCode,
    required this.responseTimeMs,
    required this.action,
    required this.isThreat,
    this.threatType,
    this.threatSeverity,
  });

  factory DNSLogModel.fromJson(Map<String, dynamic> json) {
    return DNSLogModel(
      id: json['id'] ?? json['log_id'] ?? '',
      timestamp: DateTime.tryParse(json['timestamp'] ?? '') ?? DateTime.now(),
      networkId: json['network_id'] ?? '',
      clientIp: json['client_ip'] ?? '',
      clientMac: json['client_mac'] ?? 'Unknown',
      clientName: json['client_name'] ?? json['client_ip'] ?? 'Device',
      domain: json['domain'] ?? '',
      category: json['category'] ?? 'General',
      queryType: json['query_type'] ?? 'A',
      responseCode: json['response_code'] ?? 'NOERROR',
      responseTimeMs: (json['response_time_ms'] as num?)?.toDouble() ?? 0.0,
      action: json['action'] ?? 'FORWARDED',
      isThreat: json['is_threat'] ?? false,
      threatType: json['threat_type'],
      threatSeverity: json['threat_severity'],
    );
  }
}

class ThreatAlertModel {
  final String id;
  final String networkId;
  final DateTime timestamp;
  final String domain;
  final String clientIp;
  final String clientName;
  final String threatType;
  final String severity;
  final String details;
  final bool isResolved;

  ThreatAlertModel({
    required this.id,
    required this.networkId,
    required this.timestamp,
    required this.domain,
    required this.clientIp,
    required this.clientName,
    required this.threatType,
    required this.severity,
    required this.details,
    required this.isResolved,
  });

  factory ThreatAlertModel.fromJson(Map<String, dynamic> json) {
    return ThreatAlertModel(
      id: json['id'] ?? json['alert_id'] ?? '',
      networkId: json['network_id'] ?? '',
      timestamp: DateTime.tryParse(json['timestamp'] ?? '') ?? DateTime.now(),
      domain: json['domain'] ?? '',
      clientIp: json['client_ip'] ?? '',
      clientName: json['client_name'] ?? 'Device',
      threatType: json['threat_type'] ?? 'Threat',
      severity: json['severity'] ?? 'medium',
      details: json['details'] ?? '',
      isResolved: json['is_resolved'] ?? false,
    );
  }

  ThreatAlertModel copyWith({
    String? id,
    String? networkId,
    DateTime? timestamp,
    String? domain,
    String? clientIp,
    String? clientName,
    String? threatType,
    String? severity,
    String? details,
    bool? isResolved,
  }) {
    return ThreatAlertModel(
      id: id ?? this.id,
      networkId: networkId ?? this.networkId,
      timestamp: timestamp ?? this.timestamp,
      domain: domain ?? this.domain,
      clientIp: clientIp ?? this.clientIp,
      clientName: clientName ?? this.clientName,
      threatType: threatType ?? this.threatType,
      severity: severity ?? this.severity,
      details: details ?? this.details,
      isResolved: isResolved ?? this.isResolved,
    );
  }
}
