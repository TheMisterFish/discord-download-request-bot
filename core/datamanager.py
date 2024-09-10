class DataManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DataManager, cls).__new__(cls)
            cls._instance.farms = {}
            cls._instance.videos = {}
        return cls._instance

    def update_farm(self, id, name, channel, link):
        id = id.upper()
        if id not in self.farms:
            self.farms[id] = {"name": name, "links": {}}
        self.farms[id]["name"] = name
        self.farms[id]["links"][channel] = link
        self.farms[id]["id"] = id

    def update_video(self, name, channel, link, tag):
        if name not in self.videos:
            self.videos[name] = {"links": {}, "tag": tag}
        self.videos[name]["links"][channel] = link
        self.videos[name]["tag"] = tag

    def get_farms(self):
        return list(self.farms.values())

    def get_farm_ids(self):
        return list(self.farms.keys())

    def get_videos(self):
        return [{"name": name, **data} for name, data in self.videos.items()]

    def get_video_names(self):
        return list(self.videos.keys())

datamanager = DataManager()