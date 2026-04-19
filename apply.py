############################
# Portal 2 Color Kit       #
#   by Lennektro v1.0 2026 #
############################

import os
import shutil

from PIL import Image

import srctools.vtf as vtf
import srctools.vpk as vpk

from typing import Final
from types import SimpleNamespace
from collections import namedtuple

import configparser
import mmap
import re


# helpers for managing paths
def _ensureEndswith(string, token):
    return string if string.endswith(token) else string + token
    
def _parentDirs(path, steps):
    return path.rsplit('/', steps + (1 if path.endswith('/') else 0))[0] + '/'


# byte helpers
def b_encodeInt(integer): return int(integer).to_bytes(16, 'little')
def b_decodeInt(data): return int.from_bytes(data, 'little')


# locate the script dir
SCRIPT_DIR: Final = _ensureEndswith(os.getcwd().replace('\\', '/'), '/')


# handle the options file
OPTIONS_FILE: Final = SCRIPT_DIR + "options.ini"

if not os.path.exists(OPTIONS_FILE):
    print("Error: No options file found, exiting...")
    exit(-1)

def _cfgColor(obj):
    try:
        r, g, b = map(int, str(obj).split(','))
        return (r, g, b)
    except:
        try:
            return (int(obj[0:2], 16), int(obj[2:4], 16), int(obj[4:6], 16))
        except:
            return None
        
def _cfgInt(obj):
    try:
        val = int(obj)
        return val
    except:
        return None

def _cfgBool(obj):
    try:
        return str(obj) == "true"
    except:
        return False
        
cfg = configparser.ConfigParser()
cfg.read(OPTIONS_FILE)

options = SimpleNamespace()

options.PRIMARY_COLOR = _cfgColor(cfg['ColorsSingleplayer']['Primary'])
options.SECONDARY_COLOR = _cfgColor(cfg['ColorsSingleplayer']['Secondary'])

options.DLC_FOLDER = _cfgInt(cfg['Files']['DlcFolder'])
options.NO_CLIENT_PATCHING = _cfgBool(cfg['Files']['NoClientPatching'])

options.atlas = SimpleNamespace()
options.atlas.PRIMARY = _cfgColor(cfg['ColorsAtlas']['Primary'])
options.atlas.SECONDARY = _cfgColor(cfg['ColorsAtlas']['Secondary'])

options.pbody = SimpleNamespace()
options.pbody.PRIMARY = _cfgColor(cfg['ColorsPBody']['Primary'])
options.pbody.SECONDARY = _cfgColor(cfg['ColorsPBody']['Secondary'])

if options.DLC_FOLDER is None:
    print("Error: No valid dlc folder id specified, exiting...")
    exit(-2)


# figure out all relevant paths
DLC_FOLDER: Final = _parentDirs(SCRIPT_DIR, 1) + "/portal2_dlc" + str(options.DLC_FOLDER) + "/"

if not os.path.exists(DLC_FOLDER):
    print("Error: Specified dlc folder does not seem to exist, exiting...")
    exit(-3)

VPK_CREATE_DIR: Final = SCRIPT_DIR + "pak01_dir/"
VPK_PORTALS_DIR: Final = VPK_CREATE_DIR + "materials/models/portals/"

REF_DIR: Final = SCRIPT_DIR + "ref/"

DUMMY_REF: Final = REF_DIR + "dummy-ref.png"
COLOR_REF: Final = REF_DIR + "portal-ref-color.png"
COLOR_DX8_REF: Final = REF_DIR + "portal-ref-color-dx8.png"

COOP_REF: Final = REF_DIR + "portalstaticoverlay_tinted.vmt"

PORTAL2_BIN: Final = _parentDirs(SCRIPT_DIR, 1) + "/portal2/bin/"

CLIENT_DLL: Final = PORTAL2_BIN + "client.dll"
CLIENT_SO: Final = PORTAL2_BIN + "linux32/client.so"

BIN_DIR: Final = SCRIPT_DIR + "bin/"

# definitions for patching the client
DefaultColor = namedtuple('DefaultColor', ['name', 'value', 'priority'])

