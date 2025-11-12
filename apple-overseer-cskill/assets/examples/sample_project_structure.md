# Sample Apple Platform Project Structure

This document illustrates what a well-structured Apple platform project looks like that would pass the Apple Overseer validation.

## Example: Multi-Platform iOS/macOS App

```
MyAwesomeApp/
├── MyAwesomeApp.xcodeproj/          # Xcode project
│   ├── project.pbxproj
│   └── project.xcworkspace/
├── MyAwesomeApp.xcworkspace/        # Workspace (if using CocoaPods)
├── Package.swift                     # Swift Package Manager (alternative)
│
├── Shared/                           # Code shared across platforms
│   ├── Models/
│   │   ├── User.swift
│   │   └── AppData.swift
│   ├── ViewModels/
│   │   └── MainViewModel.swift
│   ├── Services/
│   │   ├── NetworkService.swift
│   │   └── DataService.swift
│   └── Utilities/
│       └── Extensions.swift
│
├── iOS/                              # iOS-specific code
│   ├── Views/
│   │   ├── ContentView.swift
│   │   └── SettingsView.swift
│   ├── ViewControllers/              # If using UIKit
│   │   └── MainViewController.swift
│   ├── Info.plist
│   └── MyAwesomeApp-iOS.entitlements
│
├── macOS/                            # macOS-specific code
│   ├── Views/
│   │   ├── ContentView.swift
│   │   └── PreferencesView.swift
│   ├── ViewControllers/              # If using AppKit
│   │   └── MainViewController.swift
│   ├── Info.plist
│   └── MyAwesomeApp-macOS.entitlements
│
├── Resources/                        # Shared resources
│   ├── Assets.xcassets/
│   │   ├── AppIcon.appiconset/
│   │   ├── Colors/
│   │   └── Images/
│   └── Localizable.strings
│
├── Tests/
│   ├── MyAwesomeAppTests/
│   │   ├── ModelTests.swift
│   │   └── ViewModelTests.swift
│   └── MyAwesomeAppUITests/
│       └── UITests.swift
│
├── Podfile                           # CocoaPods dependencies
├── Podfile.lock
├── Cartfile                          # Carthage dependencies (alternative)
│
├── README.md
├── LICENSE
└── PrivacyInfo.xcprivacy            # Privacy manifest (iOS 17+)
```

## Example: iOS-Only SwiftUI App

```
WeatherApp/
├── WeatherApp.xcodeproj/
├── Package.swift                     # Using SPM for dependencies
│
├── Sources/
│   ├── Models/
│   │   ├── Weather.swift
│   │   └── Location.swift
│   ├── Views/
│   │   ├── ContentView.swift
│   │   ├── WeatherDetailView.swift
│   │   └── SettingsView.swift
│   ├── ViewModels/
│   │   ├── WeatherViewModel.swift
│   │   └── LocationViewModel.swift
│   ├── Services/
│   │   ├── WeatherAPIService.swift
│   │   └── LocationService.swift
│   └── App/
│       └── WeatherApp.swift
│
├── Resources/
│   └── Assets.xcassets/
│       └── AppIcon.appiconset/
│
├── Tests/
│   └── WeatherAppTests/
│
├── Info.plist
├── WeatherApp.entitlements
├── README.md
└── PrivacyInfo.xcprivacy
```

## Example: macOS AppKit Application

```
DocumentEditor/
├── DocumentEditor.xcodeproj/
│
├── Sources/
│   ├── AppDelegate.swift
│   ├── Document.swift
│   ├── WindowController.swift
│   ├── ViewController.swift
│   │
│   ├── Models/
│   │   └── DocumentModel.swift
│   ├── Views/
│   │   └── EditorView.swift
│   └── Utilities/
│       └── FileManager+Extensions.swift
│
├── Resources/
│   ├── Assets.xcassets/
│   ├── MainMenu.xib
│   └── Document.xib
│
├── Info.plist
├── DocumentEditor.entitlements       # Must have sandboxing for distribution
└── README.md
```

## Key Elements for Passing Validation

### Foundation Inspector (Level 1)

**Required Elements**:
- ✓ Valid `.xcodeproj`, `.xcworkspace`, or `Package.swift`
- ✓ Build configuration (Podfile, Cartfile, or Package.swift dependencies)
- ✓ Well-organized directory structure
- ✓ Swift files with proper imports

**Best Practices**:
- Organized directories (Models, Views, Controllers/ViewModels)
- Separate platform-specific and shared code
- Limited force unwrapping in Swift code
- Remove debug print statements

### Platform Overseers (Level 2)

