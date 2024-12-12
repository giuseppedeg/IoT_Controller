#!/usr/bin/env python
# SPDX-License-Identifier: MIT

import ctypes
import _ctypes
import comtypes
import comtypes.client
# uncomment this lines on first use and comment out the bad asserts
#comtypes.client.GetModule("portabledeviceapi.dll")
comtypes.client.GetModule("portabledevicetypes.dll")

#import comtypes.gen._1F001332_1A57_4934_BE31_AFFC99F4EE0A_0_1_0 as port #Some parameters need to be ['in', 'Out'] 
import comtypes.gen._2B00BA2F_E750_4BEB_9235_97142EDE1D3E_0_1_0 as types

import comtypes_gen._1F001332_1A57_4934_BE31_AFFC99F4EE0A_0_1_0 as port

WPD_OBJECT_NAME = comtypes.pointer(port._tagpropertykey())
WPD_OBJECT_NAME.contents.fmtid = comtypes.GUID(
    "{EF6B490D-5CD8-437A-AFFC-DA8B60EE4A3C}")
WPD_OBJECT_NAME.contents.pid = 4

WPD_OBJECT_ID = comtypes.pointer(port._tagpropertykey())
WPD_OBJECT_ID.contents.fmtid = comtypes.GUID(
    "{EF6B490D-5CD8-437A-AFFC-DA8B60EE4A3C}")
WPD_OBJECT_ID.contents.pid = 2

WPD_OBJECT_ORIGINAL_FILE_NAME = comtypes.pointer(port._tagpropertykey())
WPD_OBJECT_ORIGINAL_FILE_NAME.contents.fmtid = comtypes.GUID(
    "{EF6B490D-5CD8-437A-AFFC-DA8B60EE4A3C}")
WPD_OBJECT_ORIGINAL_FILE_NAME.contents.pid = 12

WPD_OBJECT_SIZE = comtypes.pointer(port._tagpropertykey())
WPD_OBJECT_SIZE.contents.fmtid = comtypes.GUID(
    "{EF6B490D-5CD8-437A-AFFC-DA8B60EE4A3C}")
WPD_OBJECT_SIZE.contents.pid = 11

WPD_OBJECT_PARENT_ID = comtypes.pointer(port._tagpropertykey())
WPD_OBJECT_PARENT_ID.contents.fmtid = comtypes.GUID(
    "{EF6B490D-5CD8-437A-AFFC-DA8B60EE4A3C}")
WPD_OBJECT_PARENT_ID.contents.pid = 3

WPD_OBJECT_CONTENT_TYPE = comtypes.pointer(port._tagpropertykey())
WPD_OBJECT_CONTENT_TYPE.contents.fmtid = comtypes.GUID(
    "{EF6B490D-5CD8-437A-AFFC-DA8B60EE4A3C}")
WPD_OBJECT_CONTENT_TYPE.contents.pid = 7

WPD_RESOURCE_DEFAULT = comtypes.pointer(port._tagpropertykey())
WPD_RESOURCE_DEFAULT.contents.fmtid = comtypes.GUID(
    "{E81E79BE-34F0-41BF-B53F-F1A06AE87842}")
WPD_RESOURCE_DEFAULT.contents.pid = 0