DEFAULT_COLORS: Final = (
    DefaultColor("Primary Particle", "00 3C FF FF", ('first', 'first')),
    DefaultColor("Secondary Particle", "E9 4E 02 FF", ('first', 'first')),
    DefaultColor("Primary Util", "40 A0 FF FF", ('first', 'last')),
    DefaultColor("Secondary Util", "FF A0 20 FF", ('first', 'last'))
)

LINUX_PRIORITY: Final = 0
WINDOWS_PRIORITY: Final = 1

Patch = namedtuple('Patch', ['name', 'fingerprint', 'data'])

WINDOWS_PATCH: Final = Patch(
    "UtilPortalColor",
    "0F 84 82 00 00 00 8B 0D CC 9C 9A 10 E8 EF BA FE FF 84 C0 75 73",
    "90 90 90 90 90 90 ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? 90 90"
)

LINUX_PATCH: Final = Patch(
    "UtilPortalColor",
    "75 6F A1 AC 6A ?? 01 8D 14 5B 8D 44 90 6C F3 0F 10 48 08 F3 0F 10 05 F4 DC ?? 01 F3 0F 59 C8 F3 0F 2C D1 F3 0F 10 48 04 F3 0F 59 C8 F3 0F 59 00 C6 46 03 00 88 56 02 F3 0F 2C C9 F3 0F 2C C0 88 4E 01 88 06 83 C4 04 89 F0 5B 5E C2 04 00 8D 76 00 C7 06 FF FF FF FF 83 C4 04 89 F0 5B 5E C2 04 00 C7 06 F2 CA A7 FF 83 C4 04 89 F0 5B 5E C2 04 00 83 EC 0C FF 35 30 C4 ?? 01 E8 12 73 FE FF 83 C4 10 84 C0 0F 85 78 FF FF FF 8B 44 24 18 83 E8 02 83 F8 01 76",
    "EB ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? 90 90 90 90 90 90 ?? ?? ?? ?? 90 90 90 ?? ?? ?? 77"
)

DefaultColorCoop = namedtuple('DefaultColorCoop', ['name', 'value', 'fkey'])

DEFAULT_COOP_COLORS: Final = (
    DefaultColorCoop("Atlas Primary", "[0.125 0.500 0.824]", "--AtlasPrimary--"),
    DefaultColorCoop("Atlas Secondary", "[0.075 0.000 0.824]", "--AtlasSecondary--"),
    DefaultColorCoop("PBody Primary", "[1.000 0.705 0.125]", "--PBodyPrimary--"),
    DefaultColorCoop("PBody Secondary", "[0.225 0.010 0.010]", "--PBodySecondary--")
)


# texture assembly and vpk packing logic
def colorizeImage(img, color):
    img = img.convert('RGBA')
    r, g, b, a = img.split()
    r = r.point(lambda i: i * (color[0] / 255))
    g = g.point(lambda i: i * (color[1] / 255))
    b = b.point(lambda i: i * (color[2] / 255))
    result = Image.merge('RGBA', (b, g, r, a))
    return result
    
def createVtf(img, path, alpha):
    if not alpha: img = img.convert('RGB')
    if img.size[1] < 2: img = img.resize((img.size[0], 2), Image.Resampling.NEAREST) # dirty fix for the color scale because srctools fails to write a 1px high texture
    the_vtf = vtf.VTF(*img.size, fmt=vtf.ImageFormats.BGRA8888 if alpha else vtf.ImageFormats.BGR888, thumb_fmt=vtf.ImageFormats.DXT1, frames=1, version = (7, 4))
    the_vtf.get().copy_from(img.tobytes(), vtf.ImageFormats.BGRA8888 if alpha else vtf.ImageFormats.BGR888)
    the_vtf.flags |= vtf.VTFFlags.NO_LOD
    the_vtf.flags |= vtf.VTFFlags.NO_MIP
    the_vtf.flags |= vtf.VTFFlags.PWL_CORRECTED
    the_vtf.flags |= vtf.VTFFlags.CLAMP_T
    the_vtf.flags |= vtf.VTFFlags.CLAMP_S
    if alpha: the_vtf.flags |= vtf.VTFFlags.EIGHTBITALPHA
    with open(path, 'wb') as out: the_vtf.save(out)
    
