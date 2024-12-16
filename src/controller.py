import os
from iot_comunicator import IoT_Devices_Handler, IoT_Handler
import shutil
import random
import config as C

DEFAULT_RES_TMP = C.DEFAULT_RES_TMP
RESULTS_PROTOCOL_FOLDER = C.RESULTS_PROTOCOL_FOLDER
MAX_ID_LEN = C.MAX_ID_LEN
DEFAULT_ORDER = C.DEFAULT_ORDER
ACTIVITES_PATH = C.ACTIVITES_PATH


def init_activities_name():
    if DEFAULT_ORDER:
        ordered_activities = DEFAULT_ORDER
        ordered_activities = [f"{os.path.splitext(el)[0]}.inkml" for el in ordered_activities]
    else:
        ordered_activities = os.listdir(ACTIVITES_PATH)
    
    zpadd_len = len(str(len(ordered_activities)))
    for ind, file_name in enumerate(ordered_activities):
        new_name = f"{str(ind).zfill(zpadd_len)}_{file_name}"

        os.rename(src=os.path.join(ACTIVITES_PATH, file_name),
                  dst=os.path.join(ACTIVITES_PATH, new_name))


def restore_activites_name():
    ordered_activities = os.listdir(ACTIVITES_PATH)
    
    for file_name in ordered_activities:
        new_name = file_name.split("_")
        new_name = "_".join(new_name[1:])

        os.rename(src=os.path.join(ACTIVITES_PATH, file_name),
                  dst=os.path.join(ACTIVITES_PATH, new_name))
        


def reorder_activities(user_name="", len_id=20, ind_start_rnd=4, zfill_act=2):
    fixed_ordered_activities = DEFAULT_ORDER[0:ind_start_rnd]
    random_ordered_activities = DEFAULT_ORDER[ind_start_rnd:]

    if user_name != "":
        #create a seed from username
        #randomize ordered_activities
        if len(user_name) < len_id:
            user_name = user_name.zfill(len_id)
        else:
            user_name = user_name[0:len_id]

        id_bytes = user_name.encode('utf-8')
        seed = int.from_bytes(id_bytes, 'little')

        random.seed(seed)
        random.shuffle(random_ordered_activities)
    
    rename_dict = {}
    for activityname in os.listdir(ACTIVITES_PATH):
        jump_next = False
        for not_change_order_activityname in fixed_ordered_activities:
          if not_change_order_activityname in activityname:
              if not_change_order_activityname == os.path.splitext(activityname)[0]:
                  ind = str(fixed_ordered_activities.index(not_change_order_activityname)).zfill(zfill_act)
                  rename_dict[activityname] = "_".join([ind, activityname])
              jump_next = True
              break
        if jump_next:
            continue
        
        for ind, neworder_activityname in enumerate(random_ordered_activities):
            if neworder_activityname in activityname:
                newname = f"{str(ind+ind_start_rnd).zfill(zfill_act)}_{activityname.split('_')[-1]}"
                rename_dict[activityname] = newname

    for old_name, newname in rename_dict.items():
        os.rename(src=os.path.join(ACTIVITES_PATH, old_name),dst=os.path.join(ACTIVITES_PATH, newname))



class IOT_NotConnectedError(Exception):
    """
    Exception raised when no IoT devices are founded.
    """
    def __init__(self, message="No IoT Device connected!"):
        self.message = message
        super().__init__(self.message)

class IOT_WritingStateError(Exception):
    """
    Exception raised if you try to upload inkml on a IoT in WRITING state.
    """
    def __init__(self, message="IoT Device in WRITING state!"):
        self.message = message
        super().__init__(self.message)

class IOT_ReadyStateError(Exception):
    """
    Exception raised if you try to download inkml from a IoT in READY state.
    """
    def __init__(self, message="IoT Device in READY state!"):
        self.message = message
        super().__init__(self.message)

class IOT_SaveResultsError(Exception):
    """
    Exception raised when an erroro occurrs in save results.
    """
    def __init__(self, message="Error in saving results!"):
        self.message = message
        super().__init__(self.message)

class IOT_NoPrevActivityError(Exception):
    """
    Exception raised when there are no prev activities to delete.
    """
    def __init__(self, message="No previous activity!"):
        self.message = message
        super().__init__(self.message)


