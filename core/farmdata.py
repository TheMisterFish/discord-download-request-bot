class FarmData:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FarmData, cls).__new__(cls)
            cls._instance.farms = {}
        return cls._instance

    def update_farm(self, id, name, channel, link):
        id = id.upper()
        if id not in self.farms:
            self.farms[id] = {"name": name, "links": {}}
        self.farms[id]["name"] = name
        self.farms[id]["links"][channel] = link
        self.farms[id]["id"] = id

    def get_farms(self):
        return list(self.farms.values())
    
    def get_ids(self):
        return list(self.farms.keys())

farmdata = FarmData()