class PortableDeviceContent:
    def __init__(
            self,
            objectID,
            content,
            properties=None,
            propertiesToRead=None):
        self.objectID = objectID
        self.content = content
        self.name = None
        if properties:
            self.properties = properties
        else:
            self.properties = content.Properties()
        if propertiesToRead:
            self.propertiesToRead = propertiesToRead
        else:
            global WPD_OBJECT_NAME
            self.propertiesToRead = comtypes.client.CreateObject(
                types.PortableDeviceKeyCollection,
                clsctx=comtypes.CLSCTX_INPROC_SERVER,
                interface=port.IPortableDeviceKeyCollection)
            self.propertiesToRead.Add(WPD_OBJECT_NAME)
            self.propertiesToRead.Add(WPD_OBJECT_ORIGINAL_FILE_NAME)
            self.propertiesToRead.Add(WPD_OBJECT_CONTENT_TYPE)

    def getName(self):
        if self.name:
            return self.name
        if self.objectID is None:
            return None
        global WPD_OBJECT_NAME, WPD_OBJECT_CONTENT_TYPE, WPD_OBJECT_ORIGINAL_FILE_NAME
        self.name = self.plain_name = self.properties.GetValues(
            self.objectID, self.propertiesToRead).GetStringValue(WPD_OBJECT_NAME)
        self.contentType = str(
            self.properties.GetValues(
                self.objectID,
                self.propertiesToRead).GetGuidValue(WPD_OBJECT_CONTENT_TYPE))
        if self.contentType != "{27E2E392-A111-48E0-AB0C-E17705A05F85}" and self.contentType != "{99ED0160-17FF-4C44-9D98-1D7A6F941921}":
            # its not a folder
            self.name = self.filename = self.properties.GetValues(
                self.objectID, self.propertiesToRead).GetStringValue(WPD_OBJECT_ORIGINAL_FILE_NAME)
        return self.name

    def getChildren(self):
        retObjs = []
        enumObjectIDs = self.content.EnumObjects(
            ctypes.c_ulong(0), self.objectID, ctypes.POINTER(
                port.IPortableDeviceValues)())
        while True:
            numObject = ctypes.c_ulong(16)  # block size, so to speak
            objectIDArray = (ctypes.c_wchar_p * numObject.value)()
            numFetched = ctypes.pointer(ctypes.c_ulong(0))
            # be sure to change the IEnumPortableDeviceObjectIDs 'Next'
            # function in the generated code to have objectids as inout
            enumObjectIDs.Next(
                numObject, ctypes.cast(
                    objectIDArray, ctypes.POINTER(
                        ctypes.c_wchar_p)), numFetched)
            if numFetched.contents.value == 0:
                break
            for i in range(0, numFetched.contents.value):
                curObjectID = objectIDArray[i]
                retObjs.append(
                    PortableDeviceContent(
                        curObjectID,
                        self.content,
                        self.properties,
                        self.propertiesToRead))
