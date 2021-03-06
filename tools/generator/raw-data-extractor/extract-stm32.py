
from pathlib import Path
from multiprocessing import Pool
import urllib.request
import zipfile
import shutil
import re
import io
import os

cubeurl = "https://www.st.com/content/st_com/en/products/development-tools/"\
		  "software-development-tools/stm32-software-development-tools/"\
		  "stm32-configurators-and-code-generators/stm32cubemx.html"

with urllib.request.urlopen(cubeurl) as response:
    html = response.read().decode("utf-8")
    dlurl = re.search(r'data-download-path="(/content/ccc/resource/.*?\.zip)"', html).group(1)
    dlurl = "https://www.st.com" + dlurl
    print("Downloading CubeMX...")
    print(dlurl)

shutil.rmtree("temp-stm32", ignore_errors=True)
with urllib.request.urlopen(dlurl) as content:
    z = zipfile.ZipFile(io.BytesIO(content.read()))
    item = [n for n in z.namelist() if ".exe" in n][0]
    print("Extracting SetupSTM32CubeMX.exe...")
    z = zipfile.ZipFile(io.BytesIO(z.read(item)))
    print("Extracting Core-Pack...")
    z.extract("resources/packs/pack-Core", "temp-stm32/")

print("Compiling IzPackDeserializer...")
Path("temp-stm32/bin/izpack_deserializer").mkdir(exist_ok=True, parents=True)
Path("temp-stm32/bin/com/izforge/izpack/api/data").mkdir(exist_ok=True, parents=True)
os.system("javac izpack/*.java")
shutil.move("izpack/IzPackDeserializer.class", "temp-stm32/bin/izpack_deserializer/")
for f in Path("izpack/").glob("*.class"):
	shutil.move(str(f), "temp-stm32/bin/com/izforge/izpack/api/data/")

print("Extracting Database...")
os.system("(cd temp-stm32/bin; java izpack_deserializer.IzPackDeserializer > /dev/null)")

print("Moving Database...")
shutil.rmtree("../raw-device-data/stm32-devices", ignore_errors=True)
Path("../raw-device-data/stm32-devices").mkdir(exist_ok=True, parents=True)
shutil.move("temp-stm32/output/db/mcu", "../raw-device-data/stm32-devices/")
shutil.move("temp-stm32/output/db/plugins", "../raw-device-data/stm32-devices/")

