VERSION=$(grep __version__ main.py | cut -c 16-18)

rm bin/Terawatt.apk
rm -rf terawatt_model
cp -rf ../terawatt_model .
buildozer android_new release 

cd ..

jarsigner -verbose -sigalg SHA1withRSA -digestalg SHA1 -keystore ./keystores/terawatt.keystore ./terawatt_app/bin/Terawatt-$VERSION-release-unsigned.apk terawatt

~/.buildozer/android/platform/android-sdk-20/build-tools/23.0.1/zipalign -v 4 ./terawatt_app/bin/Terawatt-$VERSION-release-unsigned.apk ./terawatt_app/bin/Terawatt.apk

