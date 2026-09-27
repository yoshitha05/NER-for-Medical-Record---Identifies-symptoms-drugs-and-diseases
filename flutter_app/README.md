# NER in Medical Records: Flutter app

Features: paste text · upload `.txt` `.pdf` `.docx` `.png` `.jpg` · Clear.

## Setup

```bash
# 1. Create the Flutter project (from the repo's top folder)
flutter create --org com.yoshitha --project-name medical_ner_app flutter_app
cd flutter_app

# 2. Add the packages
flutter pub add http file_picker

# 3. Copy lib/main.dart and lib/ner_api.dart from this folder into lib/
# 4. Copy the background image
mkdir -p assets && cp ../WApp/frontend/public/Med.webp assets/background.webp
```

In `pubspec.yaml`, under `flutter:`, add the asset:

```yaml
flutter:
  uses-material-design: true
  assets:
    - assets/background.webp
```

### Platform settings

**Android**: `android/app/src/main/AndroidManifest.xml`, just above `<application`:

```xml
<uses-permission android:name="android.permission.INTERNET" />
```

## Run

```bash
flutter run -d chrome      # quickest: runs in the browser, no emulator needed
flutter run                # on a connected Android phone or emulator
```

The first request after the Space has been idle can take up to a minute while it wakes up.