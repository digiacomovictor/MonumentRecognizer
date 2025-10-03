[app]
# Basic app configuration
title = Monument Recognizer
package.name = monumentrecognizer
package.domain = com.monumentrecognizer
source.dir = .
version = 1.0.0

# Minimal requirements to test the build
requirements = python3,kivy==2.1.0

# Source files
source.include_exts = py,png,jpg,kv
source.exclude_exts = spec,pyc

# Android configuration - minimal and safe
android.api = 31
android.minapi = 21
android.sdk = 31
android.ndk = 25b
android.archs = arm64-v8a

# Basic permissions
android.permissions = INTERNET

# Private storage
android.private_storage = True

# Portrait orientation
orientation = portrait

# Force specific paths (will be added by workflow)
android.skip_update = True

[buildozer]
log_level = 2
warn_on_root = 1