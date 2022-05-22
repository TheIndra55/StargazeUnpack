# Stargaze Framework Image viewer
# By TheIndra

from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("SF Compressed Image Container", ".pvrlzo")
    noesis.setHandlerTypeCheck(handle, checkTypeCompressed)
    noesis.setHandlerLoadRGBA(handle, loadImageCompressed)

    handle = noesis.register("SF Image Container", ".pvr")
    noesis.setHandlerTypeCheck(handle, checkType)
    noesis.setHandlerLoadRGBA(handle, loadImage)

    return 1

def checkTypeCompressed(data):
    bs = NoeBitStream(data)

    # seek to end of the file
    bs.seek(bs.getSize() - 8, NOESEEK_ABS)

    # check magic
    if bs.readUInt() != 2103577277:
        return 0
    
    return 1

def checkType(data):
    bs = NoeBitStream(data)

    bs.seek(44, NOESEEK_ABS)

    if bs.readUInt() != 559044176:
        return 0

    return 1

def loadImageCompressed(data, texList):
    bs = NoeBitStream(data)

    # seek to end of file and read out size
    bs.seek(bs.getSize() - 4, NOESEEK_ABS)
    outSize = bs.readUInt()

    bs.seek(0, NOESEEK_ABS)

    # decompress data
    compressed = bs.readBytes(bs.getSize() - 8)
    data = rapi.decompLZO(compressed, outSize)

    # continue with decompressed data
    return loadImage(data, texList)

def loadImage(data, texList):
    bs = NoeBitStream(data)
    bs.seek(4, NOESEEK_REL)

    height = bs.readUInt()
    width = bs.readUInt()
    bs.seek(4, NOESEEK_REL)
    format = bs.readUByte()
    bs.seek(3, NOESEEK_REL)
    size = bs.readUInt()

    print(format)

    # skip to image data
    bs.seek(52, NOESEEK_ABS)

    imageData = bs.readBytes(size)
    pixelType = noesis.NOESISTEX_RGBA32

    if format == 0:
        imageData = rapi.imageDecodeRaw(imageData, width, height, "b4g4r4a4")
    elif format == 5:
        imageData = rapi.imageDecodeRaw(imageData, width, height, "r8g8b8a8")
    elif format == 2:
        imageData = rapi.imageDecodeRaw(imageData, width, height, "b5g6r5")
    elif format == 32:
        pixelType == noesis.NOESISTEX_DXT1
    elif format == 34:
        pixelType == noesis.NOESISTEX_DXT3
    elif format == 36:
        pixelType = noesis.NOESISTEX_DXT5

    texList.append(NoeTexture("Image", width, height, imageData, pixelType))

    return 1
