[app]

# Application
title = Blocky Platformer
package.name = platformer
package.domain = org.adnanzamangames

# Source files
source.dir = .
source.include_exts = py,kv,png,jpg,jpeg,json,atlas,ttf,wav,mp3,ogg
source.include_patterns = offline_levels/*

version = 1.0.0

# Python dependencies
requirements = python3,kivy,requests,pyjnius

# Display
orientation = landscape
fullscreen = 1

# Android build settings
android.api = 35
android.minapi = 24
android.archs = arm64-v8a,armeabi-v7a

# Permissions
android.permissions = INTERNET,ACCESS_NETWORK_STATE

# AndroidX
android.enable_androidx = True

# Unity Ads
android.gradle_dependencies = com.unity3d.ads:unity-ads:4.21.0

# Java bridge
android.add_src = android_src

[buildozer]

log_level = 2
warn_on_root = 1