def createVpk(folder, target):
    the_vpk = vpk.VPK(dir_file=target, mode='w', version=1)
    the_vpk.add_folder(folder)
    the_vpk.write_dirfile()
    
def generateTextures(color_name, color):
    files = [
        VPK_PORTALS_DIR + "dummy-" + color_name + ".vtf",
        VPK_PORTALS_DIR + "portal-" + color_name + "-color.vtf",
        VPK_PORTALS_DIR + "portal-" + color_name + "-color-dx8.vtf"
    ]
    if color is None:
        for f in files: 
            if os.path.exists(f): os.remove(f)
        return
    createVtf(colorizeImage(Image.open(DUMMY_REF), color), files[0], True)
    createVtf(colorizeImage(Image.open(COLOR_REF), color), files[1], False)
    createVtf(colorizeImage(Image.open(COLOR_DX8_REF), color), files[2], True)

def generateCoopFile():
    lines = None
    with open(COOP_REF, 'r') as f:
        lines = f.readlines()
    colors = (
        options.atlas.PRIMARY,
        options.atlas.SECONDARY,
        options.pbody.PRIMARY,
        options.pbody.SECONDARY
    )
    modified_lines = []
    for line in lines:
        for i, dcolor in enumerate(DEFAULT_COOP_COLORS):
            line = line.replace(dcolor.fkey, dcolor.value if colors[i] is None else f"[{(colors[i][0] / 255.0)} {colors[i][1] / 255.0} {colors[i][2] / 255.0}]")
        modified_lines.append(line)
    with open(VPK_PORTALS_DIR + "portalstaticoverlay_tinted.vmt", 'w') as f:
        f.writelines(modified_lines)
    
def createTheVpk():
    with os.scandir(DLC_FOLDER) as d: 
        for f in d: 
            if f.name.endswith(".vpk"): os.remove(f.path)
    os.makedirs(VPK_PORTALS_DIR, exist_ok=True)
    generateTextures("blue", options.PRIMARY_COLOR)
    generateTextures("orange", options.SECONDARY_COLOR)
    generateCoopFile()
    createVpk(VPK_CREATE_DIR, DLC_FOLDER + "pak01_dir.vpk")
    shutil.rmtree(VPK_CREATE_DIR)
    
def strlzColor(color):
    return "'default'" if color is None else f"'{color[0]}, {color[1]}, {color[2]}'"


# client patching logic
def locateColorSeq(mm, pattern, priority):
    b = bytes.fromhex(pattern.replace(' ', ''))
    return mm.find(b) if priority == 'first' else mm.rfind(b)

def locatePatchSeq(mm, pattern):
    reg = b"".join(b"." if t in '??' else re.escape(bytes.fromhex(t)) for t in pattern.split())
    m = re.search(reg, mm, re.DOTALL)
    return m.start() if m else -1

def isLibPatched(mm, patch):
    return locatePatchSeq(mm, ' '.join(o if p == '??' else p for o, p in zip(patch.fingerprint.split(), patch.data.split()))) != -1

def findLibOffsets(lib_name, mm, patches, os_priority):
    color_offsets = [-1] * len(DEFAULT_COLORS)
    patch_offsets = [-1] * len(patches)
            
    for i, color in enumerate(DEFAULT_COLORS):
        color_offsets[i] = locateColorSeq(mm, color.value, color.priority[os_priority])
        print(f" c {color_offsets[i]} --> Found match for color '{color.name}' with priority '{color.priority[os_priority]}'" if color_offsets[i] != -1 else f"!!! Failed to find match for color '{color.name}'")
        
    for i, patch in enumerate(patches):
        patch_offsets[i] = locatePatchSeq(mm, patch.fingerprint)
        print(f" p {patch_offsets[i]} --> Found patch fingerprint {patch.fingerprint}" if patch_offsets[i] != -1 else f"!!! Failed to find fingerprint for {patch.fingerprint}")
    
    return SimpleNamespace(
        colors = color_offsets,
        patches = patch_offsets
    )