**iOS Requirements**:
- ✓ `import UIKit` or `import SwiftUI`
- ✓ Info.plist with CFBundleIdentifier
- ✓ Assets.xcassets with AppIcon
- ✓ Entitlements file (if using capabilities)

**macOS Requirements**:
- ✓ `import AppKit` / `import Cocoa` or `import SwiftUI`
- ✓ Info.plist with CFBundleIdentifier
- ✓ Assets.xcassets with AppIcon
- ✓ Entitlements with App Sandbox enabled (for distribution)

**iPadOS Requirements**:
- Similar to iOS, plus:
- ✓ Scene-based architecture (UISceneConfiguration)
- ✓ Size class handling for adaptive layouts
- ✓ Consider split view support

### Integration Coordinator (Level 3)

**Multi-Platform Projects**:

Proper conditional compilation:
```swift
#if os(iOS)
import UIKit
typealias PlatformViewController = UIViewController
#elseif os(macOS)
import AppKit
typealias PlatformViewController = NSViewController
#endif
```

Shared code organization:
```
Shared/
  ├── Models/          # Platform-agnostic data models
  ├── ViewModels/      # Business logic (if using MVVM)
  └── Services/        # API, networking, data services
```

Platform-specific code:
```
iOS/
  └── Views/           # iOS-specific UI
macOS/
  └── Views/           # macOS-specific UI
```

### Executive Overseer (Level 4)

**Quality Requirements**:
- ✓ No hardcoded API keys or credentials
- ✓ Use HTTPS for network calls
- ✓ Accessibility labels where appropriate
- ✓ Documentation (README.md)
- ✓ Privacy manifest (PrivacyInfo.xcprivacy) for iOS 17+
- ✓ Reasonable file sizes (< 500 lines average)
- ✓ Asset optimization (images < 5MB)

## Sample Package.swift (Multi-Platform)

```swift
// swift-tools-version: 5.9
import PackageDescription

let package = Package(
    name: "MyAwesomeApp",
    platforms: [
        .iOS(.v15),
        .macOS(.v12),
        .iPadOS(.v15)
    ],
    products: [
        .library(
            name: "MyAwesomeApp",
            targets: ["MyAwesomeApp"]
        ),
    ],
    dependencies: [
        .package(url: "https://github.com/example/SomePackage.git", .upToNextMajor(from: "1.0.0"))
    ],
    targets: [
        .target(
            name: "MyAwesomeApp",
            dependencies: ["SomePackage"]
        ),
        .testTarget(
            name: "MyAwesomeAppTests",
            dependencies: ["MyAwesomeApp"]
        ),
    ]
)
```

## Sample Info.plist (iOS)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleIdentifier</key>
    <string>com.example.myawesomeapp</string>
    <key>CFBundleName</key>
    <string>MyAwesomeApp</string>
    <key>CFBundleVersion</key>
    <string>1.0.0</string>
    <key>UIApplicationSceneManifest</key>
    <dict>
        <key>UIApplicationSupportsMultipleScenes</key>
        <true/>
    </dict>
    <key>NSPrivacyAccessedAPITypes</key>
    <array>
        <!-- Privacy manifest for iOS 17+ -->
    </array>
</dict>
</plist>
```

## Sample Entitlements (macOS)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>com.apple.security.app-sandbox</key>
    <true/>
    <key>com.apple.security.files.user-selected.read-write</key>
    <true/>
    <key>com.apple.security.network.client</key>
    <true/>
</dict>
</plist>
```

## Common Validation Issues and Fixes

### Issue: "No Xcode project found"
**Fix**: Ensure you have `.xcodeproj`, `.xcworkspace`, or `Package.swift` in the project root

### Issue: "No UIKit or SwiftUI imports detected"
**Fix**: Add `import UIKit` or `import SwiftUI` to your Swift files

### Issue: "Excessive force unwrapping"
**Fix**: Replace `!` with optional binding:
```swift
// Bad
let value = optional!

// Good
if let value = optional {
    // Use value
}

// Or
guard let value = optional else { return }
```

### Issue: "Multiple print statements"
**Fix**: Use proper logging:
```swift
import os.log

let logger = Logger(subsystem: "com.example.app", category: "networking")
logger.info("Request completed")
```

### Issue: "Mixed platform APIs without guards"
**Fix**: Use conditional compilation:
```swift
#if os(iOS)
import UIKit
let view = UIView()
#elseif os(macOS)
import AppKit
let view = NSView()
#endif
```

---

This structure ensures your project passes all Apple Overseer validation checkpoints and receives the stamp of approval!
