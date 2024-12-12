import os
import time
import platform
import config as C
import mtp


def get_so_USB_devices_list():
    """
    What if different OS?
    """
    devices = []

    if platform.system() == "Windows":
       pass

    elif platform.system() == "Darwin": #MacOS
        # TO TEST
        pass
    elif platform.system() == "Linux":
       pass
        # TO TEST
                    
    return devices


# IoT Manager Class
class IoT_Handler():

    PAGE_FOLDER = "PAGE_001"
    VOLUME_NAME = "MTP volume"
    UPDATED_FILE = "updated.txt"
    SAVE_FILE = C.SAVE_FILE

    STATE_READY = "READY"
    STATE_WRITING = "WRITING"

    def __init__(self, iot_address) -> None:
        self.iot_address = iot_address
        self.current_inkml = None
        self.state = self.STATE_READY # State of the tablet:
                               # "READY" -> waiting for an inkml file
                               # "WRITING" -> IoT tablet in writing mode

    def get_current_state(self):
        return self.state

    def get_current_inkml(self):
        return self.current_inkml
    
    def ls_folder(self, path=""):
        """
        The method returns the list of content of the 'src_path' in the IoT paper.
        If path is empty, the methods shows the root content.
        The root path is the device 'MTP volume'
        """
        path = self.VOLUME_NAME+"/"+path
        path = path.replace("\\", '/')
        path = path.replace("\\\\", '/')
        if path[-1] == '/':
            path = path[:-1]

        cond_list = []
        cont = mtp.getContentFromDevicePath(self.iot_address, path)
        # if not cont:
        #     raise IOT_FolderDontExistError(path)
        if cont != None:
            ch = cont.getChildren()
            if len(ch) > 0:
                for l in cont.getChildren():
                    cond_list.append(l.getName())

        return cond_list
    
    def update_inkml(self, inkml_path, clean_pages=True):
        """
        The method update the inkml file to the IoT tablet
        """
        if self.state == self.STATE_WRITING:
            raise IOT_WritingStateError()

        if clean_pages:
            self.delete_pages()

        self.delete(self.UPDATED_FILE)

        srcSize = os.path.getsize(inkml_path)
        dst =  "/".join([self.VOLUME_NAME, self.PAGE_FOLDER])
        cont = mtp.getContentFromDevicePath(self.iot_address, dst)
        if not cont:
            raise IOT_FolderDontExistError(dst)
        else:
            with open(inkml_path, "rb") as srcFile:
                cont.uploadStream(os.path.basename(inkml_path), srcFile, srcSize)

        self.current_inkml = os.path.basename(inkml_path)
        self.state = self.STATE_WRITING

    def send_stop(self):
        """
        The method sends the "stop writing" signal to the IoT tablet
        ant waits for the "updated" message
        """
        # send 'save.txt'
        srcSize = os.path.getsize(self.SAVE_FILE)
        dst =  self.VOLUME_NAME
        cont = mtp.getContentFromDevicePath(self.iot_address, dst)
        if not cont:
            raise IOT_FolderDontExistError(dst)
        else:
            with open(self.SAVE_FILE, "rb") as srcFile:
                cont.uploadStream(os.path.basename(self.SAVE_FILE), srcFile, srcSize)

        # wait for 'updatet.txt' - ATTENTION ACTIVE WAITING!!!
        root_cont = []
        counter = 0
        sleep = 0.05 #sec
        while "updated.txt" not in root_cont:
            time.sleep(sleep)
            try:
                root_cont = self.ls_folder()
            except:
                root_cont = []
            
            if counter > 30/sleep: # if waiting for more than 30 sec
                raise IOT_StopWritingError("Too long for updatet.txt file")
            
        #time.sleep(0.1)
        
        # return
        self.state = self.STATE_READY

    def download_inkml(self, dst):
        """
        The method download from the IoT tablet the current inkml file 
        (If on the devices there are more than one file with the same name, 
        the method downloads the most recent)
        It saves the file to the 'dst' path destination on the computer.
        """

        if self.state == self.STATE_WRITING:
            raise IOT_WritingStateError()
        
        src = "/".join([self.VOLUME_NAME, self.PAGE_FOLDER, self.current_inkml])
        dst = os.path.join(dst, self.current_inkml)
        cont = mtp.getContentFromDevicePath(self.iot_address, src)
        if not cont:
            raise IOT_FolderDontExistError(src)
        else:
            with open(dst, "wb") as dstfile:
                cont.downloadStream(dstfile)

    def delete(self, path_to_delete):
        """
        The method deletes the file identified by the path passed as parameter.
        It returns de deleted element if it exists, else it returns None.
        """ 
        path_to_delete = os.path.normpath(path_to_delete)
        path_to_delete = [self.VOLUME_NAME] + path_to_delete.split(os.sep)
        to_delete = path_to_delete.pop(-1)
        path_to_delete = "/".join(path_to_delete)

        cont = mtp.getContentFromDevicePath(self.iot_address, path_to_delete)
        if not cont:
            IOT_FolderDontExistError(path_to_delete)
        else:
            deleted = cont.delete(to_delete)
            return deleted
        
        return None
    
    def delete_pages(self):
        """
        The method deletes all the files in the PAGE folder on IoT tablet
        """ 
        pages = self.ls_folder(self.PAGE_FOLDER)

        for page in pages:
            path_to_delete = "/".join([self.PAGE_FOLDER, page])
            self.delete(path_to_delete)


