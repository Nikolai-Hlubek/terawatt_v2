rm -rf terawatt_model
cp -rf ../terawatt_model .
buildozer android_new debug deploy run logcat