#       enumObjectIDs.Release()
        return retObjs

    def getChild(self, name):
        matches = [c for c in self.getChildren() if c.getName() == name]
        if len(matches) == 0:
            # todo throw exception instead of returning none
            return None
        else:
            return matches[0]

    def getPath(self, path):
        cur = self
        for p in path.split("/"):
            cur = cur.getChild(p)
            if cur is None:
                return None
        return cur

    def __repr__(self):
        return "<PortableDeviceContent %s: %s>" % (
            self.objectID, self.getName())

    def uploadStream(self, fileName, inputStream, streamLen):
        global WPD_OBJECT_PARENT_ID, WPD_OBJECT_SIZE, WPD_OBJECT_ORIGINAL_FILE_NAME, WPD_OBJECT_NAME
        objectProperties = comtypes.client.CreateObject(
            types.PortableDeviceValues,
            clsctx=comtypes.CLSCTX_INPROC_SERVER,
            interface=port.IPortableDeviceValues)

        objectProperties.SetStringValue(WPD_OBJECT_PARENT_ID, self.objectID)
        objectProperties.SetUnsignedLargeIntegerValue(
            WPD_OBJECT_SIZE, streamLen)
        objectProperties.SetStringValue(
            WPD_OBJECT_ORIGINAL_FILE_NAME, fileName)
        objectProperties.SetStringValue(WPD_OBJECT_NAME, fileName)
        optimalTransferSizeBytes = ctypes.pointer(ctypes.c_ulong(0))
        pFileStream = ctypes.POINTER(port.IStream)()
        # be sure to change the IPortableDeviceContent
        # 'CreateObjectWithPropertiesAndData' function in the generated code to
        # have IStream ppData as 'in','out'
        fileStream = self.content.CreateObjectWithPropertiesAndData(
            objectProperties,
            pFileStream,
            optimalTransferSizeBytes,
            ctypes.POINTER(
                ctypes.c_wchar_p)())
        fileStream = pFileStream.value
        blockSize = optimalTransferSizeBytes.contents.value
        curWritten = 0
        while True:
            toRead = streamLen - curWritten
            block = inputStream.read(
                toRead if toRead < blockSize else blockSize)
            if len(block) <= 0:
                break
            stringBuf = ctypes.create_string_buffer(block)
            written = fileStream.RemoteWrite(
                ctypes.cast(
                    stringBuf,
                    ctypes.POINTER(
                        ctypes.c_ubyte)),
                len(block))
            curWritten += written
            if(curWritten >= streamLen):
                break
        STGC_DEFAULT = 0
        fileStream.Commit(STGC_DEFAULT)

    def downloadStream(self, outputStream):
        global WPD_RESOURCE_DEFAULT
        resources = self.content.Transfer()
        STGM_READ = ctypes.c_uint(0)
        optimalTransferSizeBytes = ctypes.pointer(ctypes.c_ulong(0))
        pFileStream = ctypes.POINTER(port.IStream)()
        optimalTransferSizeBytes, pFileStream = resources.GetStream(
            self.objectID, WPD_RESOURCE_DEFAULT, STGM_READ, optimalTransferSizeBytes, pFileStream)
        blockSize = optimalTransferSizeBytes.contents.value
        fileStream = pFileStream.value
        buf = (ctypes.c_ubyte * blockSize)()
        # make sure all RemoteRead parameters are in
        while True:
            #buf, leng = fileStream.RemoteRead(blockSize)
            buf, leng = fileStream.RemoteRead(blockSize)
            #buf, leng = fileStream.RemoteRead(buf, ctypes.c_ulong(blockSize))
            if leng == 0:
                break
            buf = bytearray(buf)
            while buf[-1] == 0 and len(buf)>0:
                buf = buf[:-1]

            outputStream.write(buf)

    def delete(self, filename):
        global WPD_OBJECT_ID
    
        element_to_delete = self.getChild(filename)

        if element_to_delete is None:
            return None
        #IPortableDevicePropVariantCollection 
        id = element_to_delete.objectID

        objectProperties = comtypes.client.CreateObject(
            types.PortableDeviceValues,
            clsctx=comtypes.CLSCTX_INPROC_SERVER,
            interface=port.IPortableDeviceValues)

        #objectProperties.SetStringValue(WPD_OBJECT_PARENT_ID, self.objectID)
        objectProperties.SetStringValue(WPD_OBJECT_ID, id)

        id_element_to_delete = objectProperties.GetValue(WPD_OBJECT_ID)

        objectIds = comtypes.client.CreateObject(
            types.PortableDevicePropVariantCollection,
            clsctx=comtypes.CLSCTX_INPROC_SERVER,
            interface=port.IPortableDevicePropVariantCollection)
        
        objectIds.Add(id_element_to_delete)

        self.content.Delete(0, objectIds)

        return element_to_delete



    


