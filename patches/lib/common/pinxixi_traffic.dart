import 'dart:convert';

import 'package:dio/dio.dart';
import 'package:fl_clash/common/pinxixi.dart';
import 'package:fl_clash/core/controller.dart';
import 'package:fl_clash/models/models.dart';

/// VPN 使用中：读取 Mihomo 会话累计流量并上报面板个人计费。
class PinxixiTrafficReporter {
  PinxixiTrafficReporter._();

  static DateTime? _lastReportAt;
  static const _minInterval = Duration(seconds: 10);

  static String? extractSubscribeToken(String url) {
    final text = url.trim();
    if (text.isEmpty) return null;
    final lower = text.toLowerCase();
    const mark = '/weixin/tui65743/gl0099gl/token=';
    final idx = lower.indexOf(mark);
    if (idx >= 0) {
      final rest = text.substring(idx + mark.length);
      final end = _tokenEnd(rest);
      final token = rest.substring(0, end).trim();
      if (token.isNotEmpty) return token;
    }
    final tokenIdx = lower.indexOf('token=');
    if (tokenIdx >= 0) {
      final rest = text.substring(tokenIdx + 6);
      final end = _tokenEnd(rest);
      final token = rest.substring(0, end).trim();
      if (token.isNotEmpty) return token;
    }
    return null;
  }

  static int _tokenEnd(String rest) {
    for (var i = 0; i < rest.length; i++) {
      final ch = rest[i];
      if (ch == '&' || ch == '?' || ch == '#' || ch == '/') return i;
    }
    return rest.length;
  }

  static String? trafficReportUrl(String subscriptionUrl) {
    final uri = Uri.tryParse(subscriptionUrl);
    if (uri == null || uri.host.isEmpty) return null;
    return '${uri.scheme}://${uri.host}${uri.hasPort ? ':${uri.port}' : ''}/api/v1/client/traffic/report';
  }

  static Future<void> tick({
    required bool vpnRunning,
    required List<Profile> profiles,
  }) async {
    if (!vpnRunning) return;
    final now = DateTime.now();
    if (_lastReportAt != null &&
        now.difference(_lastReportAt!) < _minInterval) {
      return;
    }

    Traffic total;
    try {
      total = await coreController.getTotalTraffic(true);
    } catch (_) {
      return;
    }

    var reported = false;
    for (final profile in profiles) {
      if (!Pinxixi.isSubscriptionUrl(profile.url)) continue;
      final token = extractSubscribeToken(profile.url);
      final reportUrl = trafficReportUrl(profile.url);
      if (token == null || reportUrl == null) continue;
      try {
        final dio = Dio(
          BaseOptions(
            connectTimeout: const Duration(seconds: 8),
            receiveTimeout: const Duration(seconds: 8),
            headers: {
              'Content-Type': 'application/json',
              'User-Agent': 'FlClash-Pinxixi-Traffic/1.0',
            },
          ),
        );
        await dio.post(
          reportUrl,
          data: jsonEncode({
            'token': token,
            'up': total.up,
            'down': total.down,
          }),
        );
        reported = true;
      } catch (_) {
        // ignore single profile failure
      }
    }
    if (reported) {
      _lastReportAt = now;
    }
  }
}