def writeOffsetsFile(lib_name, type, offsets):
    fb = bytearray()
    for offset in offsets: 
        fb.extend(b_encodeInt(offset))
    with open(BIN_DIR + lib_name + "-" + type + ".offsets", 'wb') as f: f.write(fb)

def readOffsetsFile(lib_name, type):
    file = BIN_DIR + lib_name + "-" + type + ".offsets"
    if not os.path.exists(file): return None
    offsets = []
    with open(file, 'rb') as f:
        while chunck := f.read(16):
            if len(chunck) < 16: break
            offsets.append(b_decodeInt(chunck))
    return offsets

def applyPatchSeq(mm, offset, pattern):
    for i, token in enumerate(pattern.split()):
        if token == '??': continue
        mm[offset + i] = int(token, 16)

def writeColorSeq(mm, offset, color, default_color):
    wcolor = tuple(int(t, 16) for t in default_color.value.split()[:3]) if color is None else color
    for i, val in enumerate(wcolor): mm[offset + i] = val
    return wcolor
        
def processLib(lib, patches, os_priority):
    lib_name = lib.rsplit('/', 1)[-1]
    if not os.path.exists(lib):
        print(f"Failed to locate {lib_name}, skipping...")
        return
    apply_patches = False
    with open(lib, 'r+b') as f:
        mm_writable = False
        mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
        if not isLibPatched(mm, patches[0]):
            print(f"Analysing {lib_name}...")
            offsets = findLibOffsets(lib_name, mm, patches, os_priority)
            if -1 in offsets.patches:
                print(f"!!! Failed to patch {lib_name}!")
                mm.close()
                return
            os.makedirs(BIN_DIR, exist_ok=True)
            print(f"Writing offsets file...")
            writeOffsetsFile(lib_name, 'colors', offsets.colors)
            print(f"Backing up {lib_name}...")
            shutil.copyfile(lib, BIN_DIR + lib_name)
            mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_WRITE)
            mm_writable = True
            print(f"Patching patches in {lib_name}...")
            for offset, patch in zip(offsets.patches, patches):
                print(f" wp {offset} --> Applying patch '{patch.name}'")
                applyPatchSeq(mm, offset, patch.data)
        if not mm_writable: mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_WRITE)
        offsets = readOffsetsFile(lib_name, 'colors')
        if offsets is None:
            print(f"!!! No valid offsets file present for {lib_name}!")
            m.close()
            return
        print(f"Patching colors in {lib_name}...")
        for i, offset in enumerate(offsets):
            wcolor = writeColorSeq(mm, offset, options.PRIMARY_COLOR if i % 2 == 0 else options.SECONDARY_COLOR, DEFAULT_COLORS[i])
            print(f" wc {offset} --> Writing '{str(wcolor)}' for '{DEFAULT_COLORS[i].name}'")
        mm.flush()
        mm.close()

def patchClient():
    processLib(CLIENT_SO, [LINUX_PATCH], LINUX_PRIORITY)
    processLib(CLIENT_DLL, [WINDOWS_PATCH], WINDOWS_PRIORITY)

# the main logic flow to apply the colors
def apply():
    print(f"Using dlc folder {options.DLC_FOLDER}")
    print(f"Applying sp colors for values PRIMARY: {strlzColor(options.PRIMARY_COLOR)} and SECONDARY: {strlzColor(options.SECONDARY_COLOR)}")
    print("Applying coop colors for values:")
    print(f" > Atlas Primary: {strlzColor(options.atlas.PRIMARY)}")
    print(f" > Atlas Secondary: {strlzColor(options.atlas.SECONDARY)}")
    print(f" > PBody Primary: {strlzColor(options.pbody.PRIMARY)}")
    print(f" > PBody Secondary: {strlzColor(options.pbody.SECONDARY)}")
    print("Generating and packing textures...")
    createTheVpk()
    if not options.NO_CLIENT_PATCHING:
        print("Running client patching routines...")
        patchClient()
    print("All done!")
    print()
    
apply()