class PortableDevice:
    def __init__(self, id):
        self.id = id
        self.desc = None
        self.device = None

    def getDescription(self):
        if self.desc:
            return self.desc

        global deviceManager
        nameLen = ctypes.pointer(ctypes.c_ulong(0))
        deviceManager.GetDeviceDescription(
            self.id, ctypes.POINTER(
                ctypes.c_ushort)(), nameLen)
        name = ctypes.create_unicode_buffer(nameLen.contents.value)
        deviceManager.GetDeviceDescription(self.id, ctypes.cast(
            name, ctypes.POINTER(ctypes.c_ushort)), nameLen)
        self.desc = name.value
        return self.desc
    
    def getID(self):
        if self.id:
            return self.id

        global deviceManager
        nameLen = ctypes.pointer(ctypes.c_ulong(0))
        deviceManager.GetDeviceDescription(
            self.id, ctypes.POINTER(
                ctypes.c_ushort)(), nameLen)
        name = ctypes.create_unicode_buffer(nameLen.contents.value)
        deviceManager.GetDeviceDescription(self.id, ctypes.cast(
            name, ctypes.POINTER(ctypes.c_ushort)), nameLen)
        self.desc = name.value
        return self.id

    def getDevice(self):
        if self.device:
            return self.device
        clientInformation = comtypes.client.CreateObject(
            types.PortableDeviceValues,
            clsctx=comtypes.CLSCTX_INPROC_SERVER,
            interface=port.IPortableDeviceValues)
        self.device = comtypes.client.CreateObject(
            port.PortableDevice,
            clsctx=comtypes.CLSCTX_INPROC_SERVER,
            interface=port.IPortableDevice)
        self.device.Open(self.id, clientInformation)
        return self.device

    def releaseDevice(self):
        if self.device:
            self.device.Release()
            self.device = None

    def getContent(self):
        return PortableDeviceContent(
            ctypes.c_wchar_p("DEVICE"),
            self.getDevice().Content())

    def __repr__(self):
        return "<PortableDevice: %s>" % self.getDescription()


deviceManager = None


def getPortableDevices():
    global deviceManager
    if not deviceManager:
        deviceManager = comtypes.client.CreateObject(
            port.PortableDeviceManager,
            clsctx=comtypes.CLSCTX_INPROC_SERVER,
            interface=port.IPortableDeviceManager)
    pnpDeviceIDCount = ctypes.pointer(ctypes.c_ulong(0))
    deviceManager.GetDevices(
        ctypes.POINTER(
            ctypes.c_wchar_p)(),
        pnpDeviceIDCount)
    if(pnpDeviceIDCount.contents.value == 0):
        return []
    pnpDeviceIDs = (ctypes.c_wchar_p * pnpDeviceIDCount.contents.value)()
    deviceManager.GetDevices(
        ctypes.cast(
            pnpDeviceIDs,
            ctypes.POINTER(
                ctypes.c_wchar_p)),
        pnpDeviceIDCount)
    return [PortableDevice(curId) for curId in pnpDeviceIDs]


def getContentFromDevicePath(dev_id, path=""):
    """
    get the list of element in device
    path is the path to view, if empty the methods shows the contento of the root path
    """
    #path = path.split("/")
    for dev in getPortableDevices():
        if dev_id == dev.getID():
            if path == "":
                cont = dev.getContent()
            else:
                cont = dev.getContent().getPath(path)
            return cont
    return None


