


class HeatingZone:
    def __init__(self, name: str, priority: int) -> None:
        self.name: str = name
        self.small_name = name.lower().replace(" ", "_")
        self.priority: int = priority
        self.requesting: bool = False
        self.heating: bool = False
        self.time_heating: int = 0
        self.delay: int = 600
    
    def database_dict(self) -> dict[str, bool|int]:
        return {f"{self.small_name}_requesting": self.requesting,\
            f"{self.small_name}_heating": self.heating,\
            f"{self.small_name}_time_heating": self.time_heating,\
            f"{self.small_name}_delay": self.delay}

    def __str__(self) -> str:
        if self.heating:
            if self.requesting:
                return f"{self.name:>12s} || {'    R' if self.requesting else 'Not r'}equesting | Heating on | On for {self.time_heating:>3d} s"
            else:
                return f"{self.name:>12s} || {'    R' if self.requesting else 'Not r'}equesting | Heating on | On for {self.time_heating:>3d} s | Delay left: {self.delay} s"
        else:
            return f"{self.name:>12s} || {'    R' if self.requesting else 'Not r'}equesting | Heating off"
    
    def __repr__(self) -> str:
        return f"{self.name}"