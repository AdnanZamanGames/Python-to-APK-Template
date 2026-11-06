BLOCKY PLATFORMER - UNITY ADS ANDROID PROJECT STARTER
====================================================

WHAT IS INCLUDED
- main.py: latest available Blocky Platformer source (2026-11-06 09:02 UTC)
- android_src/.../UnityAdsHelper.java: Java bridge for Unity Ads Android SDK 4.21.0
- buildozer.spec: Buildozer configuration with the Unity Ads Maven dependency
- offline_levels/: First_Falling.json and First_Landing.json from the project Library

UNITY ADS SETTINGS ALREADY INSERTED
- Android Game ID: 800427297
- Rewarded placement: BP_Rewarded_Android
- Interstitial placement: BP_Interstitial_Android
- Test mode: ON in Python and expected to be ON in the Unity Dashboard
- Reward rule already present in main.py: double earned coins; 150 bonus coins when the base reward is zero
- Interstitial rule already present: 20% chance on skip after community/offline level completion

IMPORTANT LIMITATIONS / BEFORE BUILDING
1. This is a source project starter, not a tested APK/AAB. It has not been compiled on your Colab runtime or tested on a phone.
2. The buildozer.spec uses the previously used Android package identity org.adnanzamangames.platformer to avoid silently creating a new app identity. If your current project uses a different package ID, the Java package folder and package.name/domain must be changed to match before building.
3. The project Library did not contain your buildozer.spec, icon.png, music, all level assets, or a complete Colab project folder. Add your current icon/assets if you use them. The app source itself references the app's own offline-level directory and handles it if empty.
4. Keep Unity Dashboard test mode ON. Unity's native SDK test flag is also ON. Do not change either to live mode until the app is approved and you're ready to release.
5. Unity's current SDK documentation requires user consent configuration before or during SDK initialization where applicable. This starter does not yet include a full consent/UMP flow. Before production release, add a consent flow suitable for your target audience and regions, and verify your Play Console Data safety / Families declarations.
6. This integration is direct Unity Ads (not Unity LevelPlay or AdMob mediation).
7. Do not add the old AdMob Java helper; this project uses UnityAdsHelper.

COLAB STEPS
1. Upload and extract this ZIP in Colab.
2. Open the extracted Blocky_Platformer_UnityAds folder.
3. Confirm buildozer.spec matches the package ID of your existing app.
4. Run: buildozer android debug
5. Check the complete build log for Java/Gradle errors. Install the APK and test only with test mode enabled.

If the build fails, send the first meaningful error block (not just the final BUILD FAILED line).

OFFICIAL UNITY DOCUMENTATION
- Android SDK integration: https://docs.unity.com/en-us/ads-android/4.21.0/sdk-integration
- Test integration: https://docs.unity.com/en-us/ads-android/4.21.0/sdk-integration/test-integration
