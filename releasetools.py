import common
import re

def FullOTA_Assertions(info):
  AddBasebandAssertion(info, info.input_zip)
  return

def IncrementalOTA_Assertions(info):
  AddBasebandAssertion(info, info.input_zip)
  return

def FullOTA_InstallEnd(info):
  OTA_InstallEnd(info)
  return

def IncrementalOTA_InstallEnd(info):
  OTA_InstallEnd(info)
  return

def AddImage(info, basename, dest):
  name = basename
  path = "IMAGES/" + name
  if path not in info.input_zip.namelist():
    return

  data = info.input_zip.read(path)
  common.ZipWriteStr(info.output_zip, name, data)
  info.script.Print("Patching {} image unconditionally...".format(dest.split('/')[-1]))
  info.script.AppendExtra('package_extract_file("%s", "%s");' % (name, dest))

def OTA_InstallEnd(info):
  AddImage(info, "dtbo.img", "/dev/block/bootdevice/by-name/dtbo")
  AddImage(info, "vbmeta.img", "/dev/block/bootdevice/by-name/vbmeta")
  AddImage(info, "vbmeta_system.img", "/dev/block/bootdevice/by-name/vbmeta_system")
  return

def AddBasebandAssertion(info, input_zip):
  android_info = input_zip.open("OTA/android-info.txt")
  for line in android_info.readlines():
    m = re.search(r'require\s+version-baseband\s*-\s*(.+)', line.decode('utf-8'))
    if m:
      hwc, modem_version, firmware_version = re.split('[=,]', m.group(1).rstrip())
      if (len(hwc) and len(modem_version) and len(firmware_version)):
        cmd = 'assert(getprop("ro.boot.hwc") == "{0}" && (xiaomi.verify_baseband("{1}") == "1" || abort("ERROR: This package requires firmware from MIUI {2} or newer. Please upgrade firmware and retry!");) || true);'
        info.script.AppendExtra(cmd.format(hwc, modem_version, firmware_version))
  return