class IoT_Controller:
    def __init__(self) -> None:
        self.inkml_history = []
        self.connector = IoT_Connector()
        self.users_status = UsersStatus(RESULTS_PROTOCOL_FOLDER)

    def get_iot_devices(self):
        return self.connector.get_iot_devices()
    
    def set_iot_address(self, iot_id:int):
        self.connector.set_iot_address(iot_id)

    def send_inkml(self, inkml_file):
        self.connector.send_inkml(inkml_file)

    def send_stop(self):
        self.connector.send_stop()

    def download_inkml(self, dst):
        self.connector.download_inkml(dst)

    def get_current_inkml_name(self):
        return self.connector.get_current_inkml_name()
    
    def get_iot_status(self):
        return self.connector.get_iot_status()
    
    def result_mover(self, id_subject,id_experiment,src=DEFAULT_RES_TMP, dst=RESULTS_PROTOCOL_FOLDER, min_file=3, file_to_move=3):
        def get_creation_time(item):
            item_path = os.path.join(src, item)
            return os.path.getctime(item_path)
        
        if len(os.listdir(src))>=min_file:
            dst_current_folder = os.path.join(dst, id_subject, id_experiment)
            if not os.path.exists(dst_current_folder):
                os.makedirs(dst_current_folder)
            curr_repetition_int = len(os.listdir(dst_current_folder))

            if curr_repetition_int == 0:
                curr_repetition_folder =  str(curr_repetition_int).zfill(MAX_ID_LEN)
            else:
                curr_repetition_folder = str(curr_repetition_int).zfill(MAX_ID_LEN)
                list_folders = os.listdir(dst_current_folder)
                list_folders.sort()
                list_folders = [int(x) for x in list_folders]
                curr_repetition_folder =  str(list_folders[-1]+1).zfill(MAX_ID_LEN)

            dst_path = os.path.join(dst_current_folder, curr_repetition_folder)
                        
            os.mkdir(dst_path)
            sorted_items = sorted( os.listdir(src), key=get_creation_time, reverse=True)

            for file in sorted_items[0:file_to_move]:
                shutil.move(os.path.join(src, file), dst_path)

            if len(os.listdir(src)) > 0:
                shutil.rmtree(src)
                os.mkdir(src)

            # update self.inkml_history
            self.users_status.increase_user_status(id_subject, '_'.join(os.path.splitext(id_experiment)[0].split('_')[2:]))
            self.update(dst_path)

            return curr_repetition_int+1
        else:
            raise IOT_SaveResultsError()


    def update(self, dst_path):
        self.inkml_history.append(self.connector.save_last(dst_path))

    def undo_last(self):
        # if in IoT in WRITING state -> send stop and return
        if self.connector.iot.get_current_state() == self.connector.iot.STATE_WRITING:
            self.send_stop()
        else:
            # get last inkml     
            if len(self.inkml_history) > 0:
                last_inkml = self.inkml_history.pop().get_last()

                #delete last recorded activity
                shutil.rmtree(last_inkml)

                # update status
                last_inkml = os.path.normpath(last_inkml)
                _, id_subject, id_repetition, _ = last_inkml.split(os.sep)
                id_repetition = '_'.join(os.path.splitext(id_repetition)[0].split('_')[2:])
                self.users_status.reduce_user_status(id_subject, id_repetition)

            else:
                raise IOT_NoPrevActivityError()




class IoT_Connector:

    class Memento:
        def __init__(self, last_activity) -> None:
            self._last = last_activity

        def get_last(self) -> str:
            """
            The Originator uses this method when restoring its state.
            """
            return self._last


    def __init__(self) -> None:
        self.devices_handeler = IoT_Devices_Handler()
        self.iot_address = None
        self.iot = None

    def get_iot_devices(self):
        """
        get list of connected devices
        """
        list_dev= [] 
        devs = self.devices_handeler.get_devices_list()
        for d in devs:
            list_dev.append(str(d['id']))

        return list_dev
    
    def set_iot_address(self, iot_id:int):
        self.iot_address = self.devices_handeler.get_dev_address(iot_id)
        if self.iot_address == None:
            raise IOT_NotConnectedError()
        self.iot = IoT_Handler(self.iot_address)
    
    def send_inkml(self, inkml_file):
        if self.iot_address is None:
            raise IOT_NotConnectedError()
        if self.iot_address == None:
            raise IOT_NotConnectedError()
        
        if self.iot.get_current_state() == self.iot.STATE_WRITING:
            raise IOT_WritingStateError()

        self.iot.update_inkml(inkml_file)

    def send_stop(self):
        if self.iot_address is None:
            raise IOT_NotConnectedError()
        if self.iot.get_current_state() == self.iot.STATE_READY:
            raise IOT_ReadyStateError()

        self.iot.send_stop()

    def download_inkml(self, dst):
        if self.iot_address is None:
            raise IOT_NotConnectedError()
        self.iot.download_inkml(dst)

    def get_current_inkml_name(self):
        if self.iot_address is None:
            raise IOT_NotConnectedError()
        return self.iot.get_current_inkml()
    
    def get_iot_status(self):
        if self.iot_address is None:
            raise IOT_NotConnectedError()
        return self.iot.get_current_state()

    def save_last(self, last_path):
        return self.Memento(last_path)

class UsersStatus:
    def __init__(self, usr_folder) -> None:
        self.users_status = {}
        self.usr_folder = usr_folder

    def add_user(self, user_name):
        if os.path.exists(os.path.join(self.usr_folder, user_name)):
            activities_state = {}
            for res_act_dir in os.listdir(os.path.join(self.usr_folder, user_name)):
                dir_name = res_act_dir.split('_')
                activity_name = '_'.join(dir_name[2:])
                activities_state[os.path.splitext(activity_name)[0]] = len(os.listdir(os.path.join(self.usr_folder, user_name, res_act_dir)))

            self.users_status[user_name] = activities_state

    def increase_user_status(self, user_name, activity_id):
        if user_name not in self.users_status:
            self.add_user(user_name)

        if activity_id in self.users_status[user_name]:
            self.users_status[user_name][activity_id] += 1
        else:
            self.users_status[user_name][activity_id] = 1

    def reduce_user_status(self, user_name, activity_id):
        if activity_id in self.users_status[user_name]:
            self.users_status[user_name][activity_id] -= 1
        
        if self.users_status[user_name][activity_id] < 0:
            self.users_status[user_name][activity_id] = 0

    def get_user_status(self, user_name):
        if user_name not in self.users_status:
            self.add_user(user_name)
        
        return self.users_status[user_name]
    
    def user_status_2_str(self, user_name):
        str_out = ""

        if user_name not in self.users_status:
            self.add_user(user_name)
            
        if user_name in self.users_status:
            for activity in self.users_status[user_name]:
                str_out += f"{activity}: {self.users_status[user_name][activity]}\n"
            
        return str_out




