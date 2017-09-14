export P4A_RELEASE_KEYSTORE=keystore/terawatt.keystore
export P4A_RELEASE_KEYSTORE_PASSWD=aleravershon
export P4A_RELEASE_KEYALIAS_PASSWD=aleravershon
export P4A_RELEASE_KEYALIAS=terawatt

mkdir keystores
keytool -genkey -v -keystore ./keystores/terawatt.keystore -alias terawatt -keyalg RSA -keysize 2048 -validity 10000

