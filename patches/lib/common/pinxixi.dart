import 'package:fl_clash/common/constant.dart';

/// 拼夕夕面板订阅：10 秒级实时同步（VPN 使用中也会按此间隔拉取）
class Pinxixi {
  static const pinxixiUpdateDuration = Duration(seconds: 10);

  /// 165 渔云实时同步状态（客户端可轮询 epoch）
  static const syncStatusUrls = [
    'http://165.99.42.254:8801/api/v1/pinxixi/sync/status',
    'http://ccjiasu.top:8801/api/v1/pinxixi/sync/status',
  ];

  static bool isSubscriptionUrl(String url) {
    final lower = url.toLowerCase();
    return lower.contains('slects.xyz') ||
        lower.contains('wzpxx') ||
        lower.contains('weixin/tui65743') ||
        lower.contains('ccjiasu.top') ||
        lower.contains('caicaijiasu.top') ||
        lower.contains('panel.wzpxx');
  }

  static Duration resolveAutoUpdateDuration(String url) =>
      isSubscriptionUrl(url) ? pinxixiUpdateDuration : defaultUpdateDuration;

  /// 到期或 1 小时内到期 → 强制刷新
  static bool needsExpireForceRefresh(int expireEpochSec) {
    if (expireEpochSec <= 0) return false;
    final now = DateTime.now().millisecondsSinceEpoch ~/ 1000;
    if (expireEpochSec <= now) return true;
    return (expireEpochSec - now) <= 3600;
  }
}