if __name__ == "__main__":
    import sys
    import os

    TEST = True

    if TEST:
        target_device = '\\\\?\\usb#vid_2d1f&pid_016f#2lnse20108______________________#{6ac27878-a6fa-4155-ba85-f98f491d4f33}'
        
        print("Devices:")
        all_devices = getPortableDevices() 
        for d in all_devices:
            print(f"{d.getDescription()} id:'{d.getID()}'")
            # print(d.getDevice()) # when i call gedDecive the pointer is created
            print()

            path = "/".join(["MTP volume", "PAGE_001"])
            cont = getContentFromDevicePath(d.getID(), path)
            ch = cont.getChildren()
            for l in cont.getChildren():
                print(f"{l.getName()}")

        print("\nExplore the target device") 
        path = "/".join(["MTP volume", "PAGE_001"])
        cont = getContentFromDevicePath(target_device, path)
        if cont == None:
            print(f"No Device founded with ID: {target_device}")
        else:
            ch = cont.getChildren()
            if len(ch) > 0:
                for l in cont.getChildren():
                    print(f"{l.getName()}")
            else:
                print(f"'{path}' is empty")


        print("\nUpload inkml on target device") 
        src = "data/inkml_file/05_H01.inkml"
        srcSize = os.path.getsize(src)
        dst =  "/".join(["MTP volume", "PAGE_001"])
        cont = getContentFromDevicePath(target_device, dst)
        if not cont:
            print(f"directory {dst} not found")
        else:
            with open(src, "rb") as srcFile:
                cont.uploadStream(os.path.basename(src), srcFile, srcSize)

        

        print("\nUpload save.txt on target device") 
        src = "in_data/assets/save.txt"
        srcSize = os.path.getsize(src)
        dst =  "/".join(["MTP volume"])
        cont = getContentFromDevicePath(target_device, dst)
        if not cont:
            print(f"directory {dst} not found")
        else:
            with open(src, "rb") as srcFile:
                cont.uploadStream(os.path.basename(src), srcFile, srcSize)

        
        
        print("Try to delete not existing file:")
        deleted = cont.delete("no_file")
        print(f"Deleted element:{deleted}")
        
        print("\nDelete 'updated.exe' from root device") 
        to_delete = "updated.txt"
        dst =  "/".join(["MTP volume"])
        cont = getContentFromDevicePath(target_device, dst)
        if not cont:
            print(f"directory {dst} not found")
        else:
            deleted = cont.delete(to_delete)
            print(f"Deleted element:{deleted}")

        print("delete drom PAGE_001")
        to_delete = "05_H01.inkml"
        dst =  "/".join(["MTP volume", "PAGE_001"])
        cont = getContentFromDevicePath(target_device, dst)
        if not cont:
            print(f"directory {dst} not found")
        else:
            deleted = cont.delete(to_delete)
            print(f"Deleted element:{deleted}")






        print("\nDownload inkml to PC")     
        file_name = "05_H01.inkml"
        src = "/".join(["MTP volume", "PAGE_001", file_name])
        dst = "/".join(["_test_out", file_name])
        cont = getContentFromDevicePath(target_device, src)
        if not cont:
            print(f"{dst} not found")
        else:
            with open(dst, "wb") as dstfile:
                cont.downloadStream(dstfile)
            
            # if dst == "-":
            #     tgtFile = sys.stdout
            # else:
            #     tgtFile = open(dst, "wb")
            # cont.downloadStream(tgtFile)
            # if dst != "-":
            #     tgtFile.close()


    if len(sys.argv) > 1 and sys.argv[1] == 'ls':
        if len(sys.argv) == 2:
            print("Devices:")
            all_devices = getPortableDevices() 
            for d in all_devices:
                print(f"{d.getDescription()} id:'{d.getID()}'")
        else:
            path = sys.argv[2]
            cont = getContentFromDevicePath(path)
            if cont:
                print(f"{path} contains:")
                for l in cont.getChildren():
                    print(f"{l.getName()}")
            else:
                print(f"{path} not found")
                exit(1)
    elif len(sys.argv) == 4 and sys.argv[1] == 'cp':
        # copy to target
        src = sys.argv[2]
        srcSize = os.path.getsize(src)
        tgt = sys.argv[3]
        cont = getContentFromDevicePath(tgt)
        if not cont:
            print(f"directory {tgt} not found")
            exit(1)
        srcFile = open(src, "rb")
        cont.uploadStream(os.path.basename(src), srcFile, srcSize)
        srcFile.close()
    elif len(sys.argv) == 4 and sys.argv[1] == 'get':
        # copy to target
        src = sys.argv[2]
        tgt = sys.argv[3]
        cont = getContentFromDevicePath(src)
        if not cont:
            print(f"directory {tgt} not found")
            exit(1)
        if tgt == "-":
            tgtFile = sys.stdout
        else:
            tgtFile = open(tgt, "wb")
        cont.downloadStream(tgtFile)
        if tgt != "-":
            tgtFile.close()
    else:
        print(f"usage: {sys.argv[0]}  TODO")
        exit()