import os
from PIL import Image
import base64
from io import BytesIO
from bs4 import BeautifulSoup


class Inkml_Manager():
    CODING_TOOLS = {
        "#br_pencil_1_1": "Tip",
        "#br_eraser_1_FF": "Ers",
    }
    CODING_HEAD = {
        'X': 'X cood.',
        'Y': 'Y cood.',
        'F': 'Pressure',
        'Z': 'Height',
        'OTx': 'X tilt',
        'OTy': 'Y tilt',
        'W': 'Thickness',
        'T': 'Time',
    }
    TIP_TYPE_CSV_HEAD = "Tip/Ers"


    def __init__(self, file_path) -> None:
        self.inkml_path = file_path
        self.file_name = os.path.splitext(os.path.basename(file_path))[0]

        with open(file_path, 'r') as f:
            file = f.read() 
        self.soup = BeautifulSoup(file, 'xml')


    def get_templateImage(self):
        """
        The metod extracts the template image from the inkml file
        and return the bmp
        """
        return self._decode_img('templateImage')

    def get_workImage(self):
        """
        The metod extracts the work image from the inkml file
        (the work image is composed by the template and the user trace)
        and return the bmp
        """
        img = self._decode_img('workImage')

        if img is None:
            img = self._decode_img('templateImage')
        return img
        
    def save_templateImage(self, dst=""):
        """
        The methods saves the bmp of the template image in the dst path
        """
        im = self._decode_img('templateImage')
        im.save(os.path.join(dst, self.file_name+'_template.bmp'))

    def save_workImage(self, dst=""):
        """
        The methods saves the bmp of the work image in the dst path
        """
        im = self._decode_img('workImage')
        if not im:
            self.save_templateImage(dst)
        else:
            im.save(os.path.join(dst, self.file_name+'.bmp'))

    def _decode_img(self, img_tag):
        """
        The method decodes the image in the tag 'img_tag' of the inkml file and returns the bmp
        """
        img_tag = self.soup.find_all(img_tag)
        if len(img_tag)>0:
            img_tag = img_tag[0]
            img_64 = base64.b64decode(img_tag.text)
            im = Image.open(BytesIO(img_64))
            return im

        return None

    def get_csv(self):
        """
        The methods extracts the trace information and saves them in a .csv file
        """
        head = self._get_channels()
        trace = self._get_trace()
        
        head_str = ""
        for el in head:
            if el['name'] in self.CODING_HEAD:
                head_str += f"{self.CODING_HEAD[el['name']]},"
            else:
                head_str += f"{el['name']},"
        head_str += self.TIP_TYPE_CSV_HEAD
        if head_str[-1] == ',':
            head_str=head_str[:-1]

        return head_str, trace

    def save_csv(self, dst=""):
        """
        The methods extracts the trace information and saves them in a .csv file
        """
        context = self.soup.find("inkml:ink")

        if context is None:
            head, csv_rows = [], []
        else:
            head, csv_rows = self.get_csv()

        with open(os.path.join(dst, self.file_name+(".csv")), "w", encoding="utf-8") as out_file:
            out_file.write(f"{head}\n")
            for row in csv_rows:
                out_file.write(f"{row}\n")


        pass

    def _get_channels(self):
        """
        The method extracts the channel from the inkml file
        """
        #context = self.soup.find_all("inkml:context")
        context = self.soup.find("inkml:context",{"xml:id":"ctx0"})
        traceFormat = context.findChildren("inkml:traceFormat")
        chn_tags = traceFormat[0].findChildren()

        channels = []
        for chn in chn_tags: 
            channels.append(chn.attrs)

        return channels

    def _get_trace(self):
        """
        The method decodes the image in the tag 'img_tag' of the inkml file and returns the bmp
        """

        trace_tags = self.soup.find_all("inkml:trace")

        trace = []
        for tr in trace_tags:
            tr_type = tr['type']
            tr_timeoffset = tr['timeOffset']
            tr_brush = tr['brushRef']

            tip = self.CODING_TOOLS[tr['brushRef']]
            tr_points = tr.contents[0].replace('\n' ,'').split(',')

            for p in tr_points:
                seq = p.split(" ")
                seq.append(tip)

                trace.append(','.join(seq))

        return trace

if __name__ == "__main__":
    print("Test inkml Manager")

    inkml_path = "_test_out/05_H01.inkml"
    out_folder = "_test_out"

    manager = Inkml_Manager(inkml_path)

    manager.save_templateImage(dst=out_folder)
    manager.save_workImage(dst=out_folder)
    
    manager.save_csv(dst=out_folder)

    print("Done!")