class IoT_Devices_Handler:
    def __init__(self) -> None:
        self.devices_id2address = {}
        self.devices_address2id = {}
        self.devices = []

    def get_devices_list(self):
        self.devices = []
        all_devices = mtp.getPortableDevices() 
        for d in all_devices:
            if "IoT" in d.getDescription():
                if d.getID() in self.devices_address2id:
                    dev_id = self.devices_address2id[d.getID()]
                else:
                    dev_id = len(self.devices)

                self.devices.append(
                {
                    'name':d.getDescription(), 
                    'address':d.getID(),
                    'id': dev_id
                })

                self.devices_id2address[dev_id] = d.getID()
                self.devices_address2id[d.getID()] = dev_id

        return self.devices
    
    def get_dev_address(self, dev_id):
        if any(d['id'] == dev_id for d in self.devices):
            return(self.devices_id2address[dev_id])
        return None
    
    def get_dev_id(self, dev_address):
        if any(d['address'] == dev_address for d in self.devices):
            return(self.devices_address2id[dev_address])
        return None



class IOT_WritingStateError(Exception):
    """
    Exception raised when try to acces the IoT in WRITING State.
    """
    def __init__(self, message="IoT Device in WRITING state"):
        self.message = message
        super().__init__(self.message)

class IOT_FolderDontExistError(Exception):
    """
    Exception raised when try to acces thenot existing folder in IoT device.
    """
    def __init__(self, src,  message="folder not exist!"):
        self.message = f"{src} {message}"
        super().__init__(self.message)

class IOT_StopWritingError(Exception):
    """
    Exception raised if a probelm occur in stop writing operation.
    """
    def __init__(self,  message="Error in Stop Writing"):
        self.message = message
        super().__init__(self.message)





if __name__ == "__main__":

    # list all connected devices
    devices_H = IoT_Devices_Handler()
    devs = devices_H.get_devices_list()
    print(devs)
    print('0', devices_H.get_dev_address(0))
    print('1', devices_H.get_dev_address(1))
    print('2', devices_H.get_dev_address(2))

    # contact device 0
    iot_0 = IoT_Handler(devices_H.get_dev_address(0))

    #explore device 0 content
    cont = iot_0.ls_folder()
    print(cont)
    cont = iot_0.ls_folder("PAGE_0001")
    print(cont)
    cont = iot_0.ls_folder("no")
    print(cont)


    # upload in inkml file on device 0
    src = "data\\inkml_file/05_H01.inkml"
    iot_0.update_inkml(src)

    # stop writing on device 0
    iot_0.send_stop()

    # delete "updated.txt" from IoT root
    # deleted = iot_0.delete("updated.txt")
    # print(f"File deleted {deleted}")

    # update again the .inkml file
    iot_0.update_inkml(src)
    iot_0.send_stop()

    # delete ".inkml" from IoT folder PAGE_001
    # deleted = iot_0.delete("PAGE_001/05_H01.inkml")
    # print(f"File deleted {deleted}")

    # delete all file in PAGE_001
    iot_0.delete_pages()


    # copy inkml file on computer
    iot_0.download_inkml("_test_out")

    # upload  in inkml dile on device 1
    # iot_1 = IoT_Handeler(devices_H.get_dev_address(1))
    # src = "data\inkml_file\\07_H03.inkml"
    # iot_1.update_inkml(src)

    
