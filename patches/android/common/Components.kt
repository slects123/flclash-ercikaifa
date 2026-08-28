package com.follow.clash.common

import android.content.ComponentName

object Components {
    /** Kotlin/Java 类所在包名（改 applicationId 后仍保持不变） */
    const val PACKAGE_NAME = "com.follow.clash"

    /**
     * Flutter MethodChannel 前缀，必须与 Dart `lib/common/constant.dart` 的
     * `packageName` 一致，否则会出现 MissingPluginException。
     */
    const val CHANNEL_PREFIX = "com.wzpxx.flclash.dev"

    val mainActivity =
        ComponentName(GlobalState.packageName, "${PACKAGE_NAME}.MainActivity")

    val quickActionActivity =
        ComponentName(GlobalState.packageName, "${PACKAGE_NAME}.QuickActionActivity")

    val serviceBroadcastReceiver =
        ComponentName(GlobalState.packageName, "${PACKAGE_NAME}.ServiceBroadcastReceiver")
}
