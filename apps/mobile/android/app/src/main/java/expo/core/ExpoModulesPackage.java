package expo.core;

import com.facebook.react.ReactPackage;
import com.facebook.react.bridge.NativeModule;
import com.facebook.react.bridge.ReactApplicationContext;
import com.facebook.react.uimanager.ViewManager;
import java.util.List;

// 兼容 EAS/Gradle 自动链接偶尔生成的旧 Expo 包路径。
public class ExpoModulesPackage implements ReactPackage {
  private final expo.modules.ExpoModulesPackage delegate = new expo.modules.ExpoModulesPackage();

  @Override
  public List<NativeModule> createNativeModules(ReactApplicationContext reactContext) {
    return delegate.createNativeModules(reactContext);
  }

  @Override
  @SuppressWarnings({"rawtypes", "unchecked"})
  public List<ViewManager> createViewManagers(ReactApplicationContext reactContext) {
    return (List<ViewManager>) (List<?>) delegate.createViewManagers(reactContext);
  }
}
