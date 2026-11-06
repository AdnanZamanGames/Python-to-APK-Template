package org.adnanzamangames.platformer;

import android.app.Activity;
import android.util.Log;

import com.unity3d.ads.InitializationConfiguration;
import com.unity3d.ads.InitializationListener;
import com.unity3d.ads.UnityAds;
import com.unity3d.ads.UnityAdsError;
import com.unity3d.ads.InterstitialAd;
import com.unity3d.ads.RewardedAd;
import com.unity3d.ads.LoadConfiguration;
import com.unity3d.ads.ShowConfiguration;
import com.unity3d.ads.InterstitialLoadListener;
import com.unity3d.ads.RewardedLoadListener;
import com.unity3d.ads.InterstitialShowListener;
import com.unity3d.ads.RewardedShowListener;
import com.unity3d.ads.ShowFinishState;

import java.util.concurrent.atomic.AtomicInteger;

/**
 * Small Java bridge for the Python/Kivy app.
 * Event codes consumed by Python:
 * 1 = rewarded earned, 2 = rewarded closed without reward,
 * 3 = rewarded unavailable/failed, 4 = interstitial closed,
 * 5 = interstitial unavailable/failed.
 */
public final class UnityAdsHelper {
    private static final String TAG = "BlockyUnityAds";
    private static volatile UnityAdsHelper instance;

    private Activity activity;
    private String rewardedPlacement;
    private String interstitialPlacement;
    private volatile boolean initialized = false;
    private volatile RewardedAd rewardedAd;
    private volatile InterstitialAd interstitialAd;
    private final AtomicInteger eventCode = new AtomicInteger(0);

    private UnityAdsHelper() { }

    public static void initialize(Activity activity, String gameId,
                                  String rewardedPlacement, String interstitialPlacement,
                                  boolean testMode) {
        if (activity == null || gameId == null) return;
        UnityAdsHelper helper = new UnityAdsHelper();
        helper.activity = activity;
        helper.rewardedPlacement = rewardedPlacement;
        helper.interstitialPlacement = interstitialPlacement;
        instance = helper;

        activity.runOnUiThread(() -> {
            try {
                InitializationConfiguration config =
                    new InitializationConfiguration.Builder(gameId)
                        .withTestMode(testMode)
                        .build();
                InitializationListener listener = error -> {
                    if (error == null) {
                        helper.initialized = true;
                        helper.loadRewarded();
                        helper.loadInterstitial();
                        Log.i(TAG, "Unity Ads initialized");
                    } else {
                        helper.initialized = false;
                        Log.e(TAG, "Unity Ads initialization failed: " + error.getMessage());
                    }
                };
                UnityAds.initialize(config, listener);
            } catch (Throwable error) {
                Log.e(TAG, "Unity Ads initialization exception", error);
            }
        });
    }

    public static boolean isReady() {
        UnityAdsHelper helper = instance;
        return helper != null && helper.initialized;
    }

    public static int consumeEvent() {
        UnityAdsHelper helper = instance;
        return helper == null ? 0 : helper.eventCode.getAndSet(0);
    }

    private void loadRewarded() {
        if (!initialized || rewardedPlacement == null || rewardedPlacement.isEmpty()) return;
        LoadConfiguration config = new LoadConfiguration.Builder(rewardedPlacement).build();
        RewardedAd.load(config, (ad, error) -> {
            if (ad != null) {
                rewardedAd = ad;
                Log.i(TAG, "Rewarded ad loaded");
            } else {
                rewardedAd = null;
                Log.w(TAG, "Rewarded ad load failed: " + (error == null ? "unknown" : error.getMessage()));
            }
        });
    }

    private void loadInterstitial() {
        if (!initialized || interstitialPlacement == null || interstitialPlacement.isEmpty()) return;
        LoadConfiguration config = new LoadConfiguration.Builder(interstitialPlacement).build();
        InterstitialAd.load(config, (ad, error) -> {
            if (ad != null) {
                interstitialAd = ad;
                Log.i(TAG, "Interstitial ad loaded");
            } else {
                interstitialAd = null;
                Log.w(TAG, "Interstitial ad load failed: " + (error == null ? "unknown" : error.getMessage()));
            }
        });
    }

    public static void showRewarded() {
        UnityAdsHelper helper = instance;
        if (helper == null || !helper.initialized) {
            if (helper != null) helper.eventCode.set(3);
            return;
        }
        helper.activity.runOnUiThread(() -> {
            RewardedAd ad = helper.rewardedAd;
            if (ad == null) {
                helper.eventCode.set(3);
                helper.loadRewarded();
                return;
            }
            helper.rewardedAd = null;
            final boolean[] rewardEarned = { false };
            try {
                ad.show(new ShowConfiguration.Builder().build(), new RewardedShowListener() {
                    @Override public void onStarted(RewardedAd shownAd) { }
                    @Override public void onClicked(RewardedAd shownAd) { }
                    @Override public void onRewarded(RewardedAd shownAd) {
                        rewardEarned[0] = true;
                        helper.eventCode.set(1);
                    }
                    @Override public void onCompleted(RewardedAd shownAd, ShowFinishState state) {
                        if (!rewardEarned[0]) helper.eventCode.set(2);
                        helper.loadRewarded();
                    }
                    @Override public void onFailed(RewardedAd shownAd, UnityAdsError error) {
                        helper.eventCode.set(3);
                        helper.loadRewarded();
                    }
                });
            } catch (Throwable error) {
                Log.e(TAG, "Rewarded show failed", error);
                helper.eventCode.set(3);
                helper.loadRewarded();
            }
        });
    }

    public static void showInterstitial() {
        UnityAdsHelper helper = instance;
        if (helper == null || !helper.initialized) {
            if (helper != null) helper.eventCode.set(5);
            return;
        }
        helper.activity.runOnUiThread(() -> {
            InterstitialAd ad = helper.interstitialAd;
            if (ad == null) {
                helper.eventCode.set(5);
                helper.loadInterstitial();
                return;
            }
            helper.interstitialAd = null;
            try {
                ad.show(new ShowConfiguration.Builder().build(), new InterstitialShowListener() {
                    @Override public void onStarted(InterstitialAd shownAd) { }
                    @Override public void onClicked(InterstitialAd shownAd) { }
                    @Override public void onCompleted(InterstitialAd shownAd, ShowFinishState state) {
                        helper.eventCode.set(4);
                        helper.loadInterstitial();
                    }
                    @Override public void onFailed(InterstitialAd shownAd, UnityAdsError error) {
                        helper.eventCode.set(5);
                        helper.loadInterstitial();
                    }
                });
            } catch (Throwable error) {
                Log.e(TAG, "Interstitial show failed", error);
                helper.eventCode.set(5);
                helper.loadInterstitial();
            }
        });
    }
}
