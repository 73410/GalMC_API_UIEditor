import os
import json
from mutagen.oggvorbis import OggVorbis

class Resources_Manager:
    cg = []
    background = []
    musics = []
    musics_id = []
    music_length = {}
    voice = []
    voice_id = []
    character = []
    text_data = []
    cg_data= []

    def __init__(self, project_dir):
        self.project_dir = project_dir
        self.load_resources()
        self.write_sound_json()

    def load_resources(self):
        """加载所有资源文件"""
        if not self.project_dir:
            return
        
        # 定义资源目录映射
        resource_dirs = {
            "cg": "assets/galmc_api/texture/cg",
            "background": "assets/galmc_api/texture/background",
            "musics": "assets/galmc_api/sounds/music",
            "voice": "assets/galmc_api/sounds/character",
            "character": "assets/galmc_api/texture/character",
            "text_data": "assets/galmc_api/data/text",
            "cg_data": "assets/galmc_api/data/cg",
        }
        for resource_type, sub_dir in resource_dirs.items():
            full_dir = os.path.join(self.project_dir, sub_dir)
            if os.path.exists(full_dir):
                files = []
                for file_name in os.listdir(full_dir):
                    if os.path.isfile(os.path.join(full_dir, file_name)):
                        files.append(file_name)
                setattr(self, resource_type, files)

    def get_list(self, resource_type):
        """获取指定类型的资源列表"""
        match resource_type:
            case "cg":
                return self.cg
            case "background":
                r = []
                for i in self.cg:
                    r.append(self.save_id("cg", i))
                for i in self.background:
                    r.append(self.save_id("background1", i))
                return r
            case "musics":
                return self.musics_id
            case "voice":
                return self.voice_id
            case "character":
                return self.character
            case "text_data":
                return self.text_data
            case "cg_data":
                return self.cg_data
            case "all_data":
                r = []
                for i in self.text_data:
                    r.append(self.save_id("text_data", i))
                for i in self.cg_data:
                    r.append(self.save_id("cg_data", i))
                return r
            case _:
                return []
    @staticmethod
    def save_id(resource_type, filename):
        resource_dirs = {
            "cg": "texture/cg/",
            "background1": "texture/background/",
            "musics": "sounds/music/",
            "voice": "sounds/character/",
            "character": "texture/character/",
            "text_data": "data/text/",
            "cg_data": "data/cg/"
        }
        if not (resource_type == "all_data" or resource_type == "musics" or resource_type == "voice" or resource_type == "background"):
            return resource_dirs[resource_type] + filename
        else:
            return filename

    def get_length(self,path):
        try:

            audio = OggVorbis(path)
            print(audio.info.length*20)
            return int(audio.info.length*20)
        except ImportError:
            # mutagen不可用，使用简单的替代方案
            try:
                # 尝试读取文件大小估算时长（不准确但可用）
                file_size = os.path.getsize(path)
                # 粗略估算：OGG大约128kbps是每秒16KB
                return max(1, int(file_size / (16 * 1024)))*20
            except:
                return -1
        except:
            return -1
    def write_sound_json(self):
        a = {}
        for i in self.musics:
            # 去掉路径前缀，仅保留文件名
            key = i.replace("assets/galmc_api/sounds/music/", "")
            key = key.rsplit('.', 1)[0]
            a.update({"music."+key :{"category": "music", "sounds":["galmc_api:music/"+key]}})
            full_dir = self.project_dir+"/assets/galmc_api/sounds/music/"+i
            self.music_length.update({"music."+key:self.get_length(full_dir)})
            self.musics_id.append("music."+key)
        for i in self.voice:
            # 去掉路径前缀，仅保留文件名
            key = i.replace("assets/galmc_api/sounds/character/", "")
            key = key.rsplit('.', 1)[0]
            a.update({"character."+key :{"category": "player", "sounds":["galmc_api:character/"+key]}})
            full_dir = self.project_dir + "/assets/galmc_api/sounds/character/" + i
            self.music_length.update({"character."+key: full_dir})
            self.voice_id.append("character."+key)
        sound_json_path = os.path.join(self.project_dir, "assets", "galmc_api", "sound.json")
        with open(sound_json_path, "w", encoding="utf-8") as f:
            json.dump(a, f, ensure_ascii=False, indent=4)
        
    def get_music_length(self, music_id):
        return self.music_length.get(music_id, 0)

    def reset(self):
        self.cg = []
        self.background = []
        self.musics = []
        self.musics_id = []
        self.music_length = {}
        self.voice = []
        self.voice_id = []
        self.character = []
        self.text_data = []
        self.cg_data = []
        self.load_resources()
        self.write_sound_json()


        
